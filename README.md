# THE STUFF MICROSOFT LEFT OUT

W.I.P. Azure stuff to make my life easier.

So far just a couple of classes and interactive scripts to make dealing with
Azure App Services less painful from a DevOps perspective.

Oh, and one for stopping and starting Azure Stream Analytics Jobs.

## INSTALLATION

`pip install azure-extras`

## CONFIGURATION

Copy [azure.example.ini](./azure.example.ini) to `$HOME/.azure.ini`, adding
your subscription and tenant details along the way.

This location can be customised with the `--config` flag at runtime.

## APP SERVICE KUDU API CLI FRONTEND

https://github.com/projectkudu/kudu

``` text
usage: az-kudu [-h] [-a NAME] [-C PATH] [-r NAME]
			   (-c COMMAND | -e SLUG | -z PATH | -Z SOURCE DESTINATION)
			   [-p PATH] [-v]

CLI Kudu API Frontend

optional arguments:
  -h, --help            show this help message and exit
  -a NAME, --app NAME   azure app service name
  -C PATH, --config PATH
						path to azure configuration file
  -r NAME, --rg NAME    azure resource group
  -c COMMAND, --cmd COMMAND
						command to run (use quotes for multi-word commands)
  -e SLUG, --endpoint SLUG
						api endpoint slug
  -z PATH, --deploy_zip PATH
						upload a zip to the server
  -Z SOURCE DESTINATION, --download_zip SOURCE DESTINATION
						download a zip of a remote path
  -p PATH, --cwd PATH   server current working directory
  -v                    increase verbosity
```

## APP SERVICE HEALTH CHECK

Workaround until
[this](https://github.com/projectkudu/kudu/wiki/Health-Check-(Preview)#overview)
is implemented in [terraform](https://github.com/terraform-providers/terraform-provider-azurerm/issues/5147)

``` text
usage: az-chkhealth [-h] [-a NAME [NAME ...]] [-r NAME] [-A ENABLE/DISABLE]
					[-C PATH] [-v]

Toggle health check in Azure App Service

optional arguments:
  -h, --help            show this help message and exit
  -a NAME [NAME ...], --app_services NAME [NAME ...]
						list of azure app services
  -r NAME, --resource_group NAME
						azure resource group
  -A ENABLE/DISABLE, --action ENABLE/DISABLE
						action to carry out - enable or disable.
  -C PATH, --config PATH
						path to azure configuration file
  -v                    increase verbosity
```

## STREAM ANALYTICS CONTROLLER

``` text
usage: az-sajctl [-h] [-C PATH] [-r NAME] [-j JOBS [JOBS ...]] [-a START/STOP]
				 [-v]

Stream Analytics Jobs Controller

optional arguments:
  -h, --help            show this help message and exit
  -C PATH, --config PATH
						path to azure configuration file
  -r NAME, --resource_group NAME
						azure resource group
  -j JOBS [JOBS ...], --stream_analytics_jobs JOBS [JOBS ...]
						list of azure stream analytics jobs
  -a START/STOP, --action START/STOP
						action to carry out - start or stop.
  -v                    increase verbosity
```
