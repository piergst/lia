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

import re
from typing import Optional, Set, Tuple

from src.config import TOP_N_RESULTS, SimilarityScore
from src.domain.knowledge.knowledge_data_objects import KnowledgeRecord, RecordHeading, RecordHeadingMatch
from src.domain.knowledge.knowledge_persistence_port import KnowledgePersistencePort
from src.domain.knowledge.knowledge_provider_port import KnowledgeProviderPort
from src.domain.knowledge.sentence_similarity_port import SentenceSimilarityPort


class KnowledgeProvider(KnowledgeProviderPort):
    """
    Provides an implementation of the core domain interface for interacting with
    a knowledge base.

    It encapsulates the logic required to manage and retrieve knowledge stored
    in a persistence layer. It also integrates functionality for sentence
    similarity evaluation, enabling advanced querying capabilities.

    Args:
            persistence (KnowledgePersistencePort): The persistence layer responsible for
                    storing and retrieving data.
            sentence_similarity_checker (SentenceSimilarityPort, optional): A
                    component used to assess the similarity between sentences, enabling
                    more contextual or fuzzy matching in queries.
    """

    def __init__(
        self, persistence: KnowledgePersistencePort, sentence_similarity_checker: Optional[SentenceSimilarityPort] = None
    ):
        self.persistence = persistence
        self.sentence_similarity_checker = sentence_similarity_checker

    def get_topics_list(self) -> Tuple[str, ...]:
        return self.persistence.get_topic_list()

    def get_available_records_headings_for_topic(self, topic_name: str) -> Tuple[RecordHeading, ...]:
        return tuple(
            (record_heading)
            for record_heading in sorted(
                self.persistence.get_referenced_headings_list_for_topic(topic_name), key=lambda x: x.text
            )
        )

    def ask(self, user_input: str) -> Tuple[Tuple[RecordHeadingMatch, ...], str]:
        if self.sentence_similarity_checker is None:
            raise ValueError("Sentence similarity checker is required to use this method")

        # "undefined" topic search is forced for every query
        topics = self.__match_topics(user_input, self.get_topics_list(), True) + ("undefined",)

        headings = self.__get_topics_headings(topics)
        if not headings:
            return ((), "")

        headings_text = tuple(heading.text for heading in headings)

        max_matches_count = TOP_N_RESULTS
        top_n_similar_ranking = self.sentence_similarity_checker.rank_similarities(
            user_input, headings_text, max_matches_count
        )

        top_n_similar_headings: Tuple[RecordHeadingMatch, ...] = tuple(
            RecordHeadingMatch(record_heading=headings[index], similarity_indice=similarity_indice)
            for index, similarity_indice in top_n_similar_ranking
        )

        top_n_similar_headings = self.__purge_headings_from_a_same_record(top_n_similar_headings)

        # A low score would indicate the match is not really relevant, so we
        # don't retrieve its body in this case
        record_body = ""
        if top_n_similar_ranking[0][1] >= SimilarityScore.MEDIUM.lower_bound():
            best_match_topic = top_n_similar_headings[0].record_heading.topic
            best_match_id = top_n_similar_headings[0].record_heading.id
            record_body = self.persistence.get_body(best_match_topic, best_match_id)

        return (top_n_similar_headings, record_body)

    def get_content_for_identified_heading(self, topic: str, heading_id: int) -> str:
        return self.persistence.get_body(topic, heading_id)

    def get_commands_from_record_tagged_as_command(self, topic: str, heading_id: int) -> Tuple[str, ...]:
        return self.persistence.get_commands_from_record(topic, heading_id)

    def get_scripts_from_record_tagged_as_script(self, topic: str, heading_id: int) -> Tuple[str, ...]:
        return self.persistence.get_scripts_from_record(topic, heading_id)

    def get_record_by_index(self, topic: str, index: int) -> KnowledgeRecord:
        return self.persistence.get_record_by_index(topic, index)

    # PRIVATE METHODS
    def __match_topics(self, sentence: str, known_topics: Tuple[str, ...], whole_word: bool = False) -> Tuple[str, ...]:
        """
        Match topics in a given sentence, based on a list of defined topics

        Args:
                sentence (str): Sentence to parse for topic search
                known_topics (Tuple[str, ...]): List of known topics for matching
                whole_word (bool, optional): Whether to match whole words only. Defaults to False.

        Returns:
                Tuple[str, ...]: Topic matches in sentence

        """
        sentence_lower = sentence.lower()
        topic_matches: Set[str] = set()

        for topic in known_topics:
            topic_lower = topic.lower()
            if whole_word:
                # Match using regex with word boundaries
                if re.search(rf"\b{re.escape(topic_lower)}\b", sentence_lower):
                    topic_matches.add(topic)
            else:
                if topic_lower in sentence_lower:
                    topic_matches.add(topic)

        return tuple(topic_matches)

    def __get_topics_headings(self, topics: Tuple[str, ...]) -> Tuple[RecordHeading, ...]:
        """
        Fetch all available headings for given topics an put them in a single list with their references.
        By references we mean contextual data of the heading : topic, id and text.

        Args:
                topics (List[str]): A list of topics to fetch headings from.

        Returns:
                Tuple[RecordHeading, ...]: A tuple containing headings related to given topics
        """
        referenced_headings_pool: Tuple[RecordHeading, ...] = tuple(
            record_heading
            for topic in topics
            for record_heading in self.persistence.get_referenced_headings_list_for_topic(topic)
        )
        return referenced_headings_pool

    def __purge_headings_from_a_same_record(
        self, headings: Tuple[RecordHeadingMatch, ...]
    ) -> Tuple[RecordHeadingMatch, ...]:
        # We need to remove headings that are siblings of the first heading
        # because they are alternative formulations for the same record and so
        # they target the same content and do not provide alternative content.
        return tuple(
            headings[index]
            for index, heading in enumerate(headings)
            if not (index > 0 and heading.record_heading.id in headings[index - 1].record_heading.alternative_headings_id)
        )
