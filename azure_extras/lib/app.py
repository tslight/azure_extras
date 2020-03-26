import json
import logging
import requests
import traceback
from time import time
from .az import AzureExtras


class AppService(AzureExtras):
    def __init__(self, path, rg):
        super().__init__(path, rg)
        self.url = f"{self.url}/providers/Microsoft.Web/sites"

    def get_publishing_credentials(self, app):
        """
        https://docs.microsoft.com/en-us/rest/api/appservice/webapps/listpublishingcredentials
        """
        url = f"{self.url}/{app}/config/publishingcredentials/list"
        params = {"api-version": "2019-08-01"}

        try:
            response = requests.post(url, headers=self.headers, params=params)
            if response.ok:
                logging.debug(json.dumps(response.json(), indent=2))
                return response.json()["properties"]
            raise AssertionError(
                f"Failed to get publishing credentials for {app}: {response.status_code}"
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
            if response.ok is False:
                raise AssertionError(
                    f"Failed to patch {url} with {patch}, Code:{response.status_code}"
                )
            content = response.json()
            success = (
                content["properties"]["healthCheckPath"]
                == patch["properties"]["healthCheckPath"]
            )
            logging.debug(json.dumps(content, indent=2, sort_keys=True))
            if success is False:
                raise AssertionError(f"Failed to patch {url} with {patch}.")
        except requests.exceptions.ConnectionError as error:
            logging.warning("Transient connection issue. Trying again...")
            logging.debug(error)
            timeout = time() + 10
            while time() < timeout:
                return self.toggle_health_check(app, action)
        except Exception as error:
            logging.debug(traceback.format_exc())
            raise error

    def get_app_service(self, app):
        """
        Get App Service
        """
        url = f"{self.url}/{app}"
        params = {"api-version": "2019-08-01"}

        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.ok:
                return response.json()["properties"]
            raise AssertionError(f"Failed to get {app}: {response.status_code}")
        except Exception as error:
            logging.error(f"Failed to get status of {app}: {error}")
            logging.debug(traceback.format_exc())

    def list_app_service_slots(self, app):
        """
        List App Service Slots
        """
        url = f"{self.url}/{app}/slots"
        params = {"api-version": "2019-08-01"}

        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.ok:
                return response.json()
            raise AssertionError(
                f"Failed to get slots for {app}: {response.status_code}"
            )
        except Exception as error:
            logging.error(f"Failed to get slots for {app}: {error}")
            logging.debug(traceback.format_exc())

    def get_app_service_slot(self, app, slot):
        """
        Get App Service Slot
        """
        url = f"{self.url}/{app}/slots/{slot}"
        params = {"api-version": "2019-08-01"}

        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.ok:
                return response.json()["properties"]
            raise AssertionError(f"Failed to get {slot}: {response.status_code}")
        except Exception as error:
            logging.error(f"Failed to get status of {slot}: {error}")
            logging.debug(traceback.format_exc())

    def toggle_app_service(self, app, action):
        """
        START/STOP an Azure App Service
        """
        logging.debug(f"{action.capitalize()} {app}")
        url = f"{self.url}/{app}/{action}"
        params = {"api-version": "2016-08-01"}

        try:
            response = requests.post(url, headers=self.headers, params=params)
            if response.ok is False:
                raise AssertionError(
                    f"Failed to {action} {app}: {response.status_code}"
                )

            logging.info(f"Sent {action.capitalize()} to {app}")

            timeout = time() + 30
            while time() < timeout:
                status = self.get_app_service(app)["state"]
                started = status == "Running" and action == "start"
                stopped = status == "Stopped" and action == "stop"
                if started or stopped:
                    return status

            raise AssertionError(f"Failed to {action} {app}: {status}")
        except requests.exceptions.ConnectionError as error:
            logging.warning("Transient connection issue. Trying again...")
            logging.debug(error)
            timeout = time() + 10
            while time() < timeout:
                return self.toggle_app_service(app, action)
        except Exception as error:
            logging.error(f"Failed to {action} {app}: {error}")
            logging.debug(traceback.format_exc())

    def toggle_app_service_slot(self, app, slot, action):
        """
        START/STOP an Azure App Service Slot
        """
        url = f"{self.url}/{app}/slots/{slot}/{action}"
        params = {"api-version": "2016-08-01"}

        try:
            response = requests.post(url, headers=self.headers, params=params)
            if response.ok is False:
                raise AssertionError(
                    f"Failed to {action} {slot}: {response.status_code}"
                )

            logging.info(f"Sent {action} to {slot}")

            timeout = time() + 30
            while time() < timeout:
                status = self.get_app_service_slot(app, slot)["state"]
                started = status == "Running" and action == "start"
                stopped = status == "Stopped" and action == "stop"
                if started or stopped:
                    return status

            raise AssertionError(f"Failed to {action} {slot}: {status}")
        except requests.exceptions.ConnectionError as error:
            logging.warning("Transient connection issue. Trying again...")
            logging.debug(error)
            timeout = time() + 10
            while time() < timeout:
                return self.toggle_app_service_slot(app, slot, action)
        except Exception as error:
            logging.error(f"Failed to {action} {slot}: {error}")
            logging.debug(traceback.format_exc())
