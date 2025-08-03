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
from pathlib import Path
from typing import Set, Tuple


class TopicParser:
    """
    TopicParser provide a bunch of methods to detect and handle topics
    from a file dataset. A file dataset is basically a structure
    of folders and files. To be considerd as a topic a file just
    have to be named following this pattern : <topic-name.md>. Ex:
    "git.md" or "vscode-config.md"
    """

    def __init__(self, dataset_dir: Path):
        self.__dataset_dir: Path = dataset_dir
        self.__topics: Tuple[str, ...] = self.__fetch_topics_from_dataset(self.__dataset_dir)

    @property
    def topics(self) -> Tuple[str, ...]:
        return self.__topics

    def match(self, sentence: str) -> Set[str]:
        topic_matches: Set[str] = {topic for topic in self.__topics if topic.lower() in sentence.lower()}
        return topic_matches

    def topic_exists(self, topic: str) -> bool:
        return topic in self.topics

    def __fetch_topics_from_dataset(self, directory: Path) -> Tuple[str, ...]:
        topics: Set[str] = {
            os.path.splitext(file)[0] for root, dirs, files in os.walk(directory) for file in files if file.endswith(".md")
        }
        return tuple(sorted(topics))
