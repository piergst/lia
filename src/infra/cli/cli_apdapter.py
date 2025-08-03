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

import os
import time
from typing import Dict, Tuple

import pyperclip
import readchar

from src.config import Color, SimilarityScore
from src.domain.knowledge.knowledge_data_objects import RecordHeading, RecordHeadingMatch
from src.domain.learning.learning_provider import LearningProvider
from src.environment import DATA_PATH, SQLITE_FILE
from src.infra.cli.cli_console import CliConsole
from src.infra.cli.cli_knowledge_provider_manager import CliKnowledgeProviderManager
from src.infra.cli.cli_rich_print import (
    print_new_line,
    print_no_relevant_match,
    print_no_results,
    print_record,
    print_rich_separator,
    print_rich_similar_headings,
    render_as_markdown,
    reviews_count_color,
    rich_ask_prompt,
    rich_input_prompt,
    rich_print,
)
from src.infra.knowledge.file.file_persistence_adapter import FilePersistenceAdapter
from src.infra.learning.sqlite_persistence_adapter import SQLitePersistenceAdapter

"""
CLI adapter which basically uses knowledge provider API and formats output for
CLI. Each "public" function here match a CLI command.
"""


def do_list(args: Dict[str, str]) -> None:
    """
    Depending on args :
            - Prints the list of topics.
            - Prints the list of available reviews for all existing topics.

    The function retrieves the command argument from the 'args' dictionary,
    which is populated by the 'cli_parser.py' module. This module parse the input
    command args (here --topics or --review-groups) and translate them in formatted
    arguments "topics" and "review_groups".

    Args:
            args (Dict[str, str]): A dictionary containing formatted command-line arguments

    """
    if args["topics"]:
        for topic in CliKnowledgeProviderManager.instance().get_topics_list():
            print(topic)
    elif args["review_groups"]:
        persistence = FilePersistenceAdapter(DATA_PATH)
        with SQLitePersistenceAdapter(SQLITE_FILE) as learning_persistence:
            learning_provider = LearningProvider(persistence, learning_persistence)

            groups_to_review = learning_provider.fetch_groups_to_review()

            for index, group in enumerate(groups_to_review):
                last_review_date = group.last_review_date.date() if group.last_review_date is not None else None
                next_review_date = group.next_review_date.date() if group.next_review_date is not None else None
                color = reviews_count_color(group.reviews_count)
                rich_print(
                    f"{index + 1} - [bold]{group.topic}[/bold] - Last review ({last_review_date}) - Next review ([{color} bold]{next_review_date}[/{color} bold]) - [{color} bold]{group.reviews_count} review[/{color} bold]"
                )


def show(args: Dict[str, str]) -> None:
    """
    Prints the list of records (heading only) associated with a given topic.

    The function retrieves the topic name from the 'args' dictionary, which is
    populated by the 'cli_parser.py' module. By design, this module associates
    the 'topic_name' key with the argument passed to the 'show' command,
    representing the sought topic.

    Args:
            args (Dict[str, str]): A dictionary containing the command-line arguments,
                                                       specifically the 'topic_name' key that specifies the
                                                       topic for which to display the associated headings.
    """

    topic = args["topic_name"]
    records_headings = [
        record_heading
        for record_heading in CliKnowledgeProviderManager.instance().get_available_records_headings_for_topic(topic)
    ]
    if records_headings:
        for record_heading in records_headings:
            print(record_heading.text)
    else:
        print(f"Topic '{topic}' does not exist.")


def ask() -> None:
    """
    Main functionality of the program: prompts the user for his ask and
    prints the best match found.
    If the knowledge provider underlying process is not already running, it
    starts it.
    """
    CliKnowledgeProviderManager.instance()

    try:
        user_input = rich_ask_prompt()
        _process_ask_and_present_results(user_input)
    except Exception as e:
        print(f"Error: {e}")


def review(args: Dict[str, str]) -> None:
    """
    Review feature allows user to learn a topic by reviewing records as a
    flashcard system. First user select a review group for a given topic and
    then enter in a loop of reviewing one by one records of the same group until
    he decides to quit.
    """
    persistence = FilePersistenceAdapter(DATA_PATH)
    if args["topic_name"] in persistence.get_topic_list():
        with SQLitePersistenceAdapter(SQLITE_FILE) as learning_persistence:
            learning_provider = LearningProvider(persistence, learning_persistence)
            groups = learning_provider.fetch_review_groups_for_topic(args["topic_name"])

            rich_print(
                f"[{Color.BLUE.value} bold]\uebf8[/{Color.BLUE.value} bold]  [bold]Available groups for review:[/bold]"
            )
            for index, group in enumerate(groups):
                last_review_date = group.last_review_date.date() if group.last_review_date is not None else None
                next_review_date = group.next_review_date.date() if group.next_review_date is not None else None
                color = reviews_count_color(group.reviews_count)
                rich_print(
                    f"  - [[{color} bold]{index + 1}[/{color} bold]] - Last review ({last_review_date}) - Next review ({next_review_date}) - [{color} bold]{group.reviews_count} review[/{color} bold]"
                )

            while True:
                text = f"[bold]Your choice [1-{len(groups)}][/bold]"
                user_input = rich_input_prompt("[bold]\uf0a9[/bold]", text)
                if user_input.isdigit() and 1 <= int(user_input) <= len(groups):
                    learning_provider.init_review_session(groups[int(user_input) - 1].id)
                    break
                elif user_input == "q" or user_input == "quit" or user_input == "exit":
                    exit()
                else:
                    print("Invalid group id. Please try again.")
            while True:
                _review_session_loop(learning_provider)
    else:
        print(f"Topic '{args['topic_name']}' does not exist.")


