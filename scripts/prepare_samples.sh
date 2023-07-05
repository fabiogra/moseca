#!/bin/bash

# Check if the "PREPARE_SAMPLES" environment variable is set
if [ -z "${PREPARE_SAMPLES}" ]; then
    echo "PREPARE_SAMPLES is unset or set to the empty string. Skipping sample preparation."
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
