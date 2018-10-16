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

import httplib
import subprocess
import time
import os
import sys
import traceback
import re
import datetime
import shlex
import psutil
import json

working_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(working_dir)
import wc_store_load_input_cfg as store_load_input_cfg
import wc_capture as wc_capture

def log_write(log_str):
    try:
        fp = open('/dev/shm/web_boot', "a")
        ct = datetime.datetime.now()
        msg = '[' + str(ct) + ']' + str(log_str) + '\n'
        fp.write(msg)
        #print msg
        fp.close
    except:
        pass

def start_encoder(query):
    headers = {'content-type': 'application/json'}
    conn = httplib.HTTPConnection('127.0.0.1')
    json_str = json.dumps(query)
    conn.request("POST", "/broadcaster/", json_str, headers)
    r = conn.getresponse()
    r.read()
    log_write(r.status)
    conn.close()
    return r

def wait_for_apache2():
    t_end = time.time() + 100
    service_status = True
    while time.time() < t_end:
        service_status = is_service_running('apache2', ' * apache2 is running')
        if service_status == True:
            log_write("Apache is running now")
            break
        time.sleep(0.5)

def is_service_running(service_name, ref_status):
    cmd = 'service ' + str(service_name) + ' status'
    try:
        opt_string = subprocess.check_output(shlex.split(cmd))
        opt_string = opt_string.rstrip()
        if opt_string == str(ref_status):
            return True
        else:
            return False
    except Exception as e:
        return False


def restore_enc_config():
    cfg_json_list = store_load_input_cfg.get_all_enc_json_cfgs()
    #for all the confis, start encoder
    for i in range(0, len(cfg_json_list)):
        try:
            add_query = cfg_json_list[i]
            log_write(add_query)
            #Start encoder
            start_encoder(add_query)
        except Exception as e:
            log_write("Error occured: " + str(e))
            pass

def restore_input_config():
    input_cfg_json_list = store_load_input_cfg.get_all_input_json_cfgs()
    #for all the confis, start encoder
    for i in range(0, len(input_cfg_json_list)):
        try:
            c = input_cfg_json_list[i]
            log_write(c)
            print c
            #Start encoder
            status = wc_capture.add_input_source(c, c['input_id'])
            log_write("status: " + str(status))
        except Exception as e:
            log_write("Error occured: " + str(e))
            pass

def restore_config():
    restore_input_config()
    restore_enc_config()

if __name__ == '__main__':

    try:
        wait_for_apache2()
        restore_config()

    except Exception as e:
        log_write(str(e))
        #traceback.print_exc()
        pass
