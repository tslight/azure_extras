import json
import logging
import re
import requests
import traceback
from configparser import ConfigParser
from azure.common.credentials import ServicePrincipalCredentials
from bs4 import BeautifulSoup


class AzureExtras:
    def __init__(self, path):
        self.client, self.secret, self.tenant, self.sub = self.get_config(path)
        token = self.get_access_token()
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self.url = f"https://management.azure.com/subscriptions/{self.sub}"
        logging.debug("HEADERS:\n" + json.dumps(self.headers))

    def get_config(self, path):
        try:
            config = ConfigParser()
            config.read(path)
            az = config["azure"]
        except Exception as error:
            logging.error(f"Failed to retrieve config from {path}. Aborting.")
            logging.error(error)

        if az:
            logging.info(f"Found Azure configuration at {path}.")
            return az["client"], az["secret"], az["tenant"], az["sub"]
        else:
            logging.error(f"Failed to retrieve Azure details from {path}. Aborting.")

    def get_access_token(self):
        try:
            credentials = ServicePrincipalCredentials(
                client_id=self.client, secret=self.secret, tenant=self.tenant,
            )
            access_token = credentials.token["access_token"]
            logging.debug(f"Access Token:\n\n{access_token}\n")
            return access_token
        except Exception as error:
            logging.debug(traceback.format_exc())
            raise error

    def get_publish_profile(self, rg, app):
        """
        Get FTP and Web App credentials (username, password, hostname)
        https://docs.microsoft.com/en-us/rest/api/appservice/webapps/listpublishingprofilexmlwithsecrets
        """
        url = f"{self.url}/resourceGroups/{rg}/providers/Microsoft.Web/sites/{app}/publishxml"
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
