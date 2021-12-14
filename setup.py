# Copyright (c) 2018, Toby Slight. All rights reserved.
# ISC License (ISCL) - see LICENSE file for details.

import setuptools
import subprocess


def get_latest_tag():
    try:
        cmd_output = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"], stdout=subprocess.PIPE
        )
        return cmd_output.stdout.strip().decode("utf-8")
    except EnvironmentError:
        print("Couldn't run git to get a version number for setup.py")


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="azure_extras",
    version=get_latest_tag(),
    author="Toby Slight",
    author_email="tslight@pm.me",
    description="The stuff Microsoft left out..",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/tslight/azure_extras",
    install_requires=["azure-common", "msrest", "msrestazure", "requests"],
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Operating System :: OS Independent",
    ),
    entry_points={
        "console_scripts": [
            "az-asctl = azure_extras.asctl:main",
            "az-healthchkctl = azure_extras.healthchkctl:main",
            "az-kuductl = azure_extras.kuductl:main",
            "az-sajctl = azure_extras.sajctl:main",
        ],
    },
)
