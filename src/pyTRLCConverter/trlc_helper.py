"""TRLC helper functions.

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
import os
from trlc.errors import Message_Handler
from trlc.trlc import Source_Manager
from trlc.ast import Record_Object
from pyTRLCConverter.log_verbose import log_verbose

# Variables ********************************************************************

# Classes **********************************************************************

# Functions ********************************************************************

def get_trlc_symbols(source_items, includes):
    # lobster-trace: SwRequirements.sw_req_destination_format
    """Get the TRLC symbol table by parsing the given folder.

    Args:
        source_items ([str]|str): One or more paths to folder with TRLC files \
                                  or a single path to a TRLC file.
        includes (str|None): Path for automatically file inclusion.

    Returns:
        Symbol_Table: TRLC symbol table
    """
    symbol_table = None

    # Create Source_Manager.
    mh = Message_Handler()
    sm = Source_Manager(mh)

    # Read all .rsl and .trlc files in the given directory.
    try:
        # Handle first the include folders, because the source folders may depend on them.
        if includes is not None:
            for folder in includes:
                log_verbose(f"Registering include folder: {folder}")
                sm.register_include(folder)

        for src_item in source_items:
            if os.path.isdir(src_item):
                log_verbose(f"Registering source folder: {src_item}")
                sm.register_directory(src_item)
            else:
                log_verbose(f"Registering source file: {src_item}")
                sm.register_file(src_item)

        symbol_table = sm.process()
    except AssertionError:
        pass

    return symbol_table

def is_item_file_name(item):
    # lobster-trace: SwRequirements.sw_req_destination_format
    """Check if the item is a file name.

    Args:
        item (str|tuple): The item to check.

    Returns:
        bool: True if the item is a file name, otherwise False.
    """
    return isinstance(item, str)

def is_item_section(item):
    # lobster-trace: SwRequirements.sw_req_destination_format
    """Check if the item is a section.

    Args:
        item (str|tuple): The item to check.

    Returns:
        bool: True if the item is a section, otherwise False.
    """
    return isinstance(item, tuple) and \
            len(item) == 2 and \
            isinstance(item[0], str) and \
            isinstance(item[1], int)

def is_item_record(item):
    # lobster-trace: SwRequirements.sw_req_destination_format
    """Check if the item is a record.

    Args:
        item (str|tuple): The item to check.

    Returns:
        bool: True if the item is a record, otherwise False.
    """
    return isinstance(item, tuple) and \
            len(item) == 2 and \
            isinstance(item[0], Record_Object) and \
            isinstance(item[1], int)

def get_file_dict_from_symbols(symbols):
    # lobster-trace: SwRequirements.sw_req_destination_format
    """Get a dictionary with the file names and their content.

    Args:
        symbols (Symbol_Table): The TRLC symbols to dump.

    Returns:
        dict: A dictionary with the file names and their content.
    """
    file_dict = {}
    item_list = None

    if symbols is not None:
        for item in symbols.iter_record_objects_by_section():
            # Is item a file name?
            if is_item_file_name(item):
                file_dict[item] = []
                item_list = file_dict[item]

            else:
                item_list.append(item)

    return file_dict

# Main *************************************************************************
