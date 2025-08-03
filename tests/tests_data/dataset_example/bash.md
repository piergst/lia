# What is the difference between `\;` and `+` in the `find ... -exec` command in bash?
```bash
find . -iname "*.txt" -exec rm {} \;
find . -iname "*.txt" -exec rm {} +
```

- `\;`: Processes each result one by one.  
- `+`: Processes all results in a single invocation.  

# How to exclude files and directories from deletion with the `rm` command in bash? #command
```bash
# bash shell only
shopt -s extglob
rm !(<filename>|<dirname>)
# or
find . -mindepth 1 ! -name "<filename>" ! -name "<dirname>" ! -path "i./<dirname>/*" -exec rm -r {} +
```

- `-mindepth 1`: Excludes the current directory from deletion.  
- `-path "./<dirname>/*"`: Excludes the contents of `<dirname>`. `! -name "<dirname>"` alone is not sufficient.  
- `+`: Executes deletion in a single batch (unlike `\;`, which executes for each result).  

# How to flatten an array into a single string in bash? #command
```bash
array=("--debug" "--create-archive" "--no-clear")
array_as_str="${array[*]}"
```

# How to concatenate a variable with a string in bash? #command
```bash
var="/home/tom"
var="$var/documents"
# or
var+="/documents"
```

# Best practices for using quotes in bash?
```bash
# Initialize variables
BUILD_DIR="path/to/build/dir"
MACOS_QT_QMAKE="/path/to/qmake"
PROJECT_DIRECTORY="/path/to/project"
BUILD_TYPE="release"
BUNDLE_NAME="MyApp"

# Initialize an empty variable
CONFIG=""

# Single-line command
cp -R "$BUILD_DIR/appliBureau/Logicmax.app" "$BUNDLE_NAME.app"

# Multi-line command
"${MACOS_QT_QMAKE}/qmake" \
    "${PROJECT_DIRECTORY}/logicielBureau.pro" \
    -spec "macx-clang" \
    CONFIG+="$BUILD_TYPE" \
    CONFIG+="qtquickcompiler" \
    CONFIG+="sdk_no_version_check"
```

- Always wrap file paths and variables in quotes.  
- Use braces `{}` for better readability, especially when variables are adjacent.  
- Commands commonly used in CLI do not usually require quotes.  

# Best practices for comparing strings, numbers, or booleans in bash?
```bash
MY_STRING="hello"

if [[ "$MY_STRING" == "hello" ]]; then
    echo "String is hello"
fi

MY_NUMBER=5

if [[ "$MY_NUMBER" -eq 5 ]]; then
    echo "Number is 5"
fi

MY_BOOL="true"

if [[ "$MY_BOOL" == "true" ]]; then
    echo "Boolean is true"
fi
```

### General Best Practices:

1. **Use double brackets `[[ ]]`**: Safer and more feature-rich than single brackets `[ ]`.  
2. **Use quotes**: Always quote variables to avoid word splitting or glob expansion issues.  
3. **Use braces for variables**: Delimit variables with `{}` for clarity, especially in concatenation scenarios.  


# How to use `;` or newlines in a bash `if/then/else` block?
```bash
#!/bin/bash

directory="/path/to/directory"

if [[ ! -d "$directory" ]]
then
  mkdir -p "$directory"
  echo "The directory $directory has been created."
else
  echo "The directory $directory already exists."
fi
```

Equivalent inline:  

```bash
if [[ ! -d "/path/to/directory" ]]; then mkdir -p "/path/to/directory" && echo "Directory created."; else echo "The directory $directory already exists."; fi
```

- Semicolon (`;`) or newline acts as a delimiter between commands.  
- In scripts, newlines are preferred for readability, while semicolons are suitable for inline commands.  

# What are `$!` and `$?` in bash?
```bash
# $!
sleep 10 &
echo "PID of the last background process: $!"

# $?
ls /nonexistentdirectory
echo "Exit code of the last command: $?"
```

# How to capture a command-line option with a value after an equal sign (`=`)? #script
```bash
#!/bin/bash

# Loop through command-line arguments
while [[ "$1" != "" ]]; do
    case $1 in
        --source-dir=* )
            SOURCE_DIR="${1#*=}"
            shift
            ;;
        --other-option )
            echo "Other option activated"
            shift
            ;;
        * )
            echo "Unknown option: $1"
            shift
            ;;
    esac
done

# Print the source directory value
echo "Source directory: $SOURCE_DIR"
```

