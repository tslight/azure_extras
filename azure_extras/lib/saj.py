import json
import logging
import requests
import traceback
from .az import AzureExtras
from time import time, sleep


class StreamAnalyticsJobs(AzureExtras):
    def __init__(self, path, rg):
        super().__init__(path, rg)
        self.url = f"{self.url}/providers/Microsoft.StreamAnalytics/streamingjobs"

    def get_stream_analytics_job(self, job):
        url = f"{self.url}/{job}"
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

    def toggle_stream_analytics_job(self, job, action):
        url = f"{self.url}/{job}/{action}"
        params = {"api-version": "2015-10-01"}

        try:
            response = requests.post(url, headers=self.headers, params=params)
            if response.ok is False:
                raise AssertionError(
                    f"Failed to {action} {job} using {url}\n"
                    + f"Response Code: {response.status_code}\n"
                    + f"Response Reason: {response.reason}"
                )

            logging.info(f"Sent {action} to {job}")
            timeout = time() + 120
            while time() < timeout:
                logging.info(f"Checking status of {action} sent to {job}..")
                results = self.get_stream_analytics_job(job)
                status = results["properties"]["jobState"]
                logging.debug(f"RESULTS: {status}")
                started = action == "start" and status == "Running"
                stopped = action == "stop" and status == "Stopped"
                if started or stopped:
                    logging.info(f"Successfully sent {action} to {job}.")
                    return results
                logging.info(f"Waiting 10 seconds before checking again...")
                sleep(10)

            raise AssertionError(
                f"Failed to {action} {job}. Timed out. Status: {status}"
            )
        except Exception as error:
            logging.debug(traceback.format_exc())
            raise error
