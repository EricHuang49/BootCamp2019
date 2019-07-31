#!/bin/bash
#SBATCH --job-name=test
#SBATCH --output=slurm_test.out
#SBATCH --time=00:05:00
#SBATCH --ntasks=1
#SBATCH --partition=broadwl
#SBATCH --account=oselab

# Run the process 
make
./compute_pi.exec
./compute_pi_monte_carlo.exec
