# Copyright (c) 2018, Akamai Technologies
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import urlparse
import subprocess
import shlex
import time
import os
import sys
import re
import json

working_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(working_dir)
import wc_codecs as codecs
import wc_capture as capture
import wc_configdb as configdb
import wc_stopencoder as stopencoder
import wc_store_load_input_cfg as store_load_input_cfg
import wc_utils as wc_utils
import wc_ffmpeg_args as wc_ffmpeg_args

USER_AGENT = 'Akamai_Broadcaster_v1.0'

def store_default_config(default_config, curr_config):
    for key in default_config.keys():

        if key == 'output':
            for out_params in default_config[key]:
                try:
                    if not out_params in curr_config[key]:
                        raise Exception('Storing default value for ' + str(out_params))
                except Exception as e:
                    print e
                    curr_config[key][out_params] = default_config[key][out_params]

        elif key == 'video':
            for common_vid_params in default_config[key]:
                try:
                    if not common_vid_params in curr_config[key]:
                        raise Exception('Storing default value for ' + str(common_vid_params))
                except Exception as e:
                    print e
                    curr_config[key][common_vid_params] = default_config[key][common_vid_params]

            for v in range(0, len(curr_config['video']['variants'])):
                for vid_params in default_config['video']['variants'][0]:
                    try:
                        if not vid_params in curr_config['video']['variants'][v]:
                            raise Exception('Storing default value for [video] ' + \
                                            str(vid_params))
                    except Exception as e:
                        print e
                        curr_config['video']['variants'][v][vid_params] = \
                                  default_config['video']['variants'][0][vid_params]

        elif key == 'audio':
            for aud_tag in curr_config[key]:
                default_aud_tag = default_config[key].keys()[0]
                for aud_params in default_config[key][default_aud_tag]:
                    try:
                        if not aud_params in curr_config[key][aud_tag]:
                            raise Exception('Storing default value for [audio] ' + str(aud_params))
                    except Exception as e:
                        print e
                        curr_config[key][aud_tag][aud_params] = default_config[key][default_aud_tag][aud_params]
        else:
            try:
                if not key in curr_config:
                    raise Exception('Storing default value for ' + str(key))
            except Exception as e:
                print e
                curr_config[key] = default_config[key]