def stop() -> None:
    CliKnowledgeProviderManager.stop_similarity_engine()


def _review_session_loop(learning_provider: LearningProvider) -> None:
    """
    This function manages the main loop of a review session where the user
    reviews knowledge records in a flashcard-like system. The user can choose
    to view the content of the current record, proceed to the next record,
    or exit the review session.

    Args:
            learning_provider (LearningProvider): The instance of LearningProvider
            used to fetch the knowledge records to review.
    """
    # Print record first heading
    record_to_review = learning_provider.get_next_record_to_review()
    print_new_line()
    print_rich_separator()
    check_icon = f"[{Color.GREEN.value} bold]\uf29c[/{Color.GREEN.value} bold]"
    heading_text = f"[bold]{record_to_review.headings[0]}[bold]"
    CliConsole.instance().print(f"{check_icon}  {heading_text}", highlight=False)

    while True:
        key = readchar.readkey()  # Instant capture of a pressed key
        if key == "q":
            print("Quit.")
            exit()
            break
        elif key == "\n":
            # Print other record's headings if existing and then record's body
            if len(record_to_review.headings) > 1:
                for heading in record_to_review.headings[1:]:
                    check_icon = f"[{Color.GREEN.value} bold]\uf29c[/{Color.GREEN.value} bold]"
                    heading_text = f"[bold]{heading}[bold]"
                    CliConsole.instance().print(f"{check_icon}  {heading_text}", highlight=False)
            print_rich_separator()
            print_new_line()
            render_as_markdown(record_to_review.body)
            print_new_line()
            break


def _process_ask_and_present_results(user_input: str) -> None:
    """
    Processes the user's input by querying the knowledge provider and
    presenting the result based on the similarity score.

    The function checks the similarity score of mathces. If the similarity score
    is above a medium threshold, the result is presented. Otherwise, a message
    indicating that no relevant content has been found is shown. The function
    also handles alternative actions that the user can make, based on the
    result.

    Args:
            user_input (str): The text input provided by the user.
    """
    console = CliConsole.instance()
    knowledge_provider = CliKnowledgeProviderManager.instance()

    if user_input == "quit" or user_input == "exit":
        return

    # Activate spinner busy indicator while processing input
    with console.status("[bold]Processing", spinner="point", spinner_style=f"{Color.BLUE.value}"):
        result: Tuple[Tuple[RecordHeadingMatch, ...], str] = knowledge_provider.ask(user_input)

    if not any(result):
        _present_no_results()
        return

    if result[0][0].similarity_indice >= SimilarityScore.MEDIUM.lower_bound():
        _present_result(result)
    else:
        _present_no_match(result)

    _prompt_for_alternative_actions(result)


def _present_result(result: Tuple[Tuple[RecordHeadingMatch, ...], str]) -> None:
    """
    Presents the result to the user, displaying the most similar heading,
    the body text, and any similar headings if available.

    Args:
            result (Tuple[Tuple[RecordMatch, ...], str]): A tuple containing the top
            similar headings and the body for the top 1. Needed to evaluate if
            result is relevant.
    """
    heading: RecordHeadingMatch = result[0][0]
    body_text: str = result[1]
    similar_headings: Tuple[RecordHeadingMatch, ...] = result[0][1:]

    print_record(heading, body_text)
    print_new_line()

    if similar_headings:
        print_rich_similar_headings(similar_headings)
        print_new_line()


def _present_no_results() -> None:
    """
    Informs the user that no  result was found.

    """
    print_new_line()
    print_no_results()


def _present_no_match(matches: Tuple[Tuple[RecordHeadingMatch, ...], str]) -> None:
    """
    Informs the user that no relevant result was found, and displays similar
    headings if available.

    Args:
            matches (Tuple[Tuple[RecordMatch, ...], str]): A tuple containing
                       the top similar headings and the body for the top 1.
    """
    similar_headings: Tuple[RecordHeadingMatch, ...] = matches[0][0:]

    print_new_line()
    print_no_relevant_match()
    print_new_line()

    if similar_headings:
        print_rich_similar_headings(similar_headings)
        print_new_line()


