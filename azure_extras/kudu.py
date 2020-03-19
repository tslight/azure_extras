#!/usr/bin/env python
import logging
import os
import sys
from argparse import ArgumentParser, ArgumentTypeError
from .lib.kudu import KuduClient


def chkpath(path):
    if os.path.exists(path):
        return os.path.abspath(path)

    raise ArgumentTypeError(f"{path} does not exist.")


def get_args():
    parser = ArgumentParser(description="CLI Kudu API fudger")
    parser.add_argument("-a", "--app", metavar=("NAME"), help="azure app name")
    parser.add_argument(
        "-C",
        "--config",
        type=chkpath,
        metavar=("PATH"),
        default=f"{os.path.expanduser('~')}/.azure.ini",
        help="path to azure configuration file",
    )
    parser.add_argument("-r", "--rg", metavar=("NAME"), help="azure resource group")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-c",
        "--cmd",
        metavar=("COMMAND"),
        help="command to run (use quotes for multi-word commands)",
    )
    group.add_argument("-e", "--endpoint", metavar=("SLUG"), help="api endpoint slug")
    group.add_argument(
        "-z",
        "--deploy_zip",
        metavar=("PATH"),
        type=chkpath,
        help="upload a zip to the server",
    )
    group.add_argument(
        "-Z",
        "--download_zip",
        default=["site/wwwroot", f"{os.path.expanduser('~')}/backup.zip"],
        nargs=2,
        metavar=("SOURCE", "DESTINATION"),
        help="download a zip of a remote path",
    )
    parser.add_argument(
        "-p",
        "--cwd",
        default="site/wwwroot",
        metavar=("PATH"),
        help="server current working directory",
    )
    parser.add_argument("-v", action="count", default=0, help="increase verbosity")
    return parser.parse_args()


def mklog(verbosity):
    if verbosity > 1:
        loglevel = logging.DEBUG
        logformat = "%(asctime)s %(threadName)s %(levelname)s %(message)s"
    elif verbosity == 1:
        loglevel = logging.INFO
        logformat = "%(asctime)s %(levelname)s %(message)s"
    else:
        loglevel = logging.WARNING
        logformat = "%(levelname)s %(message)s"

    logging.basicConfig(
        # filename='',
        format=logformat,
        datefmt="%Y-%m-%d %H:%M:%S",
        level=loglevel,
        stream=sys.stdout,
    )


def main():
    args = get_args()
    mklog(args.v)

    kudu = KuduClient(args.config, args.rg, args.app)

    try:
        if args.cmd:
            kudu.run_cmd(args.cmd, args.cwd)
        elif args.endpoint:
            kudu.get_endpoint(args.endpoint)
        elif args.deploy_zip:
            kudu.deploy_zip(args.deploy_zip)
        elif args.download_zip:
            source, destination = args.download_zip
            kudu.download_zip(source, destination)
    except Exception as error:
        logging.error(error)


if __name__ == "__main__":
    main()
