#include <iostream>
#include <cstdlib>
#include <cmath>
#include <omp.h>
#include <stdlib.h>
#include <stdio.h>
using namespace std;

// function to compute the 2-norm of a vector v of length n
double norm(double *v, int n){
    double norm = 0.;

    for(int i=0; i<n; i++)
        norm += v[i]*v[i];

    return sqrt(norm);
}

// initialise v to values between -10 and 10
void initialize(double *v, int n){
    for(int i=0; i<n; i++)
        v[i] = cos(double(i)) * 10.;
}

// This is the non-parallel version
void normalize_vector(double *v, int n){
    double norm = 0.;

    // compute the norm of v
    for(int i=0; i<n; i++)
        norm += v[i]*v[i];
    norm = sqrt(norm);

    // normalize v
    for(int i=0; i<n; i++)
        v[i] /= norm;
}

void normalize_vector_omp(double *v, int n)
{

    double norm = 0.;
    double temp_norm = 0.; 
    int th_id;
    #pragma omp parallel private(temp_norm)
    {
	th_id = omp_get_thread_num();

    	#pragma omp for
    	for(int i=0; i<n; i++){
          temp_norm += v[i]*v[i];
	}

	#pragma omp critical
	{
	norm = norm + temp_norm;
   	} 
    }

    norm = sqrt(norm);

    #pragma omp parallel
    {
	#pragma omp for
	for (int i=0;i<n;i++){
		v[i]/=norm;
	}

    } 
}

int main( void ){
    int max_threads = omp_get_max_threads();
    if(max_threads == 1){
   std::cout<< "Parallel Error\t"<< "Serial Error\t"<< "Max Thread\t"<< "Serial time\t"<<"Parallel time\t"<< "Speedup\t"<< "Efficiency\t"<< "Size of array" << std::endl;
    }
    for(int iteration=0;iteration<4;iteration++){

        const int N = 200000000*(iteration+1);
        double *v = (double*)malloc(N*sizeof(double));
        bool validated = false;

        initialize(v, N);
        // Calling the first omp function
        double time_serial = -omp_get_wtime();
        normalize_vector(v, N);
        time_serial += omp_get_wtime();
        
        double serial_error = fabs(norm(v,N) - 1.);
            
        // chck the answer

        
        initialize(v, N);
        double time_parallel = -omp_get_wtime();
        normalize_vector_omp(v, N);
        time_parallel += omp_get_wtime();

        // chck the answer

        std::cout << fabs(norm(v,N) - 1.) << "\t" <<serial_error<<  "\t" <<max_threads <<  "\t" << time_serial <<  "\t" <<time_parallel << "\t" << time_serial/time_parallel << "\t" <<(time_serial/time_parallel)/double(max_threads) << "\t" << N <<std::endl;

        free(v);

    }
    return 0;
}


