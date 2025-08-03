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

from src.infra.knowledge.sentence_similarity.sockets import (
    BaseSocket,
    ServerSocket,
)
from src.infra.knowledge.sentence_similarity.transformer_model import TransformerModel


class TransformerDaemon:
    """
    Daemon process for serving a Transformer model over a Unix socket.

    This class is responsible for initializing the transformer model, setting up
    the server socket, accepting incoming connections, processing the requests,
    and sending the responses back to the clients.
    """

    def __init__(self):
        self.__socket = None
        self.__sentence_transformer = None

    def start(self) -> None:
        try:
            self.__socket = ServerSocket()
            self.__socket.init()
            self.__load_transformer_model()
        except Exception as e:
            raise RuntimeError(f"Daemon - Error while starting: {e}")

    def listen(self) -> None:
        while True:
            socket = BaseSocket.from_socket(self.__socket.accept())
            try:
                data = socket.receive()
                self.__process_data_and_respond(data, socket)
            except Exception as e:
                socket.send(f"Daemon - Communication error: {e}")
                raise RuntimeError(f"Daemon - Communication error: {e}")
            finally:
                socket.destroy()

    def __process_data_and_respond(self, data, socket) -> None:
        if data:
            try:
                sentence, sentence_candidates, top_n = data
                answer: Tuple[Tuple[int, float], ...] = self.__sentence_transformer.rank_similarities(
                    sentence, sentence_candidates, top_n
                )
                socket.send(answer)
            except Exception as e:
                raise RuntimeError(f"Daemon - Error while processing request or sending response: {e}")

    def __load_transformer_model(self) -> None:
        if self.__sentence_transformer is None:
            try:
                self.__sentence_transformer = TransformerModel()
            except Exception as e:
                raise RuntimeError(f"Daemon - Error while loading model: {e}")


if __name__ == "__main__":
    try:
        daemon = TransformerDaemon()
        daemon.start()
        daemon.listen()
    except Exception as e:
        print(f"Daemon - Error at runtime: {e}")
