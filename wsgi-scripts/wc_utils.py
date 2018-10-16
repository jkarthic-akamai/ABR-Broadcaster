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
import time
import os
import sys
import re
import datetime
import json
import socket

working_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(working_dir)
import wc_capture as capture
import wc_configdb as configdb
import wc_stopencoder as stopencoder
import wc_store_load_input_cfg as store_load_input_cfg


def to_int(n_str):
    try:
        n = int(n_str)
    except:
        n = -1
    return n

def clamp(n, smallest, largest):
    return min(largest, max(n, smallest))

def map_vid_width_height(vid_res):
    try:
        vid_res_map = {
                  '1080p': [1920, 1080],
                  '720p': [1280, 720],
                  '480p': [720, 480],
                  '360p': [640, 360],
                  '240p': [426, 240]
                  }
        return vid_res_map[vid_res][0], vid_res_map[vid_res][1]
    except:
        return -1, -1

def map_fps_num_den(fps):
    try:
        fps_num_den = {
                  '23.98': ['24000', '1001'],
                  '24': ['24', '1'],
                  '25': ['25', '1'],
                  '29.97': ['30000', '1001'],
                  '30': ['30', '1'],
                  '50': ['50', '1'],
                  '59.94': ['60000', '1001'],
                  '60': ['60', '1']
                  }
        return fps_num_den[fps][0], fps_num_den[fps][1]
    except:
        return fps, '1'