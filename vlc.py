#!/usr/bin/python3
# filepath: /root/validation/vlc.py

__author__ = 'Lau, Shun Yang'
__email__ = 'shun.yang.lau@intel.com'
__version__ = '1.0.0'

import os
import sys
import argparse
import datetime
import time
import svtools.logging.toolbox as slt
import subprocess
from subprocess import Popen

# Input Argument
ap = argparse.ArgumentParser()
group = ap.add_argument_group('required flags')
group.add_argument('-t', '--time', dest='time', required=True, help='How long to run video playback')
args = ap.parse_args()

# Script & file path - updated for Linux paths
scriptpath = os.path.abspath(__file__)
path = os.path.dirname(scriptpath)
program_path = "/home/vlcuser/VLC_mediaplayer"  # Path to VLC AppImage

# Input for VLC video playback
runtime = args.time

# Log Path - updated for Linux paths
log_path = os.path.join(path, 'Log', 'VLC')
if not os.path.exists(log_path):
    os.makedirs(log_path)
pylog_path = os.path.join(log_path, 'vlc_py.log')

# Logging setup
_log = slt.getLogger('myscript', autosplit=True)
_log.setFile(pylog_path, overwrite=True)
_log.colorLevels = True
_log.setConsoleFormat = 'simple'
_log.setFileFormat = 'time'
_log.setConsoleLevel('INFO')
_log.setFileLevel('DEBUGALL')

def vid_cmd():
    # Update video paths to Linux paths - adjust these to your actual video locations
    video_path = "/root/validation/videos"  # Create this directory and place videos here
    
    # VLC commands updated for AppRun
    vid_k = f"./AppRun --extraintf=http:logger --verbose=3 -R {video_path}/Karma.mp4 --file-logging --logfile={os.path.join(log_path, runlog_path_k)}"
    vid_m = f"./AppRun --extraintf=http:logger --verbose=3 -R {video_path}/Moment.mp4 --file-logging --logfile={os.path.join(log_path, runlog_path_m)}"
    vid_n = f"./AppRun --extraintf=http:logger --verbose=3 -R {video_path}/NewZealand.mp4 --file-logging --logfile={os.path.join(log_path, runlog_path_n)}"

    _log.debug('command video karma: ' + vid_k)
    _log.debug('command video moment: ' + vid_m)
    _log.debug('command video new zealand: ' + vid_n)
    _log.debug('Wait 5 seconds for other application to launch')
    time.sleep(5)
    
    # Create an environment variable with DISPLAY set
    env = os.environ.copy()
    env["DISPLAY"] = ":0"
    env["VLC_IGNORE_UID_CHECK"] = "1"  # Add this if needed to run as root
    
    with open(os.path.join(log_path, runlog_path), 'w+') as LogFileHandler:
        Popen(vid_k, cwd=program_path, shell=True, stdin=None, stderr=None, stdout=LogFileHandler, env=env)
        Popen(vid_m, cwd=program_path, shell=True, stdin=None, stderr=None, stdout=LogFileHandler, env=env)
        Popen(vid_n, cwd=program_path, shell=True, stdin=None, stderr=None, stdout=LogFileHandler, env=env)
    _log.info('Launched VLC with subprocess on separate thread')

def vid_timer():
    while ((time.time() - startTime)/60.0) <= int(runtime):
        print('Target run time = ' + runtime)
        print('Current run time = ', (time.time() - startTime)/60.0, " minutes")
        time.sleep(1)
    
    # Updated process killing for Linux
    subprocess.run(["pkill", "-f", "AppRun"], shell=False)
    _log.info("VLC processes killed")

if __name__ == '__main__':
    dt = datetime.date.today()
    raw_time = datetime.datetime.now()
    tm = raw_time.strftime("%H-%M-%S")

    # Updated for Linux paths
    runlog_path_k = f'vlc_run_karma_{str(dt)}_{str(tm)}.log'
    runlog_path_m = f'vlc_run_moment_{str(dt)}_{str(tm)}.log'
    runlog_path_n = f'vlc_run_new_zealand_{str(dt)}_{str(tm)}.log'
    runlog_path = 'vlcout.log'

    startTime = time.time()
    
    try:
        vid_cmd()
    except Exception as e:
        _log.error(f'VLC not launched: {str(e)}')
        sys.exit(1)
    finally:
        vid_timer()