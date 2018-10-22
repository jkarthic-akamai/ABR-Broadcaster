# Adaptive Bitrate Broadcaster

Adaptive Bitrate Broadcaster provides a simple interface for live encoders of audio and video streams for adaptive bitrate streaming over HTTP. It supports two most popular Adaptive Bitrate(ABR) protocols namely HLS and DASH. It provides two method of interfaces.
- HTTP-based REST API interface.
- Web based GUI

## Installation
See [INSTALL.md](INSTALL.md) for installation instructions

## Usage

The Host Name `broadcaster.local` needs to get resolved to proper IP address. We need to add entries to `/etc/hosts` in order to access it from web browser. `/etc/hosts` file should be modified on the machine that runs the Web Browser, which may not be same as the machine on which ABR Broadcaster is installed.

For example if the IP address of the ABR Broadcaster's machine is `172.24.50.1` then following line needs to added to the `/etc/hosts` file.

```
172.24.50.1       broadcaster.local
```

If the web browser is opened in the same machine as where the ABR-machine is installed(say on a Laptop for example) then `127.0.0.1` IP address could be used for better ease of access.

```
127.0.0.1       broadcaster.local
```

NOTE: If you are using any kind of VPN in your machine, it is recommended to disconnect the same when making the above changes to `/etc/hosts` file. Because some VPN clients overwrite your changes to `/etc/hosts` file during disconnect, as they try to restore the original `/etc/hosts` file. You can connect back to the VPN once the above changes are done.

The broadcaster can be used either with Web GUI interface or with REST API interface.

### Web GUI
Open the Virtual Host URL [http://broadcaster.local](http://broadcaster.local) in your Browser. The usage of the webpage should be simple and self explanatory.

### REST API interface

Refer to the [API documentation](API.md) for details and examples of REST API based usage.
