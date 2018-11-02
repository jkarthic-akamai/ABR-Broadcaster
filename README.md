# Adaptive Bitrate Broadcaster

Adaptive Bitrate Broadcaster provides a simple interface for live encoders of audio and video streams for adaptive bitrate streaming over HTTP. It supports two most popular Adaptive Bitrate(ABR) protocols namely HLS and DASH. It provides two method of interfaces.
- HTTP-based REST API interface.
- Web based GUI

## Installation
See [INSTALL.md](INSTALL.md) for installation instructions

## Usage

The broadcaster can be used either with Web GUI interface or with REST API interface. They listen on port 8888.

### Web GUI
Open the Virtual Host URL http://<ip address>:8888 in your Browser. For example go to [http://127.0.0.1:8888](http://127.0.0.1:8888), when opening the browser from the same machine as ABR Broadcaster. Otherwise replace 127.0.0.1 with the IP address of the ABR Broadcaster.
The usage of the webpage should be simple and self explanatory.

### REST API interface

Refer to the [API documentation](API.md) for details and examples of REST API based usage.

## Known Issues

- Video codec `h264_videotoolbox` does not work resolutions 240p and below.
