import json
import logging
import requests
import traceback
from .app import AppService
from time import time


class KuduClient(AppService):
    """
    https://github.com/projectkudu/kudu/wiki/REST-API
    """

    def __init__(self, path, rg, app):
        super().__init__(path, rg)
        self.app = app
        self.url = self.get_publishing_credentials(app)["scmUri"] + "/api/"
        logging.debug(self.url)

    def convert_kudu_path(self, path):
        return path.replace("C:\\home\\", "").replace("\\", "/")

    def check_directory_for_logs(self, directory, allfiles=[]):
        logging.info(f"Checking {directory} for logfiles...")
        response = requests.get(f"{self.url}vfs/{directory}")
        logfiles = response.json()
        for d in logfiles:
            if d["mime"] == "inode/directory":
                converted_path = self.convert_kudu_path(d["path"])
                allfiles = allfiles + self.check_directory_for_logs(
                    converted_path, allfiles
                )
        allfiles = allfiles + logfiles
        allfiles = [
            d
            for d in allfiles
            if d["name"].endswith(".log") or d["name"].endswith(".txt")
        ]

        return allfiles

    def get_logs(self, line_count):
        # response = requests.get(self.url + "logs/recent")
        logfiles = self.check_directory_for_logs("LogFiles")
        sorted_logfiles = sorted(logfiles, key=lambda d: d["mtime"])
        logfile_count = 1
        log_lines = []

        while len(log_lines) < line_count and logfile_count <= len(sorted_logfiles):
            logpath = sorted_logfiles[len(sorted_logfiles) - logfile_count]["path"]
            logdate = sorted_logfiles[len(sorted_logfiles) - logfile_count]["mtime"]

            converted_path = self.convert_kudu_path(logpath)
            logging.info(f"Pre-pending contents of {converted_path} from {logdate}...")
            response = requests.get(f"{self.url}vfs/{converted_path}")

            lines = response.text.split("\r\n")
            log_lines = lines + log_lines
            logfile_count = logfile_count + 1
            logging.debug(f"You now have {len(log_lines)}/{line_count} lines")

        print("\n".join(log_lines[-line_count:]))

    def deploy_zip(self, path):
        """
        https://github.com/projectkudu/kudu/wiki/REST-API#zip-deployment

        Deploy from zip asynchronously. The Location header of the response
        will contain a link to a pollable deployment status.
        """
        try:
            with open(path, "rb") as f:
                zipfile = f.read()

            response = requests.put(self.url + "zipdeploy?isAsync=true", data=zipfile)

            if response.ok:
                timeout = time() + 60
                while time() < timeout:
                    logging.debug(f"Checking deployment {response.headers['Location']}")
                    status = requests.get(
                        response.headers["Location"], headers=self.headers
                    )
                    logging.debug(f"Deployment Complete: {status.json()['complete']}")
                    if status.json()["complete"]:
                        return status.json()

            raise AssertionError(
                f"Deploying {path} on {self.url}zipdeploy\n"
                + f"Code:{response.status_code}, Message: {response.text}"
            )
        except Exception as error:
            logging.debug(f"Failed to deploy {path} from {self.url}zipdeploy: {error}")
            logging.debug(traceback.format_exc())
            raise error

    def download_zip(self, source, destination):
        """
        https://github.com/projectkudu/kudu/wiki/REST-API#zip

        Zip up and download the specified folder. The zip doesn't include the
        top folder itself. Make sure you include the trailing slash!
        """
        try:
            response = requests.get(f"{self.url}zip/{source}")
            logging.debug(response.headers)
            zipbytes = response.content
            zipfile = open(destination, "wb")
            zipfile.write(zipbytes)
            zipfile.close()
        except Exception as error:
            logging.debug(
                f"Failed to download zip from {self.url}zip/{source}: {error}"
            )
            logging.debug(traceback.format_exc())
            raise error

        return response

    def get_endpoint(self, endpoint):
        """
        https://github.com/projectkudu/kudu/wiki/REST-API
        """
        try:
            response = requests.get(self.url + endpoint)
            if response.ok is False:
                raise AssertionError(
                    f"Failed to get {endpoint} on {self.url}\n"
                    + f"Code:{response.status_code}\n"
                    + f"Response: {response.text}"
                )
        except Exception as error:
            logging.debug(f"Failed to get {endpoint} from {self.url}: {error}")
            logging.debug(traceback.format_exc())
            raise error

        logging.debug(
            "Output:\n" + json.dumps(response.json(), indent=2, sort_keys=True)
        )
        return response.json()

    def run_cmd(self, cmd, cwd):
        """
        https://github.com/projectkudu/kudu/wiki/REST-API#command
        """
        logging.debug(f"Running {cmd} on {self.app}/{cwd}...")
        payload = {"command": cmd, "dir": cwd}

        try:
            response = requests.post(self.url + "command", json=payload)
            if response.ok is False:
                raise AssertionError(
                    f"Failed to run {cmd} on {self.url}/{cwd}\n"
                    + f"Code:{response.status_code}\n"
                    + f"Response: {response.text}"
                )
        except Exception as error:
            logging.debug(f"Failed to run {cmd} on {self.app}/{cwd}: {error}")
            logging.debug(traceback.format_exc())
            raise error

        logging.debug(
            "Output:\n" + json.dumps(response.json(), indent=2, sort_keys=True)
        )
        return response.json()
