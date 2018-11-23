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
import re
import datetime
import psutil
import math
import subprocess
import time
import urlparse


working_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(working_dir)
import wc_utils as wc_utils
import wc_capture as wc_capture

def get_vcodec_args(enc_params, osi):
    vid_config = enc_params['video']['variants']
    video_codec = vid_config[osi]['codec']
    video_bitrate = wc_utils.to_int(vid_config[osi]['bitrate'])
    video_width = str(vid_config[osi]['video_width'])
    video_height = str(vid_config[osi]['video_height'])

    args = ''

    '''
    osi stands for output stream index. Each codec parameter is indexed with
    output stream index. This is needed for multi-bitrate usecase to
    map the encoded streamss to appropriate output streams.
    '''
    postfix = ':' + str(osi)

    if enc_params['video']['rate_control'] == 'cbr':
        vbv_bufsize = wc_utils.to_int(video_bitrate * 0.1)
    else:
        vbv_bufsize = video_bitrate

    args += ' -c:v%s %s' % (postfix, video_codec)
    args += ' -pix_fmt%s yuv420p' % (postfix)
    args += ' -preset%s %s' % (postfix, enc_params['video']['speed_preset'])

    cc_flag = 0
    if enc_params['video']['enable_cc'] == 'on':
        cc_flag = 1
    args += ' -a53cc%s %d' % (postfix, cc_flag)

    args += ' -b:v%s %sk -bufsize%s %sk -nal-hrd%s %s ' % \
            (postfix, video_bitrate, postfix, vbv_bufsize, postfix, enc_params['video']['rate_control'])

    if (video_width != '-1' and video_height != '-1') :
        args += ' -s%s ' %postfix + video_width + 'x' + video_height + ' '

    if 'profile' in vid_config[osi]:
        args += ' -profile:v%s %s '%(postfix, vid_config[osi]['profile'])

    if 'level' in vid_config[osi]:
        args += ' -level%s %s '%(postfix, vid_config[osi]['level'])

    if 'idr_interval' in vid_config[osi]:
        args += ' -x264-params%s keyint=%s:forced-key=1 '%(postfix, vid_config[osi]['idr_interval'])

    args += '-force_key_frames%s "expr:gte(t,n_forced*%s)"  -bf%s %d -x264opts%s scenecut=-1:rc_lookahead=0' % \
            (postfix, enc_params['output']['segment_size'], postfix, \
             int(enc_params['video']['num_b_frame']), postfix)
    if psutil.cpu_count() > 8 :
        args += ':threads=12'
    args += ' '
    return args

def get_acodec_args(osi, audio_codec, audio_bitrate):
    postfix = ':' + str(osi)
    args = ' -c:a%s ' %postfix + audio_codec + '  '
    if audio_bitrate <= 32:
        args += '-ar 16000 '
    elif audio_bitrate <= 64:
        args += '-ar 24000 '
    elif audio_bitrate <= 96:
        args += '-ar 32000 '
    args += '-b:a%s %sk ' % (postfix, audio_bitrate)
    return args

