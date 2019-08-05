#include <stdio.h>
#include <mpi.h>
#include <iostream>

using namespace std;

int main (int argc, char *argv[])
{
    int rank, my_rank, size;
    int sum;

    MPI_Init(&argc, &argv);

    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    MPI_Comm_size(MPI_COMM_WORLD, &size);

    /* Compute sum of all ranks. */
    my_rank = rank+1;

    MPI_Reduce(&my_rank, &sum, 1, MPI_INT, MPI_SUM, 0, MPI_COMM_WORLD);
    
    if (rank ==0){
    	printf ("Rank %i:\tSum = %i\n", my_rank, sum);
    }


    MPI_Finalize();
    return 0;
}
