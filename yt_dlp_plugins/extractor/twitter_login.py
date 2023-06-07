import json

from yt_dlp.utils import ExtractorError, traverse_obj, try_call
from yt_dlp.extractor.twitter import TwitterBaseIE


class TwitterLoginBaseIE(TwitterBaseIE, plugin_name='TwitterLogin'):
    _NETRC_MACHINE = 'twitter'
    _flow_token = None

    _LOGIN_INIT_DATA = json.dumps({
        'input_flow_data': {
            'flow_context': {
                'debug_overrides': {},
                'start_location': {
                    'location': 'unknown'
                }
            }
        },
        'subtask_versions': {
            'action_list': 2,
            'alert_dialog': 1,
            'app_download_cta': 1,
            'check_logged_in_account': 1,
            'choice_selection': 3,
            'contacts_live_sync_permission_prompt': 0,
            'cta': 7,
            'email_verification': 2,
            'end_flow': 1,
            'enter_date': 1,
            'enter_email': 2,
            'enter_password': 5,
            'enter_phone': 2,
            'enter_recaptcha': 1,
            'enter_text': 5,
            'enter_username': 2,
            'generic_urt': 3,
            'in_app_notification': 1,
            'interest_picker': 3,
            'js_instrumentation': 1,
            'menu_dialog': 1,
            'notifications_permission_prompt': 2,
            'open_account': 2,
            'open_home_timeline': 1,
            'open_link': 1,
            'phone_verification': 4,
            'privacy_options': 1,
            'security_key': 3,
            'select_avatar': 4,
            'select_banner': 2,
            'settings_list': 7,
            'show_code': 1,
            'sign_up': 2,
            'sign_up_review': 4,
            'tweet_selection_urt': 1,
            'update_users': 1,
            'upload_media': 1,
            'user_recommendations_list': 4,
            'user_recommendations_urt': 1,
            'wait_spinner': 3,
            'web_modal': 1
        }
    }, separators=(',', ':')).encode()

    def _fetch_guest_token(self, headers, display_id):
        headers.pop('x-guest-token', None)
        self._guest_token = traverse_obj(self._download_json(
            f'{self._API_BASE}guest/activate.json', display_id,
            'Downloading guest token', data=b'', headers=headers), 'guest_token')
        if not self._guest_token:
            raise ExtractorError('Could not retrieve guest token')

    def _set_base_headers(self):
        headers = self._AUTH.copy()
        csrf_token = try_call(lambda: self._get_cookies(self._API_BASE)['ct0'].value)
        if csrf_token:
            headers['x-csrf-token'] = csrf_token
        return headers

    def _call_login_api(self, note, headers, query={}, data=None):
        response = self._download_json(
            f'{self._API_BASE}onboarding/task.json', None, note,
            headers=headers, query=query, data=data, expected_status=400)
        error = traverse_obj(response, ('errors', 0, 'message', {str}))
        if error:
            raise ExtractorError(f'Login failed, Twitter API says: {error}', expected=True)
        elif traverse_obj(response, 'status') != 'success':
            raise ExtractorError('Login was unsuccessful')

        subtask = traverse_obj(
            response, ('subtasks', ..., 'subtask_id', {str}), get_all=False)
        if not subtask:
            raise ExtractorError('Twitter API did not return next login subtask')

        self._flow_token = response['flow_token']

        return subtask

    def _perform_login(self, username, password):
        if self.is_logged_in:
            return

        self._request_webpage('https://twitter.com/', None, 'Requesting cookies')
        headers = self._set_base_headers()
        self._fetch_guest_token(headers, None)
        headers.update({
            'content-type': 'application/json',
            'x-guest-token': self._guest_token,
            'x-twitter-client-language': 'en',
            'x-twitter-active-user': 'yes',
            'Referer': 'https://twitter.com/',
            'Origin': 'https://twitter.com',
        })

        def build_login_json(*subtask_inputs):
            return json.dumps({
                'flow_token': self._flow_token,
                'subtask_inputs': subtask_inputs
            }, separators=(',', ':')).encode()

        def input_dict(subtask_id, text):
            return {
                'subtask_id': subtask_id,
                'enter_text': {
                    'text': text,
                    'link': 'next_link'
                }
            }

        next_subtask = self._call_login_api(
            'Downloading flow token', headers, query={'flow_name': 'login'}, data=self._LOGIN_INIT_DATA)

        while self.is_logged_in is False:
            del self.__dict__['is_logged_in']

            if next_subtask == 'LoginJsInstrumentationSubtask':
                next_subtask = self._call_login_api(
                    'Submitting JS instrumentation response', headers, data=build_login_json({
                        'subtask_id': next_subtask,
                        'js_instrumentation': {
                            'response': '{}',
                            'link': 'next_link'
                        }
                    }))

            elif next_subtask == 'LoginEnterUserIdentifierSSO':
                next_subtask = self._call_login_api(
                    'Submitting username', headers, data=build_login_json({
                        'subtask_id': next_subtask,
                        'settings_list': {
                            'setting_responses': [{
                                'key': 'user_identifier',
                                'response_data': {
                                    'text_data': {
                                        'result': username
                                    }
                                }
                            }],
                            'link': 'next_link'
                        }
                    }))

            elif next_subtask == 'LoginEnterAlternateIdentifierSubtask':
                next_subtask = self._call_login_api(
                    'Submitting alternate identifier', headers,
                    data=build_login_json(input_dict(next_subtask, self._get_tfa_info(
                        'one of username, phone number or email that was not used as --username'))))

            elif next_subtask == 'LoginEnterPassword':
                next_subtask = self._call_login_api(
                    'Submitting password', headers, data=build_login_json({
                        'subtask_id': next_subtask,
                        'enter_password': {
                            'password': password,
                            'link': 'next_link'
                        }
                    }))

            elif next_subtask == 'AccountDuplicationCheck':
                next_subtask = self._call_login_api(
                    'Submitting account duplication check', headers, data=build_login_json({
                        'subtask_id': next_subtask,
                        'check_logged_in_account': {
                            'link': 'AccountDuplicationCheck_false'
                        }
                    }))

            elif next_subtask == 'LoginTwoFactorAuthChallenge':
                next_subtask = self._call_login_api(
                    'Submitting 2FA token', headers, data=build_login_json(input_dict(
                        next_subtask, self._get_tfa_info('two-factor authentication token'))))

            elif next_subtask == 'LoginAcid':
                next_subtask = self._call_login_api(
                    'Submitting confirmation code', headers, data=build_login_json(input_dict(
                        next_subtask, self._get_tfa_info('confirmation code sent to your email or phone'))))

            elif next_subtask == 'LoginSuccessSubtask':
                raise ExtractorError('Twitter API did not grant auth token cookie')

            else:
                raise ExtractorError(f'Unrecognized subtask ID "{next_subtask}"')

        self.report_login()

    def _call_api(self, path, video_id, query={}, graphql=False):
        headers = self._set_base_headers()
        if self.is_logged_in:
            headers.update({
                'x-twitter-auth-type': 'OAuth2Session',
                'x-twitter-client-language': 'en',
                'x-twitter-active-user': 'yes',
            })

        for first_attempt in (True, False):
            if not self.is_logged_in:
                if not self._guest_token:
                    self._fetch_guest_token(headers, video_id)
                headers['x-guest-token'] = self._guest_token

            allowed_status = {400, 401, 403, 404} if graphql else {403}
            result = self._download_json(
                (self._GRAPHQL_API_BASE if graphql else self._API_BASE) + path,
                video_id, headers=headers, query=query, expected_status=allowed_status,
                note=f'Downloading {"GraphQL" if graphql else "legacy API"} JSON')

            if result.get('errors'):
                errors = ', '.join(set(traverse_obj(result, ('errors', ..., 'message', {str}))))
                if not self.is_logged_in and first_attempt and 'bad guest token' in errors.lower():
                    self.to_screen('Guest token has expired. Refreshing guest token')
                    self._guest_token = None
                    continue

                raise ExtractorError(
                    f'Error(s) while querying API: {errors or "Unknown error"}', expected=True)

            return result


TwitterBaseIE._NETRC_MACHINE = TwitterLoginBaseIE._NETRC_MACHINE
TwitterBaseIE._flow_token = TwitterLoginBaseIE._flow_token
TwitterBaseIE._LOGIN_INIT_DATA = TwitterLoginBaseIE._LOGIN_INIT_DATA
TwitterBaseIE._fetch_guest_token = TwitterLoginBaseIE._fetch_guest_token
TwitterBaseIE._set_base_headers = TwitterLoginBaseIE._set_base_headers
TwitterBaseIE._call_login_api = TwitterLoginBaseIE._call_login_api
TwitterBaseIE._perform_login = TwitterLoginBaseIE._perform_login
TwitterBaseIE._call_api = TwitterLoginBaseIE._call_api

__all__ = []
