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

from abc import ABC, abstractmethod
from typing import Tuple

from src.domain.knowledge.knowledge_data_objects import KnowledgeRecord, RecordHeading


class KnowledgePersistencePort(ABC):
    """
    This port give a persistence access to knowledge provider.
    """

    @abstractmethod
    def get_topic_list(self) -> Tuple[str, ...]:
        """
        Returns:
            Tuple[str, ...]: List of all the available topics in dataset
        """
        pass

    @abstractmethod
    def get_referenced_headings_list_for_topic(self, topic: str) -> Tuple[RecordHeading, ...]:
        """
        Args: topic (str): A topic name

        Returns: Tuple[RecordHeading, ...]: List of available RecordHeading for
        a given topic.
        """

        pass

    @abstractmethod
    def topic_exists(self, topic_name: str) -> bool:
        """
        Args:
            topic_name (str): A topic name

        Returns:
            bool: True if topic exists in dataset
        """
        pass

    @abstractmethod
    def get_body(self, topic: str, id: int) -> str:
        """

        Args:
            topic (str): A topic name
            id (int): A heading id

        Returns:
            str: The body (content) of the record for the identified heading in
            the given topic
        """
        pass

    @abstractmethod
    def get_commands_from_record(self, topic: str, id: int) -> Tuple[str, ...]:
        """
        Retrieve all commands from Markdown code blocks within a record.

        Summary:
            Commands are extracted from all Markdown code blocks (beginning with
            '```' and ending the same way) inside the specified record.

        Args:
            topic (str): The name of the topic.
            id (int): The ID of the record.

        Returns:
            Tuple[str, ...]: A tuple containing all commands found in the record
            associated with the given ID and topic.
        """
        pass

    @abstractmethod
    def get_scripts_from_record(self, topic: str, id: int) -> Tuple[str, ...]:
        """
        Retrieve all scripts inside Markdown code blocks within a record.

        Summary:
            Scripts are extracted from all Markdown code blocks (beginning with
            '```' and ending the same way) inside the specified record.

        Args:
            topic (str): The name of the topic.
            id (int): The ID of the record.

        Returns:
            Tuple[str, ...]: A tuple containing all scripts found in the record
            associated with the given ID and topic.
        """
        pass

    @abstractmethod
    def count_records_for_topic(self, topic: str) -> int:
        """
        Count the number of records for a given topic.

        Args:
            topic (str): The topic for which to count records.

        Returns:
            int: The number of records for the given topic.
        """
        pass

    @abstractmethod
    def get_record_by_index(self, topic: str, index: int) -> KnowledgeRecord:
        """
        Retrieve a record by its index in the topic.

        Args:
            topic (str): The topic of the record.
            index (int): The index of the record in the topic.

        Returns:
            KnowledgeRecord: The record retrieved from the topic.
        """
        pass
