#######################################################################	

all: 	serial_pi.exec parallel_pi.exec

#######################################################################	

serial_pi.exec: serial_pi.cpp
	g++ serial_pi.cpp -fopenmp -o serial_pi.exec


parallel_pi.exec: parallel_pi.cpp
	g++ parallel_pi.cpp -fopenmp -o parallel_pi.exec

#######################################################################	
	
clean :
	rm -f *.exec
