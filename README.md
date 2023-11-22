A [yt-dlp](https://github.com/yt-dlp/yt-dlp) extractor [plugin](https://github.com/yt-dlp/yt-dlp#plugins) implementing credentialed login for Twitter

---

## NOTICE

This plugin has been made obsolete by [yt-dlp version 2023.06.08.184733](https://github.com/yt-dlp/yt-dlp-nightly-builds/releases/tag/2023.06.08.184733), [commit d1795f4](https://github.com/yt-dlp/yt-dlp/commit/d1795f4a6af99c976c9d3ea2dabe5cf4f8965d3c)

**Support for Twitter login has now been added in yt-dlp. As such, this plugin will no longer be updated, and it has been disabled for yt-dlp versions where it is obsolete**

Update your yt-dlp to the latest version (`yt-dlp -U`) if you have not already.

---

 * Pass your web browser's user-agent as an argument to the `--user-agent` option if you want to avoid a "new device login" notification being triggered every time you use this plugin

 * When yt-dlp is logging in to Twitter, it may prompt you for an "alternate identifier" (see next bullet point), a confirmation code, or a two-factor authentication token

 * After you've used yt-dlp to log into Twitter, Twitter may begin requiring an "alternate idenitifier" to be entered upon each sign-in. This can be either your username, email or phone number, but it cannot be the same identifier you submitted as `--username`

 * If your account does not have 2FA enabled, you can use the `-2` option to pass your account's "alternate identifier" with your command, e.g. `-u "email@example.com" -p "strong_password" -2 "username"`

## Installation

Requires yt-dlp version [2023.05.01.235542](https://github.com/yt-dlp/yt-dlp-nightly-builds/releases/tag/2023.05.01.235542) to [2023.06.08.183630](https://github.com/yt-dlp/yt-dlp-nightly-builds/releases/tag/2023.06.08.183630).

You can install this package with pip:
```
python3 -m pip install -U https://github.com/bashonly/yt-dlp-TwitterLogin/archive/master.zip
```

See [yt-dlp installing plugins](https://github.com/yt-dlp/yt-dlp#installing-plugins) for the many other ways this plugin package can be installed.
