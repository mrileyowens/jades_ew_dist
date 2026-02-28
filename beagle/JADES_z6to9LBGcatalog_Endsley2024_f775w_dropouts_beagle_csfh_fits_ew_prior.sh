#!/bin/bash

set -euo pipefail

# Set the name of the SLURM file to submit, the SLURM job name, list of galaxy IDs,
# and the directory to store the success files
JOB_SCRIPT=JADES_z6to9LBGcatalog_Endsley2024_f775w_dropouts_beagle_csfh_fits_ew_prior.slurm
JOB_NAME=JADES_z6to9LBGcatalog_Endsley2024_f775w_dropouts_beagle_csfh_fits_ew_prior
CATALOG=JADES_z6to9LBGcatalog_Endsley2024_f775w_dropouts_ids.txt
SUCCESS_DIR=success/JADES_z6to9LBGcatalog_Endsley2024_f775w_dropouts_beagle_csfh_fits_ew_prior

# Set a maximum of 3 rounds of fitting to attempt
#MAX_ROUNDS=3
SLEEP=300

# Make the directory that will contain the success files
mkdir -p "$SUCCESS_DIR"

###############################################################################
# 1) CLEAN STALE STATE (ONCE)
###############################################################################

# Remove any lingering success files from a previous job
#echo "Cleaning stale success files..."
#rm -f "$SUCCESS_DIR"/success_*

###############################################################################
# 2) AUTOMATIC RESUBMISSION LOOP
###############################################################################

# Get the galaxy IDs from the file
mapfile -t OBJIDS < "$CATALOG"

PREV_JOBID=""

#OBJIDS=( $(head -n 10 JADES_f775w_dropouts_Endsley2024_ids.txt) )

#while true; do

# For each round
#for ROUND in $(seq 1 "$MAX_ROUNDS"); do

#echo "Submission round $ROUND / $MAX_ROUNDS"

# Instantiate the list of failed tasks
FAILED_ARRAY=()

# For each task
for i in "${!OBJIDS[@]}"; do
    #objid="${OBJIDS[$i]}"

    # If an associated success file does not exist, then add the task to the failed array
    if [[ ! -f "$SUCCESS_DIR/success_${i}" ]]; then
        FAILED_ARRAY+=("$i")
    fi
done

# If the array of failed task numbers is empty
if [[ ${#FAILED_ARRAY[@]} -eq 0 ]]; then
    echo "All objects successfully processed."
    # Quit
    exit 0
fi

# Make an array of the failed task numbers to submit
ARRAY=$(IFS=,; echo "${FAILED_ARRAY[*]}")
echo "Submitting array indices: $ARRAY"

#sbatch --array="$ARRAY" "$JOB_SCRIPT"

#if [[ -z "$PREV_JOBID" ]]; then
#	JOBID=$(sbatch --parsable --array="$ARRAY" "$JOB_SCRIPT")
#else
#	JOBID=$(sbatch --parsable --dependency=afterany:$PREV_JOBID --array="$ARRAY" "$JOB_SCRIPT")
#fi

# Submit the failed tasks to fit
JOBID=$(sbatch --parsable --array="$ARRAY" "$JOB_SCRIPT")

#echo "Waiting for jobs to finish..."
#while squeue -u "$USER" -h -n "$JOB_NAME" | grep -q .; do
#    sleep "$SLEEP"
#done

#echo "Round $ROUND submitted as job $JOBID"
#PREV_JOBID="$JOBID"

# Added a sleep time because I thought an issue may have been jobs hitting the queue too slowly compared to when various commands check for them. Maybe unnecessary
sleep 60

#scontrol wait "$JOBID"

# While the job is still in the queue, wait
echo "Waiting for jobs to finish..."
while sacct -n -j "$JOBID" --format=State | grep -Eq 'PENDING|RUNNING|COMPLETING'; do
    sleep "$SLEEP"
done

#echo "Waiting for jobs to finish..."
#while squeue -h -u "$USER" -n "$JOB_NAME" | grep -q .; do
#    sleep "$SLEEP"
#done

#echo "Waiting for job $JOBID to finish..."
#while squeue -h -j "${JOBID}_" | grep -q .; do
#    sleep "$SLEEP"
#done
#echo "Batch finished; re-checking catalog..."

echo "Pipeline complete."
