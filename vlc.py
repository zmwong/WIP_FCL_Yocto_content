__author__ = 'Lau, Shun Yang'
__email__ = 'shun.yang.lau@intel.com'
__version__ = '1.0.0'

import os
import sys
import getopt
import argparse
import re
import datetime
import time
import svtools.logging.toolbox as slt
import subprocess
from subprocess import Popen

#Input Argument
ap = argparse.ArgumentParser()
group = ap.add_argument_group('required flags')
group.add_argument('-t', '--time', dest='time', required=True, help='How long to run video playback')
args= ap.parse_args()

#Script & file path
scriptpath = (os.path.abspath(__file__))
path = os.path.dirname(scriptpath)
program_path = r"C:\Program Files (x86)\VideoLAN\VLC"

#Input for VLC video playback
runtime = args.time

#Log Path
log_path = path+'\\Log\\VLC'
if not os.path.exists(log_path):
    os.makedirs(log_path)
pylog_path = log_path+'\\vlc_py.log'

#Logging setup
_log = slt.getLogger('myscript', autosplit=True)
_log.setFile(pylog_path, overwrite = True)
_log.colorLevels = True
_log.setConsoleFormat = 'simple'
_log.setFileFormat = 'time'
_log.setConsoleLevel('INFO')
_log.setFileLevel('DEBUGALL')

def vid_cmd():
    vid_k = "vlc.exe --extraintf=http:logger --verbose=3 -R C:\validation\windows-test-content\concurrency\content\execution\Playlist\Karma.mp4 --file-logging --logfile="+log_path+runlog_path_k
    vid_m = "vlc.exe --extraintf=http:logger --verbose=3 -R C:\\Users\\Administrator\\Music\\Media\\Moment.mp4 --file-logging --logfile="+log_path+runlog_path_m
    vid_n = "vlc.exe --extraintf=http:logger --verbose=3 -R C:\\Users\\Administrator\\Music\\Media\\NewZealand.mp4 --file-logging --logfile="+log_path+runlog_path_n

    _log.debug('command video karma: '+vid_k)
    _log.debug('command video moment: '+vid_m)
    _log.debug('command video new zealand: '+vid_n)
    _log.debug('Wait 5 seconds for other application to launch')
    time.sleep(5)
    
    with open(log_path + runlog_path, 'w+') as LogFileHandler:
        Popen(vid_k, cwd=program_path, shell=True, stdin=None, stderr=None, stdout=LogFileHandler)
        Popen(vid_m, cwd=program_path, shell=True, stdin=None, stderr=None, stdout=LogFileHandler)
        Popen(vid_n, cwd=program_path, shell=True, stdin=None, stderr=None, stdout=LogFileHandler)
    _log.info('Launched VLC with subprocess on separate thread')

def vid_timer():
    while(((time.time() - startTime)/60.0) <= int(runtime)):
        print('Target run time = '+runtime)
        print('Current run time = ', (time.time() - startTime)/60.0, " minutes")
        time.sleep(1)
    subprocess.run(["taskkill", "/f", "/im", "vlc.exe"], shell=True)
    _log.info("vlc.exe is killed")

if __name__ == '__main__':
    dt = datetime.date.today()
    raw_time = datetime.datetime.now()
    tm = raw_time.strftime("%H-%M-%S")

    runlog_path_k = '\\vlc_run_karma_'+str(dt)+'_'+str(tm)+'.log'
    runlog_path_m = '\\vlc_run_moment_'+str(dt)+'_'+str(tm)+'.log'
    runlog_path_n = '\\vlc_run_new_zealand_'+str(dt)+'_'+str(tm)+'.log'
    runlog_path = '\\vlcout.log'


    startTime = time.time()
    
    try:
        vid_cmd()
    except:
        _log.error('VLC not launched')
        sys.exit(1)
    finally:
        vid_timer()