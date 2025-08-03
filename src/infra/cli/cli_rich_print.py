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
import random
import re
import subprocess
import time
from typing import Tuple

from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.styles import Style
from rich.live import Live
from rich.markdown import Markdown
from rich.padding import Padding
from rich.prompt import Prompt

from src.config import Color, SimilarityScore
from src.domain.knowledge.knowledge_data_objects import RecordHeadingMatch
from src.environment import HISTORY_FILE
from src.infra.cli.cli_console import CliConsole

"""
CLI rich print module. 
Provides high-level functions for formatting and enhancing the visual
presentation of CLI outputs.
"""


def simimilarity_score_color(similarity_score: float) -> str:
    """
    Determine the color associated with a given similarity score based on
    predefined thresholds.

    Args:
        similarity_score (float):
            The similarity score to evaluate. Expected to be a value within the
            defined range of similarity scores (e.g., [0.0, 1.0]).

    Returns:
        str:
            The color code (as a string) corresponding to the similarity score:
            - White: Default color if no range is matched.
            - Red: For scores in the "LOW" range.
            - Orange: For scores in the "MEDIUM" range.
            - Green: For scores in the "HIGH" range.
    """
    color: str = Color.WHITE.value
    if SimilarityScore.LOW.lower_bound() <= similarity_score < SimilarityScore.LOW.upper_bound():
        color = Color.RED.value
    elif SimilarityScore.MEDIUM.lower_bound() <= similarity_score < SimilarityScore.MEDIUM.upper_bound():
        color = Color.ORANGE.value
    elif SimilarityScore.HIGH.lower_bound() <= similarity_score <= SimilarityScore.HIGH.upper_bound():
        color = Color.GREEN.value
    return color


def reviews_count_color(review_count: int) -> str:
    """
    Determine the color associated with a given number of review (for a record)
    Args:
        review_count (int):
            The number of review to evaluate. Expected to be a value within the
            range [0, 3]. (Max review is 3)

    Returns:
        str:
            The color code (as a string) corresponding to the review count.
    """
    match review_count:
        case 0:
            return Color.RED.value
        case 1:
            return Color.ORANGE.value
        case 2:
            return Color.YELLOW.value
        case 3:
            return Color.LIGHT_GREEN.value
        case 4:
            return Color.GREEN.value
        case _:
            raise ValueError("Review count must be between 0 and 3")


def print_rich_heading(heading: RecordHeadingMatch) -> None:
    """
    Display a formatted and color-coded representation of a heading with its
    similarity score.

    Args:
        heading (RecordMatch):
            The heading to display, which includes the text of the heading
            and its similarity score.
    """
    similarity_score_color = simimilarity_score_color(heading.similarity_indice)
    check_icon = f"[{similarity_score_color} bold]\uf05d[/{similarity_score_color} bold]"
    heading_text = f"[bold]{heading.record_heading.text}[bold]"
    score = f"([{similarity_score_color}]{heading.similarity_indice}[/{similarity_score_color}]"
    topic = heading.record_heading.topic

    CliConsole.instance().print(f"{check_icon}  {heading_text} - {score} in {topic}.md)", highlight=False)


def print_no_relevant_match() -> None:
    """
    Display a formatted message indicating that no match was found.
    """
    fail_icon = f"[{Color.RED.value} bold]\uf05c[/{Color.RED.value} bold]"
    text = f"[bold]No match found (similarity score below {SimilarityScore.MEDIUM.lower_bound()})[bold]"

    CliConsole.instance().print(f"{fail_icon}  {text}", highlight=False)


def print_no_results() -> None:
    """
    Display a formatted message indicating that no match was found.
    """
    fail_icon = f"[{Color.RED.value} bold]\uf05c[/{Color.RED.value} bold]"
    text = "[bold]No results found, database seems to be empty.[bold]"

    CliConsole.instance().print(f"{fail_icon}  {text}", highlight=False)


def generate_gradient_line(start_color: Tuple[int, int, int], end_color: Tuple[int, int, int], width: int) -> str:
    """
    Generate a gradient line using RGB colors.

    Args:
        start_color (Tuple[int, int, int]):
            A tuple representing the RGB values (0-255) of the starting color.
        end_color (Tuple[int, int, int]):
            A tuple representing the RGB values (0-255) of the ending color.
        width (int):
            The number of characters to fill with the gradient.
    """
    gradient = []
    for i in range(width):
        # Linear interpolation for RGB values
        r = start_color[0] + (end_color[0] - start_color[0]) * (i / width)
        g = start_color[1] + (end_color[1] - start_color[1]) * (i / width)
        b = start_color[2] + (end_color[2] - start_color[2]) * (i / width)
        # Append the hex color to the list
        gradient.append(f"[rgb({int(r)},{int(g)},{int(b)})]━[/]")
    return "".join(gradient)


