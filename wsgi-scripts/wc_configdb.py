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

working_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(working_dir)

def get_config_path():
    return working_dir + '/db/'

def get_config_db():
    config_db = get_config_path() + 'config.db'
    exists = os.path.isfile(config_db)
    if exists == False:
        init_config_db(config_db)
    conn = sqlite3.connect(config_db)
    return conn

def init_config_db(path):

    conn = sqlite3.connect(path)
    c = conn.cursor()

    c.execute('DROP TABLE IF EXISTS CapInputNames')
    sql_create_cfg = 'CREATE TABLE  CapInputNames (InputId, \
                                                   InputUrl, \
                                                   InputInterface)'
    c.execute(str(sql_create_cfg))

    c.execute('DROP TABLE IF EXISTS StreamConfig')
    sql_create_cfg = 'CREATE TABLE  StreamConfig \
                                            (TIME,\
                                            InputID,\
                                            SubStreamID,\
                                            ProcessID,\
                                            VidInWidth,\
                                            VidInHt,\
                                            InScanType,\
                                            VidInFrameRate,\
                                            FrameRate) '

    c.execute(str(sql_create_cfg))

    c.close()
    conn.commit()
    conn.close()

    os.system('chmod 666 ' + path)
        
def update_config(cfg, table_name, condition={}):

    conn = get_config_db()
    c = conn.cursor()

    for col in cfg:
        cmd = 'UPDATE %s SET %s="%s"' %(table_name, col, cfg[col])
        if condition != {}:
            key = condition.keys()[0]
            val = condition[key]
            cmd += 'WHERE %s="%s"' %(key, val)

        c.execute(str(cmd))

    c.close()
    conn.commit()
    conn.close()

    return

def delete_config(table_name, condition={}):
    conn = get_config_db()
    c = conn.cursor()

    cmd = 'DELETE FROM %s ' %(table_name)
    if condition != {}:
        key = condition.keys()[0]
        val = condition[key]
        cmd += 'WHERE %s="%s"' %(key, val)
    c.execute(str(cmd))

    c.close()
    conn.commit()
    conn.close()
    return

def insert_config(cfg, table_name):

    num_keys = len(cfg)
    conn = get_config_db()
    c = conn.cursor()

    i = 0
    cmd = 'INSERT INTO %s ' %(table_name)
    cmd += ' ( '
    for key in cfg:
        cmd += '%s' %(key)
        if i != (num_keys - 1):
            cmd += ', '
        i += 1
    cmd += ' ) '

    i = 0
    cmd += ' VALUES( '
    for key in cfg:
        cmd += '"%s"' %(cfg[key])
        if i < (num_keys - 1):
            cmd += ', '
        i += 1
    cmd += ' ) '

    print cmd
    c.execute(str(cmd))
    c.close()
    conn.commit()
    conn.close()

    return

def insert_stream_config(cfg):
    insert_config(cfg, 'StreamConfig')
    return

def get_config(table_name, condition={}, sort_order={}):
    config = []
    conn = get_config_db()
    c = conn.cursor()

    cmd = 'SELECT * FROM %s ' %(table_name)
    if condition != {}:
        key = condition.keys()[0]
        val = condition[key]
        cmd += 'WHERE %s="%s"' %(key, val)
    if sort_order != {}:
        key = sort_order.keys()[0]
        order = sort_order[key]
        cmd += 'ORDER BY %s %s' %(key, order)
    c.execute(cmd)

    keys = [description[0] for description in c.description]
    rows = c.fetchall()
    for i in range(0, len(rows)):
        cfg = {}
        for k in keys:
            cfg[k] = rows[i][keys.index(k)]
        config.append(cfg)
    c.close()
    conn.close()
    return config
