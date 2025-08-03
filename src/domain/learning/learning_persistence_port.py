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

from src.domain.learning.learning_data_objects import ReviewGroup


class LearningPersistencePort(ABC):
    """
    This interface serves as the domain access port for managing the persistence
    of learning informations. It defines the essential operations required to
    interact with the persistence layer, ensuring that learning informations are
    stored, retrieved, and updated efficiently.
    """

    @abstractmethod
    def get_review_group_by_id(self, id: int) -> ReviewGroup:
        """
        Retrieve a review group by its unique identifier.

        Args:
            id (int): The unique identifier of the review group.

        Returns:
            ReviewGroup: The review group associated with the given id.
        """
        pass

    @abstractmethod
    def update_review_groups_for_topic(self, topic: str, count: int) -> None:
        """
        Update the review groups for a specific topic.

        This method is responsible for adjusting the review groups associated
        with a particular topic.  It ensures that the review groups reflect the
        current state of the learning records, based on the number of records
        available for the topic. This operation is vital for maintaining the
        accuracy and relevance of review sessions.

        Args:
            topic (str): The topic for which the review groups should be updated.
            count (int): The number of records associated with the topic.
        """
        pass

    @abstractmethod
    def get_review_groups_for_topic(self, topic: str) -> Tuple[ReviewGroup, ...]:
        """
        Retrieve review groups for a specific topic.

        This method provides access to all review groups related to a given topic. It is used to
        organize learning records into manageable groups, facilitating the review process.

        Args:
            topic (str): The topic for which the review groups should be retrieved.

        Returns:
            Tuple[ReviewGroup, ...]: A tuple containing the review groups for the given topic.
        """
        pass

    @abstractmethod
    def get_all_review_groups(self) -> Tuple[ReviewGroup, ...]:
        """
        Retrieve all review groups.

        Returns:
            Tuple[ReviewGroup, ...]: A tuple containing all review groups.
        """
        pass

    @abstractmethod
    def update_review_group_dates_and_count(self, review_group: ReviewGroup) -> None:
        """
        Update the values of a ReviewGroup in database.

        Args:
            review_group (ReviewGroup): Review group with values to update
        """

    @abstractmethod
    def get_number_of_review_groups_for_topic(self, topic: str) -> int:
        """
        Args:
            topic (str): The topic we want to know the number of review groups

        Returns:
            int: The number of review groups for the given topic
        """
        pass
