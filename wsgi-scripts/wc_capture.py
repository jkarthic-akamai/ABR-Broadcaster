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
import wc_store_load_input_cfg as store_load_input_cfg
import wc_stopencoder as stopencoder

#Input inteface supported
INPUT_INTERFACE_DECKLINK = 'decklink'
INPUT_INTERFACE_V4L2 = 'v4l2 -ts abs -video_size 1280x720'
INPUT_INTERFACE_AVFOUNDATION = 'avfoundation -video_size 1280x720 -framerate 30'
INPUT_INTERFACE_URL = 'URL'

def insert_inputname_row(input_id, input_url, input_interface):
    cap_cfg = {'InputId' : input_id,
               'InputUrl' : input_url,
               'InputInterface' : input_interface
              }
    configdb.insert_config(cap_cfg, 'CapInputNames')

def delete_inputname(input_id):
    del_cfg = {'InputId' : input_id
              }
    if len(configdb.get_config('CapInputNames', del_cfg)) == 0:
        msg = "Input Id not found"
        return False, msg
    configdb.delete_config('CapInputNames', del_cfg)
    if len(configdb.get_config('CapInputNames', del_cfg)) != 0:
        msg = "Input Id not deleted from DB"
        return False, msg
    return True, ''

def get_input_interface(id):
    cap_inp = configdb.get_config('CapInputNames',{'InputId' : str(id)})
    return cap_inp[0]['InputInterface']

def get_inputurl(id):
    cap_inp = configdb.get_config('CapInputNames',{'InputId' : str(id)})
    return cap_inp[0]['InputUrl']

def add_input_source(input_config, input_src_id=None):

    response_obj = input_config
    print 'input_src_id', input_src_id

    if input_src_id == None:
        input_src_id = allocate_input_src_id()
        if input_src_id == None:
            return 400, 'No free input Id', {}
    else:
        print 'Deleting old entry for input_src_id = ', input_src_id
        delete_inputname(input_src_id)

    response_obj['input_id'] = input_src_id
    insert_inputname_row(input_src_id, \
                         input_config['input']['input_url'], \
                         input_config['input']['input_interface'])
    store_load_input_cfg.store_input_json_cfg(response_obj)
    return 200, 'OK'

def remove_input_source(input_src_id=None):
    ret_status = 200
    ret_reason = 'OK'
    if input_src_id == None:
        inp_src = configdb.get_config('CapInputNames')
    else:
        inp_src = configdb.get_config('CapInputNames', {'InputId': input_src_id})

    for i in range(0, len(inp_src)):
        #Cannot remove hardware input sources
        if inp_src[i]['InputInterface'].find(INPUT_INTERFACE_URL) == -1:
            if len(inp_src) == 1:
                return 403, "Cannot remove SDI/v4l2/avfoundation input source"
            continue

        input_id = inp_src[i]['InputId']
        store_load_input_cfg.delete_input_json_cfg(input_id)
        status, msg = delete_inputname(input_id)
        if status == False:
            return status, msg
    return ret_status, ret_reason

