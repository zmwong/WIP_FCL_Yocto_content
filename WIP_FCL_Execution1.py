#!/usr/bin/env python3
# example of execution cmd line
# python WIP_FCL_Execution1.py -t 180 -m memrunner -l 80 -s /solar_xml/sagv_3hours.xml -v C:\Validation\windows-test-content\concurrency\content\execution\Playlist\Karma.mp4 -H 1


"""
Multi-Stress Test Line for Yocto OS
Runs: Memrunner/Prime95 + SAGV + Unigine Heaven + Video playback (3 hours)
"""

import os
import sys
import time
import argparse
import subprocess
import logging

# Configure path for common utilities
utils_folder = r'/data/validation/yocto-test-content/val_common/python_utils/'
if utils_folder not in sys.path:
    sys.path.append(utils_folder)

# Get script directory and set up log directories
script_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(script_dir, 'Log')

# Create log directory if it doesn't exist
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Create log subdirectories for each component
log_subdirs = ['multi_stress', 'memrunner', 'prime95', 'solar', 'heaven', 'MediaPlayer']
for subdir in log_subdirs:
    subdir_path = os.path.join(log_dir, subdir)
    if not os.path.exists(subdir_path):
        os.makedirs(subdir_path)

# Configure logging
multi_stress_log_dir = os.path.join(log_dir, 'multi_stress')
pylog_path = os.path.join(multi_stress_log_dir, 'multi_stress_py.log')

# Setup logger
logger = logging.getLogger('multi_stress')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# File handler
file_handler = logging.FileHandler(pylog_path)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Default paths for logs (relative to script location)
memrunner_log = os.path.join(log_dir, 'memrunner', 'memrunner_py.log')
prime95_log = os.path.join(log_dir, 'prime95', 'prime95_py.log')
solar_log = os.path.join(log_dir, 'solar', 'solar_py.log')
heaven_log = os.path.join(log_dir, 'heaven', 'heaven_terminal_log.log')
video_log = os.path.join(log_dir, 'MediaPlayer', 'MediaPlayer_py.log')

# Default SAGV XML file path
sagv_xml = '/data/validation/yocto-test-content/memory/sagv/sagv_3hours.xml'

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Multi-stress test line for Yocto OS')
    parser.add_argument('-t', '--time', dest='time', type=int, default=60,
                        help='Test run time in minutes (default: 60)')
    parser.add_argument('-m', '--mem_type', dest='mem_type', choices=['memrunner', 'prime95'], default='memrunner',
                        help='Memory stress type: memrunner or prime95 (default: memrunner)')
    parser.add_argument('-l', '--load', dest='load', type=str, default='100',
                        help='Load percentage for memrunner (default: 100)')
    parser.add_argument('-s', '--sagv', dest='sagv', type=str, default=sagv_xml,
                        help=f'Enable SAGV with XML path (default: {sagv_xml}), 0 to disable')
    parser.add_argument('-v', '--video', dest='video', type=str, 
                        default='/data/video/Amazing_Caves_1080p_24fps.wmv',
                        help='Video file path, 0 to disable')
    parser.add_argument('-H', '--heaven', dest='heaven', type=str, choices=['0', '1'], default='1',
                        help='Enable Heaven benchmark (1) or disable (0)')
    return parser.parse_args()

def run_tests(args):
    """Compile and run all tests based on arguments"""
    test_processes = []
    
    # 1. Set up memory stress (memrunner or prime95)
    if args.mem_type == 'memrunner':
        mem_cmd = f'python3 {script_dir}/memrunner.py -t {args.time} -lt {args.load}'
        logger.info(f'Memrunner cmd: {mem_cmd}')
        mem_proc = subprocess.Popen(mem_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        test_processes.append(('Memrunner', mem_proc))
    else:
        mem_cmd = f'python3 {script_dir}/prime95.py -t {args.time}'
        logger.info(f'Prime95 cmd: {mem_cmd}')
        mem_proc = subprocess.Popen(mem_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        test_processes.append(('Prime95', mem_proc))
    
    # 2. Run SAGV if enabled
    if args.sagv != '0':
        sagv_cmd = f'python3 {script_dir}/solar.py --xml {args.sagv}'
        logger.info(f'SAGV cmd: {sagv_cmd}')
        sagv_proc = subprocess.Popen(sagv_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        test_processes.append(('SAGV', sagv_proc))
    else:
        logger.warning('SAGV is disabled')
    
    # 3. Run Heaven if enabled
    if args.heaven != '0':
        heaven_cmd = f'python3 {script_dir}/heaven.py -t {args.time}'
        logger.info(f'Heaven cmd: {heaven_cmd}')
        heaven_proc = subprocess.Popen(heaven_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        test_processes.append(('Heaven', heaven_proc))
    else:
        logger.warning('Heaven is disabled')
    
    # 4. Run video playback if enabled
    if args.video != '0':
        video_cmd = f'python3 {script_dir}/MediaPlayer.py -t {args.time} -video {args.video}'
        logger.info(f'Video cmd: {video_cmd}')
        video_proc = subprocess.Popen(video_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        test_processes.append(('Video', video_proc))
    else:
        logger.warning('Video playback is disabled')
    
    # Wait for all processes to complete
    for name, proc in test_processes:
        logger.info(f'Waiting for {name} to complete...')
        proc.communicate()
        logger.info(f'{name} completed with return code: {proc.returncode}')

def check_results():
    """Check logs for SUCCESS/ERROR messages"""
    error_count = 0
    pass_count = 0
    
    # Define log files to check
    log_files = {
        'Memrunner': memrunner_log,
        'Prime95': prime95_log,
        'SAGV': solar_log,
        'Heaven': heaven_log,
        'Video': video_log
    }
    
    # Check each log file
    for name, log_file in log_files.items():
        if not os.path.exists(log_file):
            logger.warning(f"Log file not found: {log_file}")
            continue
            
        logger.info(f"Checking {name} log file: {log_file}")
        try:
            with open(log_file, 'r') as f:
                log_content = f.readlines()
                for line in log_content:
                    if 'SUCCESS' in line:
                        logger.debug(f'SUCCESS recorded in {name}: {line.strip()}')
                        pass_count += 1
                    elif 'ERROR' in line:
                        logger.error(f'ERROR recorded in {name}: {line.strip()}')
                        error_count += 1
        except Exception as e:
            logger.error(f"Error reading log file {log_file}: {e}")
    
    # Determine overall result
    if error_count > 0:
        logger.error(f'Multi-stress test FAILED with {error_count} errors')
        return False
    elif pass_count > 0:
        logger.info(f'Multi-stress test PASSED with {pass_count} successes')
        return True
    else:
        logger.warning('No success or error messages found in logs')
        return False

if __name__ == '__main__':
    args = parse_arguments()
    
    logger.info("=== Multi-Stress Test Line Starting ===")
    logger.info(f"Run time: {args.time} minutes")
    logger.info(f"Memory stress: {args.mem_type}")
    if args.mem_type == 'memrunner':
        logger.info(f"Memrunner load: {args.load}%")
    logger.info(f"SAGV XML: {args.sagv}")
    logger.info(f"Heaven: {'Enabled' if args.heaven != '0' else 'Disabled'}")
    logger.info(f"Video: {args.video if args.video != '0' else 'Disabled'}")
    
    try:
        run_tests(args)
        result = check_results()
        if result:
            logger.info("Multi-stress test line completed SUCCESSFULLY")
            sys.exit(0)
        else:
            logger.error("Multi-stress test line FAILED")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        sys.exit(1)