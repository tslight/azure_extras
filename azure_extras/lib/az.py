import json
import logging
import re
import requests
import sys
import traceback
from configparser import ConfigParser
from azure.common.credentials import ServicePrincipalCredentials
from bs4 import BeautifulSoup


def get_access_token(client_id, secret, tenant):
    try:
        credentials = ServicePrincipalCredentials(
            client_id=client_id, secret=secret, tenant=tenant,
        )
        access_token = credentials.token["access_token"]
        logging.debug(f"Access Token:\n\n{access_token}\n")
        return access_token
    except Exception as error:
        logging.debug(traceback.format_exc())
        raise error


def get_az_details(path):
    try:
        config = ConfigParser()
        config.read(path)
        az_details = config["azure"]
    except Exception as error:
        logging.error(f"Failed to retrieve config from {path}. Aborting.")
        logging.error(error)
        sys.exit(1)

    if az_details:
        logging.info(f"Found Azure configuration at {path}.")
        return az_details

    logging.error(f"Failed to retrieve Azure details from {path}. Aborting.")
    sys.exit(1)


class AzureExtras:
    def __init__(self, config_path):
        self.az = get_az_details(config_path)
        token = get_access_token(
            self.az["client_id"], self.az["secret"], self.az["tenant"]
        )
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self.url = f"https://management.azure.com/subscriptions/{self.az['sub_id']}"
        logging.debug("HEADERS:\n" + json.dumps(self.headers))

    def toggle_health_check(self, rg, app, enable):
        url = f"{self.url}/resourceGroups/{rg}/providers/Microsoft.Web/sites/{app}/config/web"
        params = {"api-version": "2018-02-01"}

        if enable:
            patch = {"properties": {"healthCheckPath": "/status/status.cshtml"}}
        else:
            patch = {"properties": {"healthCheckPath": "null"}}

        try:
            response = requests.patch(
                url, headers=self.headers, params=params, data=json.dumps(patch)
            )
            content = response.json()
            success = (
                content["properties"]["healthCheckPath"]
                == patch["properties"]["healthCheckPath"]
            )
            logging.debug(json.dumps(content, indent=2, sort_keys=True))
            if response.ok is False or success is False:
                raise AssertionError(
                    f"Failed to patch {url} with {patch}\n"
                    + f"Code:{response.status_code}"
                )
        except Exception as error:
            logging.debug(traceback.format_exc())
            raise error

    def get_stream_analytics_job(self, rg, job):
        url = f"{self.url}/resourceGroups/{rg}/providers/Microsoft.StreamAnalytics/streamingjobs/{job}"
        params = {
            "api-version": "2015-10-01",
            "$expand": "inputs,transformation,outputs,functions",
        }
        try:
            response = requests.get(url, headers=self.headers, params=params)
            body = json.loads(response.content if response.content else "{}")
            logging.debug(json.dumps(body))
            if response.ok is False:
                raise AssertionError(
                    f"Failed to get {job} status from {url}\n"
                    + f"Response Code: {response.status_code}\n"
                    + f"Response Reason: {response.reason}"
                )
        except Exception as error:
            logging.debug(traceback.format_exc())
            raise error

        return body

    def toggle_stream_analytics_job(self, rg, job, action):
        url = f"{self.url}/resourceGroups/{rg}/providers/Microsoft.StreamAnalytics/streamingjobs/{job}/{action}"
        params = {"api-version": "2015-10-01"}

        try:
            response = requests.post(url, headers=self.headers, params=params)
            body = json.loads(response.content if response.content else "{}")
            logging.debug(json.dumps(body))
            if response.ok is False:
                raise AssertionError(
                    f"Failed to {action} {job} using {url}\n"
                    + f"Response Code: {response.status_code}\n"
                    + f"Response Reason: {response.reason}"
                )
        except Exception as error:
            logging.debug(traceback.format_exc())
            raise error

        return body

    def get_publish_profile(self, rg, app):
        """
        Get FTP and Web App credentials (username, password, hostname)
        https://docs.microsoft.com/en-us/rest/api/appservice/webapps/listpublishingprofilexmlwithsecrets
        """
        url = f"{self.url}/resourceGroups/{rg}/providers/Microsoft.Web/sites/{app}/publishxml"
        params = {"api-version": "2016-08-01"}

        try:
            response = requests.post(url, headers=self.headers, params=params)
            body = json.loads(response.content if response.content else "{}")
            if response.ok:
                soup = BeautifulSoup(response.text, features="html.parser")
                logging.debug(f"Response XML:\n\n{soup.prettify()}\n")

                web_pp = soup.select("publishProfile")[0]
                ftp_pp = soup.select("publishProfile")[1]
                ftp_host = re.search(
                    r"ftp:\/\/(.*)/site/wwwroot", ftp_pp["publishurl"], re.IGNORECASE
                ).group(1)

                publish_profile = {
                    "web_url": web_pp["destinationappurl"],
                    "web_user": web_pp["username"],
                    "web_passwd": web_pp["userpwd"],
                    "ftp_host": ftp_host,
                    "ftp_user": ftp_pp["username"],
                    "ftp_passwd": ftp_pp["userpwd"],
                }

                logging.debug(
                    "Publish Profile:\n" + json.dumps(publish_profile, indent=2)
                )
                return publish_profile

            logging.debug("\n" + json.dumps(body, indent=2, sort_keys=True))
            raise AssertionError(
                f"Failed to get PublishProfile using {url}\n"
                + f"Response Code: {response.status_code}\n"
                + f"Response Message: {body['error']['message']}\n"
                + f"Response Reason: {response.reason}"
            )
        except Exception as error:
            logging.debug(traceback.format_exc())
            raise error
