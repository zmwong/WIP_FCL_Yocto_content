#!/usr/bin/python3.12
#Example regular run:
#python app_prime95.py -t 5




import os
import sys
import time

utils_folder = r'/root/validation/yocto-test-content/val_common/python_utils'
if utils_folder not in sys.path:
    sys.path.append(utils_folder)
sys.path.append(r"/data/validation/yocto-test-content/concurrency/common/reporter")

sys.path.append(r"c:\Validation\yocto-test-content\concurrency\common\reporter")
sys.path.append(r"/root/validation/yocto-test-content/val_common/python_utils")
#sys.path.append(r"/root/validation/windows-test-content/concurrency/common/reporter")
#sys.path.append(r"/root/validation/windows-test-content/val_common/python_utils")


sys.path.append(r"/root/validation/yocto-test-content/concurrency/common/reporter")

from reporter_handler import ReportHandler
from argparse import ArgumentParser
from load_external_program import Prime95
from runner_module import Runner


# Arguments management
def get_arguments():
    parser = ArgumentParser(description='Parsing all arguments')
    parser.add_argument('--time', '-t', type=int, dest='duration', default='10', help='running time in min')
    
    _opts = parser.parse_args()
    _checker_name = sys.argv[0].split("/")[-1:][0].split(".py")[0]  # Changed backslash for making it compatible with Yocto OS
    return _checker_name, _opts


def main(run_time, log):  # right now run_time is in seconds
    # initialize Prime
    log.info(f'Test Time is: {opts.duration}min')
    prime = Prime95(log)

    runner = Runner(program_list=[prime], logger=log, report=report_handler, run_time=run_time)

    """Main loop"""
    runner.start()
    sys.exit(runner.stop())


"""MAIN"""
if __name__ == '__main__':
    testname, opts = get_arguments()
    report_summery = testname + " Summery!"
    report_handler = ReportHandler(testname)
    logger = report_handler.log
    report = report_handler.rep
    report_handler.update_rep_summary(report_summery)
    logger.info(f"Arguments are: {opts}")
    runtime = int(opts.duration) * 60  # convert minutes to seconds
    # runtime=10
    main(runtime, logger)