def validate_encoder_params(encoder_params):
    min_video_bitrate = 200
    max_video_bitrate = 20000

    min_audio_bitrate = 32
    max_audio_bitrate = 320

    min_segment_size = 1
    max_segment_size = 60

    min_video_width = 160
    min_video_height = 120
    max_video_width = 4096
    max_video_height = 2160

    num_devices = capture.get_devices(False)
    input_id = encoder_params['input_id']
    out_type = encoder_params['output']['out_type']

    # TODO(Karthick) : Security RISK. More input validation needs to done here
    if int(input_id) < 0 or \
       int(input_id) > int(num_devices):
        msg = 'Invalid input_id:' + str(input_id)
        return False, msg

    if len(encoder_params['video']['variants']) <= 0:
        msg = 'No video bitrates specified'
        return False, msg

    num_vid_sub_streams = len(encoder_params['video']['variants'])
    num_aud_sub_streams = len(encoder_params['audio'])

    for n in range(0, num_vid_sub_streams):
        vid_config = encoder_params['video']['variants']

        video_codec = vid_config[n]['codec']
        if video_codec not in codecs.get_codecs():
            msg = 'Selected codec ' + video_codec + ' not supported'
            return False, msg

        video_bitrate = wc_utils.to_int(vid_config[n]['bitrate'])

        try:
            video_width = int(vid_config[n]['video_width'])
            video_height = int(vid_config[n]['video_height'])
        except:
            msg = 'Invalid video_width or video_height:' + \
                   str(vid_config[n]['video_width']) + ' or ' + \
                   str(vid_config[n]['video_height'])
            return False, msg

        if (video_bitrate > max_video_bitrate) or (video_bitrate < min_video_bitrate) :
            msg = 'Invalid video_bitrate:' + str(video_bitrate)
            return False, msg

        if (video_width != -1 and (video_width < min_video_width or
                                   video_width > max_video_width or
                                   (video_width % 2) != 0)) :
            msg = 'Invalid video_width: ' + str(video_width)
            msg += ' min:' + str(min_video_width) + ' max:' + str(max_video_width)
            msg += ' and video_width is expected to be multiple of 2'
            return False, msg
        if (video_height != -1 and (video_height < min_video_height or
                                    video_height > max_video_height or
                                    (video_height % 2) != 0)) :
            msg = 'Invalid video_height: ' + str(video_height)
            msg += ' min:' + str(min_video_height) + ' max:' + str(max_video_height)
            msg += ' and video_height is expected to be multiple of 2'
            return False, msg

    speed_preset = encoder_params['video']['speed_preset']
    if speed_preset != 'slower' and speed_preset != 'slow' and speed_preset != 'medium' and \
        speed_preset != 'fast' and speed_preset != 'faster' and speed_preset != 'veryfast' and \
        speed_preset != 'superfast' and speed_preset != 'ultrafast':
        msg = 'Invalid speed_preset: ' + str(speed_preset)
        return False, msg

    if encoder_params['video']['rate_control'] != 'cbr' and \
       encoder_params['video']['rate_control'] != 'vbr':
        msg = 'Invalid rate_control: ' + str(encoder_params['video']['rate_control'])
        return False, msg

    if (encoder_params['video']['enable_cc'] != 'on') and \
       (encoder_params['video']['enable_cc'] != 'off'):
        msg = ' Invalid  enable_cc flag ' + str(encoder_params['video']['enable_cc'])
        return False, msg

    if (encoder_params['video']['num_b_frame'] > 8):
        msg = ' Invalid number of B frames, max supported is 8 '
        return False, msg

    for aud_tag in encoder_params['audio']:
        audio_bitrate = wc_utils.to_int(encoder_params['audio'][aud_tag]['bitrate'])
        audio_codec = encoder_params['audio'][aud_tag]['codec']

        if audio_codec != 'aac':
            msg = ' Invalid audio_codec:' + str(audio_codec)
            return False, msg

        if (audio_bitrate > max_audio_bitrate) or (audio_bitrate < min_audio_bitrate):
            msg = ' Invalid audio_bitrate:' + str(audio_bitrate)
            return False, msg

    if (encoder_params['output']['burn_tc'] != 'on') and \
       (encoder_params['output']['burn_tc'] != 'off'):
        msg = ' Invalid  burn_tc flag ' + str(encoder_params['output']['burn_tc'])
        return False, msg

    if (encoder_params['output']['create_muxed_av'] != 'on') and \
       (encoder_params['output']['create_muxed_av'] != 'off'):
        msg = ' Invalid  create_muxed_av flag ' + str(encoder_params['output']['create_muxed_av'])
        return False, msg
    if (out_type != 'HLS') and (encoder_params['output']['create_muxed_av'] == 'on'):
        msg = ' Muxed AV flag is not expected to be set for non HLS format ' + out_type
        return False, msg

    if (encoder_params['output']['enable_abs_seg_path'] != 'on') and \
       (encoder_params['output']['enable_abs_seg_path'] != 'off'):
        msg = ' Invalid  enable_abs_seg_path flag ' + str(encoder_params['output']['enable_abs_seg_path'])
        return False, msg
    if (out_type != 'HLS') and (encoder_params['output']['enable_abs_seg_path'] == 'on'):
        msg = ' Enable absolute segment path flag is not expected to be set for non HLS format ' + out_type
        return False, msg
    if encoder_params['output']['enable_abs_seg_path'] == 'on':
        parsed_url = urlparse.urlparse(encoder_params['output']['abs_seg_path_base_url'])
        if False == (bool(parsed_url.scheme) and bool(parsed_url.netloc)):
            msg = ' Invalid  absolute segment path base URL ' + str(encoder_params['output']['abs_seg_path_base_url'])
            return False, msg
        if not encoder_params['output']['abs_seg_path_base_url'].endswith('/'):
            encoder_params['output']['abs_seg_path_base_url'] += '/'
    if (encoder_params['output']['seg_in_subfolder'] != 'on') and \
       (encoder_params['output']['seg_in_subfolder'] != 'off'):
        msg = ' Invalid  seg_in_subfolder flag ' + str(encoder_params['output']['seg_in_subfolder'])
        return False, msg

    if (out_type != 'HLS') and (out_type != 'DASH') and \
       (out_type != 'CMAF'):
        msg = ' Invalid  out_type ' + str(out_type)
        return False, msg

    if (out_type == 'HLS' or out_type == 'DASH' or out_type == 'CMAF'):
        segment_size = wc_utils.to_int(encoder_params['output']['segment_size'])
        if segment_size > max_segment_size or \
           segment_size < min_segment_size:
            msg = ' Invalid segment size: ' + str(segment_size)
            return False, msg

    if out_type == 'HLS' or out_type == 'DASH' or out_type == 'CMAF' :
        parsed_url = urlparse.urlparse(encoder_params['output']['ingest_url'])
        if False == (bool(parsed_url.scheme) and bool(parsed_url.netloc)):
            msg = ' Invalid  ingest_url ' + str(encoder_params['output']['ingest_url'])
            return False, msg

    if out_type == 'DASH' or out_type == 'CMAF':
        if (encoder_params['output']['dash_chunked'] != 'on') and \
           (encoder_params['output']['dash_chunked'] != 'off'):
            msg = ' Invalid  dash_chunked flag ' + str(encoder_params['output']['dash_chunked'])
            return False, msg

    if out_type == 'CMAF':
        if (encoder_params['output']['lhls'] != 'on') and \
           (encoder_params['output']['lhls'] != 'off'):
            msg = ' Invalid  LHLS flag ' + str(encoder_params['output']['lhls'])
            return False, msg
    else:
        if (encoder_params['output']['lhls'] != 'off'):
            msg = ' Invalid  LHLS flag ' + str(encoder_params['output']['lhls'])
            return False, msg
    return True, ''

