#!/bin/bash
echo "Starting prepare_samples.sh..."
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
    url=$(echo "${json_separate}" | jq -r --arg name "${name}" '.[$name][0]')
    start_time=$(echo "${json_separate}" | jq -r --arg name "${name}" '.[$name][1]')
    end_time=$(expr $start_time + 20)
    echo "Separating ${name} from ${url} with start_time ${start_time} sec"

    # Download with pytube
    yt-dlp ${url} -o "/tmp/${name}" --format "bestaudio/best"  --download-sections "*${start_time}-${end_time}"

    # Run inference
    python inference.py --input /tmp/${name} --output /tmp --full_mode 1
    echo "Done separating ${name}"
done
