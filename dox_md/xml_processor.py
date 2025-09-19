"""Process a single Doxygen XML file."""

import glob
import logging
import os.path
from typing import List, Optional
from dox_md import class_reader


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


def read_xml_file(file_path: str) -> Optional[class_reader.ClassDocumentation]:
    """
    Read and parse a Doxygen XML file.

    Args:
        file_path (str): The full path the Doxygen XML file.

    Returns:
        Optional[class_reader.ClassDocumentation]: The parsed documentation.
    """
    file_name = os.path.basename(file_path)
    if file_name.startswith("class"):
        logging.info("Processing %s", file_name)
        return class_reader.ClassDocumentation(file_path)
    logging.warning("Skipping %s", file_name)
    return None
