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

from time import sleep
from typing import Optional

from src.config import Color
from src.domain.knowledge.knowledge_provider import KnowledgeProvider
from src.environment import DATA_PATH
from src.infra.cli.cli_console import CliConsole
from src.infra.knowledge.file.file_persistence_adapter import FilePersistenceAdapter
from src.infra.knowledge.sentence_similarity.sentence_transformer_daemon_adapter import SentenceTransformerDaemonAdapter
from src.infra.knowledge.sentence_similarity.transformer_model_download_tracker import TransformerModelDownloadTracker


class CliKnowledgeProviderManager:
    """
    Singleton class to manage the CLI instance of `KnowledgeProvider`.

    This class ensures that the KnowledgeProvider and its dependencies (such as
    the sentence similarity engine) are instantiated and initialized only once
    in a CLI context. It also handles the logic to start the sentence transformer
    engine and track its model download progress if required.
    """

    __instance: Optional[KnowledgeProvider] = None

    @staticmethod
    def instance() -> KnowledgeProvider:
        """
        Returns a singleton instance of the KnowledgeProvider.

        If the instance is not yet initialized, this method will:
        - Initialize the file persistence layer.
        - Initialize the sentence similarity engine.
        - Start the engine if it's not already running.
        - Monitor and track the transformer model download progress if needed.
        - Raise an error if the model download fails or is interrupted.

        Returns:
            KnowledgeProvider: A fully initialized and ready-to-use knowledge provider.
        """
        if CliKnowledgeProviderManager.__instance is None:
            persistence = FilePersistenceAdapter(DATA_PATH)
            sentence_similarity_engine = SentenceTransformerDaemonAdapter()
            console = CliConsole.instance()

            # Start the sentence similarity engine if not running
            if not sentence_similarity_engine.is_running():
                with console.status("[bold]Loading model", spinner="point", spinner_style=f"{Color.BLUE.value}") as status:
                    sentence_similarity_engine.start()

                    model_dl_watcher = TransformerModelDownloadTracker()
                    model_dl_watcher.resume()

                    # Monitor download progress if the model is not fully available yet
                    if not model_dl_watcher.is_download_complete():
                        try:
                            status.update("[bold]Downloading model : 0%")
                            while not model_dl_watcher.is_download_complete() and model_dl_watcher.is_running():
                                percent = model_dl_watcher.download_status()
                                status.update(f"[bold]Downloading model : {percent}%")
                                sleep(0.1)

                        except KeyboardInterrupt:
                            # Clean shutdown on user interrupt
                            sentence_similarity_engine.stop()
                            raise

                        finally:
                            model_dl_watcher.stop()

                            # If the download is incomplete, stop the sentence similarity engine
                            # to ensure proper cleanup and prevent it from running with a partial model
                            if not model_dl_watcher.is_download_complete():
                                sentence_similarity_engine.stop()
                                raise RuntimeError("Model download failed, check your internet connection.")

            # Instantiate the knowledge provider once all dependencies are ready
            CliKnowledgeProviderManager.__instance = KnowledgeProvider(persistence, sentence_similarity_engine)

        return CliKnowledgeProviderManager.__instance

    @staticmethod
    def stop_similarity_engine() -> None:
        """
        Stops the running sentence similarity engine instance.
        This is useful to release resources cleanly when needed.
        """
        sentence_similarity_engine = SentenceTransformerDaemonAdapter()
        sentence_similarity_engine.stop()