def _get_available_alternative_matches(all_matches: Tuple[RecordHeadingMatch, ...]) -> Tuple[RecordHeadingMatch, ...]:
    """
    In the normal case, the best match is used to determine the final result.
    However, if the similarity score of the top 1 match falls below a defined
    threshold, the similarity search is considered to have failed to find a
    valid match. In this situation, all matches (including the top 1) are
    treated as alternatives to propose.

    Args:
            all_matches (Tuple[RecordMatch, ...]):
                    A tuple containing all the matches, sorted by
                    similarity score in descending order.

    Returns:
            Tuple[RecordMatch, ...]:
                    A tuple containing the matches considered as alternative matches
    """
    top_1_match = all_matches[0]
    if top_1_match.similarity_indice >= SimilarityScore.MEDIUM.lower_bound():
        return all_matches[1:]
    else:
        return all_matches


def _get_alternative_actions_prompt_text(best_match: RecordHeading, alternative_matches_nbr: int) -> str:
    """
    Generate the prompt text to display available actions to the user
    based on the best match and the number of alternative matches.

    Args:
            best_match (RecordHeading):
                    The best match, which may contain tags indicating whether commands
                    are available to copy.
            alternative_matches_nbr (int):
                    The number of alternative matches available for selection.
    """
    prompt_text = "[bold]What would you like to do ?[/bold]\n"

    if alternative_matches_nbr > 0:
        prompt_text += f"  - View an alternative result [1-{alternative_matches_nbr}]\n"

    prompt_text += "  - New ask (n)"

    if best_match.has_command_tag():
        prompt_text += "\n  - Copy command(s) to clipboard (c)"
    elif best_match.has_script_tag():
        prompt_text += "\n  - Copy script(s) to clipboard (c)"
    prompt_text += "\n  - Quit (q)"
    prompt_text += "\n[bold]\uf0a9  Your choice[/bold]"
    return prompt_text

def _copy_extracted_content_to_clipboard_if_tagged(heading: RecordHeading) -> None:
    """
    Copy scripts for record's body to the clipboard if the
    record is tagged as script.

    Args:
            heading (RecordHeading):
                    The heading which may contain tags indicating the presence of one or
                    multiple commands.
    """
    knowledge_provider = CliKnowledgeProviderManager.instance()
    if heading.has_command_tag():
        content = reversed(knowledge_provider.get_commands_from_record_tagged_as_command(heading.topic, heading.id))
    elif heading.has_script_tag():
        content = reversed(knowledge_provider.get_scripts_from_record_tagged_as_script(heading.topic, heading.id))
    else:
        content = tuple()

    if content:
        console = CliConsole.instance()
        # Sleep (during 0.2) is used to give clipboard managers (if any) enough time to capture multiple successive copies
        # and preserve clipboard history.
        with console.status("[bold]Copying", spinner="point", spinner_style=f"{Color.BLUE.value}"):
            for c in content:
                pyperclip.copy(c)
                time.sleep(0.2)
        print("Copied to Clipboard")


def _prompt_for_alternative_actions(match: Tuple[Tuple[RecordHeadingMatch, ...], str]) -> None:
    """
    Prompt the user to select an alternative action based on the given match.
    The user can view alternative matches, new query, copy commands to the
    clipboard, or quit.

    Args:
            match (Tuple[Tuple[RecordMatch, ...], str]):
                    A tuple containing a list of headings (representing best matches)
                    and a string which is the body of the best match.
    """
    alternative_matches = _get_available_alternative_matches(match[0])
    best_match_heading = match[0][0].record_heading

    while True:
        target_icon = f"[{Color.BLUE.value} bold]\uebf8[/{Color.BLUE.value} bold]"
        prompt_text = _get_alternative_actions_prompt_text(best_match_heading, len(alternative_matches))
        user_input = rich_input_prompt(target_icon, prompt_text).strip().lower()

        # Action 'quit'
        if user_input == "q":
            break
        # Action 'new ask'
        elif user_input == "n":
            print_rich_separator()
            os.system("clear")
            ask()
            return
        # Action 'copy command to clipboard'
        elif user_input == "c":
            # _copy_commands_to_clipboard_if_tagged(best_match_heading)
            _copy_extracted_content_to_clipboard_if_tagged(best_match_heading)
            return
        else:
            # Action 'display similar heading content'
            try:
                choice = int(user_input)
                if 1 <= choice <= len(alternative_matches):
                    os.system("clear")
                    _process_ask_and_present_results(alternative_matches[choice - 1].record_heading.text)
                    break
                else:
                    print("\nInvalid choice. Please enter a number in the valid range.\n")
            except ValueError:
                print("\nInvalid input. Please enter a valid number or action.\n")
