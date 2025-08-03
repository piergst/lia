# Lia is a knowledge base organizer providing fast and accurate natural
# language search from the command line.
# Copyright (C) 2025  Pierre Giusti
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

"""
This module provides functions to parse and extract information from Markdown files.

CONTEXT 

All data must be formulated as heading / body pairs (a "record") in simple
markdown files. In this context, markdown level 1 headings are reserved to
identify headings, all other markups are treated as part of the body.

One important feature is to provide a way to define multiple alternative
formulations for a same record to be more efficient when looking for
something. So in some cases we will have a level 1 heading followed by several
other level 1 headings, all of them being alternative formulations of the same
other and targeting the same content.  This is what we have named "siblings".
And a succession of siblings is named a "siblings block". So when we extract the
level 1 headings from a file, we also extract and associate them the ids of all
its siblings, to be able to identify them later if needed.

Tags are used to add metadata to a record and must placed at end of a level one
heading line. They are formatted as words prefixed with a hash symbol
(#) (e.g. "#tag"). They must be space separated from heading and between them
(e.g. "#tag1 #tag2").
"""

# GLOBAL REGEX PATTERNS

re_empty_line = re.compile(r"^\s*$")
re_level_1_heading = re.compile(r"^#\s")
re_code_block_start = re.compile(r"^```")

# This regex matches tags in the format #tag, where the tag starts with a '#'
# and is followed by word characters. It uses a negative lookbehind to ensure
# the '#' is not preceded by a non-whitespace character.
re_tag = re.compile(r"(?<!\S)#\w+")


# The `?` character makes the preceding quantifier non-greedy, meaning it
# will match the shortest possible string (e.g., `.*?`) until it encounters
# the character that follows it (here '\n' and '```').
re_code_block = r"```.*?\n(.*?)```"


@dataclass
class Level1Heading:
    """
    Represents a level 1 heading in a Markdown file with its metadata.

    Attributes:
        line_number (int): The line number where the heading appears in the file
        heading_text (str): The heading text without tags
        tags (Tuple[str,...]): Tags associated with the heading, defined with '#' prefix
            (e.g. #command, #example). Tags allow categorizing and adding metadata
            to the heading.
        siblings_id (Tuple[int,...]): ids (line numbers) of alternative
            formulations of the same heading associated with this heading,
            identified as all level 1 headings that follow the main heading and are
            separated by one or more newlines.
    """

    line_number: int
    text: str
    tags: Tuple[str, ...]
    siblings_id: Tuple[int, ...]


def extract_level_1_headings(file_path: Path) -> Tuple[Level1Heading, ...]:
    """
    Extracts level 1 headings (lines starting with a single '#') from a Markdown
    file along with their line numbers and any associated tags.

    Args:
        file_path (str): The path to the Markdown file.

    Returns:
        Tuple[Level1Heading, ...]: A tuple of Level1Heading

    Notes:
        - Lines starting with '#' inside code blocks are ignored.
        - Multiple level 1 headings following each others (even separated by
        newlines) are considered as heading's siblings (alternative formulations
        of the same thing) which target the same body.
        - The function assumes the file uses UTF-8 encoding.
    """
    level_1_headings: List[Level1Heading] = []
    inside_code_block: bool = False
    inside_siblings_block: bool = False
    heading_siblings: List[int] = []

    with open(file_path, "r", encoding="utf-8") as file:
        for lineIndex, line in enumerate(file, start=1):
            # Handle siblings block
            if inside_siblings_block:
                if not re_level_1_heading.match(line) and not re_empty_line.match(line):
                    inside_siblings_block = False
                    _define_siblings_for_heading(level_1_headings, heading_siblings)
                    heading_siblings = []
                elif re_empty_line.match(line):
                    pass
                else:
                    level_1_headings.append(_string_to_level_1_heading(line, lineIndex))
                    heading_siblings.append(lineIndex)
            # Handle code block
            if re_code_block_start.match(line):
                inside_code_block = not inside_code_block
            # Handle level 1 heading
            if not inside_code_block and not inside_siblings_block and re_level_1_heading.match(line):
                inside_siblings_block = True
                level_1_headings.append(_string_to_level_1_heading(line, lineIndex))
                heading_siblings.append(lineIndex)
    return tuple(level_1_headings)


