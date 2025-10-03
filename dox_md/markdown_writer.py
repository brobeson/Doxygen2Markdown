"""Write Doxygen data to Markdown files."""

import logging
import os.path
import re
from typing import Any, IO, Iterable, List, Optional, Tuple, Union


class Writer:
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

    def __init__(self, output_root: str):
        if not os.path.exists(output_root):
            os.makedirs(output_root)
        if not os.path.isdir(output_root):
            raise FileExistsError(f"{output_root} exists and is not a directory")
        self.output_root = output_root
        self.output_file: Optional[str] = None
        self.file: Optional[IO[str]] = None

    def __enter__(self):
        logging.debug("Starting writer")
        if self.file is not None:
            raise RuntimeError(
                "already writing a file, cannot write another at the same time"
            )
        self.file = open(self.output_file, encoding="utf-8", mode="w")

    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()
        self.file = None
        logging.debug("Stopping writer")

    def write_heading(self, level: int, heading: str) -> None:
        """
        Write a Markdown heading to the current file.

        Args:
            level (int): The heading level. This must be in the range [1, 6].
            heading (str): The heading text.
        """
        if self.file is not None:
            self.file.write(f"{'#' * level} {heading}\n\n")

    def write_paragraph(self, text: Union[Any | None | str]) -> None:
        """
        Write a normal paragraph of text to the current file.

        Args:
            text (str): The paragraph text to write.
        """
        if self.file is None or not text:
            return
        text = re.sub(r"([\.!?]) ([A-Z])", r"\1\n\2", text)
        self.file.write(f"{text}\n")

    def write_badge(self, label: str, message: str, color: str) -> None:
        if self.file is None:
            return
        badge_text = "![Static Badge](https://img.shields.io/badge/"
        if label:
            badge_text = f"{badge_text}{label}-"
        if message:
            badge_text = f"{badge_text}{message}-"
        if color:
            badge_text = f"{badge_text}{color}"
        badge_text = f"{badge_text})"
        self.file.write(f"{badge_text}\n")

    def write_badges(self, badges: List[Tuple[str, str, str]]) -> None:
        if self.file is not None:
            for badge in badges:
                self.write_badge(badge[0], badge[1], badge[2])
            self.file.write("\n")

    def write_code_block(self, language: str, code: str) -> None:
        if self.file is None:
            return
        self.file.write(f"```{language}\n")
        self.file.write(f"{code}\n")
        self.file.write("```\n\n")

    def write_line(self, line: Optional[str] = None) -> None:
        if self.file is not None:
            if line is None:
                self.file.write("\n")
            else:
                self.file.write(f"{line}\n")

    def write_table_header(self, columns: Iterable[str], alignments: str) -> None:
        if self.file is None:
            return
        if len(columns) != len(alignments):
            raise RuntimeError(
                "The alignment string must be the same length as the set of columns"
            )
        # self.file.write(f"|{'|'.join(columns)}|\n")
        self.write_table_row(columns)
        for alignment in alignments:
            if alignment == "c":
                self.file.write("|:-:")
            elif alignment == "r":
                self.file.write("|--:")
            else:
                if alignment != "l":
                    logging.warning(
                        "'%s' is invalid column alignment; valid options are 'l', 'c', and 'r'. Defaulting to 'l'.",
                        alignment,
                    )
                self.file.write("|:--")
        self.file.write("|\n")

    def write_table_row(self, columns: Iterable[str]) -> None:
        if self.file is None:
            return
        self.file.write(f"|{'|'.join(columns)}|\n")


def new_file(writer: Writer, file_path: str) -> Writer:
    """
    Initiate context management for writing Markdown files.

    Args:
        writer (Writer): The Writer to use for writing Markdown files.
        file_path (str): The path to the new file to write. This should be relative to
        ``writer.output_root``.

    Returns:
        Writer: This function returns ``writer``. It's safe to ignore the return value.
    """
    file_path, _ = os.path.splitext(file_path)
    file_path += ".md"
    writer.output_file = os.path.join(writer.output_root, file_path)
    return writer
