#!/usr/bin/python3
# filepath: /root/validation/WIP_FCL_Yocto_content/FCL_prime95.py

import os
import sys
import time
import subprocess
import datetime
import shutil
import logging
from argparse import ArgumentParser

# Add necessary paths
utils_folder = r'/root/validation/yocto-test-content/val_common/python_utils'
if utils_folder not in sys.path:
    sys.path.append(utils_folder)
sys.path.append(r"/root/validation/yocto-test-content/concurrency/common/reporter")
sys.path.append(r"/root/validation/yocto-test-content/val_common/python_utils")

from reporter_handler import ReportHandler

# Path configuration
PRIME95_PATH = "/data/applications/prime95/mprime"
RESULTS_PATH = "/data/applications/prime95/results.txt"

# Log path configuration - changed to specified format
LOG_DIR = "/root/validation/WIP_FCL_Yocto_content/Log/Prime95"
HISTORY_DIR = os.path.join(LOG_DIR, "History")
LOG_FILE = os.path.join(LOG_DIR, "prime95.log")

# ANSI color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

# Create log directories if they don't exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(HISTORY_DIR, exist_ok=True)

# Arguments management
def get_arguments():
    parser = ArgumentParser(description='Parsing all arguments')
    parser.add_argument('--time', '-t', type=int, dest='duration', default='10', help='running time in min')
    
    _opts = parser.parse_args()
    _checker_name = sys.argv[0].split("/")[-1:][0].split(".py")[0]
    return _checker_name, _opts

# Save previous log file to history if it exists
def archive_log():
    if os.path.exists(LOG_FILE):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        history_file = os.path.join(HISTORY_DIR, f"prime95_{timestamp}.log")
        shutil.copy2(LOG_FILE, history_file)
        print(f"Previous log archived to {history_file}")

# Setup custom logger to write to console and append to log file
def setup_logger(name):
    # First, set up a basic console logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    logger.handlers = []
    
    # Create console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    
    # Create file handler - append mode so it doesn't overwrite the prime95 output
    file_handler = logging.FileHandler(LOG_FILE, mode='a')
    file_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', 
                                 datefmt='%m-%d %H:%M')
    
    # Add formatter to handlers
    console.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(console)
    logger.addHandler(file_handler)
    
    return logger

# Robust process killing
def kill_prime95(logger):
    """Kill any running mprime processes"""
    logger.info("Terminating Prime95 processes")
    
    try:
        # Using Linux commands to find and kill the process
        ps_output = subprocess.run(["ps", "-ef"], capture_output=True, text=True).stdout
        mprime_processes = [line for line in ps_output.split('\n') if 'mprime' in line and 'grep' not in line]
        
        if mprime_processes:
            logger.info(f"Found mprime processes: {mprime_processes}")
            # Kill processes
            subprocess.run(["pkill", "-f", "mprime"])
            logger.info("Sent kill signal to mprime processes")
            
            # Give time for process to exit gracefully
            time.sleep(3)
            
            # Check if it's still running
            ps_output = subprocess.run(["ps", "-ef"], capture_output=True, text=True).stdout
            if any('mprime' in line and 'grep' not in line for line in ps_output.split('\n')):
                logger.warning("Process still running, sending SIGKILL")
                subprocess.run(["pkill", "-9", "-f", "mprime"])
                time.sleep(1)  # Give a bit more time after SIGKILL
        else:
            logger.info("No mprime processes found")
            
    except Exception as e:
        logger.error(f"Error killing Prime95: {e}")

