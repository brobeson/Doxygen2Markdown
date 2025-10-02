"""Process a single Doxygen XML file."""

import glob
import logging
import os.path
from typing import List, Optional
from xml.etree import ElementTree
from dox_md import markdown_writer


def find_xml_files(input_path: str) -> List[str]:
    """
    Find all the Doxygen XML files for processing.

    Args:
        input_path (str): The path to the directory containing Doxygen XML files.

    Returns:
        List[str]: A list of all Doxygen XML files. If ``input_path`` is absolute, the returned
        file paths will also be absolute. Otherwise the returned file paths are relative.
    """
    files = glob.glob(f"{input_path}/**/*.xml", recursive=True)
    return files


def process_xml_files(file_paths: List[str], writer: markdown_writer.Writer) -> None:
    """
    Read the Doxygen XML files.

    Args:
        file_paths (List[str]): The Doxygen XML files to process.
    """
    for file_path in file_paths:
        _process_xml_file(file_path, writer)


def _process_xml_file(file_path: str, md_writer: markdown_writer.Writer) -> None:
    file_name = os.path.basename(file_path)
    if file_name.startswith("class"):
        logging.info("Processing %s", file_name)
        class_doc = ClassDocumentation(file_path)
        with markdown_writer.new_file(md_writer, file_name) as _:
            md_writer.write_heading(1, f"`{class_doc.name}`")
    else:
        logging.warning("Skipping %s", file_name)


class MissingTag(Exception):
    """Report that a required tag is missing from the Doxygen XML."""

    def __init__(self, tag: str, file: str):
        self.tag = tag
        self.file = file

    def __str__(self) -> str:
        return f"Missing tag <{self.tag}> from file {self.file}"


class MissingValue(MissingTag):
    """Report that a required tag is present in the Doxygen XML, but is missing its value."""

    def __str__(self) -> str:
        return f"Missing value from tag <{self.tag}> from file {self.file}"


class ClassDocumentation:
    """
    Parse details for a class from Doxygen XML.

    Attributes:
        file_path(str): The path to the Doxygen XML file.
        name(str): The name of the class with namespaces. For example: ``std::vector``.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        tree = ElementTree.parse(file_path)
        root = tree.getroot().find("compounddef")
        if root is None:
            raise MissingTag("compounddef", self.file_path)
        for tag in root:
            if tag.tag == "compoundname":
                self.name = self.__get_class_name(tag)
            else:
                logging.warning("Skipping <%s> in %s", tag.tag, self.file_path)

    def __get_class_name(self, xml_tag: Optional[ElementTree.Element]) -> str:
        if xml_tag is None:
            raise MissingTag("compoundname", self.file_path)
        if xml_tag.text is None:
            raise MissingValue("compoundname", self.file_path)
        return xml_tag.text
