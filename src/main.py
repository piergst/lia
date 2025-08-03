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

import sys
from argparse import Namespace
from typing import Dict

from src.environment import init_env
from src.infra.cli.cli_apdapter import ask, review, show, do_list, stop
from src.infra.cli.cli_parse import parse_args

COMMANDS = {"ask": ask, "list": do_list, "show": show, "review": review, "stop": stop}


def execute_command(function, *args, **kwargs):
    """
    Provides flexible command handling by allowing the same function to invoke
    commands with or without arguments seamlessly.
    """
    if args and args[0]:
        return COMMANDS[function](*args, **kwargs)
    else:
        return COMMANDS[function]()


def get_arguments(args: Namespace) -> Dict:
    """
    The parse_args() function returns an object with commands and arguments as
    attributes. This method converts those attributes into a dictionary,
    excluding the "command" key, as its purpose is to extract arguments only.
    For example, it might return {"topic_name": "bash"}, where
    "topic_name" is an argument for the "show" command. Refer to parse_args()
    for more details.
    """
    return {key: value for key, value in vars(args).items() if key != "command"}


def main():
    try:
        init_env()
        prog_args = parse_args(sys.argv[1:])
        cmd = prog_args.command
        cmd_args = get_arguments(prog_args)
        execute_command(cmd, cmd_args)
    except KeyboardInterrupt:
        print("Interrupted by user.")
    except Exception as e:
        print(f"Error : {e}")


if __name__ == "__main__":
    main()
