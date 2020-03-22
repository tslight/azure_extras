# Copyright (c) 2018, Toby Slight. All rights reserved.
# ISC License (ISCL) - see LICENSE file for details.

name = "azure_extras"
from .lib.az import AzureExtras
from .lib.app import AppService
from .lib.kudu import KuduClient
from .lib.saj import StreamAnalyticsJobs