def get_decklink_devices():
    # Auto detect the device name(s) from ffmpeg logs..Expecting output in the following format
    # ...
    # [decklink @ 0x37bef60]     'DeckLink Mini Recorder'
    # ...OR...
    # [decklink @ 0x48abf60]     'DeckLink 4K Pro'
    # ...etc.,
    # Will be searching for substrings "[decklink @" and "'"(single quote), to get the device name
    device_name_query = "ffmpeg -f %s -list_devices 1 -i 'dummy'" %(INPUT_INTERFACE_DECKLINK)
    proc = subprocess.Popen(device_name_query, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    err_lines = err.splitlines()
    num_devices = 0
    for line in err_lines:
        if (line.find("[decklink @") != -1 and line.find("'") != -1):
            idx = line.find("'")
            input_config = {
                  "input": {
                    "input_interface": INPUT_INTERFACE_DECKLINK,
                    "input_url": "\'" + line[idx+1:-1] + "\'"
                   }
                }
            add_input_source(input_config)
            num_devices += 1
    return num_devices

def get_v4l2_devices():
    # Auto detect the device name(s) from v4l2-ctl logs..Expecting output in the following format
    # ...
    # /dev/video0
    # ...etc.,
    device_name_query = "v4l2-ctl --list-devices"
    proc = subprocess.Popen(device_name_query, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    err_lines = out.splitlines()
    num_devices = 0
    for line in err_lines:
        idx = line.find("/dev/")
        if (idx != -1):
            # TODO(Karthick) : Assuming a minimum resolution of 1280x720 and hardcoding it
            input_config = {
                  "input": {
                    "input_interface": INPUT_INTERFACE_V4L2,
                    "input_url": line[idx:] + ' -f alsa -i default'
                   }
                }
            add_input_source(input_config)
            num_devices += 1
    return num_devices

def get_avfoundation_devices():
    # Auto detect the device name(s) from v4l2-ctl logs..Expecting output in the following format
    # ...
    # /dev/video0
    # ...etc.,
    device_name_query = "ffmpeg -devices"
    proc = subprocess.Popen(device_name_query, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    err_lines = out.splitlines()
    num_devices = 0
    for line in err_lines:
        idx = line.find("avfoundation")
        if (idx != -1):
            # TODO(Karthick) : Assuming a minimum resolution of 1280x720 and hardcoding it
            input_config = {
                  "input": {
                    "input_interface": INPUT_INTERFACE_AVFOUNDATION,
                    "input_url": " '0:0'"
                   }
                }
            add_input_source(input_config)
            num_devices = 1
            break;
    return num_devices

def get_devices(refresh_devices):
    curr_input_id_list = get_input_src_id_list()
    num_input_src = len(curr_input_id_list)
    if num_input_src != 0 and refresh_devices == False:
        return num_input_src

    # Stop all running instances and remove all input sources if refresh is requested
    if refresh_devices == True:
        for i in range(0, num_input_src):
            stopencoder.stop_encoder(i)
        configdb.delete_config('CapInputNames')
    num_input_src = get_decklink_devices()
    num_input_src += get_v4l2_devices()
    num_input_src += get_avfoundation_devices()
    return num_input_src

def get_input_src_id_list():
    curr_input_id_list = []
    cap_inp = configdb.get_config('CapInputNames')
    for c in cap_inp:
        curr_input_id_list.append(int(c['InputId']))
    return curr_input_id_list

def allocate_input_src_id():
    curr_input_id_list = get_input_src_id_list()
    num_input_src = len(curr_input_id_list)
    for i in range(0, (num_input_src + 1)):
        if i not in curr_input_id_list:
            return i
    return None

def find_input_format(ffmpeg_cmd):
    # Search for string like below in the ffmpeg logs to find input resolution and fps
    # ...
    #    Stream #0:1: Video: rawvideo (UYVY / 0x59565955), uyvy422, 1920x1080, -4 kb/s, 24 fps, 1000k tbr, 1000k tbn, 1000k tbc
    #....
    # Todo(Karthick) : Identify the scan type as well
    proc = subprocess.Popen(ffmpeg_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    err_lines = err.splitlines()
    vid_w = 0
    vid_h = 0
    vid_fr = '0'
    scantype = ''
    status = 'No signal'

    for line in err_lines:
        if (line.find('Could not open') != -1) or \
           (line.find('Cannot enable video input') != -1):
            status = 'Device open error'
            break

        regex = '.*Stream \#\d\:\d(\[0x\d{1,4}\]){0,1}: Video: .*,.*, (\d{3,4})x(\d{3,4}).*'
        match = re.match(regex, line)
        if match == None:
            continue

        vid_w = match.groups()[1]
        vid_h = match.groups()[2]
        status = 'Active'

        f = re.match('.*(\d{2}.\d{2}) fps', line)
        if f == None:
            f = re.match('.*(\d{2}) fps', line)

        if f != None:
            vid_fr = f.groups()[0]
        break
    return vid_w, vid_h, vid_fr, scantype, status
