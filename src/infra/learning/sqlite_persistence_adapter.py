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

import sqlite3
from datetime import datetime
from math import ceil
from pathlib import Path
from typing import Tuple

from src.config import MAX_RECORDS_PER_REVIEW_GROUP
from src.domain.learning.learning_data_objects import ReviewGroup
from src.domain.learning.learning_persistence_port import LearningPersistencePort


class SQLitePersistenceAdapter(LearningPersistencePort):
    """
    SQLite-based implementation of the LearningPersistencePort.
    Manages the persistence of learning information using an SQLite database.
    """

    def __init__(self, path: Path) -> None:
        """
        Args:
            path (Path): The file path to the SQLite database.
        """
        self.path: Path = path
        self.sqlite_db: sqlite3.Connection

    def __enter__(self):
        self.__init_persistence()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__close()

    def __init_persistence(self) -> None:
        """
        Initialize the SQLite database, creating necessary tables if they do not exist.
        """
        try:
            if not self.path.exists():
                self.path.touch()

            # Enable timestamp to datetime object conversion
            sqlite3.register_converter("DATETIME", lambda x: datetime.fromisoformat(x.decode()))

            # Connect to db with active converters (datetime)
            self.sqlite_db = sqlite3.connect(self.path, detect_types=sqlite3.PARSE_DECLTYPES)
            self.__create_tables()
        except sqlite3.Error as e:
            print(f"Error when initializing SQLite persistence: {e}")
            raise

    def get_review_group_by_id(self, id: int) -> ReviewGroup:
        cursor = self.sqlite_db.cursor()
        cursor.execute(
            "SELECT id, group_index, topic, last_review_date, next_review_date, reviews_count FROM review_groups WHERE id = ?",
            (id,),
        )
        result = cursor.fetchone()
        cursor.close()
        if result is None:
            raise ValueError(f"Review group with id {id} not found")
        return ReviewGroup(*result)

    def update_review_groups_for_topic(self, topic: str, count: int) -> None:
        cursor = self.sqlite_db.cursor()

        cursor.execute("SELECT COUNT(*) FROM review_groups WHERE topic = ?", (topic,))
        existing_groups_number = cursor.fetchone()

        if existing_groups_number is None:
            existing_groups_number = 0
        else:
            existing_groups_number = existing_groups_number[0]

        required_groups = ceil(count / MAX_RECORDS_PER_REVIEW_GROUP)

        if required_groups > existing_groups_number:
            for index in range(existing_groups_number, required_groups):
                cursor.execute(
                    "INSERT INTO review_groups (topic, group_index, last_review_date, next_review_date, reviews_count) VALUES (?, ?, NULL, NULL, 0)",
                    (topic, index),
                )

        self.sqlite_db.commit()
        cursor.close()

    def get_review_groups_for_topic(self, topic: str) -> Tuple[ReviewGroup, ...]:
        cursor = self.sqlite_db.cursor()
        cursor.execute(
            "SELECT id, group_index, topic, last_review_date, next_review_date, reviews_count FROM review_groups WHERE topic = ?",
            (topic,),
        )
        result = tuple(ReviewGroup(*row) for row in cursor.fetchall())
        cursor.close()
        return result

    def get_all_review_groups(self) -> Tuple[ReviewGroup, ...]:
        cursor = self.sqlite_db.cursor()
        cursor.execute(
            "SELECT id, group_index, topic, last_review_date, next_review_date, reviews_count FROM review_groups"
        )
        result = tuple(ReviewGroup(*row) for row in cursor.fetchall())
        cursor.close()
        return result

    def update_review_group_dates_and_count(self, review_group: ReviewGroup) -> None:
        cursor = self.sqlite_db.cursor()
        sql_update = "UPDATE review_groups SET last_review_date=?, next_review_date=?, reviews_count=? WHERE id=?"
        cursor.execute(
            sql_update,
            (review_group.last_review_date, review_group.next_review_date, review_group.reviews_count, review_group.id),
        )
        self.sqlite_db.commit()
        cursor.close()

    def get_number_of_review_groups_for_topic(self, topic: str) -> int:
        cursor = self.sqlite_db.cursor()

        cursor.execute("SELECT COUNT(*) FROM review_groups WHERE topic = ?", (topic,))
        existing_groups_number = cursor.fetchone()

        if existing_groups_number is None:
            existing_groups_number = 0
        else:
            existing_groups_number = existing_groups_number[0]
        return existing_groups_number

    def __create_tables(self) -> None:
        """
        Create tables in the SQLite database if they do not already exist.
        This method is called during initialization.
        """
        self.sqlite_db.execute("""
            CREATE TABLE IF NOT EXISTS review_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                group_index INTEGER NOT NULL,
                topic TEXT NOT NULL, 
                last_review_date DATETIME, 
                next_review_date DATETIME,
                reviews_count INTEGER NOT NULL DEFAULT 0
            )
        """)
        self.sqlite_db.commit()

    def __close(self) -> None:
        """
        Closes the SQLite database connection.
        """
        if self.sqlite_db:
            self.sqlite_db.close()
