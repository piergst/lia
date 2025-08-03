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

from __future__ import annotations

from pickle import dumps, loads
from socket import AF_UNIX, SOCK_STREAM, error, socket
from typing import Any, Optional

from src.environment import SOCKET_PATH


class BaseSocket:
    """
    A base class to manage communication with a Transformer model via Unix
    sockets.

    This class provides core functionalities to send and receive serialized data
    over a socket connection. It serves as the foundation for both client and server
    socket implementations.
    """

    def __init__(self) -> None:
        self._sock: Optional[socket] = None

    @property
    def sock(self) -> Optional[socket]:
        return self._sock

    @classmethod
    def from_socket(cls, sock: socket) -> BaseSocket:
        """
        Create an instance of the class using an existing socket base object
        (socket.socket).

        Args:
            sock (socket): An already connected socket instance.

        Returns:
            TransformerModelSocketBridge: An instance of the class with the provided socket.
        """
        instance = cls()
        instance._sock = sock
        return instance

    def send(self, data) -> None:
        """
        This method serializes the data using pickle, prefixes it with its size,
        and sends it over the socket connection.

        Args:
            data: The data to be sent.

        Raises:
            ConnectionError: If the socket is not connected.
            RuntimeError: If an error occurs during data transmission.
        """

        if not self._sock:
            raise ConnectionError("Socket is not connected.")
        try:
            serialized_data = dumps(data)
            data_size = len(serialized_data)
            self._sock.sendall(data_size.to_bytes(4, "big"))
            self._sock.sendall(serialized_data)
        except Exception as e:
            raise RuntimeError(f"Socket - Error while sending : {e}")

    def receive(self) -> Any:
        """
        This method reads the size of the incoming data, retrieves the data in
        chunks, deserializes it, and returns the original object.

        Returns:
            Any: The deserialized data received from the socket.

        Raises:
            ConnectionError: If the socket is not connected.
            RuntimeError: If an error occurs during data reception.
        """
        if not self._sock:
            raise ConnectionError("Socket is not connected.")
        try:
            # Get response size
            data_size_bytes: bytes = self._sock.recv(4)
            if len(data_size_bytes) != 4:
                raise RuntimeError("Socket - Failed to receive the data size")
            data_size = int.from_bytes(data_size_bytes, "big")

            # Get raw response
            chunks: list[bytes] = []
            bytes_received_count = 0
            while bytes_received_count < data_size:
                chunk = self._sock.recv(min(4096, data_size - bytes_received_count))
                if not chunk:
                    raise RuntimeError("Socket - Socket connection closed unexpectedly")
                chunks.append(chunk)
                bytes_received_count += len(chunk)
            data = b"".join(chunks)

            # Unserialize and return the corresponding object
            return loads(data)
        except Exception as e:
            raise RuntimeError(f"Socket - Failed to receive : {e}")

    def destroy(self) -> None:
        try:
            if self._sock:
                self._sock.close()
                self._sock = None
        except error as e:
            print(f"Error closing the socket: {e}")


class ClientSocket(BaseSocket):
    """
    A client socket implementation for connecting to the Transformer model
    server.

    This class establishes a Unix socket connection with the server and provides
    context manager support for automatic connection and cleanup.
    """

    def __init__(self):
        super().__init__()

    def __enter__(self):
        try:
            self._sock = socket(AF_UNIX, SOCK_STREAM)
            self._sock.connect(str(SOCKET_PATH))
        except Exception as e:
            print(f"Error connecting to socket: {e}")
            self._sock = None
        return self

    def __exit__(self, exception_type, exception_value, traceback_info):
        self.destroy()


class ServerSocket(BaseSocket):
    """
    A server socket implementation for handling client connections to the
    Transformer model.

    This class creates and manages a Unix socket for listening to and accepting
    client connections.
    """

    def __init__(self):
        super().__init__()

    def init(self):
        try:
            self._sock = socket(AF_UNIX, SOCK_STREAM)
            self._sock.bind(str(SOCKET_PATH))
            self._sock.listen(1)
        except Exception as e:
            print(f"Error connecting to socket: {e}")
            self._sock = None

    def accept(self):
        if self._sock:
            socket, addr = self._sock.accept()
            return socket
        return None
