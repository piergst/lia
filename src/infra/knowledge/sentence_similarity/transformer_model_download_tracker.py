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

import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from threading import Thread
from typing import Optional, Tuple

from src.environment import MODEL_DL_FILE


class TransformerModelDownloadTracker:
    """
    Watches the download progress of the transformer model by monitoring a log file.
    The tracker runs in a background thread and tracks the download status of
    specific model files, based on log entries.
    """

    model_files = {
        "modules.json",
        "config_sentence_transformers.json",
        "README.md",
        "sentence_bert_config.json",
        "config.json",
        "model.safetensors",
        "tokenizer_config.json",
        "sentencepiece.bpe.model",
        "tokenizer.json",
        "special_tokens_map.json",
    }

    # Only these files are tracked in detail during the download process,
    # because not all files provide real-time download progress logs
    tracked_files = {
        "modules.json",
        "config_sentence_transformers.json",
        "sentence_bert_config.json",
        "config.json",
        "model.safetensors",
        "tokenizer_config.json",
        "sentencepiece.bpe.model",
        "special_tokens_map.json",
    }

    def __init__(self, model_dl_log_file_path: Path = MODEL_DL_FILE ) -> None:
        """
        Initializes the watcher and starts the background thread to monitor the download log file.
        """
        self.model_dl_file: Path = model_dl_log_file_path
        self.files_dl_status: dict = {}
        self._dl_watcher_running: bool = False
        self._timeout_start_time: Optional[datetime] = None
        self._thread: Thread = threading.Thread(target=self._monitor, daemon=True)
        self._thread.start()

    def is_running(self) -> bool:
        """
        Returns whether the download watcher is currently running.
        """
        return self._dl_watcher_running

    def resume(self) -> None:
        """
        Resumes the download tracking by parsing the current content of the log file.
        """
        with open(self.model_dl_file, "r", encoding="utf-8") as f:
            for line in f:
                line_data = self._get_line_data(line)
                self.files_dl_status[line_data[0]] = line_data[1]

    def _monitor(self) -> None:
        """
        Monitors the download log file in real time to update the download status of tracked files.
        Terminates when a timeout occurs (no update within 10 seconds) or when all tracked files are downloaded.
        """
        self._dl_watcher_running = True
        timeout = timedelta(seconds=30)

        while self._dl_watcher_running:
            try:
                with open(self.model_dl_file, "r", encoding="utf-8") as f:
                    f.seek(0, 2)  # Seek to the end of the file to follow new lines

                    while self._dl_watcher_running:
                        line = f.readline()

                        if line:
                            line_data = self._get_line_data(line)
                            self.files_dl_status[line_data[0]] = line_data[1]
                            self._timeout_start_time = None  # Reset timeout on new data

                        elif self._timeout_start_time is None:
                            # No new data; start timeout countdown
                            self._timeout_start_time = datetime.now()
                        else:
                            time.sleep(0.1)

                        if self._timeout_start_time is not None:
                            if (datetime.now() - self._timeout_start_time) > timeout:
                                # Stop watcher after timeout
                                self._dl_watcher_running = False

                        if self.is_download_complete():
                            self._dl_watcher_running = False

            except FileNotFoundError:
                # If the file doesn't exist yet, wait and retry
                time.sleep(0.5)

    def _get_line_data(self, line) -> Tuple[str, dict]:
        """
        Parses a line from the download log and extracts the filename and its download status.

        Expected line format:
            - modules.json: 100% 229/229 [00:00<00:00, 969kB/s]
            - model.safetensors:   2% 21.0M/1.11G [00:03<03:19, 5.47MB/s]

        Returns:
            A tuple containing:
                - filename (str)
                - a dict with 'percent', 'downloaded', and 'total' keys, or empty values if the line is invalid.
        """
        if ":" not in line:
            return ("", {})

        parts = line.split(":", 1)
        if len(parts) < 2:
            return ("", {})

        filename = parts[0].strip()
        if filename not in self.tracked_files:
            return ("", {})

        rest = parts[1].strip()
        tokens = rest.split(" ")
        if len(tokens) < 2:
            return ("", {})

        percent_token = tokens[0]
        size_token = tokens[1]

        if not percent_token.endswith("%"):
            return ("", {})

        try:
            percent = int(percent_token.replace("%", ""))
            downloaded, total = size_token.split("/")
        except (ValueError, IndexError):
            return ("", {})

        return (filename, {"percent": percent, "downloaded": downloaded, "total": total})

    def is_download_complete(self) -> bool:
        """
        Checks whether all tracked files have reached 100% download progress.

        Returns:
            True if all files are fully downloaded, False otherwise.
        """
        for filename in self.tracked_files:
            data = self.files_dl_status.get(filename)
            if not data or data["percent"] < 100:
                return False
        return True

    def download_status(self) -> int:
        """
        Returns the global download progress percentage.

        Since 'model.safetensors' represents ~99.9% of the total model size,
        its progress is used as a proxy for the entire download status.

        Returns:
            An integer representing the percent of download completed (0-100).
        """
        if not self.tracked_files:
            return 0
        return self.files_dl_status.get("model.safetensors", {}).get("percent", 0)

    def stop(self) -> None:
        """
        Stops the download watcher thread gracefully.
        """
        self._dl_watcher_running = False
        if self._thread.is_alive():
            self._thread.join(timeout=1)
