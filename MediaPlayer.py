import os
import sys
import time

utils_folder = r'/data/validation/yocto-test-content/val_common/python_utils'
if utils_folder not in sys.path:
    sys.path.append(utils_folder)
sys.path.append(r"/data/validation/yocto-test-content/concurrency/common/reporter")


sys.path.append(r"c:\Validation\yocto-test-content\concurrency\common\reporter")
sys.path.append(r"c:\Validation\yocto-test-content\val_common\python_utils/")
sys.path.append(r"c:\Validation\windows-test-content\concurrency\common\reporter")
sys.path.append(r"c:\Validation\windows-test-content\val_common\python_utils/")

from reporter_handler import ReportHandler
from argparse import ArgumentParser
from load_external_program import MediaPlayer
from runner_module import Runner


# Arguments management

def get_arguments():
    parser = ArgumentParser(description='Parsing all arguments')
    parser.add_argument('--time', '-t', type=int, dest='duration', default='10', help='running time in min')
    parser.add_argument(
        '--video_path',
        '-video',
        type=str,
        dest='video_path',
        default=r'/data/video/Amazing_Caves_1080p_24fps.wmv',
        help='Media run according to defined in video file, if none given run in default mode',
    )

    _opts = parser.parse_args()
    _checker_name = sys.argv[0].split("/")[-1:][0].split(".py")[0]
    return _checker_name, _opts


def main(run_time, log):  # right now run_time is in seconds
    # video playback 4k pcie cpu
    #video_path = os.path.join(r'c:\video', '4k_time_lapse_footage-american_cities.mp4')\
    
    video_path = opts.video_path
    log.info(fr'Test Time is: {opts.duration}min')
    log.info(fr'Video Path is: {video_path}')
    media = MediaPlayer(video_path, log)
    runner = Runner(program_list=[media], logger=log, report=report_handler, run_time=run_time)

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
    # runtime=10
    main(runtime, logger)
