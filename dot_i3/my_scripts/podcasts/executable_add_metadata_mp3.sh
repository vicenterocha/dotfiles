#!/usr/bin/env bash

# Set options n and d for the name and directory respectively
while getopts n:d: option
do
    case "${option}"
        in
        d) DIR=${OPTARG};;
        # name is not yet used
        n) NAME=${OPTARG};;
    esac
done


FILES=$( ls "$DIR" )

BDIR=$(basename "$DIR")
echo $DIR


find "$DIR" -type f -name '*.mp3' -exec sh -c '
  for file do
    echo "$file"
    id3v2 -a $BDIR "$file"
    id3v2 -A $BDIR "$file"
    id3v2 -g "Podcast" "$file"
    exiftool $DIR$file
    read line </dev/tty
  done
' sh {} +
