# Introduction

ABR Broadcaster provides REST-like API for the following tasks
- Start an encoding instance
- Stop an encoding instance
- Get status of all running instances

This section will cover usage of these APIs with examples. In all the examples `172.24.50.1` is used as the IP address of ABR Broadcaster. Replace `172.24.50.1` with the actual IP address of the ABR Broadcaster, as per your network setup.

# Encoder Configuration

All the REST API communications regarding encoder configurations happens via JSON format. An example JSON structure for encoder configuration is provided below.

```json
{
    "input_id": "0",
    "audio": {
        "aud_0": {
            "bitrate": "192"
        },
        "aud_1": {
            "bitrate": "64"
        }        
    },
    "video": {
        "speed_preset": "fast",
        "rate_control": "cbr",
        "enable_cc": "on",
        "num_b_frame": 8,
        "variants": [
            {
                "bitrate": "5000",
                "video_width": "-1",
                "video_height": "-1",
                "audio_tag": "aud_0"
            },
            {
                "bitrate": "2000",
                "video_width": "1280",
                "video_height": "720",
                "audio_tag": "aud_0"
            },
            {
                "bitrate": "1000",
                "video_width": "720",
                "video_height": "480",
                "audio_tag": "aud_1"
            }
        ]
    },
    "output": {
        "out_type": "HLS",
        "segment_size": "2",
        "create_muxed_av": "off",
        "ingest_url": "http://p-ep123456.i.akamaientrypoint.net/123456/testing",
        "b_ingest_url": "http://b-ep123456.i.akamaientrypoint.net/123456-b/testing",
    }
}
```

Each an every field in the above JSON is defined below.

## input_id

Input ID from which audio/video data should be captured for encoding.

*Valid Values* : 0 to <Number of input devices - 1>

*Type* : Integer
 
## audio

This section contains list of audio stream configurations.

### audio stream name (aud_0, aud_1, etc.,)

Name of the audio stream configuration

*Valid Values* : Any string with alpha numerical characters

*Type* : String

### bitrate

Audio encoding bitrate in kbps.

*Valid Values* : 32 to 320

*Type* : Integer

## video

This section Contains video encoding parameters.

### speed_preset

Encoding speed configuration. A slower preset will provide better quality but will consume more CPU resource.

*Valid Values* : `slower`, `slow`, `medium`, `fast`, `faster`, `veryfast`, `superfast`, `ultrafast`

*Type* : String

### enable_cc

Flag to enable closed caption. Applicable only if closed captions is present in input.

*Valid Values* : `on`, `off`

*Type* : String

### num\_b\_frame

Maximum number of consecutive B frames.

*Valid Values* : 0 to 8

*Type* : Integer

### rate_control

Encoding bitrate mode.

*Valid Values* : `cbr`, `vbr`

*Type* : String

### variants

Contains a list of variant video streams. Video stream's bitrate, resolution and audio stream name should be mentioned for each variant.

### bitrate

Video encoding bitrate in kbps.

*Valid Values* : 200 to 20000

*Type* : Integer

### video_width

Output video width in pixels. If set to -1, output video width will be same as the input video width.

*Valid Values* : 160 to 4096 OR -1

*Type* : Integer
	
### video_height

Output video height in pixels. If set to -1, output video height will be same as the input video height.

*Valid Values* : 160 to 2160 OR -1

*Type* : Integer

### audio_tag

Indicates which audio stream to be used along which this video variant. Applicable only for HLS output. For DASH and CMAF output all audio streams are mapped to all video streams.

