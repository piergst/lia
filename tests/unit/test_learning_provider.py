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
from pathlib import Path

import pytest
from freezegun import freeze_time

from src.config import MAX_RECORDS_PER_REVIEW_GROUP
from src.domain.learning.learning_provider import LearningProvider
from src.infra.knowledge.file.file_persistence_adapter import FilePersistenceAdapter
from src.infra.learning.sqlite_persistence_adapter import SQLitePersistenceAdapter
from tests.expected_results.test_learning_provider_expected_results import (
    EXPECTED_AD_REVIEW_GROUPS,
    EXPECTED_BASH_REVIEW_GROUPS,
    EXPECTED_KNOWLEDGE_RECORD_BASH_210,
    EXPECTED_KNOWLEDGE_RECORD_BASH_230,
    EXPECTED_ORDERED_GROUPS_TO_REVIEW,
)
from tests.unit.helper import (
    DATASET_PATH,
    MOCKED_REVIEW_DB_PATH,
    REVIEW_DB_FROM_DATASET_PATH,
    create_mocked_review_db,
    remove_mocked_review_db,
    remove_review_db_from_dataset,
)


@pytest.fixture(scope="function")
def setup_and_teardown_sql_db():
    print("\n[SETUP] Initializing resources...")
    remove_mocked_review_db()
    create_mocked_review_db()

    yield  # Executing tests

    print("\n[TEARDOWN] Cleaning up resources...")
    remove_mocked_review_db()


@pytest.fixture(scope="function")
def teardown_dataset_db():
    print("\n[SETUP] Initializing resources...")
    remove_review_db_from_dataset()
    yield  # Executing tests

    print("\n[TEARDOWN] Cleaning up resources...")
    remove_review_db_from_dataset()


def test_fetch_review_groups_for_topic_Should_initialize_and_return_topic_review_groups(teardown_dataset_db) -> None:
    # Given
    persistence = FilePersistenceAdapter(DATASET_PATH)
    with SQLitePersistenceAdapter(REVIEW_DB_FROM_DATASET_PATH) as learning_persistence:
        learning_provider = LearningProvider(persistence, learning_persistence)

        # When
        review_groups = learning_provider.fetch_review_groups_for_topic("bash")

        # Then
        assert len(review_groups) == 4, f"Actual len of review groups : {len(review_groups)}"
        assert review_groups == EXPECTED_BASH_REVIEW_GROUPS, f"Actual content of review groups : {review_groups}"


def test_get_next_record_to_review_Should_return_next_record_to_review(teardown_dataset_db) -> None:
    # Given
    persistence = FilePersistenceAdapter(DATASET_PATH)
    with SQLitePersistenceAdapter(REVIEW_DB_FROM_DATASET_PATH) as learning_persistence:
        learning_provider = LearningProvider(persistence, learning_persistence)

        # When
        # Select the review group with id 3 (is a bash review group)
        learning_provider.fetch_groups_to_review()
        learning_provider.init_review_session(review_group_id=4)
        next_record_to_review = learning_provider.get_next_record_to_review()

        # Then
        assert next_record_to_review == EXPECTED_KNOWLEDGE_RECORD_BASH_210, (
            f"Actual content of next record to review : {next_record_to_review}"
        )

        # When
        next_record_to_review = learning_provider.get_next_record_to_review()

        # Then
        assert next_record_to_review == EXPECTED_KNOWLEDGE_RECORD_BASH_230, (
            f"Actual content of next record to review : {next_record_to_review}"
        )


@freeze_time("2025-03-03")
def test_fetch_groups_to_review_Should_return_all_groups_to_review_ordered_by_nearest_next_review_date(
    setup_and_teardown_sql_db,
) -> None:
    print(datetime.now())
    # Given
    persistence = FilePersistenceAdapter(Path("/dev/null"))
    with SQLitePersistenceAdapter(MOCKED_REVIEW_DB_PATH) as learning_persistence:
        learning_provider = LearningProvider(persistence, learning_persistence)

        # When
        next_groups_to_review = learning_provider.fetch_groups_to_review()

        # Then
        assert next_groups_to_review == EXPECTED_ORDERED_GROUPS_TO_REVIEW, (
            f"Actual content of next groups to review : {next_groups_to_review}"
        )


@freeze_time("2025-03-11")
def test_dates_and_count_Should_be_updated_When_all_group_items_have_been_reviewd(teardown_dataset_db) -> None:
    persistence = FilePersistenceAdapter(DATASET_PATH)
    with SQLitePersistenceAdapter(REVIEW_DB_FROM_DATASET_PATH) as learning_persistence:
        learning_provider = LearningProvider(persistence, learning_persistence)

        learning_provider.fetch_review_groups_for_topic("bash")
        learning_provider.init_review_session(review_group_id=3)
        group_to_review = learning_provider.current_review_group

        # Check initial state
        assert (
            group_to_review.last_review_date is None
            and group_to_review.next_review_date is None
            and group_to_review.reviews_count == 0
        )

        for _ in range(0, MAX_RECORDS_PER_REVIEW_GROUP - 1):
            learning_provider.get_next_record_to_review()

        # Check nothing change until last group record has been reviewed
        assert (
            group_to_review.last_review_date is None
            and group_to_review.next_review_date is None
            and group_to_review.reviews_count == 0
        )

        # Getting last record
        learning_provider.get_next_record_to_review()

        # Check review group dates and count is updated after review of last group record
        assert (
            group_to_review.last_review_date == datetime(2025, 3, 11)
            and group_to_review.next_review_date == datetime(2025, 3, 12)
            and group_to_review.reviews_count == 1
        )

        # Check nothing change when a new review on the same group happens on the same day
        # even if learning provider is restarted
    with SQLitePersistenceAdapter(REVIEW_DB_FROM_DATASET_PATH) as learning_persistence:
        learning_provider = LearningProvider(persistence, learning_persistence)
        learning_provider.fetch_review_groups_for_topic("bash")
        learning_provider.init_review_session(review_group_id=3)
        group_to_review = learning_provider.current_review_group
        for _ in range(0, MAX_RECORDS_PER_REVIEW_GROUP):
            learning_provider.get_next_record_to_review()

        assert (
            group_to_review.last_review_date == datetime(2025, 3, 11)
            and group_to_review.next_review_date == datetime(2025, 3, 12)
            and group_to_review.reviews_count == 1
        )


