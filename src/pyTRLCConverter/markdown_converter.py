"""Converter to Markdown format.

    Author: Andreas Merkle (andreas.merkle@newtec.de)
"""

# This file is part of the pyTRLCConverter program.
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
from pyTRLCConverter.iconverter import IConverter
from pyTRLCConverter.ret import Ret
from pyTRLCConverter.trlc_helper import get_file_dict_from_symbols, is_item_section, is_item_record
from pyTRLCConverter.log_verbose import log_verbose

# Variables ********************************************************************

# Classes **********************************************************************

class MarkdownConverter(IConverter):
    """Converts a section tree to Markdown format.
    """
    def __init__(self) -> None:
        self._source_items = []
        self._out_path = ""
        self._project_module = None

    def register(self, args_parser):
        """Register converter specific argument parser.

        Args:
            args_parser (object): Argument parser
        """
        parser = args_parser.add_parser(
            'markdown',
            help="Convert to Markdown format."
        )

        parser.add_argument(
            "-o",
            "--out",
            type=str,
            default="",
            required=False,
            help="Output path, e.g. /out/markdown."
        )

        parser.add_argument(
            "-p",
            "--project",
            type=str,
            default=None,
            required=False,
            help="Python module with project specific conversion functions."
        )

        parser.set_defaults(func=self.convert)

    def convert(self, args, symbols):
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

        # Load the project module if specified.
        if args.project is not None:
            result = self._load_project_module(args.project)

        if result == Ret.OK:
            # Prepare output folder.
            self._create_out_folder()

            # Generate one Markdown file for every file.
            files_dict = get_file_dict_from_symbols(symbols)

            for file_name, item_list in files_dict.items():
                self._init_project_module()

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
                    result = self._generate_out_file(file_name, item_list)

                    if result != Ret.OK:
                        break

        return result

    def _load_project_module(self, project_module):
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
        """Create output folder if it doesn't exist.
        """
        if 0 < len(self._out_path):
            if not os.path.exists(self._out_path):
                os.makedirs(self._out_path)

    def _generate_out_file(self, file_name, item_list):
        """Generate the output file.

        Args:
            file_name (str): File name of the input file.
            item_list ([Element]): List of elements.

        Returns:
            Ret: Status
        """
        result = Ret.OK
        input_file_name = os.path.basename(file_name)
        output_file_name = os.path.splitext(input_file_name)[0] + ".md"

        # Add path to the output file name.
        if 0 < len(self._out_path):
            output_file_name = os.path.join(self._out_path, output_file_name)

        with open(output_file_name, "w", encoding="utf-8") as fd:
            result = self._convert(fd, item_list)

        return result

    def _convert(self, fd, item_list):
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
                result = self._convert_section(fd, item[0], item[1])
            elif is_item_record(item):
                result = self._convert_record_object(fd, item[0], item[1])
            else:
                result = Ret.ERROR

            if result != Ret.OK:
                break

        return Ret.OK

    def _init_project_module(self):
        """Initialize the project module.
        """
        if self._project_module is not None:
            if hasattr(self._project_module, "init"):
                self._project_module.init(self._source_items, self._out_path)

    def _convert_section(self, fd, section, level):
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
            fd.write(f"{'#' * (level + 1)} {section}\n\n")

        else:
            if hasattr(self._project_module, "convert_section"):
                result = self._project_module.convert_section(fd, section, level)
            else:
                result = Ret.ERROR

        return result

    def _convert_record_object(self, fd, record_object, level):
        """Convert a record object to the destination format.

        Args:
            fd (File): File descriptor of the output file.
            record_object (Record_Object): The record object to convert.
            level (int): The record level.

        Returns:
            Ret: Status
        """
        result = Ret.OK

        if self._project_module is None:
            fd.write(f"{record_object.name}\n")
            fd.write(f"{record_object.to_python_dict()}\n\n")

        else:
            if hasattr(self._project_module, "convert_record_object"):
                result = self._project_module.convert_record_object(fd, record_object, level)
            else:
                result = Ret.ERROR

        return result

# Functions ********************************************************************

# Main *************************************************************************
