#!/usr/bin/env python
import logging
import os
from argparse import ArgumentParser
from .lib.az import AzureExtras
from .lib.utils import chkpath, mklog


def get_args():
    parser = ArgumentParser(description="Toggle health check in Azure App Service")
    parser.add_argument("-a", "--app", metavar=("NAME"), help="azure app service name")
    parser.add_argument("-r", "--rg", metavar=("NAME"), help="azure resource group")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-e", "--enable", action="store_true", help="enable health check"
    )
    group.add_argument(
        "-d", "--disable", action="store_true", help="disable health check"
    )
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

    try:
        if args.enable:
            print(f"Enabling Health Check on {args.app}.. ", end="", flush="True")
            az.toggle_health_check(args.rg, args.app, enable=True)
        elif args.disable:
            print(f"Disabling Health Check on {args.app}.. ", end="", flush="True")
            az.toggle_health_check(args.rg, args.app, enable=False)
        print("DONE.")
    except Exception as error:
        print("FAIL.")
        logging.error(error)


if __name__ == "__main__":
    main()
