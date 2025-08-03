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

from os import getenv, makedirs
from pathlib import Path

"""
Module for environment variables and initialization. 

"""

DATA_PATH = Path(getenv("XDG_DATA_HOME", Path(Path.home(), ".local", "share")), "lia", "data")
CACHE_PATH = Path(getenv("XDG_CACHE_HOME", Path(Path.home(), ".cache")), "lia")
HISTORY_FILE = Path(CACHE_PATH, "history")
SOCKET_PATH = Path(CACHE_PATH, "lia.sock")
SQLITE_FILE = Path(CACHE_PATH, "review_db.sqlite")
LOG_FILE = Path(CACHE_PATH, "daemon.log")
MODEL_DL_FILE = Path(CACHE_PATH, ".model_dl")
MODEL_PATH = Path(Path(__file__).resolve().parent.parent, "paraphrase-multilingual-mpnet-base-v2")


def init_env() -> None:
    init_data_path()
    init_history_file()
    init_log_file()
    init_model_dl_file()
    # clear_log_file()


def init_data_path() -> None:
    makedirs(DATA_PATH, exist_ok=True)

    # Ensure "undefined.md" exists, as it is queried in all searches by default
    Path(DATA_PATH, "undefined.md").touch(exist_ok=True)


def init_history_file() -> None:
    makedirs(CACHE_PATH, exist_ok=True)
    if not HISTORY_FILE.exists():
        HISTORY_FILE.touch()


def init_log_file() -> None:
    if not LOG_FILE.exists():
        LOG_FILE.touch()


def init_model_dl_file() -> None:
    if not MODEL_DL_FILE.exists():
        MODEL_DL_FILE.touch()


def clear_log_file() -> None:
    if LOG_FILE.exists():
        LOG_FILE.unlink()
