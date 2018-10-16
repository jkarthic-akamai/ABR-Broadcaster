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

import webapp2
import os
import sys
#from webapp2 import template #also added
working_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(working_dir)
import wc_stopencoder as stopencoder
import wc_startencoder as startencoder
import wc_encoder_status as encoder_status
import wc_input_source as wc_input_source

class EncHandler(webapp2.RequestHandler):
    os.environ['PATH'] = ':'.join([os.getenv('PATH'), '/usr/local/bin'])
    def get(self, inst_id=None):

        status_code, reason, resp_body = encoder_status.get_encoder_status(inst_id)
        status = str(status_code) + ' ' + str(reason)
        self.response.set_status(status)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(resp_body)

    def post(self, inst_id=None):
        enc_params = self.request.json

        status_code, reason = startencoder.start_encoder(enc_params)
        status = str(status_code) + ' ' + str(reason)
        self.response.set_status(status)
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write('')

    def delete(self, inst_id=None):
        status_code, reason = stopencoder.stop_encoder(inst_id)
        status = str(status_code) + ' ' + str(reason)
        self.response.set_status(status)
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write('')

class InputHandler(webapp2.RequestHandler):
    def post(self):
        input_config = self.request.json

        status_code, reason = wc_input_source.add_input(input_config)
        status = str(status_code) + ' ' + str(reason)
        self.response.set_status(status)
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write('')

    def delete(self, inst_id=None):
        status_code, reason = stopencoder.stop_encoder(inst_id)
        if status_code == 200:
            status_code, reason = wc_input_source.remove_input(inst_id)

        status = str(status_code) + ' ' + str(reason)
        self.response.set_status(status)
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write('')

application = webapp2.WSGIApplication([
    (r'/broadcaster/{0,1}', EncHandler),
    (r'/broadcaster/(\d+)/{0,1}', EncHandler),
    (r'/broadcaster/input/{0,1}', InputHandler),
    (r'/broadcaster/input/(\d+)/{0,1}', InputHandler)
], debug=True)
