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

from rich.console import Console


class CliConsole:
    """
    Singleton class to ensure only one instance of Console is created.
    Useful when multiple parts of the application need access to the same
    Console object without passing it explicitly.
    """

    __instance = None

    @staticmethod
    def instance():
        if CliConsole.__instance is None:
            CliConsole.__instance = Console()
        return CliConsole.__instance
