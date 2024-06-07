#!/bin/bash

# Run a python script which checks that the AQI data is up-to-date and downloads
# the new one if needed.

# This script can be ran as a cron job, which is why it allows only one instance
# of the update script to be ran at a time (in case updating AQI takes longer than
# the interval of the cron job).

update_aqi () {
    max_retries=20
    retry_interval=1  # Adjust this to control the interval between retries (in seconds)
    retry_count=0

    while [ $retry_count -lt $max_retries ]; do
        echo "Attempting to run the Python script (Attempt #$((retry_count + 1)))..."
        /usr/local/bin/python3 /aqi_tools.py "/graphhopper_data/aqi_data.nc"

        # Check the exit status of the Python script
        if [ $? -eq 0 ]; then
            echo "AQI updating was successful script ran successfully."
            break  # Exit the loop if the Python script succeeded
        else
            echo "Python script failed. Retrying in $retry_interval seconds..."
            sleep $retry_interval
            retry_count=$((retry_count + 1))
        fi
    done

    if [ $retry_count -eq $max_retries ]; then
        echo "Maximum number of retries ($max_retries) reached. Python script still failed."
    else
        touch /intial_aqi_update_true
    fi
}

previous_instance_active () {
  pgrep -a bash | grep -v "^$$ " | grep --quiet 'update_aqi.sh' 
}

if previous_instance_active
then 
  date +'PID: $$ Previous instance is still active at %H:%M:%S, aborting ... '
else 
  update_aqi
fi