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

from src.domain.knowledge.knowledge_data_objects import RecordHeading, RecordHeadingMatch

EXPECTED_TOPICS = ("bash", "c++", "greenclip", "python", "rust", "vscode-python")

EXPECTED_BASH_HEADINGS = (
	("Best practices for comparing strings, numbers, or booleans in bash?", ()),
	("Best practices for using quotes in bash?", ()),
	("How to append an element to an array in bash?", ("script",)),
	("How to capture a command-line option with a value after an equal sign (`=`)?", ("script",)),
	("How to check for the presence of a value in an array in Bash?", ("script",)),
	("How to check if a directory exists in bash?", ("script",)),
	("How to concatenate a variable with a string in bash?", ("command",)),
	("How to count the number of words in a text file using bash?", ("command",)),
	("How to create a hexdump from a file in bash?", ("command",)),
	("How to declare a `for` loop over a range of numbers in bash?", ("script",)),
	("How to declare and use functions in bash?", ("script", "testtag123")),
	("How to display an array's contents in bash?", ("script",)),
	("How to exclude files and directories from deletion with the `rm` command in bash?", ("command",)),
	("How to extract a range of lines from a file in bash?", ("command",)),
	("How to find the script's directory from within itself?", ("script",)),
	("How to flash an ISO using `dd` in bash?", ("command",)),
	("How to flatten an array into a single string in bash?", ("command",)),
	("How to get the size of an array in bash?", ("script", "array")),
	("How to include special characters with `echo` in bash?", ("command", "ZZTop", "3rdTag")),
	("How to iterate over an array in bash?", ("script",)),
	("How to make a file executable for all users in bash?", ("command",)),
	("How to read the content of a compressed file (bz2, gz) directly in bash?", ("command",)),
	("How to recover the original data file from a hexdump in bash?", ("command",)),
	("How to use `;` or newlines in a bash `if/then/else` block?", ()),
	("How to use `seq` to loop over a sequence of numbers in bash?", ("script",)),
	("How to use `shift` to iterate over arguments in a bash script?", ("script",)),
	("What are `$!` and `$?` in bash?", ()),
	("What is the difference between `\;` and `+` in the `find ... -exec` command in bash?", ()),
)

EXPECTED_TOP_3_HEADINGS_BASH_1 = (
	RecordHeadingMatch(
		record_heading=RecordHeading(
			topic="bash",
			id=191,
			text="How to check for the presence of a value in an array in Bash?",
			tags=("script",),
			alternative_headings_id=(),
		),
		similarity_indice=0.931554,
	),
	RecordHeadingMatch(
		record_heading=RecordHeading(
			topic="bash",
			id=260,
			text="How to check if a directory exists in bash?",
			tags=("script",),
			alternative_headings_id=(),
		),
		similarity_indice=0.711219,
	),
	RecordHeadingMatch(
		record_heading=RecordHeading(
			topic="bash",
			id=185,
			text="How to display an array's contents in bash?",
			tags=("script",),
			alternative_headings_id=(),
		),
		similarity_indice=0.565154,
	),
)


