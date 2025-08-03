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

from src.domain.knowledge.knowledge_data_objects import KnowledgeRecord
from src.domain.learning.learning_data_objects import ReviewGroup


class LearningProviderPort(ABC):
    """
    This interface is the domain access port to learning provider.
    It provides all necessary functions to interact with  the learning provider.
    """

    @property
    @abstractmethod
    def current_review_group(self) -> ReviewGroup:
        """
        Stores the current reviewed group during a review session
        """
        pass

    @abstractmethod
    def fetch_review_groups_for_topic(self, topic: str) -> Tuple[ReviewGroup, ...]:
        """
        Retrieve review groups for a given topic. Review groups reference
        collections of records to organize and facilitate the review process. Each
        review group is uniquely identified and contains information such as the
        group index, the topic, the last review date, and the next review date.
        These groups help structure and track review sessions for different
        topics.

        Args:
            topic (str): The topic for which the review groups should be retrieved.

        Returns:
            Tuple[ReviewGroup, ...]: A tuple containing the review groups retrieved for the given topic.
        """
        pass

    @abstractmethod
    def init_review_session(self, review_group_id: int) -> None:
        """
        A review session is a structured process where a user goes through a set
        of learning records grouped under a specific review group. The session
        helps in systematically reviewing and reinforcing knowledge on a
        particular topic. During the session, records are presented one by one
        for review, and the session tracks progress through the records. This
        method initializes the review session for a given review group, setting
        up necessary parameters and state to begin the review process.

        Args:
            review_group_id (int): The identifier of the review group for which the session should be initialized.
        """
        pass

    @abstractmethod
    def get_next_record_to_review(self) -> KnowledgeRecord:
        """
        Retrieve the next record to review in the current review session.

        This method fetches the next learning record from the current review group
        that is being reviewed. It ensures that the records are presented in a
        sequential manner, allowing the user to systematically review each record
        in the group. The method also updates the state to keep track of the
        current position within the review group.

        Returns:
            KnowledgeRecord: The next record to be reviewed in the current session.
        """
        pass

    @abstractmethod
    def fetch_groups_to_review(self) -> Tuple[ReviewGroup, ...]:
        """
        Retrieve all groups to review ordered following these priority rules:
          - nearest next review date
          - lowest number of reviews
          - topic name alphabetically
          - groups with no next review date are at the end of the list ordered
          by topic name alphabetically

        Returns:
            Tuple[ReviewGroup, ...]: A tuple containing all groups to review.
        """
        pass

    @abstractmethod
    def get_number_of_records_in_review_group(self) -> int:
        """
        Returns:
            int: Number of records to review for the current review group
        """
        pass
