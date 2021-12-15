import json
import logging
import subprocess
import traceback
from configparser import ConfigParser
from azure.common.credentials import (
    ServicePrincipalCredentials,
    get_azure_cli_credentials,
)


def get_cmd_stdout(cmd):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    process.wait()
    data, err = process.communicate()
    return data.decode("utf-8")


class AzureExtras:
    def __init__(self, path, rg):
        self.config_path = path
        sub = self.get_subscription()
        token = self.get_access_token()
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self.url = (
            f"https://management.azure.com/subscriptions/{sub}/resourceGroups/{rg}"
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

    def get_subscription(self):
        try:
            return get_azure_cli_credentials()[1]
        except Exception as error:
            logging.warning("Couldn't get subscription id from Azure CLI.")

        try:
            client, secret, tenant, sub = self.get_config(self.config_path)
            return sub
        except Exception as error:
            logging.error("Failed to get a subscription id.")

    def get_access_token(self):
        try:
            access_token = json.loads(get_cmd_stdout("az account get-access-token"))[
                "accessToken"
            ]
            logging.info("Authenticated with Azure CLI credentials.")
            return access_token
        except Exception as error:
            logging.warning("Failed to authenticate using Azure CLI credentials.")

        try:
            client, secret, tenant, sub = self.get_config(self.config_path)
            credentials = ServicePrincipalCredentials(
                client_id=client,
                secret=secret,
                tenant=tenant,
            )
            access_token = credentials.token["access_token"]
            logging.info(
                f"Authenticated with Service Principal credentials from {self.config_path}"
            )
            logging.debug(f"Access Token:\n\n{access_token}\n")
            return access_token
        except Exception as error:
            logging.debug(traceback.format_exc())
            raise error
