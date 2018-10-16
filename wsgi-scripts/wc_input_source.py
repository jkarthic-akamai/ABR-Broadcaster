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

import os
import sys
import urlparse

working_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(working_dir)

import wc_capture as wc_capture

def add_input(input_config):
    #TODO (rpatagar) add validation for input_config, test case also
    parsed_url = urlparse.urlparse(input_config['input']['input_url'])
    if False == (bool(parsed_url.scheme)):
        msg = ' Invalid  input_url ' + str(input_config['input']['input_url'])
        return 400, msg

    input_config['input']['input_interface'] = wc_capture.INPUT_INTERFACE_URL
    statuscode, msg = wc_capture.add_input_source(input_config)
    return statuscode, msg

def remove_input(input_src_id=None):
    ret_status, ret_reason = wc_capture.remove_input_source(input_src_id)
    return ret_status, ret_reason
