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

import argparse
from typing import Sequence

from src.config import VERSION


def parse_args(args: Sequence[str]) -> argparse.Namespace:
    """
    Defines the commands and options available for the CLI and sets up argument
    parsing to enable the conversion of the program's argument list into
    well-defined options and commands whenever possible.

    The "--help" or "-h" option is automatically provided by argparse.
    Args:
        args (Sequence[str]): Command-line arguments to parse.

    Returns:
        argparse.Namespace: Contains the parsed options and arguments.
    """
    parser = argparse.ArgumentParser(
        usage="\t%(prog)s (with no arg to ask something)\n"
          "\t%(prog)s [-h | --help] [-v | --version] [list | show | review <arg> | stop]"
    )
    parser.add_argument("-v", "--version", action="version", version="%(prog)s {}".format(VERSION))

    # Allows users to invoke specific actions by defining subcommands. The
    # selected subcommands are stored in the 'command' attribute of a
    # argparse.Namespace object, which is later used to identify the desired
    # command.

    subparsers = parser.add_subparsers(
        dest="command", title="Available commands (lia <command> -h to get specific help)", metavar=""
    )

    # "lia list" command
    parser_list = subparsers.add_parser(
        "list",
        help="list topics or review groups",
        usage="lia list [-h | --help] <[-t | --topics <topics>] | [-r | --review-groups]>",
    )
    parser_list_group = parser_list.add_mutually_exclusive_group(required=True)
    parser_list_group.add_argument("-t", "--topics", action="store_true", help="List available topics")
    parser_list_group.add_argument(
        "-r", "--review-groups", action="store_true", help="List available review groups (ordered by review priority)"
    )

    # "lia show" command
    parser_show = subparsers.add_parser(
        "show", help="Show content of a specific topic", usage="lia show [-h | --help] <topic_name>"
    )
    parser_show._positionals.title = "Required argument"
    parser_show.add_argument("topic_name", type=str, help="name of the topic to display content of")

    # "lia review" command
    parser_review = subparsers.add_parser("review", help="Review a topic", usage="lia review [-h | --help] <topic_name>")
    parser_review._positionals.title = "Required argument"
    parser_review.add_argument("topic_name", type=str, help="name of the topic to review")

    # "lia stop" command
    subparsers.add_parser(
        "stop",
        help="Stop the sentence similarity engine daemon",
        usage="lia stop [-h | --help]"
    )

    # Invoking the program without arguments should default to the "ask"
    # command, which represents the program's primary functionality
    if args:
        parsed_args = parser.parse_args(args)
    else:
        parsed_args = argparse.Namespace(command="ask")
    return parsed_args
