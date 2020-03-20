# THE STUFF MICROSOFT LEFT OUT

W.I.P. Azure stuff to make my life easier.

So far just a couple of classes to make dealing with Azure App Services less
painful from a DevOps perspective.

## INSTALLATION

`pip install azure-extras`

## CONFIGURATION

Copy [azure.example.ini](./azure.example.ini) to `$HOME/.azure.ini`, adding
your subscription and tenant details along the way.

This location can be customised with the `--config` flag at runtime.

## APP SERVICE KUDU API CLI FRONTEND

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

``` text
usage: az-health-check [-h] [-a NAME] [-r NAME] (-e | -d) [-C PATH] [-v]

Toggle health check in Azure App Service

optional arguments:
  -h, --help              :show this help message and exit
  -a NAME, --app NAME     :azure app service name
  -r NAME, --rg NAME      :azure resource group
  -e, --enable            :enable health check
  -d, --disable           :disable health check
  -C PATH, --config PATH  :path to azure configuration file
  -v                      :increase verbosity
```
