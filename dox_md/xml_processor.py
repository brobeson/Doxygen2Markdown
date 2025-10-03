"""Process a single Doxygen XML file."""

import glob
import logging
import os.path
from typing import List, Tuple
from dox_md import class_reader, markdown_writer


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


def process_xml_files(
    file_paths: List[str], header_search_path: str, writer: markdown_writer.Writer
) -> None:
    """
    Read the Doxygen XML files.

    Args:
        file_paths (List[str]): The Doxygen XML files to process.
    """
    for file_path in file_paths:
        _process_xml_file(file_path, header_search_path, writer)


def _process_xml_file(
    file_path: str, header_search_path: str, md_writer: markdown_writer.Writer
) -> None:
    file_name = os.path.basename(file_path)
    if file_name.startswith("class"):
        logging.info("Processing %s", file_name)
        class_doc = class_reader.ClassDocumentation(file_path, header_search_path)
        with markdown_writer.new_file(md_writer, file_name) as _:
            md_writer.write_heading(1, f"`{class_doc.name}`")
            md_writer.write_badges(
                [("Language", "C%2B%2B", "blue"), ("Kind", "Class", "blue")]
            )
            md_writer.write_code_block("c++", f"#include <{class_doc.location}>")
            md_writer.write_paragraph(class_doc.brief)
            for section in class_doc.sections:
                _write_brief_section(section, md_writer)
            if class_doc.detailed:
                md_writer.write_heading(2, "Detailed Description")
                md_writer.write_paragraph(class_doc.detailed)
    else:
        logging.warning("Skipping %s", file_name)


def _write_brief_section(
    section: class_reader.Section, writer: markdown_writer.Writer
) -> None:
    writer.write_heading(2, section.name)
    writer.write_table_header(("Function", "Description"), "ll")
    for member in _combine_brief_section(section):
        writer.write_table_row((f"`{member[0]}`", member[1]))
    writer.write_line()


def _combine_brief_section(section: class_reader.Section) -> List[Tuple[str, str]]:
    combined: List[Tuple[str, str]] = []
    names: List[str] = []
    for member in section.members:
        if member.name and member.name not in names:
            names.append(member.name)
    for name in names:
        t = (name, "")
        for member in section.members:
            if name == member.name and member.brief:
                t = (name, member.brief)
        combined.append(t)
    return combined
