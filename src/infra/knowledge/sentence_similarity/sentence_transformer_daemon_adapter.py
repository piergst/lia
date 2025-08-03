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

from typing import Tuple

from src.domain.knowledge.sentence_similarity_port import SentenceSimilarityPort
from src.infra.knowledge.sentence_similarity.daemon_process_handler import DeamonProcessHandler
from src.infra.knowledge.sentence_similarity.sockets import ClientSocket


class SentenceTransformerDaemonAdapter(SentenceSimilarityPort):
    """
    Implementation of the sentence similarity interface in the context
    of using a local sentence transformer model to evaluate semantic similarity.
    This implementation uses a Unix socket daemon to communicate with the
    model for evaluating sentence similarity.
    The design choice to employ a daemon process was made to avoid reloading
    the model with each user interaction (in a cli context), which would otherwise
    significantly impact performance and make the application unusable.
    By using a persistent background process, the model remains loaded in memory,
    allowing for rapid and efficient similarity evaluations.
    """

    def __init__(self):
        self.__daemon_process_handler = DeamonProcessHandler()

    def start(self) -> None:
        self.__daemon_process_handler.start_daemon()

    def rank_similarities(
        self, input_sentence: str, candidate_sentences: Tuple[str, ...], top_n: int
    ) -> Tuple[Tuple[int, float], ...]:
        with ClientSocket() as socket:
            socket.send((input_sentence, candidate_sentences, top_n))
            return socket.receive()

    def stop(self) -> None:
        if self.__daemon_process_handler.retrieve_daemon():
            self.__daemon_process_handler.stop_daemon()
        else:
            self.__daemon_process_handler.clear_socket_file()

    def is_running(self) -> bool:
        return self.__daemon_process_handler.is_daemon_running()