def get_dash_mux_args(enc_params):
    segment_size = wc_utils.to_int(enc_params['output']['segment_size'])

    now = datetime.datetime.now()
    curr_time = str(now.hour) +  str(now.minute) + str(now.second)

    if enc_params['output']['seg_in_subfolder'] == 'on' :
        chunk_name = '%s/chunk-stream_\$RepresentationID\$-\$Number%%05d\$.m4s' %(curr_time)
        init_seg_name = '%s/init-stream\$RepresentationID\$.m4s' %(curr_time)
    else:
        chunk_name = 'chunk-stream_%s_\$RepresentationID\$-\$Number%%05d\$.m4s' %(curr_time)
        init_seg_name = 'init-stream_%s_\$RepresentationID\$.m4s' %(curr_time)
    chunk_name = chunk_name.replace(':', '\:')
    streaming = 0
    if enc_params['output']['dash_chunked'] == 'on':
        streaming = 1

    dash_cmd = ''
    dash_cmd += '%s=%s' %('f', 'dash')
    dash_cmd += ':%s=\'%s\'' %('media_seg_name', chunk_name)
    dash_cmd += ':%s=\'%s\'' %('init_seg_name', init_seg_name)
    dash_cmd += ':%s=%s' %('min_seg_duration', int(segment_size)*1000000)
    dash_cmd += ':%s=%s' %('window_size', 3)
    dash_cmd += ':%s=%s' %('use_timeline', 0)
    dash_cmd += ':%s=%s' %('http_user_agent', enc_params['output']['user_agent'])
    dash_cmd += ':%s=%s' %('streaming', streaming)
    dash_cmd += ':%s=%s' %('index_correction', 1)
    dash_cmd += ':%s=%s' %('timeout', 0.5)
    dash_cmd += ':%s=%s' %('method', 'PUT')

    if (segment_size < 8) :
        dash_cmd += ':%s=%s' %('http_persistent', 1)
    if (enc_params['output']['out_type'] == 'CMAF'):
        dash_cmd += ":%s=%s" % ('hls_playlist', 1)

    dash_cmd += ' '
    return dash_cmd

def get_hls_mux_args(enc_params, hls_ingest_url):
    output_config = enc_params['output']
    segment_size = wc_utils.to_int(output_config['segment_size'])
    ffmpeg_out_url = hls_ingest_url
    now = datetime.datetime.now()
    ccgroup_name = 'cc'

    hls_args = ''
    hls_args += '%s=%s' %('f', 'hls')

    var_stream_map = ''
    if enc_params['output']['create_muxed_av'] == 'on' :
        for n in range(0, len(enc_params['video']['variants'])):
            var_stream_map += " a\:%d,v\:%d" %(n, n)
            if enc_params['video']['enable_cc'] == 'on':
                var_stream_map += ",ccgroup\:%s" %ccgroup_name
    else:
        for aud_tag in enc_params['audio']:
            aud_id = wc_utils.to_int(enc_params['audio'].keys().index(aud_tag))
            var_stream_map += " a\:%d,agroup\:%s" %(aud_id, aud_tag)
        for n in range(0, len(enc_params['video']['variants'])):
            var_stream_map += " v\:%d,agroup\:%s" \
                   %(n, enc_params['video']['variants'][n]['audio_tag'])
            if enc_params['video']['enable_cc'] == 'on':
                var_stream_map += ",ccgroup\:%s" %ccgroup_name

    if enc_params['output']['seg_in_subfolder'] == 'on' :
        hls_segment_filename = '%s/variant_%%v/stream_%02d%02d%02d_%%d.ts' %\
                               (ffmpeg_out_url.replace(':', '\:'),
                                now.hour, now.minute, now.second)
    else:
        hls_segment_filename = '%s/stream_%02d%02d%02d_%%v_%%d.ts' %\
                               (ffmpeg_out_url.replace(':', '\:'),
                                now.hour, now.minute, now.second)

    hls_flags = 'program_date_time+round_durations'

    hls_ts_options = 'mpegts_pmt_start_pid=480:mpegts_start_pid=481'

    hls_args += ':%s=\'%s\'' %('var_stream_map', var_stream_map)
    hls_args += ':%s=\'%s\'' %('hls_segment_filename', hls_segment_filename)
    hls_args += ':%s=%s' %('hls_time', segment_size)
    hls_args += ':%s=%s' %('hls_flags', hls_flags)
    hls_args += ':%s=\'%s\'' %('hls_ts_options', str(hls_ts_options).replace(':', '\:'))
    hls_args += ':%s=%s' %('http_persistent', 1)
    hls_args += ':%s=%s' %('http_user_agent', enc_params['output']['user_agent'])
    hls_args += ':%s=%s' %('hls_list_size', 6)
    hls_args += ':%s=\'%s\'' %('cc_stream_map', "ccgroup\:%s,instreamid\:CC1" %ccgroup_name)
    hls_args += ':%s=%s' %('master_pl_name', enc_params['output']['hls_master_manifest'])
    hls_args += ':%s=%s' %('master_pl_publish_rate', 100)
    hls_args += ':%s=%s' %('timeout', 0.5)
    hls_args += ':%s=%s' %('method', 'PUT')

    if output_config['enable_abs_seg_path'] == 'on' :
        hls_args += ':%s=\'%s\'' %('hls_base_url',
                                 str(output_config['abs_seg_path_base_url']).replace(':', '\:'))

    return hls_args