*Valid Values* : Any string with alpha numerical characters. But value provided here should be a valid audio stream name already mentioned in [audio](#audio) section.

*Type* : String

## output

This section contains output stream configuration.

### out_type

Output format type

*Valid Values* : `HLS`, `DASH`, `CMAF`

*Type* : String

### segment_size

Segment duration in seconds.

*Valid Values* : 1 to 60

*Type* : Integer

### seg_in_subfolder

Flag to create segments in subfolders.

*Valid Values* : `on`, `off`

*Type* : String

### create\_muxed\_av

Flag to enable the muxing of audio and video into a single TS stream. Applicable only when `out_type` is `HLS`

*Valid Values* : `on`, `off`

*Type* : String

### ingest_url

HTTP Ingest server URL. All the segments and playlist will be uploaded to this given URL using HTTP PUT/POST.
It should be noted that this should be just the base URL. The manifest files will be internally named as master.m3u8 and out.mpd for HLS and DASH respectively

*Valid Values* : A valid http URL

*Type* : String

### b\_ingest\_url

Same as [ingest_url](#ingest_url). The stream will also be uploaded this is Backup URL.

*Valid Values* : A valid http URL

*Type* : String

### enable\_abs\_seg\_path

Flag to enable insertion of absolute segment path in the media manifest file. Applicable only when `out_type` is `HLS`.

*Valid Values* : `on`, `off`

*Type* : String

### abs\_seg\_path\_base_url

The absolute base URL that should be used for segment paths in media playlists. Applicable only when `out_type` is `HLS` and `enable_abs_seg_path` is `on`.

*Valid Values* : A valid http URL

*Type* : String

### dash_chunked

Flag to enable chunking in the mp4 segment. Each frame will be created in a MOOF/MDAT fragment. Applicable only when `out_type` is `DASH` or `CMAF`.

*Valid Values* : `on`, `off`

*Type* : String

### dash_segtimeline

Flag to enable SegmentTimeline embedded in the DASH number scheme template. Applicable only when `out_type` is `DASH` or `CMAF`.

*Valid Values* : `on`, `off`

*Type* : String

## Input Status

This section contains information about the input source. An example input status section below.

```json
        "input": {
            "status": "Active",
            "width" : "1920",
            "height": "1080",
            "scantype" : "p",
            "framerate" : "24"
        }
```

### status

Indicates if input source is detected or not. Value `Active` indicates that source is detected.

### width

Video width of the input source in pixels.

### height

Video height of the input source in pixels.

### scantype

Scan Type of the input source. `p` means progressive and `i` means interlaced.

### framerate

Video frame rate of input source

# Start an encode instance

**Path** : http://*ip_address*:8888/broadcaster/

**Request Type** : POST

**Request Body** : [Encoder Configuration JSON](#encoder-configuration) without [input status](#input-status) section

**Examples** :

``` 
curl -X POST http://172.24.50.1:8888/broadcaster/ -d @<path-to-json-config-file>  --header "Content-Type: application/json"
curl -X POST http://172.24.50.1:8888/broadcaster/ -d '{< json configuration >}'  --header "Content-Type: application/json"
```

# Stop an encode instance

**Path** : http://*ip_address*:8888/broadcaster/<input_id>

**Request Type** : DELETE

**Examples** :

```
curl -X DELETE http://172.24.50.1:8888/broadcaster/0
```

# Stop all encode instances

**Path** : http://*ip_address*:8888/broadcaster/

**Request Type** : DELETE

**Examples** :

```
curl -X DELETE http://172.24.50.1:8888/broadcaster/
```

# Get encoder status for a input

**Path** : http://*ip_address*:8888/broadcaster/<input_id>

**Request Type** : GET

**Response body** : [Encoder Configuration JSON](#encoder-configuration)

**Examples** :

```
curl -X GET http://172.24.50.1:8888/broadcaster/0
```

# Get encoder status for all inputs

**Path** : http://*ip_address*:8888/broadcaster/

**Request Type** : GET

**Response body** : JSON array of [Encoder Configurations](#encoder-configuration) within the key name `devices`

**Examples** :

```
curl -X GET http://172.24.50.1:8888/broadcaster/
```

# Conclusion

The Web UI uses these REST APIs for the every communication with the encoder. Hence for more clarification and subtle details, it is better to have a look at the transactions of Web UI directly from your browser. And ofcourse pull requests are welcome to make this document better and complete.
