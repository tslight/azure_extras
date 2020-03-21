import json
import logging
import requests
import traceback
from .az import AzureExtras


class AppService(AzureExtras):
    def __init__(self, config_path):
        super().__init__(config_path)
        self.provider = "providers/Microsoft.Web/sites"

    def toggle_health_check(self, rg, app, action):
        url = f"{self.url}/resourceGroups/{rg}/{self.provider}/{app}/config/web"
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
