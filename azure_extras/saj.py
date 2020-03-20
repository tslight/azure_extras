import os
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, as_completed
from .lib.az import AzureExtras
from .lib.utils import chkpath, mklog


def get_args():
    parser = ArgumentParser()
    parser.add_argument(
        "-C",
        "--config",
        type=chkpath,
        metavar=("PATH"),
        default=f"{os.path.expanduser('~')}/.azure.ini",
        help="path to azure configuration file",
    )
    parser.add_argument("-rg", "--resource_group", help="azure resource group")
    parser.add_argument(
        "-s",
        "--stream_analytics_jobs",
        nargs="+",
        help="list of azure stream analytics jobs",
    )
    parser.add_argument("-a", "--action", help="action to carry out - start or stop.")
    parser.add_argument("-v", action="count", default=0, help="increase verbosity")
    return parser.parse_args()


def main():
    args = get_args()
    mklog(args.v)
    az = AzureExtras(args.config)

    # http://masnun.com/2016/03/29/python-a-quick-introduction-to-the-concurrent-futures-module.html
    with ThreadPoolExecutor(max_workers=len(args.stream_analytics_jobs)) as e:
        future_job = {
            e.submit(
                az.toggle_stream_analytics_job, args.resource_group, job, args.action
            ): job
            for job in args.stream_analytics_jobs
        }
        for future in as_completed(future_job):
            try:
                future.result()
            except ValueError as e:
                logging.error(e)
                exit(1)
    with ThreadPoolExecutor(max_workers=len(args.stream_analytics_jobs)) as e:
        {
            e.submit(az.get_stream_analytics_job, args.resource_group, job): job
            for job in args.stream_analytics_jobs
        }
