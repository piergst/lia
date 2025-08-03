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
import socket

import psutil
import pytest

from src.environment import SOCKET_PATH
from src.infra.knowledge.sentence_similarity.daemon_process_handler import DeamonProcessHandler


def test_daemon_socket_start_and_stop() -> None:
    # Arrange
    daemon_process_handler = DeamonProcessHandler()

    # Act
    try:
        daemon_process_handler.start_daemon()
        # Check daemon starts only once
        daemon_process_handler.start_daemon()

        # Assert
        assert daemon_process_handler.daemon_pid != 0, f"Daemon PID is null : PID = {daemon_process_handler.daemon_pid}"
        assert os.path.exists(SOCKET_PATH), f"Socket path {SOCKET_PATH} does not exist."

        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                sock.connect(str(SOCKET_PATH))
        except Exception as e:
            assert False, f"Error occured when connecting to daemon socket : {e}"
    except Exception as e:
        assert False, f"Error occured when starting daemon : {e}"

    # Act
    try:
        daemon_process_handler.stop_daemon()
        # Check behavior on multiple stop call
        daemon_process_handler.stop_daemon()

        # Assert
        assert daemon_process_handler.daemon_pid == 0, (
            f"Daemon PID is not null : PID = {daemon_process_handler.daemon_pid}"
        )
        assert not os.path.exists(SOCKET_PATH), f"Socket path {SOCKET_PATH} does not exist."
    except Exception as e:
        assert False, f"Error occured when stopping daemon : {e}"


def test_daemon_kill_on_terminate_fail(mocker):
    # Arrange
    # mock terminate() function to disable it and be sure that if terminate
    # fails then kill() is properly executed
    mock_terminate = mocker.patch("psutil.Process.terminate")
    mock_terminate.side_effect = None
    mock_wait = mocker.patch("psutil.Process.wait")
    mock_wait.side_effect = psutil.TimeoutExpired(0)

    # Act
    daemon_process_handler = DeamonProcessHandler()
    daemon_process_handler.start_daemon()
    daemon_process_handler.stop_daemon()

    # Assert
    assert daemon_process_handler.daemon_pid == 0, f"Daemon PID is not null : PID = {daemon_process_handler.daemon_pid}"
    assert not os.path.exists(SOCKET_PATH), f"Socket path {SOCKET_PATH} does not exist."


def test_daemon_proc_no_such_proc(mocker):
    """
    This test simulates a case where a process searched by DeamonProcessHandler does
    not exist or is inaccessible by manipulating the behavior of psutil.process_iter
    and the objects it returns. It validates that the start_daemon method handles
    this situation correctly by raising a psutil.NoSuchProcess exception
    """
    # Arrange
    mock_process_iter = mocker.patch("psutil.process_iter", autospec=True)
    mock_proc = mocker.Mock()
    mock_proc.info = mocker.MagicMock()
    mock_proc.info.__getitem__.side_effect = psutil.NoSuchProcess(1)
    mock_process_iter.return_value = iter([mock_proc])

    # Act & Assert
    daemon_process_handler = DeamonProcessHandler()
    with pytest.raises(psutil.NoSuchProcess):
        daemon_process_handler.start_daemon()


def test_daemon_proc_access_denied(mocker):
    """
    This test simulates a case where access to a process's information is denied
    while DeamonProcessHandler is searching for a specific process. By manipulating
    the behavior of psutil.process_iter and the objects it returns, it ensures that
    the start_daemon method correctly raises a psutil.AccessDenied exception in such
    scenarios.
    """
    # Arrange
    mock_process_iter = mocker.patch("psutil.process_iter", autospec=True)
    mock_proc = mocker.Mock()
    mock_proc.info = mocker.MagicMock()
    mock_proc.info.__getitem__.side_effect = psutil.AccessDenied(1)
    mock_process_iter.return_value = iter([mock_proc])
    daemon_process_handler = DeamonProcessHandler()

    # Act & Assert
    with pytest.raises(psutil.AccessDenied):
        daemon_process_handler.start_daemon()


def test_daemon_proc_zombie(mocker):
    """
    This test simulates a case where a process searched by DeamonProcessHandler is
    in a zombie state, making its information inaccessible. By manipulating the
    behavior of psutil.process_iter and the objects it returns, it validates that
    the start_daemon method properly raises a psutil.ZombieProcess exception in this
    situation.
    """
    # Arrange
    mock_process_iter = mocker.patch("psutil.process_iter", autospec=True)
    mock_proc = mocker.Mock()
    mock_proc.info = mocker.MagicMock()
    mock_proc.info.__getitem__.side_effect = psutil.ZombieProcess(1)
    mock_process_iter.return_value = iter([mock_proc])
    daemon_process_handler = DeamonProcessHandler()

    # Act & Assert
    with pytest.raises(psutil.ZombieProcess):
        daemon_process_handler.start_daemon()
