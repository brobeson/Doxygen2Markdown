"""Write Doxygen data to Markdown files."""

from enum import Enum
import io
from typing import Collection, Iterable, Optional, Tuple, Union


class File:
    """
    Write information to a Markdown file.

    To use this as a context manager, first instantiate a Writer, then use ``new_file()`` to
    invoke context management.

    .. code-block:: py

        writer = Writer("docs/")
        with new_file(writer, "vector.md") as _:
            writer.write_heading(1, "`std::vector`")

    Attributes:
        output_root(str): The root directory in which to write any Markdown files.
        output_file(str): The path, relative to ``output_root``, for the current file.
        file: The file stream for ``output_file``.
    """

    def __init__(self, stream: io.TextIOBase):
        if not stream.writable():
            raise IOError("The stream must be writable but is not.")
        self.__stream = stream

    def write_line(self, line: Optional[str] = None) -> None:
        """
        Write a single line to the Markdown stream. Append a newline character after to the line of
        text.

        Args:
            line (Optional[str], optional): The line of text to print. If this is `None`, write a
            blank line to the file. Defaults to None.
        """
        if line is None:
            self.__write_line("")
        else:
            self.__write_line(line)

    def write_lines(self, lines: Iterable[str]) -> None:
        """
        Write multiple lines to the Markdown file.

        Args:
            lines (Iterable[str]): Write these lines to the Markdown file. This function appends a
            newline to each line.
        """
        self.__stream.writelines(["f{l}\n" for l in lines])

    def write_heading(self, level: int, heading: str) -> None:
        """
        Write a Markdown heading to the current file.

        Args:
            level (int): The heading level. This must be in the range [1, 6].
            heading (str): The heading text.
        """
        self.__write_line(f"{'#' * level} {heading}\n")

    def write_image(self, image_path: str, alt_text: str) -> None:
        """
        Write an image to the Markdown file.

        Args:
            image_path (str): The path to the image. This can be a file path, a URL, or any other
            image source accepted by Markdown.
            alt_text (str): The alt text to include with the image.
        """
        self.__write_line(f"![{alt_text}]({image_path})")

    def __write_line(self, line: str) -> None:
        """
        Write a single line to the Markdown stream. This is an internal helper function; all
        interface functions should ultimately write through this function.

        Args:
            line (str): The line of text to print. This function appends a newline.
        """
        self.__stream.write(f"{line}\n")


class CodeBlock:
    """
    Start a fenced code block in a Markdown file, and automatically close the block when you are
    done writing code to the file.

    Attributes:
        md(File): Open a code block in this file.
        language(str): The language code for the block. This is the language text printed after
        the initial fence.

    .. code-block:: python

       from markdown import File, CodeBlock
       with open("README.md", mode="w", encoding="utf=8") as f:
           md = File(f)
           md.write_heading("Example Code Block")
           with CodeBlock(md, "c++"):
               md.write_line("#include <iostream>")

    """

    def __init__(self, md: File, language: str):
        self.md = md
        self.language = language

    def __enter__(self):
        self.md.write_line(f"```{self.language}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.md.write_line("```\n")

    def write_code(self, code: Union[str, Iterable[str]]):
        """
        Write code to the code block.

        Args:
            code (Union[str, Iterable[str]]): The line or lines of code to write. Each line of
            code has a newline appended by this function.
        """
        if isinstance(code, str):
            self.md.write_line(code)
        else:
            self.md.write_lines(code)


class Table:
    """
    Start a table in a Markdown file.

    Attributes:
        md(File): Open a code block in this file.
        language(str): The language code for the block. This is the language text printed after
        the initial fence.

    .. code-block:: python

       from markdown import File, CodeBlock
       with open("README.md", mode="w", encoding="utf=8") as f:
           md = File(f)
           md.write_heading("Example Code Block")
           with CodeBlock(md, "c++"):
               md.write_line("#include <iostream>")

    """

    class Alignment(Enum):
        """Table column alignment specifiers"""

        LEFT = ":--"
        CENTER = ":-"
        RIGHT = "--:"

    def __init__(self, md: File, columns: Collection[Tuple[str, Alignment]]):
        self.md = md
        self.write_row([c[0] for c in columns])
        self.write_row([c[1].value for c in columns])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.md.write_line()

    def write_row(self, columns: Iterable[str]) -> None:
        """
        Write a single row of a table.

        Args:
            columns (Iterable[str]): The text for each column of the row. To skip a column, that
            entry in ``columns`` must be an empty string.
        """
        self.md.write_line(f"|{'|'.join(columns)}|")