def test_siblings_headers_should_not_be_considered_as_different_record_to_review(teardown_dataset_db) -> None:
    # Given
    persistence = FilePersistenceAdapter(DATASET_PATH)
    with SQLitePersistenceAdapter(REVIEW_DB_FROM_DATASET_PATH) as learning_persistence:
        learning_provider = LearningProvider(persistence, learning_persistence)

        review_groups = learning_provider.fetch_review_groups_for_topic("ad")
        assert review_groups == EXPECTED_AD_REVIEW_GROUPS


def test_reviewing_group_with_less_than_max_records_per_review_group_Should_loop_the_correct_number_of_records(
    teardown_dataset_db,
) -> None:
    # Given
    persistence = FilePersistenceAdapter(DATASET_PATH)
    with SQLitePersistenceAdapter(REVIEW_DB_FROM_DATASET_PATH) as learning_persistence:
        learning_provider = LearningProvider(persistence, learning_persistence)

        learning_provider.fetch_review_groups_for_topic("bash")
        for index in range(1, 5):
            learning_provider.init_review_session(review_group_id=index)
            first_review_group_record = learning_provider.get_next_record_to_review()
            for _ in range(learning_provider.get_number_of_records_in_review_group() - 1):
                learning_provider.get_next_record_to_review()
            next_loop_first_review_group_record = learning_provider.get_next_record_to_review()
            assert first_review_group_record == next_loop_first_review_group_record


def test_Once_all_records_have_been_reviewed_next_review_date_and_review_count_Should_be_updated(
    setup_and_teardown_sql_db,
) -> None:
    # Given
    persistence = FilePersistenceAdapter(Path(DATASET_PATH))
    with SQLitePersistenceAdapter(MOCKED_REVIEW_DB_PATH) as learning_persistence:
        learning_provider = LearningProvider(persistence, learning_persistence)

        # When
        with freeze_time("2025-02-22"):
            learning_provider.fetch_review_groups_for_topic("bash")
            learning_provider.init_review_session(review_group_id=5)
            # Check initial state
            assert learning_provider.current_review_group.reviews_count == 1
            if (next_review_date := learning_provider.current_review_group.next_review_date) is not None:
                assert next_review_date.date() == datetime.today().date()
            for _ in range(learning_provider.get_number_of_records_in_review_group()):
                learning_provider.get_next_record_to_review()

            assert learning_provider.current_review_group.reviews_count == 2
            if (next_review_date := learning_provider.current_review_group.next_review_date) is not None:
                assert next_review_date.date() == (datetime.today() + timedelta(days=5)).date()

        # When
        with freeze_time("2025-02-27"):
            learning_provider.fetch_review_groups_for_topic("bash")
            learning_provider.init_review_session(review_group_id=5)
            # Check initial state
            assert learning_provider.current_review_group.reviews_count == 2
            if (next_review_date := learning_provider.current_review_group.next_review_date) is not None:
                assert next_review_date.date() == datetime.today().date()
            for _ in range(learning_provider.get_number_of_records_in_review_group()):
                learning_provider.get_next_record_to_review()

            assert learning_provider.current_review_group.reviews_count == 3
            if (next_review_date := learning_provider.current_review_group.next_review_date) is not None:
                assert next_review_date.date() == (datetime.today() + timedelta(days=23)).date()

        # When
        with freeze_time("2025-03-23"):
            learning_provider.fetch_review_groups_for_topic("bash")
            learning_provider.init_review_session(review_group_id=5)
            # Check initial state
            assert learning_provider.current_review_group.reviews_count == 3
            if (next_review_date := learning_provider.current_review_group.next_review_date) is not None:
                assert next_review_date.date() == (datetime.today() + timedelta(days=-1)).date()
            for _ in range(learning_provider.get_number_of_records_in_review_group()):
                learning_provider.get_next_record_to_review()

            assert learning_provider.current_review_group.reviews_count == 4
            assert learning_provider.current_review_group.next_review_date is None


def test_number_of_records_of_last_review_group_Should_be_one_for_a_one_record_topic(teardown_dataset_db) -> None:
    # Given
    persistence = FilePersistenceAdapter(DATASET_PATH)
    with SQLitePersistenceAdapter(REVIEW_DB_FROM_DATASET_PATH) as learning_persistence:
        learning_provider = LearningProvider(persistence, learning_persistence)

        # When
        learning_provider.fetch_review_groups_for_topic("curl")
        learning_provider.init_review_session(review_group_id=1)
        records_nbr = learning_provider.get_number_of_records_in_review_group()

        # Then
        assert records_nbr == 1, f"Actual records number is : {records_nbr}"
