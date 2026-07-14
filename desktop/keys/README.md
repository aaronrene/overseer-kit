# Desktop release public keys (§QR.5.3 / §QR.6.3)

This directory holds **public** verifying material only for Linux detached
signatures on `.AppImage` installers (minisign by default).

| Allowed | Forbidden |
| --- | --- |
| `*.pub`, `*.minisign.pub`, `*.asc` (public) | Private keys, `.p12`, `.pfx`, `.key`, passphrases |
| This README | Anything matching secret patterns |

Private signing keys live only as GitHub Actions secrets (`LINUX_SIGNING_KEY`,
optional `LINUX_SIGNING_KEY_PASSWORD`). Never commit private key material here.

Kit dogfood Apple notarization mode: **App Store Connect API key** preferred in
CI when configured (`APPLE_API_KEY` + `APPLE_API_KEY_ID` + `APPLE_API_ISSUER` +
`APPLE_TEAM_ID`); otherwise app-specific password mode
(`APPLE_ID` + `APPLE_APP_SPECIFIC_PASSWORD` + `APPLE_TEAM_ID`).
