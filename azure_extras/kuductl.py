import json
import logging
import os
from argparse import ArgumentParser
from .lib.kudu import KuduClient
from .lib.utils import chkpath, mklog


def get_args():
    parser = ArgumentParser(description="CLI Kudu API Frontend")
    parser.add_argument("-a", "--app", metavar=("NAME"), help="azure app service name")
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
        "-l", "--logs", const=50, type=int, nargs="?", help="get logs lines"
    )
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


def run_cmd(kudu, cmd, cwd):
    print(f"Running {cmd} in {kudu.app}/{cwd}.. ", end="", flush="True")
    try:
        response = kudu.run_cmd(cmd, cwd)
        if response["Error"] == "":
            print("DONE.")
        else:
            print("FAILED.")
            raise AssertionError(
                +f"Exitcode: {response['ExitCode']} "
                + f"Message: {response['Error']}".strip()
            )
        print(response["Output"].strip())
    except Exception as error:
        logging.error(error)


def get_endpoint(kudu, endpoint):
    print(f"Getting resource from {kudu.app}/{endpoint}.. ", end="", flush="True")
    try:
        response = kudu.get_endpoint(endpoint)
        print("Done.")
        if response:
            logging.info(f"{kudu.app}{endpoint}:")
            print(json.dumps(response, indent=2, sort_keys=True))
        else:
            logging.info(f"{kudu.app}{endpoint} returned no data.")
    except Exception as error:
        print("FAILED.")
        logging.error(error)


def deploy_zip(kudu, path):
    print(f"Deploying {path} to {kudu.app}.. ", end="", flush="True")
    try:
        response = kudu.deploy_zip(path)
        print(f"DONE.") if response["complete"] else print(f"FAILED.")
        logging.info("\n" + json.dumps(response, indent=2, sort_keys=True))
    except Exception as error:
        print(f"FAILED.")
        logging.error(error)


def download_zip(kudu, paths):
    source, destination = paths
    print(
        f"Downloading zip from {kudu.app}/{source} to {destination}.. ",
        end="",
        flush="True",
    )
    try:
        response = kudu.download_zip(source, destination)
        print("DONE.") if response.ok else print("FAILED.")
    except Exception as error:
        print(f"FAILED.")
        logging.error(error)


def main():
    args = get_args()
    mklog(args.v)
    kudu = KuduClient(args.config, args.rg, args.app)

    if args.cmd:
        run_cmd(kudu, args.cmd, args.cwd)
    elif args.logs:
        kudu.get_logs(args.logs)
    elif args.endpoint:
        get_endpoint(kudu, args.endpoint)
    elif args.deploy_zip:
        deploy_zip(kudu, args.deploy_zip)
    elif args.download_zip:
        download_zip(kudu, args.download_zip)


if __name__ == "__main__":
    main()
