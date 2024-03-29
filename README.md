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
      - Show C:
          set:
            # Destination can be specified per/series and supports jinja expressions
            destination: video/{{ series_name|replace(' ','.') }}
    synology:
      host: diskstation
      port: 5001
      secure: true
      verify: false
      username: synology
      password: mypassword
      # Optional destination folder to use by default for all series
      destination: video/Download
```

By default this uses `https`, which is controlled by the `secure` flag. For 
most home users, the Synology will have a self-signed certificate, so by 
default the certificates are not verified (controlled by the `verify` flag).

The `destination` option can be used to specify the target path of the 
download on the Synology system starting from a shared path.  This cannot
specify a path that does not already exist, doing so will result in the 
error: `Destination does not exist`
