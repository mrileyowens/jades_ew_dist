#!/bin/bash

#SBATCH --job-name=JADES_z6to9LBGcatalog_Endsley2024_f775w_dropouts_beagle_csfh_fits_ew_prior
#SBATCH --account=fc_starkhpc
#SBATCH --mail-user=m.riley.owens@berkeley.edu
#SBATCH --mail-type=ALL
#SBATCH --output=logs/slurm-%A_%a.out
#SBATCH --error=logs/slurm-%A_%a.err
#SBATCH --partition=savio4_htc
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=1:00:00

SUCCESS_DIR=/global/scratch/users/mrileyowens/jades_ew_dist/success/JADES_z6to9LBGcatalog_Endsley2024_f775w_dropouts_beagle_csfh_fits_ew_prior
mkdir -p "$SUCCESS_DIR"

SUCCESS_FILE=$SUCCESS_DIR/success_${SLURM_ARRAY_TASK_ID}  

# Now all the bash
source $HOME/.bashrc

readarray -t ids < JADES_z6to9LBGcatalog_Endsley2024_f775w_dropouts_ids.txt
nobjects=1
start_ind=$(( ${nobjects}*${SLURM_ARRAY_TASK_ID} ))

for id in "${ids[@]:${start_ind}:${nobjects}}"; do
  singularity run -B /global/scratch/users/mrileyowens/software/beagle/:/BEAGLE_virtual_workdir /global/scratch/users/mrileyowens/software/beagle/beagle_0.29.2.simg --parameter-file /global/scratch/users/mrileyowens/jades_ew_dist/beagle/params/JADES_z6to9LBGcatalog_Endsley2024_f775w_dropouts_beagle_csfh_fits/${id}_csfh_ew_prior.param --fit && touch "$SUCCESS_FILE"
done
