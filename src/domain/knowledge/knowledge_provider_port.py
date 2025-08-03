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

from src.domain.knowledge.knowledge_data_objects import KnowledgeRecord, RecordHeading, RecordHeadingMatch


class KnowledgeProviderPort(ABC):
    """
    This interface is the input port for the domain (knowledge providing).
    It provides all necessary functions to interact with knowledge base.
    """

    @abstractmethod
    def ask(self, user_input: str) -> Tuple[Tuple[RecordHeadingMatch, ...], str]:
        """
        Find the best match to a given user input.

        Args:
            user_input (str): The input for which an search is sought.

        Returns:
            Tuple[Tuple[RecordHeadingMatch, ...], str]: A tuple containing:
                - The top N (see config.py) matching headings
                (Tuple[RecordHeadingMatch, ...]) ordered by the highest similarity
                score with the input.
                - (str) : body of the record which heading is the top
                matching with the user input.
        """
        pass

    @abstractmethod
    def get_topics_list(self) -> Tuple[str, ...]:
        """
        Retrieve the list of all available topics.

        Returns:
            Tuple[str, ...]: A tuple containing the names of all topics.
        """
        pass

    @abstractmethod
    def get_available_records_headings_for_topic(self, topic_name: str) -> Tuple[RecordHeading, ...]:
        """
        Retrieve the list of available headings for a specific topic.

        Args:
            topic_name (str): The name of the topic for which the headings
                should be fetched.

        Returns:
            Tuple[RecordHeading, ...]: A tuple of RecordHeading for each available
            heading in topic.
        """
        pass

    @abstractmethod
    def get_content_for_identified_heading(self, topic: str, heading_id: int) -> str:
        """
        Retrieve the content for a specific heading identified by its topic and
        unique identifier.

        Args:
            - topic (str): The name of the topic to which the record belongs.
            - heading_id (int): The unique identifier of the heading.

        Returns:
            str: The content related to the specified heading.
        """
        pass

    @abstractmethod
    def get_commands_from_record_tagged_as_command(self, topic: str, record_id: int) -> Tuple[str, ...]:
        """
        Retrieve all commands from a record tagged with the 'commands' label.

        Args:
            topic (str): The targeted topic.
            record_id (int): The ID of the record.

        Returns:
            Tuple[str, ...]: The commands retrieved from the tagged record.
        """
        pass

    @abstractmethod
    def get_record_by_index(self, topic: str, index: int) -> KnowledgeRecord:
        """
        Retrieve a record by its index in the topic. By index, we mean the index
        of the record in the ordered list of records for a given topic.
        Args:
            topic (str): The topic of the record.
            index (int): The index of the record in the topic.

        Returns:
            KnowledgeRecord: The record retrieved from the topic.
        """
        pass