def get_args(enc_params):

    out_type = enc_params['output']['out_type']

    if not 'tee_port' in enc_params['output']:
        enc_params['output']['tee_port'] = 0

    ffmpeg_output_args = ' '
    ffmpeg_input_args  = ' '

    if enc_params['input']['input_interface'] != wc_capture.INPUT_INTERFACE_URL:
        ffmpeg_input_args += ' -copyts '
        ffmpeg_input_args += ' -probesize 10M -f %s ' %(enc_params['input']['input_interface'])
    else:
        if (urlparse.urlparse(enc_params['input']['inputurl']).scheme == 'file'):
            ffmpeg_input_args += ' -re '

    if enc_params['input']['input_interface'] == wc_capture.INPUT_INTERFACE_DECKLINK :
        '''
        video capture format is yuv 422
        audio sampling frequency is always 48kHz
        number of bits per audio sample is 16
        number audio channels are 2
        '''
        ffmpeg_input_args += ' -bm_v210 0 -audio_depth 16 -channels 2 '
        qbufsize = int(enc_params['input']['vid_width']) * \
                   int(enc_params['input']['vid_height']) * 2 * \
                   math.ceil(float(enc_params['input']['vid_framerate']))
        qbufsize += 48000 * 2 * 2
        ffmpeg_input_args += ' -queue_size %d ' %qbufsize
        ffmpeg_input_args += '-decklink_copyts 1 -audio_pts abs_wallclock -video_pts abs_wallclock '

    ffmpeg_input_args += '-i %s ' % (enc_params['input']['inputurl'])
    ffmpeg_input_args += '-flags +global_header '
    if enc_params['input']['input_interface'] != wc_capture.INPUT_INTERFACE_URL and\
       enc_params['input']['input_interface'] != wc_capture.INPUT_INTERFACE_AVFOUNDATION:
        fps_num, fps_den = wc_utils.map_fps_num_den(enc_params['input']['vid_framerate'])
        ffmpeg_input_args += '-r %s/%s ' %(fps_num, fps_den)

    if (enc_params['output']['burn_tc'] == 'on'):
        ffmpeg_output_args += '-vf drawbox="x=0:y=0:width=%s:height=%s:color=white:t=fill",drawtext="x=15:y=20:fontfile=/usr/share/fonts/truetype/freefont/%s.ttf:fontsize=%s:fontcolor=black:'\
                              %(enc_params['output']['drawbox_width'], enc_params['output']['drawbox_height'], enc_params['output']['fonttype'], enc_params['output']['fontsize'])
        if enc_params['input']['input_interface'] == wc_capture.INPUT_INTERFACE_URL and (urlparse.urlparse(enc_params['input']['inputurl']).scheme == 'file'):
            ffmpeg_output_args += 'expansion=strftime:text=\'%H\\:%M\\:%S\'"'
        else:
            ffmpeg_output_args += 'text=\'%%{pts\\:hms\\:%d\\:24HH}\'"'%((time.timezone * -1))

    ffmpeg_output_args += ' -af aresample=async=1 '
    num_vid_sub_streams = len(enc_params['video']['variants'])
    num_aud_sub_streams = len(enc_params['audio'])

    vid_config = enc_params['video']['variants']
    for n in range(0, num_vid_sub_streams):
        ffmpeg_output_args += get_vcodec_args(enc_params, n)

    if enc_params['output']['create_muxed_av'] == 'on' :
        num_aud_sub_streams = num_vid_sub_streams
        for n in range(0, num_vid_sub_streams):
            audio_ref_tag = vid_config[n]['audio_tag']
            audio_bitrate = wc_utils.to_int(enc_params['audio'][audio_ref_tag]['bitrate'])
            audio_codec = enc_params['audio'][audio_ref_tag]['codec']
            ffmpeg_output_args += get_acodec_args(n, audio_codec, audio_bitrate)
    else :
        for aud_tag in enc_params['audio']:
            aud_id = wc_utils.to_int(enc_params['audio'].keys().index(aud_tag))
            audio_bitrate = wc_utils.to_int(enc_params['audio'][aud_tag]['bitrate'])
            audio_codec = enc_params['audio'][aud_tag]['codec']
            ffmpeg_output_args += get_acodec_args(aud_id, audio_codec,
                                                  audio_bitrate)

    ffmpeg_output_args += ' -f tee '

    for n in range(0, num_vid_sub_streams):
        ffmpeg_output_args += '-map 0:v '
    for n in range(0, num_aud_sub_streams):
        if enc_params['input']['input_interface'] == wc_capture.INPUT_INTERFACE_V4L2:
            ffmpeg_output_args += '-map 1:a? '
        else:
            ffmpeg_output_args += '-map 0:a? '

    if (out_type == 'HLS'):
        hls_ingest_url = enc_params['output']['ingest_url'].rstrip('/')

        ffmpeg_mux_args = get_hls_mux_args(enc_params, hls_ingest_url)

        if enc_params['output']['seg_in_subfolder'] == 'on' :
            ffmpeg_out_url = '%s/variant_%%v/media.m3u8 ' %hls_ingest_url
        else:
            ffmpeg_out_url = '%s/media_%%v.m3u8 ' %hls_ingest_url

        ffmpeg_output_args +=  '"[%s]%s' %(ffmpeg_mux_args, ffmpeg_out_url)
        if enc_params['output']['b_ingest_url'] != '':
            hls_ingest_url = enc_params['output']['b_ingest_url'].rstrip('/')

            ffmpeg_mux_args = get_hls_mux_args(enc_params, hls_ingest_url)
            if enc_params['output']['seg_in_subfolder'] == 'on' :
                ffmpeg_out_url = '%s/variant_%%v/media.m3u8 ' %hls_ingest_url
            else:
                ffmpeg_out_url = '%s/media_%%v.m3u8 ' %hls_ingest_url
            ffmpeg_output_args +=  '|[%s]%s' %(ffmpeg_mux_args, ffmpeg_out_url)

        ffmpeg_output_args +=  '"'

    elif (out_type == 'DASH' or out_type == 'CMAF'):
        dash_ingest_url  = enc_params['output']['ingest_url'].rstrip('/')

        ffmpeg_mux_args   = get_dash_mux_args(enc_params)
        ffmpeg_out_url = '%s/%s ' %(dash_ingest_url,\
                                    enc_params['output']['dash_master_manifest'])
        ffmpeg_output_args +=  '"[%s]%s' %(ffmpeg_mux_args, ffmpeg_out_url)

        if enc_params['output']['b_ingest_url'] != '':
            dash_ingest_url  = enc_params['output']['b_ingest_url'].rstrip('/')

            ffmpeg_mux_args   = get_dash_mux_args(enc_params)
            ffmpeg_out_url = '%s/%s ' %(dash_ingest_url,\
                                        enc_params['output']['dash_master_manifest'])
            ffmpeg_output_args +=  '|[%s]%s' %(ffmpeg_mux_args, ffmpeg_out_url)

        ffmpeg_output_args +=  '"'

    args = ffmpeg_input_args + ffmpeg_output_args
    return args
