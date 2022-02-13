#!/usr/bin/env bash

shopt -s globstar

src_dir="$1"
dest_dir="$2"

{ [ -z "$src_dir" ] || [ -z "$dest_dir" ]; } && exit 1

# Manually create a repo by moving the files from src_dir to dest_dir preserving
# the underlying directory structure. Additionally we prepend the file's path
# relative to src_dir to the beginning of each file.

# Create all necessary subdirectories (recursively) inside dest_dir
for dir in "$src_dir"/**/; do
    mkdir -p "$dest_dir${dir/$src_dir/}"
done

# Copy the files preserving the structure of src_dir inside dest_dir
for file in "$src_dir"/**; do
    dest_file="$dest_dir${file/$src_dir/}"
    [ -d "$dest_file" ] || { echo "${dest_file/$dest_dir/}"; cat "$file"; } > "$dest_file"
done
