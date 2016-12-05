# -*- coding: utf-8 -*-
""" This module is used for displaying status and controlling cmus music player in i3bar using py3status.    
"""

import sys
import time
import subprocess
import re
from subprocess import Popen, PIPE

###########
# STYLING #
###########
 
OUTPUT_FORMAT = "%status% %artist% - %tracknumber%. %title%"
CMUS_NOT_RUNNING_MSG = ""
CACHE_TIMEOUT = 0.5
NOTHING_PLAYING_MSG = "Nothing playing."
SHOW_PROGRESS_BAR = True
PROGRESS_BAR_STYLE = {1: u"█",
                      2: u" " }
PROGRESS_BAR_LENGTH = 10

# Status symbols
PLAY_SYM  = u"▷"
PAUSE_SYM = u"⌷⌷"
STOP_SYM  = u"◻"

# PLAY_SYM  = u"▶"
# PAUSE_SYM = u"▮▮" 
# STOP_SYM  = u"◼"

########################
# If cmus-remote doesn't use default socket (~/.cmus/socket),
# it can be defined in CMUS_ARGS using --server <SOCKET> argument.
########################

CMUS_CMD  = "cmus-remote"
CMUS_ARGS = "-Q"
CMUS_STATUS_MAP = {"playing" : PLAY_SYM,
                   "stopped" : STOP_SYM,
                   "paused"  : PAUSE_SYM
                  }

########################
# ON_CLICK_MAP is used for mapping mouse clicks to process calls.
# 
# xev can be used to check the mouse button numbers.

ON_CLICK_MAP = {1 : [CMUS_CMD] + ["-u"], # Play/pause
                9 : [CMUS_CMD] + ["-n"], # Next track
                8 : [CMUS_CMD] + ["-r"]  # Previous track
                }


class Py3status:
    cache_timeout = CACHE_TIMEOUT
    output_format = OUTPUT_FORMAT
    show_progress_bar = SHOW_PROGRESS_BAR
    progress_bar_length = PROGRESS_BAR_LENGTH
    not_running_msg = CMUS_NOT_RUNNING_MSG
    nothing_playing_msg = NOTHING_PLAYING_MSG
    cmus_args = CMUS_ARGS
    cmus_args = cmus_args.split()    
    show_playtime = True

    def status(self):
        status_out_dict = self._main()
        status_output = self._format_status_output(status_out_dict)
        if self.show_progress_bar:
             status_output += " " + self._get_progress_bar(status_out_dict)
        if self.show_playtime:
            playtime = self._get_playtime(status_out_dict)
            if playtime:
                status_output += " " + playtime
        return {"full_text" : status_output,
                "cached_until" : self.py3.time_in(self.cache_timeout)}
    
    def on_click(self, event):
        button = event["button"]
        if button in ON_CLICK_MAP:
            cmusProcess = Popen(ON_CLICK_MAP[button], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            output, error = cmusProcess.communicate()
            error = error.decode()

    def _get_playtime(self, input_data):
        playtime_str = ""
        try:
            position = float(input_data["position"])
        except:
            return ""
        m, s = divmod(position, 60)
        h, m = divmod(m, 60)
        if h:
             playtime_str += " %d:%02d:%02d" % (h, m, s)
        else:
             playtime_str += " %02d:%02d" % (m, s)
        return playtime_str


    def _main(self):
        cmus_status = {"sets" : {},
                       "tags" : {}
                      }
    
        try:
            cmus_status_cmd = [CMUS_CMD] + self.cmus_args
            cmusProcess = Popen(cmus_status_cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            output, error = cmusProcess.communicate()
            error = error.decode("utf-8")
        except FileNotFoundError:
            cmus_status["status"] = "cmus-remote not found."
            return cmus_status
           
        if error:
            if "not running" in error:
                 cmus_status["status"] = self.not_running_msg
            else:
                 cmus_status["status"] = error
            return cmus_status 
    
        cmus_remote_output = output.decode("utf-8")
        
        cmus_remote_output = cmus_remote_output.splitlines()
        cmus_remote_output = [x.split(" ", 1) for x in cmus_remote_output]
    
        for output in cmus_remote_output:
            if "tag" in output:
                 tmpList = output[1].split(" ", 1)
                 tmpDict = dict(zip([tmpList[0]], [tmpList[1]]))
                 cmus_status["tags"].update(tmpDict)
            elif "set" in output:
                 tmpList = output[1].split(" ", 1)
                 tmpDict = dict(zip([tmpList[0]], [tmpList[1]]))
                 cmus_status["sets"].update(tmpDict)
            else:
                 if "status" in output:
                     output[1] = CMUS_STATUS_MAP[output[1]]
                 cmus_status.update(dict(zip([output[0]], [output[1]])))
        return cmus_status
    
    def _get_progress_bar(self, input_data):
        try:
            duration = float(input_data["duration"])
            position = float(input_data["position"])
            progress = position/duration            

            progress_str = []
            for i in range(self.progress_bar_length):
                if i < round(progress*self.progress_bar_length):
                     progress_str.append(PROGRESS_BAR_STYLE[1])
                else:
                     progress_str.append(PROGRESS_BAR_STYLE[2])
    
            progress_str = "".join(progress_str)
            return progress_str
    
        except:
            return ""

    def _format_status_output(self, input_data):
        status_output = ""
        cmus_status = input_data
        status_vars = re.findall(r'%(\w+)%', self.output_format)
        tmp_status_output = self.output_format
        for status_var in status_vars:
             if status_var in cmus_status:
                 status_var = status_var
                 try:
                     status = cmus_status[status_var]
                 except:
                     status = status_var
                 if status == self.not_running_msg:
                     return status
                 tmp_status_output = tmp_status_output.replace("%" + status_var + "%", status)
             elif status_var in cmus_status["tags"]:
                 tmp_status_output = tmp_status_output.replace("%" + status_var + "%", cmus_status["tags"][status_var])
    
             elif status_var in cmus_status["sets"]:
                 tmp_status_output = mp_status_output.replace("%" + status_var + "%", cmus_status["sets"][status_var])
    
        if not len(cmus_status["tags"]):
            if cmus_status["status"] in ["stopped", CMUS_STATUS_MAP["stopped"]]:
                return self.nothing_playing_msg
            elif not cmus_status["status"] in ["playing", "paused"]:
                return cmus_status["status"]
    
        status_output = re.sub(r'%(\w+)%', '', tmp_status_output)
        return status_output

if __name__ == "__main__":
     from py3status.module_test import module_test
     module_test(Py3status)
