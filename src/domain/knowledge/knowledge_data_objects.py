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

from dataclasses import dataclass
from typing import Tuple

from pytest import approx


@dataclass
class RecordHeading:
    """
    Represents a the heading of a record for a given topic.

    Attributes:
        topic (str): The category or domain to which the record belongs.
        id (int): A unique identifier for the record heading in the given topic.
        text (str): The full text or phrasing of the record heading.
        tags (Tuple[str,...]): A tuple of tags associated to the heading
        alternative_headings_id (Tuple[int,...]): A tuple of alternative
        headings ids (a single record can have multiple headings).
    """

    topic: str
    id: int
    text: str
    tags: Tuple[str, ...]
    alternative_headings_id: Tuple[int, ...]

    def __str__(self) -> str:
        return f"{self.topic}@{self.id}-{self.tags} : {self.text}"

    def __eq__(self, other):
        if not isinstance(other, RecordHeading):
            return False
        return (
            self.topic == other.topic
            and self.id == other.id
            and self.text == other.text
            and self.tags == other.tags
            and self.alternative_headings_id == other.alternative_headings_id
        )

    def has_command_tag(self) -> bool:
        return "command" in self.tags

    def has_script_tag(self) -> bool:
        return "script" in self.tags

    def has_alternative_headings(self) -> bool:
        return len(self.alternative_headings_id) > 0


@dataclass
class RecordHeadingMatch:
    """
    Represents a match in the context of similarity evaluation with other headings text.

    Attributes:
        record_heading (RecordHeading): The record heading concerned by similarity evaluation
        similarity_indice (float): A numerical value ranging from 0 to 1 that indicates
            how closely the heading text relates to another heading text.
    """

    record_heading: RecordHeading
    similarity_indice: float

    def __str__(self):
        return (
            f"{self.record_heading.topic}@{self.record_heading.id} - {self.similarity_indice} : {self.record_heading.text}"
        )

    def __eq__(self, other):
        if not isinstance(other, RecordHeadingMatch):
            return False
        # Compare similarity_indice with tolerance (because it is a double)
        return self.record_heading == other.record_heading and self.similarity_indice == approx(other.similarity_indice)


@dataclass
class KnowledgeRecord:
    """
    Represents a knowledge record with :
        - Heading(s) which is the record's title. A same record can have
        multiple headings.
        - Body, which is the content associated to the headings.

    Attributes:
        heading_text Tuple[str, ...]: The heading text of the knowledge record.
        body_text (str): The body text of the knowledge record.
    """

    id: int
    headings: Tuple[str, ...]
    body: str

    def __init__(self, id: int, headings: Tuple[str, ...], body: str) -> None:
        self.id = id
        self.headings = headings
        self.body = body
