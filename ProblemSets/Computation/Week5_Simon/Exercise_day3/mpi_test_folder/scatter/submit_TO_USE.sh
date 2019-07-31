#!/bin/bash -l

#SBATCH --ntasks=16

#SBATCH --time=00:02:00

#SBATCH --output=scatter.out
#SBATCH --error=scatter.err


### MPI executable
make
mpiexec -np $SLURM_NTASKS ./scatter.exec
