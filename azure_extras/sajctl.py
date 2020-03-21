import os
import logging
import sys
import time

from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, as_completed
from .lib.az import AzureExtras
from .lib.utils import chkpath, get_seconds, mklog


def get_args():
    parser = ArgumentParser(description="Stream Analytics Jobs Controller")
    parser.add_argument(
        "-C",
        "--config",
        type=chkpath,
        metavar=("PATH"),
        default=f"{os.path.expanduser('~')}/.azure.ini",
        help="path to azure configuration file",
    )
    parser.add_argument(
        "-r", "--resource_group", metavar=("NAME"), help="azure resource group"
    )
    parser.add_argument(
        "-j",
        "--stream_analytics_jobs",
        metavar=("JOBS"),
        nargs="+",
        help="list of azure stream analytics jobs",
    )
    parser.add_argument(
        "-a",
        "--action",
        metavar=("START/STOP"),
        help="action to carry out - start or stop.",
    )
    parser.add_argument("-v", action="count", default=0, help="increase verbosity")
    return parser.parse_args()


def check_job_status(az, rg, job, action):
    """
    This function makes sure the Stream Analytics Job identified by the input
    parameter 'job' is actually up and running.
    """
    seconds = get_seconds(seconds=15)
    for sec in seconds:
        status = az.get_stream_analytics_job(rg, job)["properties"]["jobState"]
        started = action == "start" and status == "Running"
        stopped = action == "stop" and status == "Stopped"

        if started or stopped:
            logging.info(f"Successfully sent {action} to {job}.")
            return

        logging.info(f"Waiting {sec:.1f} seconds before checking {job} again...")
        time.sleep(sec)
        logging.info(f"Checking status of {action} for {job}...")
    logging.critical(f"{job} timed out after {sum(seconds)} seconds. Aborting.")


def sajctl():
    args = get_args()
    mklog(args.v)
    az = AzureExtras(args.config)

    # http://masnun.com/2016/03/29/python-a-quick-introduction-to-the-concurrent-futures-module.html
    with ThreadPoolExecutor(max_workers=len(args.stream_analytics_jobs)) as executor:
        future_job = {
            executor.submit(
                az.toggle_stream_analytics_job, args.resource_group, job, args.action
            ): job
            for job in args.stream_analytics_jobs
        }
        for future in as_completed(future_job):
            job = future_job[future]
            print(f"Sending {args.action} to {job}.. ", end="", flush="True")
            try:
                future.result()
            except ValueError as error:
                print(f"FAILED.")
                logging.error(error)
                sys.exit(1)
            else:
                print(f"DONE.")

    print("Checking status of " + ", ".join(args.stream_analytics_jobs) + "...")

    with ThreadPoolExecutor(max_workers=len(args.stream_analytics_jobs)) as executor:
        future_job = {
            executor.submit(
                check_job_status, az, args.resource_group, job, args.action
            ): job
            for job in args.stream_analytics_jobs
        }
        for future in as_completed(future_job):
            job = future_job[future]
            print(f"Checking {args.action} status of {job}.. ", end="", flush="True")
            try:
                future.result()
            except ValueError as error:
                print(f"FAILED.")
                logging.error(error)
                sys.exit(1)
            else:
                print(f"DONE.")


if __name__ == "__main__":
    sajctl()
