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
 
STATUS_OUTPUT_FORMAT = "%status% %artist% - %tracknumber%. %title%"
CMUS_NOT_RUNNING_MSG = ""
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
CMUS_ARGS = ["-Q"]
CMUS_STATUS_CMD = [CMUS_CMD] + CMUS_ARGS
CMUS_STATUS_MAP = {"playing" : PLAY_SYM,
                   "stopped" : STOP_SYM,
                   "paused"  : PAUSE_SYM
                  }

########################
# ON_CLICK_MAP is used for mapping mouse clicks to process calls.
# 
# xev can be used to check the mouse button numbers.

CACHE_UNTIL = 0.5 # In seconds
ON_CLICK_MAP = {1 : [CMUS_CMD] + ["-u"], # Play/pause
                9 : [CMUS_CMD] + ["-n"], # Next track
                8 : [CMUS_CMD] + ["-r"]  # Previous track
                }
def main():
    cmus_status = {"sets" : {},
                   "tags" : {}
                  }

    try:
        cmusProcess = Popen(CMUS_STATUS_CMD, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        output, error = cmusProcess.communicate()
        error = error.decode("utf-8")
    except FileNotFoundError:
        cmus_status["status"] = "cmus-remote not found."
        return cmus_status
       
    if error:
        if "not running" in error:
             cmus_status["status"] = CMUS_NOT_RUNNING_MSG
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

def get_progress_bar(input_data):
    try:
        duration = float(input_data["duration"])
        position = float(input_data["position"])
        progress = position/duration
        
        progress_str = []
        for i in range(PROGRESS_BAR_LENGTH):
            if i < round(progress*PROGRESS_BAR_LENGTH):
                 progress_str.append(PROGRESS_BAR_STYLE[1])
            else:
                 progress_str.append(PROGRESS_BAR_STYLE[2])

        progress_str = "".join(progress_str)
        return progress_str

    except:
        return ""

def format_status_output(input_data):
    status_output = ""
    cmus_status = input_data
    status_vars = re.findall(r'%(\w+)%', STATUS_OUTPUT_FORMAT)
    tmp_status_output = STATUS_OUTPUT_FORMAT
    for status_var in status_vars:
         if status_var in cmus_status:
             status_var = status_var
             try:
                 status = cmus_status[status_var]
             except:
                 status = status_var
             if status == CMUS_NOT_RUNNING_MSG:
                 return status
             tmp_status_output = tmp_status_output.replace("%" + status_var + "%", status)
         elif status_var in cmus_status["tags"]:
             tmp_status_output = tmp_status_output.replace("%" + status_var + "%", cmus_status["tags"][status_var])

         elif status_var in cmus_status["sets"]:
             tmp_status_output = mp_status_output.replace("%" + status_var + "%", cmus_status["sets"][status_var])

    if not len(cmus_status["tags"]):
        if cmus_status["status"] in ["stopped", CMUS_STATUS_MAP["stopped"]]:
            return NOTHING_PLAYING_MSG
        elif not cmus_status["status"] in ["playing", "paused"]:
            return cmus_status["status"]

    status_output = re.sub(r'%(\w+)%', '', tmp_status_output)
    return status_output

class Py3status:
    def status(self):
        status_out_dict = main()
        status_output = format_status_output(status_out_dict)
        if SHOW_PROGRESS_BAR:
             status_output += " " + get_progress_bar(status_out_dict)
        return {"full_text" : status_output,
                "cached_until" : self.py3.time_in(CACHE_UNTIL)}
    
    def on_click(self, event):
        button = event["button"]
        if button in ON_CLICK_MAP:
            cmusProcess = Popen(ON_CLICK_MAP[button], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            output, error = cmusProcess.communicate()
            error = error.decode()

if __name__ == "__main__":
   print(format_status_output(main()))
   print(get_progress_bar(main()))
