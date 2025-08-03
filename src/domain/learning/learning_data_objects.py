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
from datetime import datetime
from typing import Optional

@dataclass
class ReviewGroup:
    """
    A review group references a set of records destined to be reviewed together for a given topic.

    Attributes:
        id (int): The id of the review group.
        group_index (int): The index of the review group (among all review
            groups for the same topic in order of creation).
        topic (str): The topic of the review group.
        last_review_date (datetime): The date of the last review.
        next_review_date (datetime): The date of the next review.
        reviews_count (int): The number of reviews for the review group.
    """

    id: int
    group_index: int
    topic: str
    last_review_date: Optional[datetime]
    next_review_date: Optional[datetime]
    reviews_count: int

    def __init__(
        self,
        id: int,
        group_index: int,
        topic: str,
        last_review_date: Optional[datetime],
        next_review_date: Optional[datetime],
        reviews_count: int,
    ) -> None:
        self.id = id
        self.group_index = group_index
        self.topic = topic
        self.last_review_date = last_review_date
        self.next_review_date = next_review_date
        self.reviews_count = reviews_count
