### CPP compiler wrapper
CXX=mpicxx

### Optimization flags
FFLAGS=-O3 -fopenmp

#######################################################################	

all: BS.exec BS_only_omp.exec
 
#######################################################################	

## BS
BS.exec: BS.cpp
	$(CXX) $(FFLAGS) BS.cpp -o BS.exec


BS_only_omp.exec: BS_only_omp.cpp
	g++ BS_only_omp.cpp -fopenmp -o BS_only_omp.exec

	

#######################################################################	

clean :
	rm -f *.exec

#######################################################################	