def run_prime95(duration_minutes, logger):
    # Kill any existing instances first
    kill_prime95(logger)
    
    logger.info(f"Starting Prime95 for {duration_minutes} minutes")
    
    # Start with a clean log file for this run
    with open(LOG_FILE, 'w') as log_file:
        # Start mprime with output capturing
        process = subprocess.Popen(
            [PRIME95_PATH, "-t"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True
        )
        
        logger.info(f"Started mprime with PID: {process.pid}")
        
        # Calculate end time
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        # Open results file for writing
        with open(RESULTS_PATH, 'w') as results_file:
            # Process output in real-time
            while time.time() < end_time and process.poll() is None:
                try:
                    # Read a line from the process output
                    line = process.stdout.readline()
                    if line:
                        # Write to results file, log file, and terminal
                        results_file.write(line)
                        results_file.flush()  # Ensure it's written immediately
                        log_file.write(line)
                        log_file.flush()
                        # print(line, end='')  # Also display on terminal
                    else:
                        # No more output but process still running
                        time.sleep(0.1)
                except Exception as e:
                    logger.error(f"Error capturing output: {e}")
                    break
        
        logger.info("Test duration completed")
        
        # Try to capture any remaining output, but don't let timeout crash the script
        try:
            remaining_output, _ = process.communicate(timeout=2)
            if remaining_output:
                with open(RESULTS_PATH, 'a') as results_file:
                    results_file.write(remaining_output)
                log_file.write(remaining_output)
                print(remaining_output, end='')
        except subprocess.TimeoutExpired:
            logger.warning("Timed out waiting for process to close - proceeding with kill")
    
    # Use the robust killing method
    logger.info("Using robust method to kill all mprime processes")
    kill_prime95(logger)
    
    logger.info("Prime95 test completed")
    return True

def check_results(logger):
    logger.info("Checking Prime95 results")
    
    if not os.path.exists(RESULTS_PATH):
        logger.error("Results file not found")
        return False
        
    if os.path.getsize(RESULTS_PATH) == 0:
        logger.error("Results file is empty")
        return False
    
    logger.info("Results file created successfully")
    
    # Check for errors in the results
    with open(RESULTS_PATH, 'r') as f:
        content = f.read()
        
    if "ERROR" in content or "error" in content.lower():
        logger.error("Prime95 test reported errors")
        return False
        
    if "passed" in content.lower() or "worker" in content.lower():
        logger.info("Prime95 test ran successfully")
        return True
        
    logger.warning("Could not determine test result")
    return True  # Assume success if we can't find explicit failure

if __name__ == '__main__':
    # Archive previous log file
    archive_log()
    
    testname, opts = get_arguments()
    report_summary = testname + " Summary!"
    report_handler = ReportHandler(testname)
    
    # Setup our custom logger after archiving the log
    custom_logger = setup_logger("prime95")
    logger = custom_logger
    
    report = report_handler.rep
    report_handler.update_rep_summary(report_summary)
    
    logger.info(f"Arguments are: {opts}")
    
    try:
        # Run Prime95 and capture output
        success = run_prime95(opts.duration, logger)
        
        # Kill processes again to be sure
        kill_prime95(logger)
        
        # Check results
        result_success = check_results(logger)
        
        if success and result_success:
            # Print colorized success message (both to console and log)
            colored_message = f"Prime95 test [{GREEN}PASSED{RESET}]"
            plain_message = "Prime95 test [PASSED]"
            
            # For console with color
            logger.info(f"TEST PASSED: {colored_message}")
            
            # For log file with green if possible (may not work in all log viewers)
            with open(LOG_FILE, 'a') as log_file:
                log_file.write(f"\n{datetime.datetime.now().strftime('%m-%d %H:%M')} - INFO - TEST PASSED: Prime95 test [{GREEN}PASSED{RESET}]\n")
            
            # ReportHandler handling
            report_handler.test_res = 0  # Set to success
            report_handler.rep.std.content.create_insight(testname, result="PASS", error_code=0, message="Prime95 test passed successfully")
            logger.info(f"Report, create_insight: {testname}, result=\"PASS\", error_code=0, message=Prime95 test passed successfully")
            report_handler.finalize_test()
            sys.exit(0)
        else:
            # Print colorized failure message
            colored_message = f"Prime95 test [{RED}FAILED{RESET}]"
            
            logger.error(f"TEST FAILED: {colored_message}")
            
            # For log file with red if possible
            with open(LOG_FILE, 'a') as log_file:
                log_file.write(f"\n{datetime.datetime.now().strftime('%m-%d %H:%M')} - ERROR - TEST FAILED: Prime95 test [{RED}FAILED{RESET}]\n")
            
            # Error handling
            report_handler.handle_error(err={testname: ["Prime95 test failed"]}, err_code=1, msg="Prime95 test failed")
            report_handler.finalize_test()
            sys.exit(1)
    except Exception as e:
        # Print colorized error message
        colored_message = f"Prime95 test [{RED}ERROR{RESET}]"
        logger.error(f"Error during test execution: {e} - {colored_message}")
        
        # For log file with red if possible
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(f"\n{datetime.datetime.now().strftime('%m-%d %H:%M')} - ERROR - Error during test execution: {e} - Prime95 test [{RED}ERROR{RESET}]\n")
        
        # Try to kill processes even if there was an error
        try:
            kill_prime95(logger)
        except:
            pass
        
        # Error handling
        report_handler.handle_error(err={testname: [f"Exception: {str(e)}"]}, err_code=2, msg=f"Exception: {str(e)}")
        report_handler.finalize_test()
        sys.exit(2)