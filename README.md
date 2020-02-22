# flexget-synology
Synology Plugin for FlexGet

This is an output plugin that will send magnet links to a Synology NAS to download.

# Configuration

```
templates:
  TV:
    series:
      - Show A
      - Show B
    synology:
      host: diskstation
      port: 5001
      secure: true
      verify: false
      username: synology
      password: mypassword
```

By default this uses `https`, which is controlled by the `secure` flag. For most home users, the Synology will have a self-signed certificate, so by default the certificates are not verified (controlled by the `verify` flag).

