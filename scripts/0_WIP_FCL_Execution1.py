#!/usr/bin/env python3
# filepath: /root/validation/WIP_FCL_Yocto_content/WIP_FCL_Execution1.py
# example of execution cmd line
# python3 WIP_FCL_Execution1.py -t 180 -m memrunner -l 80 -s /solar_xml/sagv_3hours.xml -v C:\Validation\windows-test-content\concurrency\content\execution\Playlist\Karma.mp4 -H 1


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
import shutil
import datetime
from concurrent.futures import ThreadPoolExecutor

# Configure path for common utilities
utils_folder = r'/root/validation/yocto-test-content/val_common/python_utils/'
if utils_folder not in sys.path:
    sys.path.append(utils_folder)

# Get script directory and set up log directories
script_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(script_dir, 'Log')

# Create log directory if it doesn't exist
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Create log subdirectories for each component
log_subdirs = ['Latest Execution', 'memrunner', 'prime95', 'solar', 'heaven', 'MediaPlayer']
for subdir in log_subdirs:
    subdir_path = os.path.join(log_dir, subdir)
    if not os.path.exists(subdir_path):
        os.makedirs(subdir_path)

# Create history directory for archived logs
history_dir = os.path.join(log_dir, 'Latest Execution', 'History')
if not os.path.exists(history_dir):
    os.makedirs(history_dir)

# Configure logging with new paths
execution_log_dir = os.path.join(log_dir, 'Latest Execution')
execution_log_path = os.path.join(execution_log_dir, 'execution.log')

# Archive previous log file if it exists
def archive_log():
    if os.path.exists(execution_log_path):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        history_file = os.path.join(history_dir, f"execution_{timestamp}.log")
        try:
            shutil.copy2(execution_log_path, history_file)
            print(f"Previous log archived to {history_file}")
        except Exception as e:
            print(f"Error archiving log file: {e}")

# Archive the previous log before setting up the new logger
archive_log()

# Setup logger
logger = logging.getLogger('multi_stress')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Clear any existing handlers
logger.handlers = []

# File handler - using 'w' mode to overwrite instead of append
file_handler = logging.FileHandler(execution_log_path, mode='w')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Default paths for logs (relative to script location)
memrunner_log = os.path.join(log_dir, 'Memrunner', 'memrunner_py.log')
prime95_log = os.path.join(log_dir, 'Prime95', 'prime95_py.log')
solar_log = os.path.join(log_dir, 'Solar', 'solar_py.log')
heaven_log = os.path.join(log_dir, 'Heaven', 'heaven_terminal_log.log')
video_log = os.path.join(log_dir, 'MediaPlayer', 'MediaPlayer_py.log')

# Default SAGV XML file path
sagv_xml = '/root/validation/WIP_FCL_Yocto_content/solar_xml/sagv_1hour.xml'

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Multi-stress test line for Yocto OS')
    parser.add_argument('-t', '--time', dest='time', type=int, default=60,
                        help='Test run time in minutes (default: 60)')
    parser.add_argument('-m', '--mem_type', dest='mem_type', choices=['memrunner', 'prime95'], default='prime95',
                        help='Memory stress type: memrunner or prime95 (default: prime95)')
    parser.add_argument('-l', '--load', dest='load', type=str, default='100',
                        help='Load percentage for memrunner/prime95 (default: 100)')
    parser.add_argument('-s', '--sagv', dest='sagv', type=str, default=sagv_xml,
                        help=f'Enable SAGV with XML path (default: {sagv_xml}), 0 to disable')
    parser.add_argument('-v', '--video', dest='video', type=str, 
                        default='/root/validation/windows-test-content/concurrency/content/execution/Playlist/Karma.mp4',
                        help='Video file path, 0 to disable')
    parser.add_argument('-H', '--heaven', dest='heaven', type=str, choices=['0', '1'], default='1',
                        help='Enable Heaven benchmark (1) or disable (0)')
    return parser.parse_args()

def run_process(cmd, name):
    """Run a single process and monitor it"""
    logger.info(f'Starting {name}: {cmd}')
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return_code = process.returncode
    logger.info(f'{name} completed with return code: {return_code}')
    return name, return_code, stdout, stderr

def run_tests(args):
    """Run all tests concurrently"""
    test_commands = []
    
    # Prepare commands for all enabled tests
    
    # 1. Memory stress (memrunner or prime95)
    if args.mem_type == 'memrunner':
        mem_cmd = f'python3 {script_dir}/memrunner.py -t {args.time} -lt {args.load}'
        test_commands.append((mem_cmd, 'Memrunner'))
    else:
        mem_cmd = f'python3 {script_dir}/FCL_prime95.py -t {args.time}'
        test_commands.append((mem_cmd, 'Prime95'))
    
    # 2. SAGV - IMPORTANT: don't pass --time parameter to solar.py
    if args.sagv != '0':
        # Solar.py doesn't accept a time parameter, use the XML for duration control
        sagv_cmd = f'python3 {script_dir}/solar.py -x {args.sagv}'
        test_commands.append((sagv_cmd, 'SAGV'))
    
    # 3. Heaven
    if args.heaven != '0':
        heaven_cmd = f'python3 {script_dir}/heaven.py -t {args.time}'
        test_commands.append((heaven_cmd, 'Heaven'))
    
    # 4. Video playback
    if args.video != '0':
        video_cmd = f'python3 {script_dir}/MediaPlayer.py -t {args.time} -video {args.video}'
        test_commands.append((video_cmd, 'Video'))
    
    # Execute all commands concurrently
    results = []
    with ThreadPoolExecutor(max_workers=len(test_commands)) as executor:
        # Submit all jobs
        futures = [executor.submit(run_process, cmd, name) for cmd, name in test_commands]
        
        # Log that all tests have been started
        logger.info(f"All {len(futures)} tests have been launched concurrently")
        
        # Wait for all to complete and collect results
        for future in futures:
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Exception in test execution: {e}")
    
    return results

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
                    if 'SUCCESS' in line or 'PASSED' in line:
                        logger.info(f'SUCCESS recorded in {name}: {line.strip()}')
                        pass_count += 1
                    elif 'ERROR' in line or 'FAILED' in line:
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
        start_time = time.time()
        results = run_tests(args)
        execution_time = (time.time() - start_time) / 60
        logger.info(f"All tests completed in {execution_time:.2f} minutes")
        
        # Check for any failed tests based on return codes
        failed_tests = [name for name, return_code, _, _ in results if return_code != 0]
        if failed_tests:
            logger.error(f"Tests with non-zero return codes: {', '.join(failed_tests)}")
        
        # Check log files for SUCCESS/ERROR messages
        overall_result = check_results()
        if overall_result:
            logger.info("Multi-stress test line completed SUCCESSFULLY")
            sys.exit(0)
        else:
            logger.error("Multi-stress test line FAILED")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        sys.exit(1)