### Explanation:

1. `--source-dir=*`: Matches options starting with `--source-dir=` followed by any string (`*`).  
2. `${1#*=}`: Removes everything before the `=` in the argument and assigns the remaining value to `SOURCE_DIR`.  
3. `shift`: Shifts positional arguments, making the next one `$1`.  

# How to use `shift` to iterate over arguments in a bash script? #script
```bash
while [[ "$1" != "" ]]; do
    case $1 in
        -r | --release )
            BUILD_TYPE="release"
            shift
            ;;
        -d | --debug )
            BUILD_TYPE="debug"
            shift
            ;;
    esac
done
```

# How to iterate over an array in bash? #script
```bash
array=("val1" "val2" "val3")

for element in "${array[@]}"; do
    echo "Element: $element"
done
```

# How to display an array's contents in bash? #script
```bash
my_array=("apple" "banana" "cherry")
echo ${my_array[@]}
```

# How to check for the presence of a value in an array in Bash? #script
```bash
my_array=("apple" "banana" "cherry")
search_element="banana"
array_string="${my_array[@]}"

if [[ "$array_string" == *"$search_element"* ]]; then
  echo "Found"
else
  echo "Not Found"
fi
```
# How to include special characters with `echo` in bash? #command #ZZTop #3rdTag
```bash
echo -e "First line\nSecond line"
```

- `-e`: Enables interpretation of backslash escapes.  

# How to declare and use functions in bash? #script #testtag123
```bash
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

# How to declare a `for` loop over a range of numbers in bash? #script

# How to use `seq` to loop over a sequence of numbers in bash? #script

```bash
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

# How to get the size of an array in bash? #script #array
```bash
myArray=(1 2 3)
arraySize=${#myArray[@]}
```

# How to append an element to an array in bash? #script
```bash
declare -a myArray
myArray+=(5)
```

# How to check if a directory exists in bash? #script
```bash
directory="<path/to/directory>"

if [[ ! -d "$directory" ]]; then
    mkdir -p "$directory"
    echo "The directory $directory has been created."
else
    echo "The directory $directory already exists."
fi
```

# How to find the script's directory from within itself? #script
```bash
#!/bin/bash
echo "Script directory: $(dirname "$(realpath "$0")")"
```

# How to flash an ISO using `dd` in bash? #command
### 1. Identify the USB drive
```bash
lsblk
```

### 2. Unmount the USB drive
Before writing to the USB drive, unmount all its partitions:
```bash
sudo umount </dev/sdx>
```
Replace `sdx` with the USB drive name.


### 3. Flash the ISO image using `dd`
```bash
sudo dd if=<path/to/file.iso> of=</dev/sdx> bs=4M status=progress oflag=sync
```
- **if=**: path to the ISO image.
- **of=**: USB drive device (e.g., `/dev/sdb`, not `/dev/sdb1`).
- **bs=4M**: block size to speed up the process.
- **status=progress**: display progress (optional).
- **oflag=sync**: ensures data is written properly to the USB drive.

### 4. Verify the result
Once the command finishes, run the following again:
```bash
lsblk
```
Check that the USB drive contains a bootable partition.

### 5. Safely eject the USB drive
Once the process is complete, safely eject the USB drive:
```bash
sudo eject </dev/sdx>
```

# How to count the number of words in a text file using bash? #command
```bash
wc -w <filename>
```

# How to extract a range of lines from a file in bash? #command
```bash
sed -n '10,20p' <filename>
# Or 
head -n 20 <filename> | tail -n 11 
```

# How to make a file executable for all users in bash? #command
```bash
chmod a+x <filename>
```

# How to read the content of a compressed file (bz2, gz) directly in bash? #command
```bash
bzcat <filename>.bz2 
# Or
zcat <filename>.gz
```
The `bzcat` command (for `.bz2` files) and `zcat` command (for `.gz` files) offer the primary advantage of reading and extracting the compressed content directly without writing it to disk.

# How to create a hexdump from a file in bash? #command
```bash
xxd <filename>
```

# How to recover the original data file from a hexdump in bash? #command
```bash
xxd -r <filename>
```