#!/bin/bash
#PBS -l select=1:ncpus=4:mem=24gb:ngpus=1:gpu_type=RTX6000
#PBS -l walltime=00:30:00
#PBS -N pneumonia_detection_job_trial_2

module load anaconda3/personal

cd $PBS_O_WORKDIR

# Start the Ollama server
ollama serve &

# Wait for 5 seconds to ensure the Ollama server is running
sleep 5

# Run the Python script
python3 job-trial-2.py
