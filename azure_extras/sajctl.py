import os
import logging

from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, as_completed
from .lib.az import AzureExtras
from .lib.utils import chkpath, mklog


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


def sajctl():
    args = get_args()
    mklog(args.v)
    az = AzureExtras(args.config)

    print(f"Sending {args.action} to " + ", ".join(args.stream_analytics_jobs) + "...")

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
            print(f"Status of {job}: ", end="", flush="True")
            try:
                result = future.result()
            except ValueError as error:
                print(f"FAILED")
                logging.error(error)
            else:
                print(result["properties"]["jobState"].upper())


if __name__ == "__main__":
    sajctl()