def start_encoder(enc_params):
    print 'Starting encoder'

    """
    WSGI Application that gets called with the set environment and the
    response generation function.
    """
    default_config = {
                  "input_id": "-1",
                  "video": {
                      "speed_preset": "fast",
                      "rate_control": "cbr",
                      "enable_cc": "on",
                      "num_b_frame":8,
                      "variants": [
                          {
                            "codec": "libx264",
                            "bitrate": "-1",
                            "video_width": "-1",
                            "video_height": "-1",
                            "audio_tag": "0"
                          }
                      ]
                    },
                  "audio": {
                    "0": {
                      "bitrate": "-1",
                      "codec": "aac"
                    }
                  },
                  "output": {
                    "out_type": "HLS",
                    "segment_size": "5",
                    "burn_tc": "off",
                    "create_muxed_av": "off",
                    "enable_abs_seg_path": "off",
                    "abs_seg_path_base_url": "",
                    "seg_in_subfolder": "off",
                    "ingest_url": "",
                    "b_ingest_url":"",
                    "dash_chunked": "off",
                    "lhls": "off",
                    "hls_master_manifest" : "master.m3u8",
                    "dash_master_manifest" : "out.mpd"
                  },
                }
    ffmpeg_proc_name = 'ffmpeg '

    store_default_config(default_config, enc_params)
    status, msg = validate_encoder_params(enc_params)
    if False == status:
        reason = 'Bad Request: ' + msg
        return 400, reason

    input_id = str(enc_params['input_id'])
    segment_size = wc_utils.to_int(enc_params['output']['segment_size'])
    out_type = enc_params['output']['out_type']

    print 'Inside start_encoder.py input_id:' + str(enc_params['input_id'])

    #Kill any existing process
    stopencoder.stop_encoder(input_id)

    #Store the json input in a file
    store_load_input_cfg.store_json_cfg(enc_params)

    enc_params['input'] = {}
    enc_params['input']['input_interface'] = capture.get_input_interface(int(input_id))
    enc_params['input']['inputurl'] = capture.get_inputurl(int(input_id))

    ffmpeg_format_args = ''

    if enc_params['input']['input_interface'] == capture.INPUT_INTERFACE_URL:
        ffmpeg_format_args += ' -timeout 1000000 -analyzeduration 5000000 '
    else:
        ffmpeg_format_args += ' -probesize 10M -f ' + enc_params['input']['input_interface']

    ffmpeg_format_args += ' -i %s' %(enc_params['input']['inputurl'])

    vid_w, vid_h, vid_fr, scantype, device_status = capture.find_input_format(ffmpeg_proc_name + ffmpeg_format_args)
    if device_status != 'Active':
        print 'Input signal detection failed: ' + str(device_status)

    enc_params['input']['vid_width'] = vid_w
    enc_params['input']['vid_height'] = vid_h
    enc_params['input']['vid_framerate'] = vid_fr
    enc_params['input']['vid_scantype'] = scantype

    enc_params['output']['user_agent'] = USER_AGENT
    enc_params['output']['drawbox_width'] = 500
    enc_params['output']['drawbox_height'] = 88
    enc_params['output']['fonttype'] = "FreeSerif"
    enc_params['output']['fontsize'] = 80

    args = wc_ffmpeg_args.get_args(enc_params)
    print ffmpeg_proc_name + args
    proc = subprocess.Popen(shlex.split(ffmpeg_proc_name + args))
    pid = proc.pid

    current_time = time.time() * 1000000

    for n in range(0, len(enc_params['video']['variants'])):

        cfg = { 'TIME' : int(current_time),                                     #current time
                'InputID' : int(input_id),                                      #Input ID
                'SubStreamID' : int(n),                                         #Substream ID
                'ProcessID' : pid,                                              #ProcessID
                'VidInWidth' : int(vid_w),                                      #Input video width
                'VidInHt' : int(vid_h),                                         #Input video height
                'InScanType' : str(scantype),                                   #Input scantype
                'VidInFrameRate' : str(vid_fr),                                 #Input framerate
                'FrameRate' : str(vid_fr),                                      #Output framerate
                }

        configdb.insert_stream_config(cfg)

    print 'All Ok, encoder started successfully'
    return 200, 'OK'
