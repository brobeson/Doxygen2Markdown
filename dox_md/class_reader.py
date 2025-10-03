"""Read Doxygen XML files that document classes."""

# cspell:ignore briefdescription compounddef compoundname detaileddescription sectiondef

from dataclasses import dataclass
import logging
from typing import Dict, List, Optional
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


@dataclass
class Function:
    type: Optional[str]
    arguments: Optional[str]
    name: Optional[str]
    brief: Optional[str]


class Section:
    def __init__(self, tag: ElementTree.Element):
        self.name = self.__read_name(tag.attrib)
        self.members = []
        for child in tag:
            kind = child.attrib["kind"]
            if kind == "function":
                f = Function(
                    child.findtext("type").strip(),
                    child.findtext("argsstring").strip(),
                    child.findtext("name").strip(),
                    child.findtext("briefdescription").strip(),
                )
                # if f.arguments:
                #     f.arguments = re.sub("\\s+", " ", f.arguments)
                self.members.append(f)
            else:
                logging.warning('Skipping <%s kind="%s"', child.tag, kind)

    def __read_name(self, attributes: Dict[str, str]) -> str:
        kind = attributes["kind"]
        if kind == "public-func":
            logging.warning("Skipping 'public-func' section.")
            return "Public Member Functions"
        if kind == "public-static-attrib":
            logging.warning("Skipping 'public-static-attrib' section.")
            return "Static Public Attributes"
        if kind == "public-static-func":
            logging.warning("Skipping 'public-static-func' section.")
            return "Static Public Member Functions"
        logging.warning("Unknown <sectiondef> kind of '%s'", kind)
        return ""

    def __lt__(self, other) -> bool:
        return self.name < other.name


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
        self.sections: List[Section] = []
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
            elif tag.tag == "sectiondef":
                self.sections.append(Section(tag))
            else:
                logging.warning("Skipping <%s> in %s", tag.tag, self.file_path)
        self.sections.sort()

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
