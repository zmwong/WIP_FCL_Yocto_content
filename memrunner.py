"""
written by: mtuaf, modified by: FV_BDC_Concurrency for Yocto Support
December 2019, Modified: November 2024
"""


#Command Example:
#python app_memrunner.py -t 5 -lt 80

import os
import sys
import time

utils_folder = r'/data/validation/yocto-test-content/val_common/python_utils/'
if utils_folder not in sys.path:
    sys.path.append(utils_folder)
sys.path.append(r"/data/validation/yocto-test-content/concurrency/common/reporter/")

from reporter_handler import ReportHandler
from argparse import ArgumentParser
from load_external_program import MemRunner
from runner_module import Runner


# Arguments management
def get_arguments():
    parser = ArgumentParser(description='Parsing all arguments')
    parser.add_argument('--time', '-t', type=int, dest='duration', default='10', help='running time in min')
    parser.add_argument('--load', '-lt', type=str, dest='load', default='100', required=False, help='load (stress) percentage')

    _opts = parser.parse_args()
    _checker_name = sys.argv[0].split("/")[-1:][0].split(".py")[0]  # Changed backslash for making it compatible with Yocto OS
    return _checker_name, _opts


def main(run_time, log):  # right now run_time is in seconds
    # memory-stress
    mem_load = f'-lt {opts.load}%'
    log.info(fr'Test Time is: {opts.duration}min')
    log.info(fr'Memory Load (Stress) Percentage: {mem_load}')
    
    mem = MemRunner(log, run_time, lt=mem_load)
    #mem = MemRunner(logger, run_time, lt='-lt 100%') #Original commandline
    runner = Runner(program_list=[mem], logger=log, report=report_handler, run_time=run_time)
    
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
    runtime = int(opts.duration) * 60  # convert minutes to seconds
    main(runtime, logger)
