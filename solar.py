#!/usr/bin/python3
# filepath: /root/validation/solar.py
# Solar test runner for Yocto using solar.sh wrapper

__author__ = 'Lau, Shun Yang'
__email__ = 'shun.yang.lau@intel.com'
__version__ = '2.0.1'  # Updated to use solar.sh wrapper

import os
import sys
import datetime
import argparse
import re
import time
import shutil
import subprocess
import psutil
import svtools.logging.toolbox as slt

# Update import paths for Yocto
sys.path.append("/data/validation/yocto-test-content/concurrency/common/reporter")
sys.path.append("/data/validation/yocto-test-content/val_common/python_utils/")
sys.path.append("/data/validation/windows-test-content/concurrency/common/reporter")
sys.path.append("/data/validation/windows-test-content/val_common/python_utils/")

# Input Argument
ap = argparse.ArgumentParser()
group = ap.add_argument_group('required flags')
group.add_argument('-x', '--xml', dest='xml', required=True, help='Solar XML file')
args = ap.parse_args()

# Script & file path - updated for Yocto
scriptpath = os.path.abspath(__file__)
path = os.path.dirname(scriptpath)

# Path to solar.sh wrapper script
solar_sh = "/data/applications/solar_install/solar.sh"

# Input for solar test
xml = args.xml

# Log Path - updated for Yocto
log_path = os.path.join(path, 'Log', 'Solar')
if not os.path.exists(log_path):
    os.makedirs(log_path)
cleanup_path = os.path.join(log_path, 'History')
pylog_path = os.path.join(log_path, 'solar_py.log')

# Logging Setup
_log = slt.getLogger('myscript', autosplit=True)
_log.setFile(pylog_path, overwrite=True)
_log.colorLevels = True
_log.setConsoleFormat = 'simple'
_log.setFileFormat = 'time'
_log.setConsoleLevel('INFO')
_log.setFileLevel('DEBUGALL')

# Solar Checker
done_msg = "SOLAR END RESULTS"
result_msg = "finished with result"
pass_msg = "Pass EC:"
fail_msg = "Fail EC:"

# Construct & run command using solar.sh
def solar_cmd():
    full_log_path = os.path.join(log_path, runlog_path)
    _log.info('Launching Solar using solar.sh wrapper')
    
    # Using solar.sh with appropriate arguments
    cmd = [solar_sh, "/cfg", xml, "/logpath", log_path, "/logfile", runlog_path]
    _log.info(f'Command: {" ".join(cmd)}')
    
    try:
        # Run the command and capture output
        process = subprocess.run(cmd, capture_output=True, text=True)
        _log.info(f"Return code: {process.returncode}")
        _log.debug(f"Output: {process.stdout}")
        
        if process.stderr:
            _log.error(f"Error output: {process.stderr}")
            
        return process.returncode
    except Exception as e:
        _log.error(f"Error executing solar.sh: {e}")
        return 1

def solar_check():
    solar_done = 0
    solar_pass = 0
    solar_fail = 0

    full_log = os.path.join(log_path, runlog_path)
    
    if not os.path.exists(full_log):
        _log.error(f"Log file not found: {full_log}")
        return False
        
    with open(full_log) as log:
        for aline in log:
            if re.search(done_msg, aline):
                solar_done += 1

            if re.search(result_msg, aline):
                if re.search(pass_msg, aline):
                    _log.debug('Logging pass message')
                    solar_pass += 1
                elif re.search(fail_msg, aline):
                    _log.debug('Logging fail message')
                    solar_fail += 1

    if solar_done == 0:
        _log.error('Solar does not finish')
        return False
    else:
        if solar_pass > 0 and solar_fail == 0:
            _log.success('Solar passed without failure')
            return True
        else:
            _log.error('Solar is failing, please check log: '+full_log)
            return False

def kill_solar_process():
    # Linux equivalent of killing a process
    try:
        # Using pkill to kill Solar by name
        subprocess.call(['pkill', '-f', 'Solar'])
        _log.info("Solar processes terminated")
    except Exception as e:
        _log.error(f"Error killing Solar processes: {e}")

def logcleanup():
    if not os.path.exists(cleanup_path):
        os.makedirs(cleanup_path)
    for file in os.listdir(log_path):
        if runlog_path not in file and 'py.log' not in file:
            oldfile = os.path.join(log_path, file)
            if os.path.exists(os.path.join(cleanup_path, file)):
                os.remove(os.path.join(cleanup_path, file))
            shutil.move(oldfile, cleanup_path)

if __name__ == '__main__':
    # Kill solar - simplified for Linux
    try:
        _log.info('Attempting to kill any running Solar instances')
        kill_solar_process()
        time.sleep(10)
    except Exception as e:
        _log.error(e)

    dt = datetime.date.today()
    raw_time = datetime.datetime.now()
    tm = raw_time.strftime("%H-%M-%S")

    runlog_path = f'solar_{str(dt)}_{str(tm)}.csv'

    try:
        logcleanup()
        ret_code = solar_cmd()
        
        if ret_code == 0:
            if solar_check():
                sys.exit(0)
            else:
                sys.exit(500)
        else:
            _log.error(f'Solar execution failed with return code {ret_code}')
            sys.exit(ret_code)
    except Exception as e:
        _log.error('Solar not run')
        _log.error('Error: ' + str(e))
        sys.exit(504)