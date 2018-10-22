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

import json
import os
import sys
import re

working_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(working_dir)
import wc_configdb

def get_json_cfg_filename(input_id):
    json_dir = wc_configdb.get_config_path()
    return json_dir + 'enc_%s.json'%(input_id)

def get_input_json_cfg_filename(input_id):
    json_dir = wc_configdb.get_config_path()
    return json_dir + 'input_%s.json'%(input_id)

def get_all_json_cfgs(regexp):
    file_list = []
    try:
        json_dir = wc_configdb.get_config_path()
        for dirpath, dirnames, filenames in os.walk(json_dir):
            for filename in filenames:
                match = re.match(regexp, filename)
                if match != None:
                    file_list.append(read_json_cfg_from_file(os.path.join(json_dir, filename)))
    except:
        pass

    return file_list

def get_all_enc_json_cfgs():
    file_list = get_all_json_cfgs('enc\_\d+\.json')
    return file_list

def get_all_input_json_cfgs():
    file_list = get_all_json_cfgs('input\_\d+\.json')
    return file_list

def store_json_cfg(enc_params):
    try:
        filename = get_json_cfg_filename(enc_params['input_id'])
        fp = open(filename, 'w')
        json.dump(enc_params, fp, indent=4)
        fp.close()
    except Exception as e:
        print e
        pass

def store_input_json_cfg(input_config):
    try:
        filename = get_input_json_cfg_filename(input_config['input_id'])
        fp = open(filename, 'w')
        json.dump(input_config, fp, indent=4)
        fp.close()
    except Exception as e:
        print 'error', e
        pass

def read_json_cfg_from_file(filename):
    try:
        fp = open(filename, 'r')
        enc_params = json.load(fp)
        fp.close()
        return enc_params
    except Exception as e:
        print e
        return {}

def get_json_cfg(input_id):
    filename = get_json_cfg_filename(input_id)
    enc_params = read_json_cfg_from_file(filename)
    return enc_params

def get_input_json_cfg(input_id):
    filename = get_json_cfg_filename(get_input_json_cfg_filename(input_id))
    input_config = read_json_cfg_from_file(filename)
    return input_config

def delete_json_cfg(input_id):
    try:
        os.remove(get_json_cfg_filename(input_id))
    except OSError:
        pass

def delete_input_json_cfg(input_id):
    try:
        os.remove(get_input_json_cfg_filename(input_id))
    except OSError:
        pass
