#!/bin/bash -l

#SBATCH --ntasks=16

#SBATCH --time=00:02:00

#SBATCH --output=broadcast.out
#SBATCH --error=broadcast.err


### MPI executable
mpiexec -np $SLURM_NTASKS ./broadcast.exec
