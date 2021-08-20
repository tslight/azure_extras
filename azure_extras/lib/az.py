import json
import logging
import traceback
from configparser import ConfigParser
from azure.common.credentials import ServicePrincipalCredentials


class AzureExtras:
    def __init__(self, path, rg):
        self.client, self.secret, self.tenant, self.sub = self.get_config(path)
        token = self.get_access_token()
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self.url = (
            f"https://management.azure.com/subscriptions/{self.sub}/resourceGroups/{rg}"
        )
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
