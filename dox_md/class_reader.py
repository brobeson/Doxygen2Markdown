"""Read Doxygen XML files that document classes."""

# cspell:ignore briefdescription compounddef compoundname detaileddescription

import logging
from typing import Optional
from xml.etree import ElementTree


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

    def __init__(self, file_path: str, header_search_path: str):
        self.file_path = file_path
        self.header_search_path = header_search_path
        tree = ElementTree.parse(file_path)
        root = tree.getroot().find("compounddef")
        if root is None:
            raise MissingTag("compounddef", self.file_path)
        self.kind = root.attrib["kind"]
        self.language = root.attrib["language"]
        for tag in root:
            if tag.tag == "briefdescription":
                self.brief = tag.text
                if isinstance(self.brief, str):
                    self.brief = self.brief.strip()
            elif tag.tag == "compoundname":
                self.name = self.__get_class_name(tag)
            elif tag.tag == "detaileddescription":
                self.detailed = self.__get_detailed_description(tag)
            elif tag.tag == "location":
                self.location = self.__get_location(tag)
            else:
                logging.warning("Skipping <%s> in %s", tag.tag, self.file_path)

    def __get_class_name(self, xml_tag: Optional[ElementTree.Element]) -> str:
        if xml_tag is None:
            raise MissingTag("compoundname", self.file_path)
        if xml_tag.text is None:
            raise MissingValue("compoundname", self.file_path)
        return xml_tag.text

    def __get_detailed_description(self, xml_tag: Optional[ElementTree.Element]) -> str:
        if xml_tag is None:
            return ""
        text = ""
        for para_tag in xml_tag.findall("para"):
            if para_tag.text:
                text = text + para_tag.text.strip() + "\n\n"
        return text.strip()

    def __get_location(self, tag: Optional[ElementTree.Element]) -> str:
        if tag is None:
            return ""
        return tag.attrib["file"].replace(self.header_search_path, "")
