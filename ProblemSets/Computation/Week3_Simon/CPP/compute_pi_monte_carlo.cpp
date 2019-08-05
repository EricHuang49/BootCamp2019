// my *second program in C++
#include <iostream>
#include <math.h>
#include <random>
using namespace std;

static long num_steps = 100000;

int main()
{
	int i;
	double x, y = 0.0;
	double pi, sum = 0.0;
		
	std::default_random_engine generator;
	std::uniform_real_distribution<double> distribution(-1.0, 1.0);

	
	for (i=0; i<num_steps; i++){

		x = distribution(generator);
		y = distribution(generator);
		
		if (x*x+y*y <= 1){
			sum++;
		}
	}



	pi = 4 * sum/num_steps;
	cout << pi<<endl; 

	return 0;
	//TODO: Write the function solution...
}
