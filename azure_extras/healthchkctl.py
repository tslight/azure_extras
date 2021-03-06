import logging
import os
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, as_completed
from .lib.app import AppService
from .lib.utils import chkpath, mklog


def get_args():
    parser = ArgumentParser(
        description="Enable or disable Health check in Azure App Services"
    )
    parser.add_argument(
        "-a",
        "--app_services",
        nargs="+",
        metavar=("NAME"),
        help="list of azure app services",
    )
    parser.add_argument(
        "-r", "--resource_group", metavar=("NAME"), help="azure resource group"
    )
    parser.add_argument(
        "-A",
        "--action",
        metavar=("ENABLE/DISABLE"),
        help="action to carry out - enable or disable.",
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


def healthchkctl(config, rg, apps, action):
    app_service = AppService(config, rg)

    # http://masnun.com/2016/03/29/python-a-quick-introduction-to-the-concurrent-futures-module.html
    with ThreadPoolExecutor(max_workers=len(apps)) as executor:
        future_app = {
            executor.submit(app_service.toggle_health_check, app, action): app
            for app in apps
        }
        for future in as_completed(future_app):
            app = future_app[future]
            print(f"Sending {action} to {app}.. ", end="", flush="True")
            try:
                future.result()
            except ValueError as error:
                print(f"FAILED.")
                logging.error(error)
            else:
                print(f"DONE.")


def main():
    args = get_args()
    mklog(args.v)
    healthchkctl(args.config, args.resource_group, args.app_services, args.action)


if __name__ == "__main__":
    main()
