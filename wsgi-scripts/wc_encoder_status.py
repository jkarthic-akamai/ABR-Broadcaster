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

import sqlite3
import os
import sys
import json

working_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(working_dir)
import wc_codecs as codecs
import wc_process as process
import wc_capture as capture
import wc_configdb as configdb
import wc_store_load_input_cfg as store_load_input_cfg

def get_encoder_status(input_id=None, refresh_input=False):
    ffmpeg_cmd = 'ffmpeg '
    jrows = []

    #Get ethernet interface status
    capture.get_devices(refresh_input)

    if input_id == None:
        inp_src = configdb.get_config('CapInputNames', {}, \
                                      {'InputID': 'ASC'})
    else:
        inp_src = configdb.get_config('CapInputNames', {'InputId': input_id}, \
                                      {'InputID': 'ASC'})

    for i in range(0, len(inp_src)):
        input_id = inp_src[i]['InputId']
        input_interface = inp_src[i]['InputInterface']

        if input_interface == capture.INPUT_INTERFACE_URL:
            ffmpeg_format_args = ' -timeout 1000000 -analyzeduration 5000000 '
        else:
            ffmpeg_format_args = ' -probesize 10M -f ' + input_interface

        ffmpeg_format_args += ' -i '

        cfg = configdb.get_config('StreamConfig', {'InputID': input_id})
        stream_status = False
        if cfg:
            pid = int(cfg[0]['ProcessID'])
            stream_status = process.is_process_active(pid)
            jrow = store_load_input_cfg.get_json_cfg(input_id)

            jrow['input'] = {}
            jrow['input']['status'] = 'Active'
            jrow['input']['width'] = str(cfg[0]['VidInWidth'])
            jrow['input']['height'] = str(cfg[0]['VidInHt'])
            jrow['input']['scantype'] = str(cfg[0]['InScanType'])
            jrow['input']['framerate'] = str(cfg[0]['VidInFrameRate'])
            jrow['status'] = 'Active'

        if stream_status == False:
            jrow = {
                  "input_id": str(input_id),
                  "video": {
                    "speed_preset": "",
                    "rate_control": "",
                    "variants": []
                  },
                  "audio": {
                  },
                  "output": {
                    "out_type": "",
                    "segment_size": "",
                    "burn_tc": "",
                    "ingest_url": "",
                    "create_muxed_av": "",
                    "enable_abs_seg_path": "",
                    "abs_seg_path_base_url": ""
                  },

                 "status" : "InActive"
                }

            jrow['input'] = {}
            inputurl = capture.get_inputurl(input_id)
            vid_w, vid_h, vid_fr, scantype, device_status = capture.find_input_format(ffmpeg_cmd + ffmpeg_format_args + inputurl)
            jrow['input']['status'] = device_status
            jrow['input']['width'] = str(vid_w)
            jrow['input']['height'] = str(vid_h)
            jrow['input']['scantype'] = str(scantype)
            jrow['input']['framerate'] = str(vid_fr)

        jrow['input']['input_interface'] = inp_src[i]['InputInterface']
        jrow['input']['input_url'] = inp_src[i]['InputUrl']

        jrows.append(jrow)

    json_ret = {}
    json_ret['devices'] = jrows
    json_ret['codecs'] = codecs.get_codecs()

    json_str = json.dumps(json_ret, indent = 4)

    return 200, 'OK', json_str
