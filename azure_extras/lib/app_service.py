import json
import logging
import re
import requests
import traceback
from bs4 import BeautifulSoup
from .az import AzureExtras


class AppService(AzureExtras):
    def __init__(self, path, rg):
        super().__init__(path, rg)
        self.url = f"{self.url}/providers/Microsoft.Web/sites"

    def get_publish_profile(self, app):
        """
        Get FTP and Web App credentials (username, password, hostname)
        https://docs.microsoft.com/en-us/rest/api/appservice/webapps/listpublishingprofilexmlwithsecrets
        """
        url = f"{self.url}/{app}/publishxml"
        params = {"api-version": "2016-08-01"}

        try:
            response = requests.post(url, headers=self.headers, params=params)
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

            logging.debug("\n" + json.dumps(response.json(), indent=2, sort_keys=True))
            raise AssertionError(
                f"Failed to get PublishProfile using {url}\n"
                + f"Response Code: {response.status_code}\n"
                + f"Response Message: {body['error']['message']}\n"
                + f"Response Reason: {response.reason}"
            )
        except Exception as error:
            logging.debug(traceback.format_exc())
            raise error

    def toggle_health_check(self, app, action):
        url = f"{self.url}/{app}/config/web"
        params = {"api-version": "2018-02-01"}

        if action == "enable":
            patch = {"properties": {"healthCheckPath": "/status/status.cshtml"}}
        elif action == "disable":
            patch = {"properties": {"healthCheckPath": "null"}}
        else:
            raise ValueError(f"{action} is invalid!")

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

    def toggle_app_service(self, app, action):
        """
        START/STOP an Azure App
        https://docs.microsoft.com/en-us/rest/api/appservice/webapps/start
        https://docs.microsoft.com/en-us/rest/api/appservice/webapps/stop
        """
        logging.debug(f"{action.capitalize()} {app_name}")
        url = f"{self.url}/{app}/{action}"
        params = {"api-version": "2016-08-01"}

        try:
            response = requests.post(url, headers=self.headers, params=params)
            if response.status_code == 200:
                logging.info(f"{action.capitalize()} {app}")
                return True
            else:
                logging.error(f"Failed to {action} {app}: {response.status_code}")
                return False
        except Exception as error:
            logging.error(f"Failed to {action} {app}: {error}")
            logging.debug(traceback.format_exc())
            return False

    def toggle_app_service_slot(self, app, slot, action):
        """
        START/STOP an Azure App Slot
        """
        url = f"{self.url}/{app}/slots/{slot}/{action}"
        params = {"api-version": "2016-08-01"}

        try:
            response = requests.post(url, headers=self.headers, params=params)
            if response.status_code == 200:
                logging.info(f"{action.capitalize()} {slot}")
                return True
            else:
                logging.error(f"Failed to {action} {slot}: {response.status_code}")
                return False
        except Exception as error:
            logging.error(f"Failed to {action} {slot}: {error}")
            logging.debug(traceback.format_exc())
            return False
