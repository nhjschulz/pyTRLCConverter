"""Abstract converter interface which all convertes shall fullfill.

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
from abc import ABC, abstractmethod
from pyTRLCConverter.ret import Ret

# Variables ********************************************************************

# Classes **********************************************************************

# pylint: disable=too-few-public-methods
class IConverter(ABC):
    """Abstract converter interface."""
    def __init__(self) -> None:
        pass

    @abstractmethod
    def register(self, args_parser):
        """Register converter specific argument parser.

        Args:
            args_parser (object): Argument parser
        """
        raise NotImplementedError

    @abstractmethod
    def convert(self, args, symbols) -> Ret:
        """Convert the section tree to the destination format.

        Args:
            args (object): Program arguments.
            symbols (Symbol_Table): The symbol table.
        
        Returns:
            Ret: Status
        """
        raise NotImplementedError

# Functions ********************************************************************

# Main *************************************************************************
