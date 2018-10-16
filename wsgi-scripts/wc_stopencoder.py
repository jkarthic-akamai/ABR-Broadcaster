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
import urlparse
import psutil
import time
import signal
import json
import urllib

working_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(working_dir)
import wc_configdb as configdb
import wc_capture as capture
import wc_process as process
import wc_store_load_input_cfg as store_load_input_cfg

def stop_encoder(input_id=None):

    if input_id == None:
        inp_src = configdb.get_config('CapInputNames')
    else:
        inp_src = configdb.get_config('CapInputNames', {'InputId': input_id})
        if len(inp_src) == 0:
            return 400, 'Bad Request: Invalid Id'

    for i in range(0, len(inp_src)):
        input_id = inp_src[i]['InputId']
        cfg = configdb.get_config('StreamConfig', {'InputID': str(input_id)})
        if cfg:
            pid = int(cfg[0]['ProcessID'])
            try:
                if True == process.is_process_active(pid):
                    psproc = psutil.Process(pid)
                    #Terminate signal doesn't reach WSGI process. Using SIGUSR2 as a workaround.
                    #psproc.send_signal(signal.SIGTERM);
                    psproc.send_signal(signal.SIGUSR2);
                    process.wait_for_process(pid, timeout=7)
            except psutil.AccessDenied as err:
                print ("Access Denied err ", err.msg)
            except psutil.TimeoutExpired as err:
                print ("Time out expired ", err.msg)
                psproc.kill()
            except:
                print ("No such process ")

            configdb.delete_config('StreamConfig', {'InputID': input_id})

        store_load_input_cfg.delete_json_cfg(input_id)

    return 200, 'OK'
