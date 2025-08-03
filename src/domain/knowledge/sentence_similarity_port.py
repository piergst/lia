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

from abc import ABC, abstractmethod
from typing import Tuple


class SentenceSimilarityPort(ABC):
    """
    This port is an abstract base class that manages sentence similarity
    operations. It requires the use of a subprocess or detached service to
    handle the model (typically a Transformer-based model) to avoid long loading
    times during each call.

    Responsibilities:
        - Manages the lifecycle of the model by leveraging a subprocess to load
        and keep the model active, ensuring efficient runtime execution.
        - Provides methods to check if the process is running and to start or
        stop the process as needed.
    """

    @abstractmethod
    def rank_similarities(
        self, input_sentence: str, candidate_sentences: Tuple[str, ...], top_n: int
    ) -> Tuple[Tuple[int, float], ...]:
        """
        Find the best matching sentences by similarity between an input sentence
        and a pool of candidate sentences.

        Args:
            input_sentence (str): The input sentence to evaluate.
            candidate_sentences (Tuple[str, ...]): A tuple containing candidate
                sentences to compare with the input sentence.
            top_n (int): The number of top matches to return. For example, 3 to
                return the top 3 matches, 10 for the top 10.

        Returns:
            Tuple[Tuple[int, float], ...]: A tuple containing up to `top_n`
                similar results as an inner tuple ordered by highest similarity
                score and containing:
                    - index (int): The index of the matching sentence in `candidate_sentences`.
                    - score (float): The similarity score of the matching sentence with the input sentence.
        """
        pass

    @abstractmethod
    def start(self) -> None:
        """
        Since sentence similarity likely depends on an underlying model, a start
        method is provided to manage the service responsible for owning and
        loading the model, particularly to control when the model is loaded at
        runtime.
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """
        The stop method is primarily useful for testing purposes and has no
        significant practical application otherwise.
        """
        pass

    @abstractmethod
    def is_running(self) -> bool:
        """
        Verify whether the process owning the model is already running.

        This check helps prevent unnecessary start requests if the process is
        already active.

        Returns:
            bool: True if the process is running, False otherwise.
        """

        pass
