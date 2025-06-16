##################################################################################
#                                                                                #
# Author: Gautam, Gyanu                                                          #
# Name:   app_heaven.py                                                          #
# Description: Full Wrapper for Heaven app on Yocto OS                           #
#                                                                                #
##################################################################################
#                                                                               ##
#               INTEL CORPORATION PROPRIETARY INFORMATION                       ##
#   This software is supplied under the terms of a license agreement or         ##
#   nondisclosure agreement with Intel Corporation and may not be copied        ##
#   or disclosed except in accordance with the terms of that agreement.         ##
#                                                                               ##
#       Copyright (c) 2025 Intel Corporation. All Rights Reserved.              ##
#                                                                               ##
##################################################################################
# Usage: app_heaven.py -t 60  (To run the app for 60 minutes)                   ##
##################################################################################
import os
import sys
import time
import subprocess
import psutil
from datetime import datetime
import datetime
import argparse
import logging

# defining logger module
def create_logger(name, path):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', \
                                  datefmt='%m/%d/%Y %I:%M:%S%p')
    file_handler = logging.FileHandler(os.path.join(path, name + r'.log'))

    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger

# Making Log file path and initializing logger
#if os.path.exists(os.getcwd() + '/heaven_RunLogs'):
#    pass
#else:
#    os.mkdir(os.getcwd() + '/heaven_RunLogs')
## logger = create_logger('DE_PLL_Log', os.getcwd()+'\\DE_PLL_Logs')
logger = create_logger('heaven_terminal_log', os.getcwd())

# Killing Heaven after runtime completes
def killtree(pid):
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    for p in children:
        logger.info(f"Killing child - {str(p)}")
        try:
            p.kill()
        except:
            logger.error(f"couldnt kill child - {str(p)}")
            sys.exit(1)
    logger.info(f"Killing parent - {str(parent)}")
    try:
        parent.kill()
    except:
        logger.error(f"couldnt kill parent - {str(p)}")
        sys.exit(1)

# Triggering Heaven WL on target
def startHeaven(cmd_heaven,iteration):
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y%m%d_%H%M%S")
    final_cmd = cmd_heaven + f' >> {os.getcwd()}/heaven_log_iteration_no_{iteration}_{formatted_datetime}.log'
    proc_heaven = subprocess.Popen(final_cmd, shell=True)
    time.sleep(1)
    if not isRunningHeaven():
        logger.error("Application run failed")
        sys.exit(1)
    return proc_heaven

# Monitoring if heaven is running
def isRunningHeaven():
    for proc in psutil.process_iter():
        if proc.name().startswith('heaven'):
            return True
    return False

# Main function with all the magic, Start -> Monitor -> Close after runtime
def main(run_time):
    #dir_heaven = r'/data/applications/heaven/Unigine_Heaven-4.0/bin/heavenx64'
    cmd_heaven = 'DISPLAY=:0 /data/applications/heaven/Unigine_Heaven-4.0-Pro/bin/heaven_x64 \
        -video_app opengl -sound_app openal -project_name Heaven -data_path ../ \
            -system_script heaven/unigine.cpp -engine_config ../data/heaven_4.0.cfg -video_multisample 0 \
                -video_fullscreen 1 -video_mode -1 -video_width 1280 -video_height 720 -frame -1 -duration 0 -type 0 -level 0  \
                    -extern_plugin GPUMonitor -extern_define RELEASE,HEAVEN_ADV,AUTOMATION,QUALITY_ULTRA,TESSELLATION_NORMAL'
    start_time = time.time()
    logger.info('************** Executing Heaven iter = 1 **************')
    i=1
    proc_heaven = startHeaven(cmd_heaven,i)
    i = 2
    while time.time() - start_time <= run_time:
        if not isRunningHeaven():
            logger.info(f'************** Re-executing Heaven iter = {i} **************')
            proc_heaven = startHeaven(cmd_heaven,i)
            i += 1
        else:
            logger.info('--Polling...')
            time.sleep(3)
            logger.info('Heaven Running!')
            time.sleep(15)
    
    if isRunningHeaven():
        killtree(proc_heaven.pid)
        logger.info('[PASSED] Heaven Run Completed Successfully!')
        sys.exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--time", help="Runtime of the script in minutes")
    args = parser.parse_args()
    run_time = int(args.time) if args.time else 10 #print('Enter duration to run script in minutes')
    run_time = run_time * 60  # Converting to seconds
    main(run_time)