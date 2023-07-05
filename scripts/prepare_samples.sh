#!/bin/bash

# Check if the "DISABLE_SAMPLES" environment variable is set
if [ -n "${DISABLE_SAMPLES}" ]; then
    echo "DISABLE_SAMPLES is set. Skipping sample preparation."
    exit 0
fi

# Read JSON file into a variable
json=$(cat sample_songs.json)

# Iterate through keys and values
for name in $(echo "${json}" | jq -r 'keys[]'); do
    url=$(echo "${json}" | jq -r --arg name "${name}" '.[$name]')
    echo "Separating ${name} from ${url}"

    # Download with pytube
    yt-dlp ${url} -o "/tmp/${name}" --format "bestaudio/best"
    mkdir -p "/tmp/vocal_remover"

    # Run inference
    python inference.py --input /tmp/${name} --output /tmp
    echo "Done separating ${name}"
done


# Read JSON file into a variable
json_separate=$(cat separate_songs.json)

# Iterate through keys and values
for name in $(echo "${json_separate}" | jq -r 'keys[]'); do
    url=$(echo "${json_separate}" | jq -r --arg name "${name}" '.[$name]')
    echo "Separating ${name} from ${url}"

    # Download with pytube
    yt-dlp ${url} -o "/tmp/${name}" --format "bestaudio/best"  --download-sections "*45-110"
    mkdir -p "/tmp/vocal_remover"

    # Run inference
    python inference.py --input /tmp/${name} --output /tmp --only_no_vocals false
    echo "Done separating ${name}"
done
