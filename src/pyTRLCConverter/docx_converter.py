"""Converter to Markdown format.

    Author: Norbert Schulz (norbert.schulz@newtec.de)
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
import sys
import importlib
import docx
from pyTRLCConverter.iconverter import IConverter
from pyTRLCConverter.ret import Ret
from pyTRLCConverter.trlc_helper import get_file_dict_from_symbols, is_item_section, is_item_record
from pyTRLCConverter.log_verbose import log_verbose

# Variables ********************************************************************

# Classes **********************************************************************

class DocxConverter(IConverter):
    """Converts a section tree to docx format.
    """
    def __init__(self) -> None:
        # lobster-trace: SwRequirements.sw_req_markdown
        self._source_items = []
        self._out_path = ""
        self._project_module = None
        self._docx_filename = None
        self._docx = None

    def register(self, args_parser):
        # lobster-trace: SwRequirements.sw_req_markdown
        """Register converter specific argument parser.

        Args:
            args_parser (object): Argument parser
        """
        parser = args_parser.add_parser(
            'docx',
            help="Convert to docx format."
        )

        parser.set_defaults(func=self.convert)

    def convert(self, args, symbols):
        # lobster-trace: SwRequirements.sw_req_prj_spec
        # lobster-trace: SwRequirements.sw_req_markdown_file
        """Convert the section tree to the destination format.

        Args:
            args (object): Program arguments.
            symbols (Symbol_Table): The symbol table.
        
        Returns:
            Ret: Status
        """
        result = Ret.OK

        # Take over some program arguments.
        self._source_items = args.source
        self._out_path = args.out

        # Add path to the output file name.
        if 0 < len(self._out_path):
            self._docx_filename = os.path.join(self._out_path, "output.docx")
        else:
            self._docx_filename = "output.docx"

        # Load the project module if specified.
        if args.project is not None:
            result = self._load_project_module(args.project)

        if result == Ret.OK:
            # Prepare output folder.
            self._create_out_folder()

            # create word document
            self._docx = docx.Document()

            # get input file list
            files_dict = get_file_dict_from_symbols(symbols)

            for file_name, item_list in files_dict.items():
                self._project_module_init()

                # Skip files from excluded paths.
                skip_it = False
                if args.exclude is not None:
                    for excluded_path in args.exclude:
                        if os.path.commonpath([excluded_path, file_name]) == excluded_path:
                            skip_it = True
                            break

                if skip_it is True:
                    log_verbose(f"Skip file {file_name}.")
                else:
                    log_verbose(f"Generate for {file_name}.")

                    result = self._convert(item_list)

                    if result != Ret.OK:
                        break

            self._docx.save(self._docx_filename)
        return result

    def _load_project_module(self, project_module):
        # lobster-trace: SwRequirements.sw_req_prj_spec
        # lobster-trace: SwRequirements.sw_req_prj_spec_func
        """Load the project module.

        Args:
            project_module (str): Python module name.

        Returns:
            Ret: Status
        """
        result = Ret.OK
        try:
            sys.path.append(os.path.dirname(project_module))
            module_name = os.path.basename(project_module).replace('.py', '')
            self._project_module = importlib.import_module(module_name)
        except ImportError as exc:
            print(exc)
            result = Ret.ERROR

        return result

    def _create_out_folder(self):
        # lobster-trace: SwRequirements.sw_req_markdown_out_folder
        """Create output folder if it doesn't exist.
        """
        if 0 < len(self._out_path):
            if not os.path.exists(self._out_path):
                os.makedirs(self._out_path)

    def _convert(self, item_list):
        # lobster-trace: SwRequirements.sw_req_markdown_section
        # lobster-trace: SwRequirements.sw_req_markdown_record
        """Convert the list of items to the destination format.
            The item list contains a list of tuples with sections and
            record objects.

        Args:
            fd (File): File descriptor of the output file.
            item_list (list[tuple]): The item list.
        
        Returns:
            Ret: Status
        """
        result = Ret.OK

        for item in item_list:
            if is_item_section(item):
                result = self._convert_section(item[0], item[1])
            elif is_item_record(item):
                result = self._convert_record_object(item[0], item[1])
            else:
                result = Ret.ERROR

            if result != Ret.OK:
                break

        return Ret.OK

    def _project_module_init(self):
        # lobster-trace: SwRequirements.sw_req_prj_exec
        """Initialize the project module.
        """
        if self._project_module is not None:
            if hasattr(self._project_module, "init"):
                self._project_module.init(self._source_items, self._out_path)

    def _project_module_convert_section(self, section, level):
        # lobster-trace: SwRequirements.sw_req_prj_exec
        """Convert a section to the destination format in a user project specific way.

        Args:
            fd (File): File descriptor of the output file.
            section (str): The section name.
            level (int): The section level.

        Returns:
            Ret: Status
        """
        result = Ret.ERROR

        if self._project_module is not None:
            if hasattr(self._project_module, "convert_section"):
                result = self._project_module.convert_section(section, level)

        return result

    def _project_module_convert_record_object(self, record_object, level):
        # lobster-trace: SwRequirements.sw_req_prj_exec
        """Convert a record object to the destination format in a use project specific way.

        Args:
            record_object (Record_Object): The record object to convert.
            level (int): The record level.

        Returns:
            Ret: Status
        """
        result = Ret.ERROR

        if self._project_module is not None:
            if hasattr(self._project_module, "convert_record_object"):
                result = self._project_module.convert_record_object(self, record_object, level)

        return result


    def _convert_section(self, section, level):
        # lobster-trace: SwRequirements.sw_req_markdown_section
        # lobster-trace: SwRequirements.sw_req_markdown_prj_spec
        # lobster-trace: SwRequirements.sw_req_no_prj_spec
        """Convert a section to the destination format.

        Args:
            fd (File): File descriptor of the output file.
            section (str): The section name.
            level (int): The section level.

        Returns:
            Ret: Status
        """
        result = Ret.OK

        if self._project_module is None:
            self._docx.add_heading(section, level)
        else:
            result = self._project_module_convert_section(section, level)

        return result

    def _convert_record_object(self, record_object, level):
        # lobster-trace: SwRequirements.sw_req_markdown_record
        # lobster-trace: SwRequirements.sw_req_markdown_prj_spec
        # lobster-trace: SwRequirements.sw_req_no_prj_spec
        """Convert a record object to the destination format.

        Args:
            record_object (Record_Object): The record object to convert.
            level (int): The record level.

        Returns:
            Ret: Status
        """
        result = Ret.OK

        if self._project_module is None:
            self._docx.add_heading(f"{record_object.name} ({record_object.n_typ.name})", level + 1)
            attributes = record_object.to_python_dict()

            table = self._docx.add_table(rows=1, cols=2)
            table.style = 'Table Grid'
            table.autofit = True

            header_cells = table.rows[0].cells
            header_cells[0].text = "Element"
            header_cells[1].text = "Value"

            for key, value in attributes.items():
                if value is None:
                    value = "N/A"

                cells = table.add_row().cells
                cells[0].text = key
                cells[1].text = value
        else:
            result = self._project_module_convert_record_object(record_object, level)

        return result

# Functions ********************************************************************


# Main *************************************************************************
