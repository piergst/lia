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
from pathlib import Path

"""
Helper class to handle setup and cleanup of databases needed by tests.  Notice
that an initial clean database with no review history is create when running 
a fresh (cache clean) instance, which has to be deleted after every tests run.
"""

TESTS_DIR: Path = Path(__file__).resolve().parent.parent
DATASET_PATH = Path(TESTS_DIR, "tests_data", "dataset_example")
SQL_FOR_MOCKING_REVIEW_DB_PATH = Path(TESTS_DIR, "tests_data", "mock_review_db.sql")
MOCKED_REVIEW_DB_PATH = Path(TESTS_DIR, "tests_data", "mocked_review_db.sqlite")
REVIEW_DB_FROM_DATASET_PATH = Path(TESTS_DIR, "tests_data", "review_db_from_dataset.sqlite")


def create_mocked_review_db():
    try:
        if not MOCKED_REVIEW_DB_PATH.exists():
            MOCKED_REVIEW_DB_PATH.touch()

        with SQL_FOR_MOCKING_REVIEW_DB_PATH.open("r", encoding="utf-8") as file:
            sql_script = file.read()

        with sqlite3.connect(MOCKED_REVIEW_DB_PATH) as connection:
            cursor = connection.cursor()
            cursor.executescript(sql_script)
            connection.commit()

    except Exception as e:
        print(f"Error when initializing test database: {e}")
        raise


def remove_mocked_review_db():
    if MOCKED_REVIEW_DB_PATH.exists():
        MOCKED_REVIEW_DB_PATH.unlink()


def remove_review_db_from_dataset():
    if REVIEW_DB_FROM_DATASET_PATH.exists():
        REVIEW_DB_FROM_DATASET_PATH.unlink()