def print_rich_separator() -> None:
    """
    Display a separator as a gradient color line
    """
    width = CliConsole.instance().width
    line = generate_gradient_line((0, 255, 255), (255, 0, 255), width)
    CliConsole.instance().print(line, markup=True)

    # Example of single color separtor with title
    # CliConsoleSingleton.instance().print(Rule("My Separator", style="cyan"))


def print_rich_similar_headings(headings: Tuple[RecordHeadingMatch, ...]) -> None:
    """
    Display a formatted and color-coded list of similar headings.

    Args:
        headings (Tuple[RecordMatch, ...]):
            A tuple containing similar headings, each with its text and similarity score.
    """
    console = CliConsole.instance()
    similar_icon = f"[{Color.BLUE.value} bold]\uf0ec[/{Color.BLUE.value} bold]"
    similar_title = f"{similar_icon}  [bold]Similar results :[/bold]"
    console.print(f"{similar_title}")
    for index, heading in enumerate(headings):
        similarity_score_color = simimilarity_score_color(heading.similarity_indice)
        heading_index = f"[[{similarity_score_color}]{index + 1}[/{similarity_score_color}]]"
        heading_score = f"([{similarity_score_color}]{heading.similarity_indice}[/{similarity_score_color}]"
        topic = heading.record_heading.topic

        padded_text = Padding(f"- {heading_index} {heading.record_heading.text} - {heading_score} in {topic}.md)", (0, 2))

        console.print(padded_text)


def stream_text(texte, min_delay=0.005, max_delay=0.01):
    """
    (Not used) Test of a streamed generation of output.
    """
    buffer = ""

    with Live("", refresh_per_second=40) as live:
        for char in texte:
            buffer += char
            rendered_text = CliConsole.instance().render_str(buffer)
            live.update(rendered_text)
            time.sleep(random.uniform(min_delay, max_delay))


def print_new_line():
    print("")


def render_as_markdown(text):
    # Try to display image if terminal is kitty
    if os.getenv("TERM") == "xterm-kitty":
        image_pattern = r"!\[.*?\]\((.*?)\)"
        images_paths = re.findall(image_pattern, text)

        # Render markdown without image links
        markdown_without_images = re.sub(image_pattern, "", text)
        markdown = Markdown(markdown_without_images)
        CliConsole.instance().print(markdown)

        # Display images
        for image in images_paths:
            if os.path.exists(f"{image}"):
                try:
                    subprocess.run(["kitty", "+kitten", "icat", f"{image}"], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Erreur when trying to display image : {image}: {e}")
            else:
                CliConsole.instance().print(f"[red]Image not found: {image}[/red]")
    else:
        markdown = Markdown(text)
        CliConsole.instance().print(markdown)
    return markdown


def print_record(heading: RecordHeadingMatch, body: str) -> None:
    """
    Display a record (heading + content) using rich text formatting.

    Args:
        heading (RecordMatch):
            The heading to display, including its metadata such as similarity score.
        body (str):
            The body of the record, formatted as a Markdown string.
    """
    print_new_line()
    print_rich_heading(heading)
    print_rich_separator()
    print_new_line()
    render_as_markdown(body)
    print_new_line()
    print_rich_separator()


def rich_print(text: str) -> None:
    """
    Displays a message to the user using the `rich` library.

    This function formats the message with a customizable text, providing
    a visually appealing interface for user output.
    """
    CliConsole.instance().print(text)


def rich_input_prompt(icon: str, text: str) -> str:
    """
    Displays a simple input prompt to the user using the `rich` library.

    This function formats the prompt with a customizable icon and text, providing
    a visually appealing interface for user input.

    Args:
        icon (str): The icon to display before the prompt text. The icon must be
            formatted using `rich`-compatible markup and should be a Unicode
            character. For example:
            `target_icon = f"[{Color.BLUE.value} bold]\uebf8[/{Color.BLUE.value} bold]"`.
        text (str): The text of the prompt displayed to the user.

    Returns:
        str: The input provided by the user.
    """
    input = Prompt.ask(f"{icon}  {text} ")
    return input


def rich_ask_prompt() -> str:
    """
    Prompts the user for his ask, allowing navigation through input history
    using the arrow keys.
    The history functionality relies on the `prompt_toolkit` library, as `rich`
    does not natively support this feature.  However, since the formatting and
    styling of `prompt_toolkit` are incompatible with `rich`, a custom
    `prompt_toolkit` styling is applied specifically for this prompt.

    Returns:
        str: The input provided by the user.

    Raises:
        Exception: If there is an issue accessing or creating the history file.
    """
    try:
        if not HISTORY_FILE.exists():
            HISTORY_FILE.touch()
        history = FileHistory(HISTORY_FILE)
        session: PromptSession = PromptSession(history=history)
    except Exception as e:
        print(f"Error with file : {HISTORY_FILE}: {e}")

    style = Style.from_dict(
        {
            "arrow": Color.BLUE.value,
            "text": "bold",
        }
    )
    arrow_icon = "<text>\uf0a9</text>"
    prompt_text = f"{arrow_icon}  <text>ask</text> : "
    user_input = session.prompt(HTML(prompt_text), style=style)
    return user_input
