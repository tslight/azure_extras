import logging
import os
import sys
import numpy as np
from argparse import ArgumentTypeError


def chkpath(path):
    if os.path.exists(path):
        return os.path.abspath(path)

    raise ArgumentTypeError(f"{path} does not exist.")


def get_seconds(seconds=180):
    # linear space
    start, stop, step = 10, 100, 10
    linspace = np.linspace(start, stop, step)
    # calculate the exponential increments
    # amplitude mult, exp amplitude, const adder
    mult, exp, adder = 15, 0.01, -10
    exp_list = mult * np.exp(exp * linspace) + adder
    sec_list = [seconds]
    sec_list.extend(exp_list)
    logging.debug("Time steps: {}".format(sec_list))
    logging.debug("Number of steps:{}".format(len(sec_list)))
    return sec_list


def mklog(verbosity):
    if verbosity > 1:
        loglevel = logging.DEBUG
        logformat = "%(asctime)s %(threadName)s %(levelname)s %(message)s"
    elif verbosity == 1:
        loglevel = logging.INFO
        logformat = "%(asctime)s %(levelname)s %(message)s"
    else:
        loglevel = logging.WARNING
        logformat = "%(levelname)s %(message)s"

    logging.basicConfig(
        # filename='',
        format=logformat,
        datefmt="%Y-%m-%d %H:%M:%S",
        level=loglevel,
        stream=sys.stdout,
    )
