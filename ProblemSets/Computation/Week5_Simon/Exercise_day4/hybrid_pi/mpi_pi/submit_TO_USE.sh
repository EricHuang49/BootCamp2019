#!/bin/bash -l

#SBATCH --ntasks=16

#SBATCH --time=00:02:00

#SBATCH --output=mpi_pi.out
#SBATCH --error=mpi_pi.err


### MPI executable
mpiexec -np $SLURM_NTASKS ./mpi_pi.exec
