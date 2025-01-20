"""Log verbose functionality.

    Author: Andreas Merkle (andreas.merkle@newtec.de)
"""

# pyTRLCConverter - A tool to convert PlantUML diagrams to image files.
# Copyright (c) 2024 - 2025 NewTec GmbH
#
# This file is part of pyTRLCConverter program.
#
# The pyTRLCConverter program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# The pyTRLCConverter program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with pyTRLCConverter.
# If not, see <https://www.gnu.org/licenses/>.

# Imports **********************************************************************

# Variables ********************************************************************

_VERBOSE_ENABLED = False

# Classes **********************************************************************

# Functions ********************************************************************

def is_verbose_enabled():
    """Check if verbose mode is enabled.
    
    Returns:
        bool: True if verbose mode is enabled, False otherwise.
    """
    return _VERBOSE_ENABLED

def enable_verbose(enable):
    """Enable or disable verbose mode.
    
    Args:
        enable (bool): True to enable verbose mode, False to disable it.
    """
    global _VERBOSE_ENABLED # pylint: disable=global-statement
    _VERBOSE_ENABLED = enable

def log_verbose(message):
    """Print a message if verbose mode is enabled.
    
    Args:
        message (str): The message to print.
    """
    if _VERBOSE_ENABLED:
        print(message)

# Main *************************************************************************
