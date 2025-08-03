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

import socket

import pytest

from src.infra.knowledge.sentence_similarity.sockets import ClientSocket


def test_should_raise_error_if_socket_is_not_connected(mocker) -> None:
    with pytest.raises(ConnectionError, match="Socket is not connected."):
        with ClientSocket() as socket:
            socket.send("Request on closed socket")


def test_should_raise_error_if_data_size_is_incomplete(mocker):
    # Mock socket receive less than 4 bytes for response size
    mock_socket = mocker.MagicMock(spec=socket.socket)
    mock_socket.recv.side_effect = [b"\x00\x01"]

    with pytest.raises(RuntimeError, match="Socket - Failed to receive the data size"):
        ClientSocket.from_socket(mock_socket).receive()


def test_should_raise_error_when_connection_close_while_receiving(mocker):
    # Mock a correct first 4 bytes response indicating an 8 bytes following
    # response, then a connection close error with a truncated answer shorter
    # than expected 8 bytes.
    # mock_socket = mocker.patch('socket.socket')
    # mock_instance = mock_socket.return_value
    mock_socket = mocker.MagicMock(spec=socket.socket)
    mock_socket.recv.side_effect = [b"\x00\x00\x00\x08", b"\x01\x02\x03", b""]

    with pytest.raises(RuntimeError, match="Socket - Socket connection closed unexpectedly"):
        ClientSocket.from_socket(mock_socket).receive()
