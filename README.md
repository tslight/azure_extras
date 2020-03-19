# THE STUFF MICROSOFT LEFT OUT

## INSTALLATION

`pip install azure_extras`

## KUDU CLI FRONTEND

``` text
usage: az-kudu [-h] [-a NAME] [-C PATH] [-r NAME]
			   (-c COMMAND | -e SLUG | -z PATH | -Z SOURCE DESTINATION)
			   [-p PATH] [-v]

CLI Kudu API fudger

optional arguments:
  -h, --help            show this help message and exit
  -a NAME, --app NAME   azure app name
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

``` text
usage: az-health-check [-h] [-a NAME] [-r NAME] [-C PATH] [-v]

Enable health check in Azure App Service

optional arguments:
  -h, --help            show this help message and exit
  -a NAME, --app NAME   azure app name
  -r NAME, --rg NAME    azure resource group
  -C PATH, --config PATH
						path to azure configuration file
  -v                    increase verbosity
```
