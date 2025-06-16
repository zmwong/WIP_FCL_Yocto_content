__author__ = 'Lau, Shun Yang'
__email__ = 'shun.yang.lau@intel.com'
__version__ = '1.0.2'

# - v1.0.2 Changes -
# 1. Solar XML variable added for OC mode

import os
import sys
import getopt
import argparse
import re
import datetime
import subprocess
import svtools.logging.toolbox as slt

sagv_xml = r"C:\validation\windows-test-content\memory\mtl_s\solar_xml\sagv_3hours.xml"
oc_sagv_xml = r"C:\validation\windows-test-content\memory\mtl_s\solar_xml\sagv_dmb_oc.xml"

#Input Argument
ap = argparse.ArgumentParser()
group = ap.add_argument_group('required flags')
group.add_argument('-t', '--time', dest='time', help='Test run time in minutes', default = 180)
group.add_argument('-m', '--mark', dest='mark', help='Loop count for 3DMark, 10 minutes per loop, 0 to disable', default= 9)
group.add_argument('-r', '--runner', dest='runner', help='Instance of Memrunner: 1 or 2', default= 1)
group.add_argument('-v', '--vlc', dest='vlc', help='VLC run time in minutes, 0 to disable', default = 180)
group.add_argument('-x', '--xml', dest='xml', help='Enable Solar with xml path, 0 to disable', default = sagv_xml)
args= ap.parse_args()

#Script & file path
scriptpath = (os.path.abspath(__file__))
path = os.path.dirname(scriptpath)


#Log Path
log_path = path+'\\Log\\MMX'
if not os.path.exists(log_path):
    os.makedirs(log_path)
pylog_path = log_path+'\\mmex_py.log'
mark_pypath = path+'\\Log\\3DMark\\3dmark_py.log'
memrun_pypath = path+'\\Log\\memrunner\\memrunner_py.log'
solar_pypath = path+'\\Log\\Solar\\solar_py.log'


#Logging setup
_log = slt.getLogger('myscript', autosplit=True)
_log.setFile(pylog_path, overwrite = True)
_log.colorLevels = True
_log.setConsoleFormat = 'simple'
_log.setFileFormat = 'time'
_log.setConsoleLevel('INFO')
_log.setFileLevel('DEBUGALL')


#Input Argument
mark = int(args.mark)
runner = int(args.runner)
vidtime = int(args.vlc)
xml = args.xml
runtime = args.time


def compile_test():
    #Create VLC command
    if vidtime == 0:
        _log.warning('VLC is no enabled')
    else:
        vidcmd = 'python vlc.py --time '+str(vidtime)
        _log.info('VLC cmd: '+vidcmd)


    
    #Create memrunner command
    if runner == 1:
        runnercmd = 'python memrunner.py -p 0 -t '+str(runtime)
        _log.info('Memrunner cmd: '+runnercmd)
    elif runner == 2:
        halftm = int(int(runtime)/2)
        runnercmd1 = 'python memrunner.py -p 0 -t '+str(halftm)
        runnercmd2 = 'python memrunner.py -p 1 -t '+str(halftm)
        _log.info('2 Memrunner instances')
        _log.info('1st Memrunner cmd: '+runnercmd1)
        _log.info('2nd Memrruner cmd: '+runnercmd2)
    else:
        _log.warning('memrunner not enabled')
    
    #Detect and create 3DMark command
    if mark == 0:
        _log.warning('3DMark is not enabled')
    else:
        markcmd = 'python 3dmark.py --loop '+str(mark)
        _log.info('3DMark cmd: '+markcmd)

    #Detect and create xml command
    if xml == 0:
        _log.warning('Solar not enabled')
    else:
        solarcmd = 'python solar.py --xml '+str(xml)
        _log.info('Solar cmd: '+solarcmd)

    _log.info('Triggering all test cmd')
    if vidtime != 0:
        vid_proc = subprocess.Popen(vidcmd, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if runner == 1:
        memrun_proc = subprocess.Popen(runnercmd, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif runner == 2:
        memrun_proc0 = subprocess.Popen(runnercmd1, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(halftm)
        memrun_proc1 = subprocess.Popen(runnercmd2, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if mark != 0:
        mark_proc = subprocess.Popen(markcmd, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if xml != 0:
        solar_proc = subprocess.Popen(solarcmd, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if vidtime != 0:
        vid_proc.communicate()

    if runner == 1:
        memrun_proc.communicate()
    elif runner == 2:
        memrun_proc0.communicate()
        memrun_proc1.communicate()

    if mark != 0:
        mark_proc.communicate()

    if xml != 0:
        solar_proc.communicate()

def mmex_check():
    error_count = 0
    pass_count = 0

    if mark != 0:
        try:
            with open(mark_pypath, 'r') as file0:
                _log.info('Opened 3DMark py log file')
                mark_log = file0.readlines()
                for line in mark_log:
                    if 'SUCCESS' in line:
                        _log.debug('SUCCESS recorded')
                        _log.debug(line)
                        pass_count += 1
                    elif 'ERROR' in line:
                        _log.debug('ERROR recorded')
                        _log.debug(line)
                        error_count +=1
        except FileNotFoundError:
            _log.warning(f"File Not Found: {mark_pypath}")
            mark_log = None

    if runner != 0:
        try:
            with open(memrun_pypath, 'r') as file1:
                _log.info('Opened Memrunner py log file')
                memrunner_log = file1.readlines()
                for line in memrunner_log:
                    if 'SUCCESS' in line:
                        _log.debug('SUCCESS recorded')
                        _log.debug(line)
                        pass_count += 1
                    elif 'ERROR' in line:
                        _log.debug('ERROR recorded')
                        _log.debug(line)
                        error_count +=1
        except FileNotFoundError:
            _log.warning(f"File Not Found: {memrun_pypath}")
            memrunner_log = None

    if xml != 0:
        try:
            with open(solar_pypath, 'r') as file2:
                _log.info('Opened Solar py log file')
                solar_log = file2.readlines()
                for line in solar_log:
                    if 'SUCCESS' in line:
                        _log.debug('SUCCESS recorded')
                        _log.debug(line)
                        pass_count += 1
                    elif 'ERROR' in line:
                        _log.debug('ERROR recorded')
                        _log.debug(line)
                        error_count +=1
        except FileNotFoundError:
            _log.warning(f"File Not Found: {solar_pypath}")
            solar_log = None

    if error_count > 0:
        _log.error('MMEX content fail.')
        sys.exit(1)
    elif pass_count > 0 and error_count == 0:
        _log.success('MMEX content passed!')
        sys.exit(0)

if __name__ == '__main__':
    dt = datetime.date.today()
    raw_time = datetime.datetime.now()
    tm = raw_time.strftime("%H-%M-%S")

    runlog_name = '\\mmx_'+str(dt)+'_'+str(tm)+'.log'

    try:
        compile_test()
    except:
        _log.error('MMX content not run.')
        sys.exit(1)
    finally:
        mmex_check()
