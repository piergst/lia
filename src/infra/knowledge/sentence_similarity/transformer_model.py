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

from typing import List, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer, util


class TransformerModel:
    """
    A class to compute and rank sentence similarities using a Transformer-based model.

    This class leverages the SentenceTransformer library to encode sentences into embeddings
    and calculate cosine similarities between them. It provides functionality to rank candidate
    sentences based on their similarity to an input sentence.
    The model used is "paraphrase-multilingual-mpnet-base-v2", suitable for multilingual sentence
    similarity tasks.

    Attributes:
        __model (SentenceTransformer): A pre-trained Transformer model for sentence similarity evaluation.
    """

    def __init__(self):
        self.__model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")
        # self.__model = SentenceTransformer("/home/pierre/Repitories/lia/paraphrase-multilingual-mpnet-base-v2")
        # self.__model.save("/home/pierre/Repositories/lia/lia/paraphrase-multilingual-mpnet-base-v2")
        # self.__model = SentenceTransformer(str(MODEL_PATH))

    def rank_similarities(
        self, input_sentence: str, candidate_sentences: Tuple[str, ...], top_n: int
    ) -> Tuple[Tuple[int, float], ...]:
        """
        Computes the similarities between an input sentence and a list of candidate sentences,
        and ranks the candidates by similarity.

        Args:
            input_sentence (str): The sentence for which to calculate similarities.
            candidate_sentences (Tuple[str, ...]): A tuple of candidate sentences to compare against.
            top_n (int): The number of top results to return.

        Returns:
            Tuple[Tuple[int, float], ...]: A tuple containing the top_n most similar sentences
                as tuples of (index, similarity_score), sorted in descending order of similarity.

        Raises:
            RuntimeError: If there is an issue during similarity computation.

        Example:
            ```
            input_sentence = "How are you?"
            candidates = ("Hello there!", "How is it going?", "Goodbye.")
            print(model.rank_similarities(input_sentence, candidates, top_n=2))
            ((1, 0.894233), (0, 0.765432))
            ```
        """
        try:
            # Compute embeddings for the input sentence and candidate sentences
            embeddings = self.__model.encode([input_sentence] + list(candidate_sentences))
            # embeddings = self.__model.encode([input_sentence.lower()] + [s.lower() for s in candidate_sentences])

            # Compute cosine similarities between the input sentence embedding and candidate embeddings
            similarities = util.pytorch_cos_sim(embeddings[0], embeddings[1:])

            # Convert the similarities tensor to a list for easier sorting
            # Use np.atleast_1d to ensure that the result is always a list, even if similarities.squeeze()
            # returns a scalar (e.g., when there is only one candidate sentence).
            similarities_list: List[float] = np.atleast_1d(similarities.squeeze()).tolist()

            # Sort the similarities in descending order while keeping track of original indices
            ranking: List[Tuple[int, float]] = sorted(enumerate(similarities_list), key=lambda x: x[1], reverse=True)

            # Return the top_n similarities along with their indices, rounding the scores to 6 decimal places
            return tuple((index, round(rank, 6)) for index, rank in ranking[:top_n])

        except Exception as e:
            raise RuntimeError(f"LiaModel - Failing to get a result from model: {type(e).__name__}: {e}")


if __name__ == "__main__":
    model = TransformerModel()
