#!/bin/bash -l

#SBATCH --ntasks=16

#SBATCH --time=00:02:00

#SBATCH --output=allreduce.out
#SBATCH --error=allreduce.err


### MPI executable
make
mpiexec -np $SLURM_NTASKS ./allreduce.exec
