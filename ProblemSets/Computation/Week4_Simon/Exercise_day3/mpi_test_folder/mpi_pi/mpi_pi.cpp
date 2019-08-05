#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <mpi.h>
#include <iostream>

using namespace std;

int main(int argc, char *argv[])
{
    int rank, size;
    int niter_total = 60000000;
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
   
    int niter = niter_total/size;
    double x,y;
    int i, count_total;
    int count=0;
    double z;
    double pi;

    for(int i=0; i<niter; ++i)
    {   
        x = (double)random()/RAND_MAX;
        y = (double)random()/RAND_MAX;
        z = sqrt((x*x)+(y*y));
    
        if (z<=1)
        {
            ++count;
        }
    }
    
    if (rank ==0){
    count_total = count;

    	for (int i=1; i<size;i++){
		int curr_count;

        	MPI_Recv(&curr_count, 1, MPI_INT, i, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE); 	   
		count_total = count_total+curr_count;    

    }

    pi = ((double)count_total/(double)niter_total)*4.0;
  
    printf("Pi: %f\n", pi);
 

    }

    else{

	MPI_Send(&count, 1, MPI_INT, 0, 0, MPI_COMM_WORLD);
   
   }


    MPI_Finalize();
    return 0;
}


