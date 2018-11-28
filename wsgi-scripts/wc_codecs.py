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

import subprocess
import re
import os
import sys

working_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(working_dir)
import wc_configdb as configdb

def refresh_codecs():
    supported_codecs_list = ['libx264', 'h264_videotoolbox', 'libvpx-vp9', 'libx265']
    device_name_query = "ffmpeg -encoders"
    proc = subprocess.Popen(device_name_query, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    configdb.delete_config('Codecs')
    for codec in supported_codecs_list:
        if out.find(codec) != -1:
            print codec
            codec_cfg = {'Name' : codec}
            configdb.insert_config(codec_cfg, 'Codecs')

def get_codecs():
    codec_list = []
    codec_list_db = configdb.get_config('Codecs')
    if len(codec_list_db) == 0:
        refresh_codecs()
        codec_list_db = configdb.get_config('Codecs')
    for codec in codec_list_db:
        codec_list.append(codec['Name'])
    return codec_list    

if __name__ == "__main__":
    refresh_codecs()