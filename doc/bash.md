
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

# What is the difference between `\;` and `+` in the `find ... -exec` command in bash? #command
# How to process result one by one with the find command in bash ? #command
```bash
find . -iname "*.txt" -exec rm {} \;
find . -iname "*.txt" -exec rm {} +
```

- `\;`: Processes each result one by one.  
- `+`: Processes all results in a single invocation.  
```bash
find . -iname "*.txt" -exec rm {} \;
find . -iname "*.txt" -exec rm {} +
```

- `\;`: Processes each result one by one.  
- `+`: Processes all results in a single invocation.  

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
# How to extract parameters from bash script input ? #script
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