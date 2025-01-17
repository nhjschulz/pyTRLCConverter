"""The main module with the program entry point.

The main module contains the table with the supported converters.

Author: Andreas Merkle (andreas.merkle@newtec.de)
"""

# *******************************************************************************
# Copyright (c) NewTec GmbH 2024   -   www.newtec.de
# *******************************************************************************

# Imports **********************************************************************

import sys
import logging

try:
    from pyTRLCConverter.version import __version__, __author__, __email__, __repository__, __license__
except ModuleNotFoundError:
    # provide dummy information when not installed as package but called directly
    # also necessary to get sphinx running without error
    __version__ = 'dev'
    __author__ = 'development'
    __email__ = 'none'
    __repository__ = 'none'
    __license__ = 'none'

# Variables ********************************************************************

LOG: logging.Logger = logging.getLogger(__name__)

# Classes **********************************************************************

# Functions ********************************************************************


def main() -> int:
    """ The program entry point function.

    .. uml::

        Alice -> Bob: Hi!
        Alice <- Bob: How are you?

    Returns:
        int: System exit status.
    """
    logging.basicConfig(level=logging.INFO)
    LOG.info("Hello World!")
    return 0  # return without errors

# Main *************************************************************************


if __name__ == "__main__":
    sys.exit(main())
