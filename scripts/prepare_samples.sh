#!/bin/bash

# Read the secret into a variable
export PREPARE_SAMPLES=$(cat /run/secrets/PREPARE_SAMPLES)

# Check if the "PREPARE_SAMPLES" environment variable is set
if [ -z "${PREPARE_SAMPLES}" ]; then
    echo "PREPARE_SAMPLES is unset or set to the empty string. Skipping sample preparation."
    exit 0
fi

# Read JSON file into a variable
json=$(cat sample_songs.json)

mkdir -p "/tmp/vocal_remover"

# Iterate through keys and values
for name in $(echo "${json}" | jq -r 'keys[]'); do
    url=$(echo "${json}" | jq -r --arg name "${name}" '.[$name]')
    echo "Separating ${name} from ${url}"

    # Download with pytube
    yt-dlp ${url} -o "/tmp/${name}" --format "bestaudio/best"

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

    # Run inference
    python inference.py --input /tmp/${name} --output /tmp --only_no_vocals false
    echo "Done separating ${name}"
done
