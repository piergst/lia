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

import errno
import os
import pty
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import psutil

from src.environment import LOG_FILE, MODEL_DL_FILE, SOCKET_PATH
from src.infra.knowledge.sentence_similarity.transformer_model_download_tracker import TransformerModelDownloadTracker

DAEMON_MODULE_NAME: str = "transformer_daemon.py"
DAEMON_MODULE_PATH: Path = Path(__file__).resolve().parent / DAEMON_MODULE_NAME


class DeamonProcessHandler:
    """
    Handle the management of the daemon process, including starting, stopping,
    and checking its status.
    This class interacts with a daemon process that communicates through a Unix
    socket.  It provides methods to start and stop the daemon, check if it's
    running, and manage socket files.
    """

    def __init__(self):
        self._daemon_pid = 0

    @property
    def daemon_pid(self):
        return self._daemon_pid

    def start_daemon(self) -> None:
        """
        Start the daemon process if it is not already running.

        This method attempts to start the daemon by invoking the corresponding
        Python script (transformer_daemon.py). It waits for the socket file to
        be created, indicating that the daemon has started successfully. Process
        will keep alive even if parent terminal is killed.
        """
        proc = self._get_daemon_process()
        if proc is None:
            self.clear_socket_file()

            # Disable Xet: its chunked/preallocated downloads can stall and break progress tracking.
            env = dict(os.environ)
            env.setdefault("HF_HUB_DISABLE_XET", "1")

            master_fd, slave_fd = pty.openpty()
            process = subprocess.Popen(
                [sys.executable, DAEMON_MODULE_PATH],
                stdout=slave_fd,
                stderr=slave_fd,
                preexec_fn=os.setsid,  # Detach process from parent
                env=env,
            )
            os.close(slave_fd)
            thread = threading.Thread(target=self._forward_output, args=(master_fd,), daemon=True)
            thread.start()

            start_timeout = 10.0
            while start_timeout > 0 and not os.path.exists(SOCKET_PATH):
                time.sleep(0.1)
                start_timeout -= 0.1
            self._daemon_pid = process.pid
            # print(f"Daemon started with PID: {process.pid}.")
        else:
            self._daemon_pid = proc.pid

    def stop_daemon(self):
        """
        Stop the running daemon process if it is currently active.

        This method attempts to terminate the daemon process by using its PID.
        If the process does not respond within a specified timeout, it is
        forcefully killed.
        """
        if self.daemon_pid != 0:
            proc = psutil.Process(self._daemon_pid)
            if proc:
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                    print(f"Daemon process (PID {proc.pid}) stopped.")
                except psutil.TimeoutExpired:
                    proc.kill()
                    print(f"Daemon process (PID {proc.pid}) forcibly killed.")
                self._daemon_pid = 0
                self.clear_socket_file()
        else:
            print("No running daemon to stop.")

    def is_daemon_running(self) -> bool:
        return self._get_daemon_process() is not None

    def retrieve_daemon(self) -> bool:
        proc = self._get_daemon_process()
        if proc is not None:
            self._daemon_pid = proc.pid
            return True
        return False

    def clear_socket_file(self) -> None:
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)

    def _forward_output(self, master_fd):
        """
        Read and forward the output from a pseudo-terminal master file descriptor.

        This method continuously reads lines from the given `master_fd`, which is the
        master side of a pseudo-terminal (pty), and writes them to two different log files
        depending on their content:

        - If a line contains any of the filenames listed in
        `TransformerModelDownloadWatcher.expected_files`, it is written to
        `MODEL_DL_FILE`.
        - Otherwise, it is written to `LOG_FILE`.

        Each line is flushed immediately after writing to ensure real-time logging.

        A pseudo-terminal is used instead of a standard pipe to ensure that the subprocess
        produces unbuffered, line-by-line output. Many command-line tools detect when they
        are not connected to a terminal and switch to block buffering, which delays output.
        Using a `pty` tricks the subprocess into thinking it's interacting with a real
        terminal, allowing this function to capture the output as it is generated.

        Args:
            master_fd (int): File descriptor of the master side of the pseudo-terminal.

        Raises:
            OSError: Re-raised if the error is not due to a normal end-of-input
                    (e.g. not `errno.EIO` on POSIX systems).
        """

        try:
            with (
                os.fdopen(master_fd, "r", encoding="utf-8", errors="replace") as stdout,
                open(LOG_FILE, "a", encoding="utf-8") as logfile,
                open(MODEL_DL_FILE, "a", encoding="utf-8") as model_dl_file,
            ):
                for line in stdout:
                    if line.split(":", 1)[0] in TransformerModelDownloadTracker.model_files:
                        model_dl_file.write(line)
                        model_dl_file.flush()
                    else:
                        clean_line = line.strip()
                        if clean_line:
                            logfile.write(f"[{datetime.now().isoformat()}] {clean_line}\n")
                            logfile.flush()
        except OSError as e:
            if e.errno != errno.EIO:
                raise

    def _get_daemon_process(self) -> Optional[psutil.Process]:
        """
        Retrieve the daemon process if it is currently running.

        This method checks the list of running processes to find the one
        associated with the daemon by matching names with the known name of the
        daemon module.

        Returns:
            Optional[psutil.Process]: The process object representing the running daemon, or None
            if the daemon is not found.
        """
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                if proc.info["cmdline"] is not None and any(DAEMON_MODULE_NAME in s for s in proc.info["cmdline"]):
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                raise
        return None
