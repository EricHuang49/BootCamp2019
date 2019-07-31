#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <omp.h>
using namespace std;
int main()
{

    int max_threads = omp_get_max_threads();

    if (max_threads == 1){
        std::cout<< "Answer \t" <<"Max Thread \t"<< "Parallel time \t"<< "Size of array"<<std::endl;
    
    }
    
   
    for (int iteration=3;iteration<8;iteration++){
        
        const int niter = 50000000*(iteration+1);
        int count=0;
        double pi;
        double z;
        double *x = (double*)malloc(niter*sizeof(double));
        double *y = (double*)malloc(niter*sizeof(double));

        for(int i=0; i<niter; ++i)
        {
            x[i] = (double)random()/RAND_MAX;
            y[i] = (double)random()/RAND_MAX;
        }

       double time = -omp_get_wtime();


        #pragma omp parallel private(z)
        {
            int temp_count = 0;
            #pragma omp for
            for (int i=0; i<niter; ++i){
                z = sqrt((x[i]*x[i])+(y[i]*y[i]));
                if (z<=1){
                   ++temp_count;
                }

            }

            #pragma omp critical
            {
                count = count + temp_count;
            }
        }

        pi = ((double)count/(double)niter)*4.0;          //p = 4(m/n)

        time += omp_get_wtime();

        std::cout << pi << "\t" <<max_threads << "\t" <<time << "\t" << niter << std::endl;


        
        free(x);
        free(y);
    }

   return 0;
}
