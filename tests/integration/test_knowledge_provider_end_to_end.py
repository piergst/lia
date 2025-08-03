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

import pytest

from src.domain.knowledge.knowledge_provider import KnowledgeProvider
from src.infra.knowledge.file.file_persistence_adapter import FilePersistenceAdapter
from src.infra.knowledge.sentence_similarity.sentence_transformer_daemon_adapter import SentenceTransformerDaemonAdapter
from tests.expected_results.test_knowledge_provider_expected_results import (
    EXPECTED_TOP_1_ANSWER_AD_1,
    EXPECTED_TOP_1_ANSWER_AD_2,
    EXPECTED_TOP_1_ANSWER_BASH,
    EXPECTED_TOP_1_ANSWER_CURL,
    EXPECTED_TOP_1_ANSWER_ENUMERATE,
    EXPECTED_TOP_1_HEADING_AD,
    EXPECTED_TOP_2_HEADINGS_AD,
    EXPECTED_TOP_3_HEADINGS_BASH_1,
    EXPECTED_TOP_3_HEADINGS_CURL,
    EXPECTED_TOP_3_HEADINGS_ENUMERATE,
)

TESTS_DIR: Path = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def knowledge_provider():
    print("\nSetup : starting knowledge provider")
    persistence = FilePersistenceAdapter(f"{TESTS_DIR}/tests_data/dataset_example")
    sentence_similarity_checker = SentenceTransformerDaemonAdapter()
    sentence_similarity_checker.start()
    knowledge_provider = KnowledgeProvider(persistence, sentence_similarity_checker)
    yield knowledge_provider  # L'objet est utilisé par les tests
    print("\nTeardown : stopping knowledge provider")
    sentence_similarity_checker.stop()
    del knowledge_provider


def test_should_seek_matches_for_a_given_query(knowledge_provider):
    result = knowledge_provider.ask("How to check if an array contains a given value in bash?")

    # Then

    assert result[0] == EXPECTED_TOP_3_HEADINGS_BASH_1, f"Actual headings = {result[0]}"

    assert result[1] == EXPECTED_TOP_1_ANSWER_BASH, f"Actual answer = {result[1]}"


def test_should_find_match_in_file_containing_only_one_heading(knowledge_provider):
    result = knowledge_provider.ask("How to use session cookie with curl ?")

    assert result[0] == EXPECTED_TOP_3_HEADINGS_CURL, f"Actual headings = {result[0]}"

    assert result[1] == EXPECTED_TOP_1_ANSWER_CURL, f"Actual answer = {result[1]}"


def test_should_seek_results_even_if_topic_is_unknown(knowledge_provider):
    result = knowledge_provider.ask("enumerate directories ?")

    assert result[0] == EXPECTED_TOP_3_HEADINGS_ENUMERATE, f"Actual headings = {result[0]}"

    assert result[1] == EXPECTED_TOP_1_ANSWER_ENUMERATE, f"Actual answer = {result[1]}"


def test_should_return_matches_for_a_record_with_an_alternative_heading(knowledge_provider) -> None:
    result = knowledge_provider.ask("Which file contains users and password information in AD?")

    # Then
    assert result[0] == EXPECTED_TOP_2_HEADINGS_AD, f"Actual headings = {result[0]}"

    assert result[1] == EXPECTED_TOP_1_ANSWER_AD_1, f"Actual answer = {result[1]}"


def test_should_return_only_one_heading_for_a_record_with_multiple_alternative_headings(knowledge_provider) -> None:
    result = knowledge_provider.ask("What does the SYSVOL folder contain in AD?")

    # Then
    assert result[0] == EXPECTED_TOP_1_HEADING_AD, f"Actual headings = {result[0]}"

    assert result[1] == EXPECTED_TOP_1_ANSWER_AD_2, f"Actual answer = {result[1]}"
