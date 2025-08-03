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

from pathlib import Path
from typing import List, Tuple

from src.domain.knowledge.knowledge_data_objects import KnowledgeRecord, RecordHeading
from src.domain.knowledge.knowledge_persistence_port import KnowledgePersistencePort
from src.infra.knowledge.file.file_markdown_parser import (
    Level1Heading,
    extract_commands,
    extract_scripts,
    extract_level_1_heading_from_line,
    extract_level_1_headings,
    extract_section,
)
from src.infra.knowledge.file.file_topic_parser import TopicParser


class FilePersistenceAdapter(KnowledgePersistencePort):
    """
    Implementation of the persistence interface in the context
    of a file persistence type.
    """

    def __init__(self, dataset_dir: Path):
        self.__dataset_dir: Path = dataset_dir

    def get_topic_list(self) -> Tuple[str, ...]:
        topic_parser = TopicParser(self.__dataset_dir)
        return topic_parser.topics

    def get_referenced_headings_list_for_topic(self, topic: str) -> Tuple[RecordHeading, ...]:
        return tuple(
            (
                RecordHeading(
                    topic=topic,
                    id=heading.line_number,
                    text=heading.text,
                    tags=heading.tags,
                    alternative_headings_id=heading.siblings_id,
                )
            )
            for heading in extract_level_1_headings(Path(f"{self.__dataset_dir}/{topic}.md"))
        )

    def topic_exists(self, topic_name: str) -> bool:
        topic_parser = TopicParser(self.__dataset_dir)
        return topic_parser.topic_exists(topic_name)

    def get_body(self, topic: str, id: int) -> str:
        return extract_section(id, f"{self.__dataset_dir}/{topic}.md")

    def get_commands_from_record(self, topic: str, id: int) -> Tuple[str, ...]:
        record_body = self.get_body(topic, id)
        return extract_commands(record_body)

    def get_scripts_from_record(self, topic: str, id: int) -> Tuple[str, ...]:
        record_body = self.get_body(topic, id)
        return extract_scripts(record_body)

    def get_commands_from_record(self, topic: str, id: int) -> Tuple[str, ...]:
        record_body = self.get_body(topic, id)
        return extract_commands(record_body)

    def count_records_for_topic(self, topic: str) -> int:
        return len(
            self._purge_level_1_headings_from_siblings(extract_level_1_headings(Path(f"{self.__dataset_dir}/{topic}.md")))
        )

    def get_record_by_index(self, topic: str, index: int) -> KnowledgeRecord:
        heading = self._purge_level_1_headings_from_siblings(
            extract_level_1_headings(Path(f"{self.__dataset_dir}/{topic}.md"))
        )[index]
        headings_text: Tuple[str, ...] = (heading.text,) + tuple(
            extract_level_1_heading_from_line(id, Path(f"{self.__dataset_dir}/{topic}.md")).text
            for id in heading.siblings_id
        )
        body = self.get_body(topic, heading.line_number)
        return KnowledgeRecord(id=heading.line_number, headings=headings_text, body=body)

    @staticmethod
    def _purge_level_1_headings_from_siblings(level_1_headings: Tuple[Level1Heading, ...]) -> Tuple[Level1Heading, ...]:
        purged_headings: List[Level1Heading] = []
        sibling_ids: List[int] = []
        for heading in level_1_headings:
            if heading.line_number not in sibling_ids:
                purged_headings.append(heading)
                sibling_ids.extend(heading.siblings_id)
        return tuple(purged_headings)
