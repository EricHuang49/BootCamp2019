#include <iostream>
#include <cstdlib>
#include <cmath>
#include <omp.h>
#include <stdlib.h>
#include <stdio.h>
using namespace std;

int main(void){
    
    int max_threads = omp_get_max_threads();
    
    if (max_threads == 1){
    std::cout<< "Answer \t"<< "True answer \t"<<"Max Thread \t"<< "Parallel time \t"<< "Size of array"<<std::endl;
    
    }
    
    for(int iteration=0;iteration<7;iteration++){

        const int N = 100000000*(iteration+1);
        double *a = (double*)malloc(N*sizeof(double));
        double *b = (double*)malloc(N*sizeof(double));
        
        
            // initialize the vectors
            for(int i=0; i<N; i++) {
                a[i] = 1./2.;
                b[i] = double(i+1);
            }


            double time = -omp_get_wtime();
            double dot=0.;
            double curr_dot = 0.;

            #pragma omp parallel private(curr_dot)
            {
                #pragma omp for
                for(int i=0; i<N; i++) {
                    curr_dot += a[i] * b[i];
                }

                #pragma omp critical
                {
                    dot = dot + curr_dot;
                }
            }
            time += omp_get_wtime();

       
        double expected = double(N+1)*double(N)/4.;
        // chck the answer
        std::cout << dot << "\t" <<expected <<  "\t" <<max_threads << "\t" <<time << "\t" <<N<< std::endl;

        free(a);
        free(b);
    }
        
    return 0;

    
    
}

