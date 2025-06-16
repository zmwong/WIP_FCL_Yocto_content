# - v1.0.1 Changes -
# 1. Logcleanup causing test launch failures [FIXED]
# 2. Old Log files not moving to history folder [FIXED]

# - v1.0.2 Changes -
# 1. TaskKill solar at beginning

# - v1.0.3 Changes -
# 1. Sys.exit(500) for genuine test failure

# - v1.0.4 Quick Fix -
# 1. wmic command is EOL on newer IVT image. Removed taskkill functionality to ungate run.

__author__ = 'Lau, Shun Yang'
__email__ = 'shun.yang.lau@intel.com'
__version__ = '1.0.3'

import os
import sys
import datetime
import getopt
import argparse
import re
import time
import glob
import shutil
import subprocess
import psutil
import svtools.logging.toolbox as slt

sys.path.append(r"c:\Validation\yocto-test-content\concurrency\common\reporter")
sys.path.append(r"c:\Validation\yocto-test-content\val_common\python_utils/")
sys.path.append(r"c:\Validation\windows-test-content\concurrency\common\reporter")
sys.path.append(r"c:\Validation\windows-test-content\val_common\python_utils/")

#Input Argument
ap = argparse.ArgumentParser()
group = ap.add_argument_group('required flags')
group.add_argument('-x', '--xml', dest='xml', required=True, help='Solar XML file')
args = ap.parse_args()

#Script & file path
scriptpath = (os.path.abspath(__file__))
path = os.path.dirname(scriptpath)
program_path = "C:\\Applications\\solar3\\*\\Solar.exe"
program_cli = "C:\\Applications\\solar3\\*\\SolarPanel.exe"
program = glob.glob(program_path)
program = program[0]
programcli = glob.glob(program_cli)
programcli = programcli[0]

#Input for solar test
xml = args.xml

#Log Path
log_path = path+'\\Log\\Solar\\'
if not os.path.exists(log_path):
    os.makedirs(log_path)
cleanup_path = log_path+'\\History'
pylog_path = log_path+'\\solar_py.log'

#Logging Setup
_log = slt.getLogger('myscript', autosplit=True)
_log.setFile(pylog_path, overwrite = True)
_log.colorLevels = True
_log.setConsoleFormat = 'simple'
_log.setFileFormat = 'time'
_log.setConsoleLevel('INFO')
_log.setFileLevel('DEBUGALL')

#Solar Checker
done_msg = "SOLAR END RESULTS"
result_msg = "finished with result"
pass_msg = "Pass EC:"
fail_msg = "Fail EC:"

#Construct & run command
def solar_cmd():
    cmd = 'start /wait cmd.exe /c \"'+program+' /cfg '+xml+' /logpath '+log_path+' /logfile '+runlog_path+'\"'
    _log.info('Launching Solar')
    _log.info('Command: '+cmd)
    subprocess.run(['start', '/wait', 'cmd.exe', '/c', program, '/cfg', xml, '/logpath', log_path, '/logfile', runlog_path],shell=True)

def solar_check():
    solar_done = 0
    solar_pass = 0
    solar_fail = 0

    full_log = log_path + runlog_path
    log = open(full_log)
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
        sys.exit(504)
    else:
        if solar_pass > 0 and solar_fail == 0:
            _log.success('Solar passed without failure')
            sys.exit(0)
        else:
            _log.error('Solar is failing, please check log: '+full_log)
            sys.exit(500)

def kill_process_by_path(target_path):
    # Normalize the target path for accurate comparison
    target_path = os.path.realpath(target_path)
    for proc in psutil.process_iter(attrs=['pid', 'exe']):
        try:
            # Compare process path to target path
            if proc.info['exe'] and os.path.realpath(proc.info['exe']) == target_path:
                # Terminate the process if a match is found
                proc.kill()
                _log.info(f"Process {target_path} has been successfully terminated.")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            _log.error(f"Not able to kill process {target_path}: {e}")



def kill_specific_cmd(title):
    # Escape double quotes in the title
    escaped_title = title.replace('"', '""')

    # Construct the WMIC command to get process IDs based on window title
    cmd = f'wmic process where "name=\'OpenConsole.exe\' and commandline like \'%{escaped_title}%\'" get ProcessId'

    try:
        # Execute the command and get the output
        output = subprocess.check_output(cmd, shell=True, text=True)

        # Skip the first line which is the column name "ProcessId"
        process_ids = output.strip().split('\n')[1:]

        # Remove empty lines and strip whitespace
        process_ids = [pid.strip() for pid in process_ids if pid.strip()]

        for pid in process_ids:
            # Kill the process using its PID
            subprocess.call(['taskkill', '/PID', str(pid), '/f'])
            print(f"Killed CMD process with PID: {pid}")

    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")


def logcleanup():
    if not os.path.exists(cleanup_path):
        os.makedirs(cleanup_path)
    for file in os.listdir(log_path):
        if runlog_path not in file and 'py.log' not in file:
            oldfile = log_path+'\\'+file
            if os.path.exists(cleanup_path+'\\'+file):
                os.remove(cleanup_path+'\\'+file)
            shutil.move(oldfile, cleanup_path)

if __name__ == '__main__':

    #kill solar
    try:
        _log.info('Taskkill disabled')
        #kill_process_by_path(program)
        #kill_specific_cmd("Intel (R) Solar CLI")
        #kill_process_by_path(programcli)
        time.sleep(10)

    except Exception as e:
        _log.error(e)

    dt = datetime.date.today()
    raw_time = datetime.datetime.now()
    tm = raw_time.strftime("%H-%M-%S")


    runlog_path = 'solar_'+str(dt)+'_'+str(tm)+'.csv'


    try:
        logcleanup()
        solar_cmd()
        solar_check()
    except Exception as e:
        _log.error('Solar not run')
        _log.error('Error: ' + str(e))
        sys.exit(504)
