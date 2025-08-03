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

import importlib.metadata
from enum import Enum

VERSION = importlib.metadata.version("lia")

MAX_RECORDS_PER_REVIEW_GROUP: int = 7

TOP_N_RESULTS = 3


class Color(Enum):
    GREEN = "#8ce10b"
    LIGHT_GREEN = "#d1e231"
    YELLOW = "#ffb900"
    ORANGE = "#ff5c0f"
    RED = "#ff000f"
    BLUE = "#008df8"
    WHITE = "#ffffff"
    PURPLE = "#6d43a6"


class SimilarityScore(Enum):
    HIGH = (0.8, 1.0)
    MEDIUM = (0.6, 0.8)
    LOW = (0.0, 0.6)

    def lower_bound(self):
        return self.value[0]

    def upper_bound(self):
        return self.value[1]
