"""Converter to Markdown format.

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
        # lobster-trace: SwRequirements.sw_req_markdown
        self._source_items = []
        self._out_path = ""
        self._project_module = None

    def register(self, args_parser):
        # lobster-trace: SwRequirements.sw_req_markdown
        """Register converter specific argument parser.

        Args:
            args_parser (object): Argument parser
        """
        parser = args_parser.add_parser(
            'markdown',
            help="Convert to Markdown format."
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

        # Load the project module if specified.
        if args.project is not None:
            result = self._load_project_module(args.project)

        if result == Ret.OK:
            # Prepare output folder.
            self._create_out_folder()

            # Generate one Markdown file for every file.
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
                    result = self._generate_out_file(file_name, item_list)

                    if result != Ret.OK:
                        break

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

    def _generate_out_file(self, file_name, item_list):
        # lobster-trace: SwRequirements.sw_req_markdown_out_folder
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
                result = self._convert_section(fd, item[0], item[1])
            elif is_item_record(item):
                result = self._convert_record_object(fd, item[0], item[1])
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

    def _project_module_convert_section(self, fd, section, level):
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
                result = self._project_module.convert_section(fd, section, level)

        return result

    def _project_module_convert_record_object(self, fd, record_object, level):
        # lobster-trace: SwRequirements.sw_req_prj_exec
        """Convert a record object to the destination format in a use project specific way.

        Args:
            fd (File): File descriptor of the output file.
            record_object (Record_Object): The record object to convert.
            level (int): The record level.

        Returns:
            Ret: Status
        """
        result = Ret.ERROR

        if self._project_module is not None:
            if hasattr(self._project_module, "convert_record_object"):
                result = self._project_module.convert_record_object(fd, record_object, level)

        return result

    def _convert_section(self, fd, section, level):
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
            fd.write(f"{'#' * (level + 1)} {section}\n\n")

        else:
            result = self._project_module_convert_section(fd, section, level)

        return result

    def _convert_record_object(self, fd, record_object, level):
        # lobster-trace: SwRequirements.sw_req_markdown_record
        # lobster-trace: SwRequirements.sw_req_markdown_prj_spec
        # lobster-trace: SwRequirements.sw_req_no_prj_spec
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
            result = self._project_module_convert_record_object(fd, record_object, level)

        return result

# Functions ********************************************************************

def markdown_escape(text):
    # lobster-trace: SwRequirements.sw_req_markdown_escape
    """Escapes the text to be used in a Markdown document.

    Args:
        text (str): Text to escape

    Returns:
        str: Escaped text
    """
    characters = ["\\", "`", "*", "_", "{", "}", "[", "]", "<", ">", "(", ")", "#", "+", "-", ".", "!", "|"]

    for character in characters:
        text = text.replace(character, "\\" + character)

    return text

def markdown_create_heading(text, level):
    # lobster-trace: SwRequirements.sw_req_markdown_heading
    """Create a Markdown heading.
        The text will be automatically escaped for Markdown if necessary.

    Args:
        text (str): Heading text
        level (int): Heading level

    Returns:
        str: Markdown heading
    """
    return f"{'#' * level} {markdown_escape(text)}\n\n"

def markdown_create_table_head(column_titles):
    # lobster-trace: SwRequirements.sw_req_markdown_table
    """Create the table head for a Markdown table.
        The titles will be automatically escaped for Markdown if necessary.

    Args:
        column_titles ([str]): List of column titles.

    Returns:
        str: Table head
    """
    table_head = "|"

    for column_title in column_titles:
        table_head += f" {markdown_escape(column_title)} |"

    table_head += "\n"

    table_head += "|"

    for column_title in column_titles:
        for _ in range(len(markdown_escape(column_title))):
            table_head += "-"

        table_head += " |"

    table_head += "\n"

    return table_head

def markdown_append_table_row(row_values):
    # lobster-trace: SwRequirements.sw_req_markdown_table_row
    """Append a row to a Markdown table.
        The values will be automatically escaped for Markdown if necessary.

    Args:
        row_values ([str]): List of row values.

    Returns:
        str: Table row
    """
    table_row = "|"

    for row_value in row_values:
        table_row += f" {markdown_escape(row_value)} |"

    table_row += "\n"

    return table_row

def markdown_create_link(text, url):
    # lobster-trace: SwRequirements.sw_req_markdown_link
    """Create a Markdown link.
        The text will be automatically escaped for Markdown if necessary.
        There will be no newline appended at the end.

    Args:
        text (str): Link text
        url (str): Link URL

    Returns:
        str: Markdown link
    """
    return f"[{markdown_escape(text)}]({url})"

def markdown_create_diagram_link(diagram_file_name, diagram_caption):
    # lobster-trace: SwRequirements.sw_req_markdown_image
    """Create a Markdown diagram link.
        The caption will be automatically escaped for Markdown if necessary.

    Args:
        diagram_file_name (str): Diagram file name
        diagram_caption (str): Diagram caption

    Returns:
        str: Markdown diagram link
    """
    return f"![{markdown_escape(diagram_caption)}](./{diagram_file_name})\n"

# Main *************************************************************************
