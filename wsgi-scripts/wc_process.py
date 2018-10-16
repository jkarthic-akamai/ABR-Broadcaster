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

import psutil
import time
import subprocess

def is_process_active(pid):
    try:
        psproc = psutil.Process(pid)
        proc_status = psproc.status()
        if proc_status.lower() != 'zombie':
            return True
        else:
            return False
    except:
        return False

def wait_for_process(pid, timeout=None):
    start_time = time.time()
    while True == is_process_active(pid):
        if timeout is not None and (time.time() - start_time) >= timeout:
            raise psutil.TimeoutExpired("Process is still alive")
        time.sleep(0.1)