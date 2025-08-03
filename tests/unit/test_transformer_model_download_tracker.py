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

from pathlib import Path

from src.infra.knowledge.sentence_similarity.transformer_model_download_tracker import TransformerModelDownloadTracker

TESTS_DIR: Path = Path(__file__).resolve().parent.parent
MODEL_DL_PATH = Path(TESTS_DIR, "tests_data", "mock_model_dl")


def test_percent_after_resume():
    model_dl_watcher = TransformerModelDownloadTracker(MODEL_DL_PATH)
    model_dl_watcher.resume()
    assert model_dl_watcher.download_status() == 14
