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

from datetime import datetime

from src.domain.knowledge.knowledge_data_objects import KnowledgeRecord
from src.domain.learning.learning_data_objects import ReviewGroup

EXPECTED_BASH_REVIEW_GROUPS = (
    ReviewGroup(
        id=1,
        group_index=0,
        topic="bash",
        last_review_date=None,
        next_review_date=None,
        reviews_count=0,
    ),
    ReviewGroup(
        id=2,
        group_index=1,
        topic="bash",
        last_review_date=None,
        next_review_date=None,
        reviews_count=0,
    ),
    ReviewGroup(
        id=3,
        group_index=2,
        topic="bash",
        last_review_date=None,
        next_review_date=None,
        reviews_count=0,
    ),
    ReviewGroup(
        id=4,
        group_index=3,
        topic="bash",
        last_review_date=None,
        next_review_date=None,
        reviews_count=0,
    ),
)

EXPECTED_KNOWLEDGE_RECORD_BASH_210 = KnowledgeRecord(
    id=210,
    headings=("How to declare and use functions in bash?",),
    body=r"""```bash
# STRING RETURN
get_greeting() {
    echo "Hello world!"
}

greeting=$(get_greeting)
echo $greeting  

# NUMERICAL RETURN
add_numbers() {
    local sum=$(( $1 + $2 ))
    echo $sum
}

result=$(add_numbers 5 7)
echo $result  # Outputs 12
```

""",
)
EXPECTED_KNOWLEDGE_RECORD_BASH_230 = KnowledgeRecord(
    id=230,
    headings=(
        "How to declare a `for` loop over a range of numbers in bash?",
        "How to use `seq` to loop over a sequence of numbers in bash?",
    ),
    body=r"""```bash
for i in {0..20}; do
    echo "i = $i"
done
```

For specific steps:

```bash
for i in $(seq 0 2 20); do
    echo "i = $i"
done
```

""",
)

EXPECTED_ORDERED_GROUPS_TO_REVIEW = (
    # These expected results need current day to be 2025-03-03
    # Oldest overdue review / few count
    ReviewGroup(
        id=10,
        group_index=0,
        topic="curl",
        last_review_date=datetime(2025, 2, 10, 0, 0),
        next_review_date=datetime(2025, 2, 17, 0, 0),
        reviews_count=2,
    ),
    # Oldest overdue review / few count / alphabetical
    ReviewGroup(
        id=14,
        group_index=0,
        topic="python",
        last_review_date=datetime(2025, 2, 10, 0, 0),
        next_review_date=datetime(2025, 2, 17, 0, 0),
        reviews_count=2,
    ),
    # Oldest overdue review / most count
    ReviewGroup(
        id=1,
        group_index=0,
        topic="ad",
        last_review_date=datetime(2025, 1, 18, 0, 0),
        next_review_date=datetime(2025, 2, 17, 0, 0),
        reviews_count=3,
    ),
    # Oldest overdue review / most count / alphabetical
    ReviewGroup(
        id=4,
        group_index=0,
        topic="bash",
        last_review_date=datetime(2025, 1, 18, 0, 0),
        next_review_date=datetime(2025, 2, 17, 0, 0),
        reviews_count=3,
    ),
    # Overdue review / less count
    ReviewGroup(
        id=5,
        group_index=1,
        topic="bash",
        last_review_date=datetime(2025, 1, 23, 0, 0),
        next_review_date=datetime(2025, 2, 22, 0, 0),
        reviews_count=1,
    ),
    # Overdue review / less count / alphabetical
    ReviewGroup(
        id=15,
        group_index=1,
        topic="python",
        last_review_date=datetime(2025, 1, 23, 0, 0),
        next_review_date=datetime(2025, 2, 22, 0, 0),
        reviews_count=1,
    ),
    # Overdue review / most count
    ReviewGroup(
        id=2,
        group_index=1,
        topic="ad",
        last_review_date=datetime(2025, 1, 23, 0, 0),
        next_review_date=datetime(2025, 2, 22, 0, 0),
        reviews_count=2,
    ),
    # Overdue review / most count / alphabetical
    ReviewGroup(
        id=6,
        group_index=2,
        topic="bash",
        last_review_date=datetime(2025, 1, 23, 0, 0),
        next_review_date=datetime(2025, 2, 22, 0, 0),
        reviews_count=2,
    ),
    # Current day review less count
    ReviewGroup(
        id=11,
        group_index=1,
        topic="curl",
        last_review_date=datetime(2025, 3, 2, 0, 0),
        next_review_date=datetime(2025, 3, 3, 0, 0),
        reviews_count=1,
    ),
    # Current day review less count / alphabetical
    ReviewGroup(
        id=16,
        group_index=2,
        topic="python",
        last_review_date=datetime(2025, 3, 2, 0, 0),
        next_review_date=datetime(2025, 3, 3, 0, 0),
        reviews_count=1,
    ),
    # Current day review most count
    ReviewGroup(
        id=7,
        group_index=3,
        topic="bash",
        last_review_date=datetime(2025, 2, 24, 0, 0),
        next_review_date=datetime(2025, 3, 3, 0, 0),
        reviews_count=2,
    ),
    # Current day review most count / alphabetical
    ReviewGroup(
        id=12,
        group_index=2,
        topic="curl",
        last_review_date=datetime(2025, 2, 24, 0, 0),
        next_review_date=datetime(2025, 3, 3, 0, 0),
        reviews_count=2,
    ),
    # Future review less count
    ReviewGroup(
        id=3,
        group_index=2,
        topic="ad",
        last_review_date=datetime(2025, 3, 2, 0, 0),
        next_review_date=datetime(2025, 3, 9, 0, 0),
        reviews_count=1,
    ),
    # Future review less count / alphabetical
    ReviewGroup(
        id=8,
        group_index=4,
        topic="bash",
        last_review_date=datetime(2025, 3, 2, 0, 0),
        next_review_date=datetime(2025, 3, 9, 0, 0),
        reviews_count=1,
    ),
    # Future review most count /
    ReviewGroup(
        id=9,
        group_index=5,
        topic="bash",
        last_review_date=datetime(2025, 2, 25, 0, 0),
        next_review_date=datetime(2025, 3, 27, 0, 0),
        reviews_count=2,
    ),
    # Future review most count / alphabetical
    ReviewGroup(
        id=13,
        group_index=3,
        topic="curl",
        last_review_date=datetime(2025, 2, 25, 0, 0),
        next_review_date=datetime(2025, 3, 27, 0, 0),
        reviews_count=2,
    ),
)

EXPECTED_AD_REVIEW_GROUPS = (
    ReviewGroup(
        id=1,
        group_index=0,
        topic="ad",
        last_review_date=None,
        next_review_date=None,
        reviews_count=0,
    ),
)
