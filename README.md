A [yt-dlp](https://github.com/yt-dlp/yt-dlp) extractor [plugin](https://github.com/yt-dlp/yt-dlp#plugins) implementing credentialed login for Twitter

---

 * Pass your web browser's user-agent as an argument to the `--user-agent` option if you want to avoid a "new device login" notification being triggered every time you use this plugin

 * When yt-dlp is logging in to Twitter, it may prompt you for an "alternate identifier" (see next bullet point), a confirmation code, or a two-factor authentication token

 * After you've used yt-dlp to log into Twitter, Twitter may begin requiring an "alternate idenitifier" to be entered upon each sign-in. This can be either your username, email or phone number, but it cannot be the same identifier you submitted as `--username`

 * If your account does not have 2FA enabled, you can use the `-2` option to pass your account's "alternate identifier" with your command, e.g. `-u "email@example.com" -p "strong_password" -2 "username"`

## Installation

Requires yt-dlp [2023.05.01](https://github.com/yt-dlp/yt-dlp-nightly-builds/releases/tag/2023.05.01.235542) or above.

You can install this package with pip:
```
python3 -m pip install -U https://github.com/bashonly/yt-dlp-TwitterLogin/archive/master.zip
```

See [yt-dlp installing plugins](https://github.com/yt-dlp/yt-dlp#installing-plugins) for the many other ways this plugin package can be installed.
