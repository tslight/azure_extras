import os
import logging

from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, as_completed
from .lib.saj import StreamAnalyticsJobs
from .lib.utils import chkpath, mklog


def get_args():
    parser = ArgumentParser(description="Start or stop Stream Analytics Jobs")
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


def sajctl(config, rg, jobs, action):
    saj = StreamAnalyticsJobs(config, rg)
    print(f"Sending {action} to " + ", ".join(jobs) + "...")

    # http://masnun.com/2016/03/29/python-a-quick-introduction-to-the-concurrent-futures-module.html
    with ThreadPoolExecutor(max_workers=len(jobs)) as executor:
        future_job = {
            executor.submit(saj.toggle_stream_analytics_job, job, action): job
            for job in jobs
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


def main():
    args = get_args()
    mklog(args.v)
    sajctl(args.config, args.resource_group, args.stream_analytics_jobs, args.action)


if __name__ == "__main__":
    main()