def extract_level_1_heading_from_line(lineNumber: int, file_path: Path) -> Level1Heading:
    """
    Extracts a level 1 heading from a given line number in a file.

    Args:
        lineNumber (int): The line number where the heading comes from.

    Returns:
        Level1Heading: An object containing the line index, the extracted heading,
        and any associated tags.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        for _ in range(lineNumber - 1):
            next(file)
        line = file.readline()
    if not re_level_1_heading.match(line):
        raise ValueError(f"String {line} does not start with a level 1 heading")
    tags = _extract_tags(line)
    heading = re_tag.sub("", line).strip()
    return Level1Heading(lineNumber, re_level_1_heading.sub("", heading).strip(), tags, ())


def extract_section(line_nbr: int, file_path: str) -> str:
    """
    Extract all content from the specified line until the next level 1 heading.

    Args:
        line_nbr (int): Extraction beginning line
        file_path (str): Path to markdown file
    """
    extract: str = ""

    # Identify code blocks to accept lines beggining with '#' which are comments
    # and not level one header in this context
    inside_code_block: bool = False
    inside_siblings_block: bool = True

    with open(file_path, "r", encoding="utf-8") as file:
        for _ in range(line_nbr):
            next(file)
        for line in file:
            if inside_siblings_block:
                if re_empty_line.match(line) or re_level_1_heading.match(line):
                    continue
                else:
                    inside_siblings_block = False
            if re_code_block_start.match(line):
                inside_code_block = not inside_code_block
            if not re_level_1_heading.match(line) or inside_code_block:
                extract += line
            else:
                break
    return extract


def extract_commands(markdown_text: str) -> Tuple[str, ...]:
    """
    Extracts all commands from a Markdown text containing code blocks,
    ignoring lines that are comments.

    Args:
        markdown_text (str): The input Markdown text containing code blocks.

    Returns:
        Tuple[str, ...]: A tuple containing all non-comment lines found in the
        code blocks. Returns an empty tuple if no such lines are found.
    """
    code_blocks = __extract_code_blocks(markdown_text)
    commands: List[str] = []
    for block in code_blocks:
        lines: List[str] = [line.strip() for line in block.splitlines()]
        # Filter out comment lines (language-agnostic common styles)
        commands.extend([line for line in lines if line and not line.startswith(("#", "//", "--", ";"))])
    return tuple(commands)

def extract_scripts(markdown_text: str) -> Tuple[str, ...]:
    """
    Extracts all contents from Markdown code blocks. 

    Args:
        markdown_text (str): The input Markdown text containing code blocks.

    Returns:
        Tuple[str, ...]: A tuple containing each code block full content.
        Returns an empty tuple if no code blocks are found.
    """
    return  tuple(__extract_code_blocks(markdown_text))

def _string_to_level_1_heading(string: str, lineNumber: int) -> Level1Heading:
    """
    Extracts a level 1 heading from a given string.

    Args:
        string (str): The input string from which to extract the heading.
        lineNumber (int): The line number where the string comes from.

    Returns:
        Level1Heading: An object containing the line index, the extracted heading,
        and any associated tags.
    """
    if not re_level_1_heading.match(string):
        raise ValueError(f"String {string} does not start with a level 1 heading")
    tags = _extract_tags(string)
    heading = re_tag.sub("", string).strip()
    return Level1Heading(lineNumber, re_level_1_heading.sub("", heading).strip(), tags, ())


def _define_siblings_for_heading(level_1_headings: List[Level1Heading], siblings_ids: List[int]) -> None:
    """
    Handles the assignment of siblings IDs to level 1 headings based on the
    presence of sibling headings.

    Args:
        level_1_headings (List[Level1Heading]): A list of Level1Heading objects
            considered as siblings (alternative formulations)
        siblings_ids (List[int]): The list of siblings ids (line numbers)
    """
    if len(siblings_ids) > 1:
        # As in siblings block we extract ids from all siblings, we need to remove
        # from each concerned heading the id of itself
        # Concerned headings are straightly linked to the number of siblings in the block
        start_index = len(level_1_headings) - len(siblings_ids)
        end_index = len(level_1_headings)
        for heading in level_1_headings[start_index:end_index]:
            heading.siblings_id = tuple(sibling_id for sibling_id in siblings_ids if sibling_id != heading.line_number)


def _extract_tags(line) -> Tuple[str, ...]:
    """
    Extracts tags from a given line.
    Tags are expected to be formatted as words prefixed with a hash symbol (#) (e.g. "#tag").

    Args:
        line (str): The input line from which to extract tags.

    Returns:
        Tuple[str, ...]: A tuple containing the extracted tags.
    """
    tags = tuple(tags[1:] for tags in re_tag.findall(line))
    return tags


def __extract_code_blocks(markdown_text: str) -> list:
    """
    Extracts all code blocks from a Markdown text.

    Args:
        markdown_text (str): The Markdown text.

    Returns:
        list: A list of strings, where each string is the content of a code block.
    """

    # The `re.DOTALL` option allows the dot (`.`) to match newline characters
    # (`\n`) as well.  This ensures that the content of a code block spanning
    # multiple lines will be fully captured.
    return re.findall(re_code_block, markdown_text, re.DOTALL)
