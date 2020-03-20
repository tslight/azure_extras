#!/usr/bin/env python
import logging
import os
import sys
from argparse import ArgumentParser, ArgumentTypeError
from .lib.az import AzureExtras
from .lib.utils import chkpath, mklog


def get_args():
    parser = ArgumentParser(description="Enable health check in Azure App Service")
    parser.add_argument("-a", "--app", metavar=("NAME"), help="azure app service name")
    parser.add_argument("-r", "--rg", metavar=("NAME"), help="azure resource group")
    parser.add_argument(
        "-C",
        "--config",
        type=chkpath,
        metavar=("PATH"),
        default=f"{os.path.expanduser('~')}/.azure.ini",
        help="path to azure configuration file",
    )
    parser.add_argument("-v", action="count", default=0, help="increase verbosity")
    return parser.parse_args()


def main():
    args = get_args()
    mklog(args.v)
    az = AzureExtras(args.config)

    print(f"Enabling Health Check on {args.app}.. ", end="", flush="True")
    try:
        az.enable_health_check(args.rg, args.app)
        print("DONE.")
    except Exception as error:
        print("FAIL.")
        logging.error(error)


if __name__ == "__main__":
    main()
