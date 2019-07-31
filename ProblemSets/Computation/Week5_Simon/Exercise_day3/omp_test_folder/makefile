#######################################################################	

all: 	normalize_vec.exec dot_prod.exec serial_pi.exec parallel_pi.exec

#######################################################################	

## Normalize a vector
normalize_vec.exec: normalize_vec.cpp
	g++ normalize_vec.cpp -fopenmp -o normalize_vec.exec

dot_prod.exec: dot_prod.cpp
	g++ dot_prod.cpp -fopenmp -o dot_prod.exec


serial_pi.exec: serial_pi.cpp
	g++ serial_pi.cpp -fopenmp -o serial_pi.exec


parallel_pi.exec: parallel_pi.cpp
	g++ parallel_pi.cpp -fopenmp -o parallel_pi.exec

#######################################################################	
	
clean :
	rm -f *.exec
