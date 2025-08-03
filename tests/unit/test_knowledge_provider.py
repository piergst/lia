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
    EXPECTED_BASH_HEADINGS,
    EXPECTED_COMMAND,
    EXPECTED_COMMANDS_1,
    EXPECTED_COMMANDS_2,
    EXPECTED_TOP_1_ANSWER_BASH,
    EXPECTED_TOP_3_HEADINGS_BASH_1,
    EXPECTED_TOP_3_HEADINGS_BASH_2,
    EXPECTED_TOPICS,
)

TESTS_DIR: Path = Path(__file__).resolve().parent.parent


@pytest.fixture
def mock_os_walk(mocker) -> None:
    """
    Mock directories and files arborescence
    """
    mock = mocker.patch("os.walk")
    mock.return_value = [
        ("/root", ("cheat", "note"), ()),
        ("/root/cheat", (), ("bash.md", "python.md", "rust.md", "vscode-python.md")),
        ("/root/note", (), ("bash.md", "c++.md", "greenclip.md", "python.md")),
    ]


def test_should_return_all_topics_with_the_support_of_a_file_persistance(mock_os_walk) -> None:
    # Given
    persistence = FilePersistenceAdapter(Path("/mock"))
    knowledge_provider = KnowledgeProvider(persistence)

    # When
    topics = knowledge_provider.get_topics_list()

    # Then
    assert topics == EXPECTED_TOPICS, f"Actual topics = {topics}"


def test_should_return_heading_list_from_a_given_topic_with_the_support_of_a_file_persistence() -> None:
    # Given
    persistence = FilePersistenceAdapter(Path(f"{TESTS_DIR}/tests_data/dataset_example"))
    knowledge_provider = KnowledgeProvider(persistence)

    # When
    heading_list = tuple(
        (record_heading.text, record_heading.tags)
        for record_heading in knowledge_provider.get_available_records_headings_for_topic("bash")
    )

    # Then
    assert heading_list == EXPECTED_BASH_HEADINGS, f"Actual headings = \n{(heading_list)}"


def test_should_return_top_3_similar_headings_and_top_1_content_when_asked(mocker) -> None:
    """
    This test completely mock the sentence similarity module to avoid daemon
    setup and model loading. The mock returns an expected set of similarities
    values. So this test aims to check the conversion from similarity values to
    the actual similar sentences and to check the validity of the content returned.
    """
    mock_sim_ctor = mocker.patch(
        "src.infra.knowledge.sentence_similarity.sentence_transformer_daemon_adapter.SentenceTransformerDaemonAdapter.__init__"
    )
    mock_sim_ctor.side_effect = None
    mock_sim_ctor.return_value = None
    mock_sim_find = mocker.patch(
        "src.infra.knowledge.sentence_similarity.sentence_transformer_daemon_adapter.SentenceTransformerDaemonAdapter.rank_similarities"
    )
    mock_sim_find.return_value = ((12, 0.931554), (19, 0.711219), (11, 0.565154))

    # Given
    persistence = FilePersistenceAdapter(Path(f"{TESTS_DIR}/tests_data/dataset_example"))
    sentence_similarity_checker = SentenceTransformerDaemonAdapter()
    knowledge_provider = KnowledgeProvider(persistence, sentence_similarity_checker)

    # When
    result = knowledge_provider.ask("How to check if an array contains a given value in bash?")

    # Then
    assert result[0] == EXPECTED_TOP_3_HEADINGS_BASH_1, f"Actual headings = {result[0]}"

    assert result[1] == EXPECTED_TOP_1_ANSWER_BASH, f"Actual answer = {result[1]}"


def test_should_return_content_for_identified_heading() -> None:
    # Given
    persistence = FilePersistenceAdapter(Path(f"{TESTS_DIR}/tests_data/dataset_example"))
    knowledge_provider = KnowledgeProvider(persistence)

    # When
    heading_id = 191  # Line number of heading "How to check for the presence of a value in an array in Bash?" in bash.md
    content = knowledge_provider.get_content_for_identified_heading("bash", heading_id)

    # Then
    assert content == EXPECTED_TOP_1_ANSWER_BASH, f"Actual content = {content}"


def test_should_return_top_3_similar_headings_and_no_content_if_max_similarity_score_is_under_0_6(mocker) -> None:
    """
    This test completely mock the sentence similarity module to avoid daemon
    setup and model loading.  The mock returns an expected set of similarities
    """

    mock_sim_ctor = mocker.patch(
        "src.infra.knowledge.sentence_similarity.sentence_transformer_daemon_adapter.SentenceTransformerDaemonAdapter.__init__"
    )
    mock_sim_ctor.side_effect = None
    mock_sim_ctor.return_value = None
    mock_sim_find = mocker.patch(
        "src.infra.knowledge.sentence_similarity.sentence_transformer_daemon_adapter.SentenceTransformerDaemonAdapter.rank_similarities"
    )
    mock_sim_find.return_value = ((7, 0.579725), (13, 0.516847), (18, 0.506158))

    # Given
    persistence = FilePersistenceAdapter(Path(f"{TESTS_DIR}/tests_data/dataset_example"))
    sentence_similarity_checker = SentenceTransformerDaemonAdapter()
    knowledge_provider = KnowledgeProvider(persistence, sentence_similarity_checker)

    # When
    result = knowledge_provider.ask("Is there turtles in bash?")

    # Then
    assert result[0] == EXPECTED_TOP_3_HEADINGS_BASH_2, f"Actual headings = {result[0]}"

    # Check that no result is returned in this context
    assert result[1] == ""


def test_should_return_command_extracted_from_a_record_which_is_tagged_as_command() -> None:
    # Given
    persistence = FilePersistenceAdapter(Path(f"{TESTS_DIR}/tests_data/dataset_example"))
    knowledge_provider = KnowledgeProvider(persistence)

    # When
    heading_id = 313  # Line number of heading "How to count the number of words in a text file using bash?" in bash.md
    command = knowledge_provider.get_commands_from_record_tagged_as_command("bash", heading_id)

    # Then
    assert command == EXPECTED_COMMAND, f"Actual command : {command}"


def test_should_return_commands_extracted_from_a_record_which_is_tagged_as_commands() -> None:
    # Given
    persistence = FilePersistenceAdapter(Path(f"{TESTS_DIR}/tests_data/dataset_example"))
    knowledge_provider = KnowledgeProvider(persistence)

    # When
    heading_id = 318  # Line number of heading "How to count the number of words in a text file using bash?" in bash.md
    commands = knowledge_provider.get_commands_from_record_tagged_as_command("bash", heading_id)

    # Then
    assert commands == EXPECTED_COMMANDS_1, f"Actual commands are : {commands}"


def test_should_return_commands_extracted_from_a_long_record_which_is_tagged_as_commands() -> None:
    # Given
    persistence = FilePersistenceAdapter(Path(f"{TESTS_DIR}/tests_data/dataset_example"))
    knowledge_provider = KnowledgeProvider(persistence)

    # When
    heading_id = 276  # Line number of heading "How to flash an ISO with `dd` in bash?"
    commands = knowledge_provider.get_commands_from_record_tagged_as_command("bash", heading_id)

    # Then
    assert commands == EXPECTED_COMMANDS_2, f"Actual commands are : {commands}"
