"""Process a single Doxygen XML file."""

import glob
import logging
import os.path
from typing import List
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
        with markdown_writer.new_file(md_writer, file_name) as _:
            md_writer.write_heading(1, file_path)
    else:
        logging.warning("Skipping %s", file_name)
