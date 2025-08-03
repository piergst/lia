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

import time

starting_time = time.time()

def print_elapsed_time(stage:str):
    elapsed_seconds = time.time() - starting_time 
    if elapsed_seconds < 1:
        elapsed_milliseconds = elapsed_seconds * 1000
        print(f"Temps écoulé ({stage}): {elapsed_milliseconds:.2f} millisecondes")
    else:
        print(f"Temps écoulé ({stage}): {elapsed_seconds:.2f} secondes")