EXPECTED_TOP_3_HEADINGS_BASH_2 = (
	RecordHeadingMatch(
		record_heading=RecordHeading(
			topic="bash",
			id=117,
			text="What are `$!` and `$?` in bash?",
			tags=(),
			alternative_headings_id=(),
		),
		similarity_indice=0.579725,
	),
	RecordHeadingMatch(
		record_heading=RecordHeading(
			topic="bash",
			id=203,
			text="How to include special characters with `echo` in bash?",
			tags=(
				"command",
				"ZZTop",
				"3rdTag",
			),
			alternative_headings_id=(),
		),
		similarity_indice=0.516847
	),
	RecordHeadingMatch(
		record_heading=RecordHeading(
			topic="bash",
			id=254,
			text="How to append an element to an array in bash?",
			tags=("script",),
			alternative_headings_id=(),
		),
		similarity_indice=0.506158,
	),
)
EXPECTED_TOP_3_HEADINGS_CURL = (
	RecordHeadingMatch(
		record_heading=RecordHeading(
			topic="curl",
			id=1,
			text="How to use a session cookie for an HTTP request with curl ?",
			tags=("script",),
			alternative_headings_id=(),
		),
		similarity_indice=0.899267,
	),
	RecordHeadingMatch(
		record_heading=RecordHeading(
			topic="undefined",
			id=20,
			text="How to create a minimal local HTTP server?",
			tags=("command",),
			alternative_headings_id=(),
		),
		similarity_indice=0.302886,
	),
	RecordHeadingMatch(
		record_heading=RecordHeading(
			topic="undefined",
			id=1,
			text="How to retrieve my public IP?",
			tags=("command",),
			alternative_headings_id=(),
		),
		similarity_indice=0.154411,
	),
)
EXPECTED_TOP_3_HEADINGS_ENUMERATE = (
	RecordHeadingMatch(
		record_heading=RecordHeading(
			topic="undefined",
			id=10,
			text="How to enumerate directories on a website?",
			tags=("command",),
			alternative_headings_id=(),
		),
		similarity_indice=0.810043,
	),
	RecordHeadingMatch(
		record_heading=RecordHeading(
			topic="undefined",
			id=20,
			text="How to create a minimal local HTTP server?",
			tags=("command",),
			alternative_headings_id=(),
		),
		similarity_indice=0.084169,
	),
	RecordHeadingMatch(
		record_heading=RecordHeading(
			topic="undefined",
			id=1,
			text="How to retrieve my public IP?",
			tags=("command",),
			alternative_headings_id=(),
		),
		similarity_indice=0.075079,
	),
)
EXPECTED_TOP_2_HEADINGS_AD = (
	RecordHeadingMatch(
		record_heading=RecordHeading(
			topic="ad",
			id=1,
			text="Which central file contains information about users, groups, and their passwords in AD?",
			tags=(),
			alternative_headings_id=(3,),
		),
		similarity_indice=0.901147,
	),
	RecordHeadingMatch(
		record_heading=RecordHeading(
			topic="ad",
			id=42,
			text="What Are the Two Main Identifiers Used for User Authentication in AD?",
			tags=(),
			alternative_headings_id=(44,),
		),
		similarity_indice=0.635815,
	),
)

EXPECTED_TOP_1_HEADING_AD = (
	RecordHeadingMatch(
		record_heading=RecordHeading(
			topic="ad",
			id=12,
			text="What is the SYSVOL folder in AD?",
			tags=(),
			alternative_headings_id=(14, 16, 18, 20),
		),
		similarity_indice=0.986023,
	),
)

EXPECTED_TOP_1_ANSWER_BASH = '```bash\nmy_array=("apple" "banana" "cherry")\nsearch_element="banana"\narray_string="${my_array[@]}"\n\nif [[ "$array_string" == *"$search_element"* ]]; then\n  echo "Found"\nelse\n  echo "Not Found"\nfi\n```\n'

EXPECTED_TOP_1_ANSWER_CURL = '```bash\nURL="http://url.com"\nCOOKIE_FILE="cookie.txt"\nHTML_CONTENT=$(curl -c "$COOKIE_FILE" -s "$URL")\n$DATA="bar\nRESPONSE=$(curl -s -b "$COOKIE_FILE" -d "foo=$DATA" -X POST "$URL")\necho "$RESPONSE"\nrm -r "$COOKIE_FILE"\n```\n'

EXPECTED_TOP_1_ANSWER_ENUMERATE = "```bash\ngobuster dir --no-error -u http://<targetip> -w /path/to/wordlist.txt\n```\n\n- **`dir`**: search for subdirectories of the domain\n- **`--no-error`**: suppress access error logging\n- **`-u`**: target URL\n- **`-w`**: wordlist path\n\n"

EXPECTED_TOP_1_ANSWER_AD_1 = r"""NTDS.DIT is a central file in AD (stored on DCs: C:\Windows\NTDS\). It is the
database that contains information about users, groups, etc. But most
importantly, it contains password hashes for all users in the domain (->
possibility of brute force or pass-the-hash attack). Furthermore, if the Store
password with reversible encryption option is enabled, passwords will be stored
in plaintext...

"""

EXPECTED_TOP_1_ANSWER_AD_2 = "The SYSVOL folder is a set of files and folders that reside on the local hard disk of each domain controller in a domain and are replicated by the File Replication service (FRS). It contains logon scripts, group policy data, and other domain-wide data.\n\n"


EXPECTED_COMMAND = ("wc -w <filename>",)

EXPECTED_COMMANDS_1 = ("sed -n '10,20p' <filename>", "head -n 20 <filename> | tail -n 11")

EXPECTED_COMMANDS_2 = (
	"lsblk",
	"sudo umount </dev/sdx>",
	"sudo dd if=<path/to/file.iso> of=</dev/sdx> bs=4M status=progress oflag=sync",
	"lsblk",
	"sudo eject </dev/sdx>",
)
