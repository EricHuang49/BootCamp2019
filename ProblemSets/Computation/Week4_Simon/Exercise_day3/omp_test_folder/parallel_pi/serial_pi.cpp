#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <omp.h>


int main()
{
    double niter = 50000000;
    double x,y;
    int i;
    int count=0;
    double z;
    double pi;
    //srand(time(NULL));
    //main loop
   double time = -omp_get_wtime();

    for(int i=0; i<niter; ++i)
    {
        //TODO: Implement data generating process in different loop to provide consistency.
        x = (double)random()/RAND_MAX;
        y = (double)random()/RAND_MAX;
        z = sqrt((x*x)+(y*y));
        //check to see if point is in unit circle
        if (z<=1)
        {
            ++count;
        }
    }
    pi = ((double)count/(double)niter)*4.0;
    time += omp_get_wtime();

    printf("Pi: %f\n", pi);
    printf("The solution took %f\n seconds", time);
    return 0;
}
    //printf("Pi: %f\n", pi);
