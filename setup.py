# Copyright (c) 2018, Toby Slight. All rights reserved.
# ISC License (ISCL) - see LICENSE file for details.

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="azure_extras",
    version="0.1.8",
    author="Toby Slight",
    author_email="tslight@pm.me",
    description="The stuff Microsoft left out..",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/tspub/py/azure_extras",
    install_requires=["azure", "requests"],
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
