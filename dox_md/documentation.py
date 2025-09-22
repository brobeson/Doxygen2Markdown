"""Bridge between Doxygen XML and Markdown output."""

import logging
import os
from typing import List, Tuple
from dox_md import class_reader, markdown


class Documentation:
    """
    Manage and write a set of documentation using Markdown output.

    Attributes:
        root_directory(str): Write the Markdown files in this directory.
    """

    def __init__(self, root_directory: str) -> None:
        if os.path.exists(root_directory) and not os.path.isdir(root_directory):
            raise FileExistsError(f"{root_directory} exists, but is not a directory")
        os.makedirs(root_directory, exist_ok=True)
        self.root_directory = root_directory

    def write_class(self, docs: class_reader.ClassDocumentation) -> None:
        """
        Write a Markdown file for class documentation.

        Args:
            docs (class_reader.ClassDocumentation): The parsed XML data for the class to document.
        """
        filename = _full_md_file_path(self.root_directory, "classes", docs.name)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, mode="w", encoding="utf-8") as stream:
            file = markdown.File(stream)
            file.write_heading(1, f"`{docs.name}`")
            _write_badges(file)
            file.write_line()
            with markdown.CodeBlock(file, "c++") as block:
                block.write_code(f"#include <{docs.location}>")
            if docs.brief:
                file.write_line(docs.brief)
            for section in docs.sections:
                _write_brief_section(file, section)
            if docs.detailed:
                file.write_heading(2, "Detailed Description")
                file.write_line(docs.detailed)
                file.write_line()
            for section in docs.sections:
                _write_detailed_section(file, section, docs.name)


def _full_md_file_path(root: str, kind: str, name: str) -> str:
    filename = os.path.join(root, kind, name.replace("::", ".") + ".md")
    return filename


def _write_badges(file: markdown.File) -> None:
    file.write_image(
        "https://img.shields.io/badge/Language-C%2B%2B-blue", "Language C++"
    )
    file.write_image("https://img.shields.io/badge/Kind-Class-blue", "Language C++")


def _write_brief_section(file: markdown.File, section: class_reader.Section) -> None:
    if section.members:
        file.write_heading(2, section.name)
        if isinstance(section.members[0], class_reader.Function):
            _write_function_briefs(file, section)
        elif isinstance(section.members[0], class_reader.Variable):
            _write_variable_briefs(file, section.members)  # type: ignore


def _write_function_briefs(file: markdown.File, section: class_reader.Section) -> None:
    with markdown.Table(
        file,
        [
            ("Function", markdown.Table.Alignment.LEFT),
            ("Description", markdown.Table.Alignment.LEFT),
        ],
    ) as table:
        for member in _combine_brief_section(section):
            table.write_row((f"`{member[0]}`", member[1]))


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
    return [(f"{m[0]}", m[1]) for m in combined]


def _write_variable_briefs(
    file: markdown.File, members: List[class_reader.Variable]
) -> None:
    with markdown.Table(
        file,
        [
            ("Attribute", markdown.Table.Alignment.LEFT),
            ("Description", markdown.Table.Alignment.LEFT),
        ],
    ) as table:
        for member in members:
            table.write_row(
                (f"`{member.type} {member.name} {member.value}`", member.brief)
            )


def _write_detailed_section(
    file: markdown.File, section: class_reader.Section, class_name: str
) -> None:
    if section.members:
        if isinstance(section.members[0], class_reader.Function):
            _write_function_details(file, section, class_name)
        else:
            logging.warning(
                "Skipping output of %s details section", type(section.members[0])
            )


def _write_function_details(
    file: markdown.File, section: class_reader.Section, class_name: str
) -> None:
    for member in _combine_brief_section(section):
        heading = f"`{class_name}::{member[0]}`"
        file.write_heading(3, heading)
        for m in section.members:
            if m.name == member[0]:
                with markdown.CodeBlock(file, "c++") as block:
                    block.write_code(f"{m.type} {m.name} {m.parameters}")  # type: ignore
                if m.parameter_details:
                    with markdown.Table(
                        file,
                        [
                            ("Parameter", markdown.Table.Alignment.LEFT),
                            ("Description", markdown.Table.Alignment.LEFT),
                        ],
                    ) as table:
                        for parameter in m.parameter_details:
                            table.write_row([parameter.name, parameter.documentation])
                if m.details:
                    file.write_line(m.details)
