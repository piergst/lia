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

from datetime import datetime, timedelta
from typing import Tuple

from src.config import MAX_RECORDS_PER_REVIEW_GROUP
from src.domain.knowledge.knowledge_data_objects import KnowledgeRecord
from src.domain.knowledge.knowledge_persistence_port import KnowledgePersistencePort
from src.domain.learning.learning_data_objects import ReviewGroup
from src.domain.learning.learning_persistence_port import LearningPersistencePort
from src.domain.learning.learning_provider_port import LearningProviderPort


class LearningProvider(LearningProviderPort):
    """
    Provides an implementation of the core domain interface for managing and
    reviewing learning records.

    It integrates with both persistence and knowledge systems to facilitate the
    learning process, enabling the organization and review of learning records.
    This class encapsulates the logic required to manage review sessions,
    retrieve review groups, and fetch records for review.

    Args:
        learning_persistence (LearningPersistencePort): The persistence layer
            responsible for storing and retrieving learning sessions (reviews)
            informations.
        knowledge_persistence (KnowledgePersistencePort): The persistence layer
            responsible for storing and retrieving knowledge records.
    """

    def __init__(
        self,
        knowledge_persistence: KnowledgePersistencePort,
        learning_persistence: LearningPersistencePort,
    ) -> None:
        """
        Args:
            learning_persistence (LearningPersistencePort): The persistence layer for reviews informations.
            knowledge_persistence (KnowledgePersistencePort): The persistence layer for knowledge records.
            current_review_group (int): Stores the current reviewed group during a review session
            current_review_record_position (int): Store the current reviewed record position during a review session
        """
        self._learning_persistence = learning_persistence
        self._knowledge_persistence = knowledge_persistence
        self._current_review_group: ReviewGroup = None
        self._current_reviewed_record_position: int = 0

    @property
    def current_review_group(self) -> ReviewGroup:
        return self._current_review_group

    def fetch_review_groups_for_topic(self, topic: str) -> Tuple[ReviewGroup, ...]:
        self.__update_review_groups_for_topic(topic)
        return self._learning_persistence.get_review_groups_for_topic(topic)

    def init_review_session(self, review_group_id: int) -> None:
        self._current_review_group = self._learning_persistence.get_review_group_by_id(review_group_id)
        self._current_reviewed_record_position = 0

    def get_next_record_to_review(self) -> KnowledgeRecord:
        global_record_position = (
            self.current_review_group.group_index * MAX_RECORDS_PER_REVIEW_GROUP + self._current_reviewed_record_position
        )
        if (
            self._current_reviewed_record_position < self.get_number_of_records_in_review_group() - 1
            and self._current_reviewed_record_position < MAX_RECORDS_PER_REVIEW_GROUP - 1
        ):
            self._current_reviewed_record_position += 1
        else:
            self._current_reviewed_record_position = 0
            self._update_review_group_dates_and_count()
        return self._knowledge_persistence.get_record_by_index(self.current_review_group.topic, global_record_position)

    def fetch_groups_to_review(self) -> Tuple[ReviewGroup, ...]:
        for topic in self._knowledge_persistence.get_topic_list():
            self.__update_review_groups_for_topic(topic)
        groups = self._learning_persistence.get_all_review_groups()
        ordered_groups = sorted(
            groups,
            key=lambda x: (
                x.next_review_date if x.next_review_date is not None else datetime.max,
                x.reviews_count,
                x.topic,
                x.next_review_date is None,
            ),
        )
        return tuple(ordered_groups)

    def get_number_of_records_in_review_group(self) -> int:
        if self._is_last_group_of_review_groups():
            review_groups_nbr = len(
                self._learning_persistence.get_review_groups_for_topic(self.current_review_group.topic)
            )
            total_records = self._knowledge_persistence.count_records_for_topic(self.current_review_group.topic)
            return total_records - (review_groups_nbr - 1) * MAX_RECORDS_PER_REVIEW_GROUP
        else:
            return MAX_RECORDS_PER_REVIEW_GROUP

    def __update_review_groups_for_topic(self, topic: str) -> None:
        """
        Update the review groups for a given topic.
        """
        self._learning_persistence.update_review_groups_for_topic(
            topic, self._knowledge_persistence.count_records_for_topic(topic)
        )

    def _update_review_group_dates_and_count(self):
        """
        When EACH records of a review group have been reviewed at least
        once, review group dates and count is update to define when will
        be the next review regarding the 2-7-30 (day) learning pattern.
        """
        daysDeltaFrom1to2 = 1
        daysDeltaFrom2to7 = 5
        daysDeltaFrom7to30 = 23
        today = datetime.today().date()
        if self.current_review_group.reviews_count == 0:
            self.current_review_group.last_review_date = datetime.today()
            self.current_review_group.next_review_date = datetime.today() + timedelta(days=daysDeltaFrom1to2)
            self.current_review_group.reviews_count += 1
            self._learning_persistence.update_review_group_dates_and_count(self.current_review_group)
        elif self.current_review_group.reviews_count == 1 and self.current_review_group.next_review_date.date() <= today:
            self.current_review_group.last_review_date = datetime.today()
            self.current_review_group.next_review_date = datetime.today() + timedelta(days=daysDeltaFrom2to7)
            self.current_review_group.reviews_count += 1
            self._learning_persistence.update_review_group_dates_and_count(self.current_review_group)

        elif self.current_review_group.reviews_count == 2 and self.current_review_group.next_review_date.date() <= today:
            self.current_review_group.last_review_date = datetime.today()
            self.current_review_group.next_review_date = datetime.today() + timedelta(days=daysDeltaFrom7to30)
            self.current_review_group.reviews_count += 1
            self._learning_persistence.update_review_group_dates_and_count(self.current_review_group)

        elif self.current_review_group.reviews_count == 3 and self.current_review_group.next_review_date.date() <= today:
            self.current_review_group.last_review_date = datetime.today()
            self.current_review_group.next_review_date = None
            self.current_review_group.reviews_count += 1
            self._learning_persistence.update_review_group_dates_and_count(self.current_review_group)

    def _is_last_group_of_review_groups(self) -> bool:
        """
        Returns:
            bool: True if the current_review_group is the last review group for
            the current reviewed topic
        """
        current_review_groups_number = self._learning_persistence.get_number_of_review_groups_for_topic(
            self.current_review_group.topic
        )
        if current_review_groups_number == 0:
            raise ValueError(f"No group found for topic : {self.current_review_group.topic}")
        return current_review_groups_number - 1 == self.current_review_group.group_index
