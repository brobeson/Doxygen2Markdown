"""Read Doxygen XML files that document classes."""

# cspell:ignore briefdescription compounddef compoundname detaileddescription sectiondef argsstring
# cspell:ignore basecompoundref collaborationgraph inheritancegraph listofallmembers

from dataclasses import dataclass
import logging
from typing import Dict, List, Optional
from xml.etree import ElementTree


@dataclass
class Parameter:
    """
    Represents a function parameter.

    Attributes:
        name(str): The name of the parameter.
        documentation(str): The documentation for the parameter.
    """

    name: str
    documentation: str


@dataclass
class Member:
    """
    Represents a class member. This can be a type alias, function, or data.

    Attributes:
        type(str): The variable type, function return type, or alias source type.
        name(str): The name of the member.
        brief(str): The Doxygen ``@brief`` description.
    """

    type: str
    name: str
    brief: str
    details: str


@dataclass
class Function(Member):
    """
    Represents a function.

    Attributes:
        parameter(str): The complete set of function parameters, with parentheses.
        parameter_details(List[Parameter]): The detailed documentation for each function parameter.
    """

    parameters: str
    parameter_details: List[Parameter]


@dataclass
class Variable(Member):
    """
    Represents a variable or constant.

    Attributes:
        value(str): The initial value of the variable.
    """

    value: str


class Section:
    """
    Represents a section of the overall ``@brief`` description.

    Attributes:
        name(str): The human-readable name of the section.
        members(List[Member]): A list of all the class members that are in this section.
    """

    def __init__(self, tag: ElementTree.Element):
        self.name = self.__read_name(tag.attrib)
        self.members: List[Member] = []
        for child in tag:
            kind = child.attrib["kind"]
            if kind == "function":
                self.members.append(
                    Function(
                        _find_text(child, "type"),
                        _find_text(child, "name"),
                        _find_text(child, "briefdescription"),
                        _find_text(child, "detaileddescription"),
                        _find_text(child, "argsstring"),
                        _read_parameters(
                            child.find("detaileddescription/para/parameterlist")
                        ),
                    )
                )
            if kind == "variable":
                self.members.append(
                    Variable(
                        _find_text(child, "type"),
                        _find_text(child, "name"),
                        _find_text(child, "briefdescription"),
                        _find_text(child, "detaileddescription"),
                        _find_text(child, "initializer"),
                    )
                )
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

    skipped_tags = [
        "basecompoundref",
        "inheritancegraph",
        "collaborationgraph",
        "location",
        "listofallmembers",
    ]

    def __init__(self, file_path: str):
        self.file_path = file_path
        tree = ElementTree.parse(file_path)
        root = tree.getroot().find("compounddef")
        if root is None:
            raise RuntimeError(f"Missing tag <compounddef> from file {self.file_path}")
        self.kind = root.attrib["kind"]
        self.language = root.attrib["language"]
        self.sections: List[Section] = []
        self.location = _find_text(root, "includes")
        self.brief = _find_text(root, "briefdescription")
        self.name = _find_text(root, "compoundname")
        self.detailed = _find_text(root, "detaileddescription/para")
        self.sections = [Section(tag) for tag in root.iter("sectiondef")]
        self.sections.sort()
        for tag in ClassDocumentation.skipped_tags:
            logging.warning("Skipping <%s> in %s", tag, self.file_path)


def _find_text(tag: ElementTree.Element, child: str) -> str:
    return tag.findtext(child, default="").strip()


def _read_parameters(tag: Optional[ElementTree.Element]) -> List[Parameter]:
    if tag is None:
        return []
    parameters: List[Parameter] = []
    parameters = [
        _read_parameter(parameter_item) for parameter_item in tag.iter("parameteritem")
    ]
    return parameters


def _read_parameter(tag: ElementTree.Element) -> Parameter:
    return Parameter(
        _find_text(tag, "parameternamelist/parametername"),
        _find_text(tag, "parameterdescription/para"),
    )
