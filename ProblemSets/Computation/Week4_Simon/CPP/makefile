#######################################################################	
all: compute_pi.exec compute_pi_monte_carlo.exec
#######################################################################	

## Example 1
compute_pi.exec: compute_pi.cpp
	g++ compute_pi.cpp -o compute_pi.exec

#######################################################################	
compute_pi_monte_carlo.exec: compute_pi_monte_carlo.cpp
	g++ -std=c++11 compute_pi_monte_carlo.cpp -o compute_pi_monte_carlo.exec

#######################################################################
clean :
	rm -f *.exec
	rm -f *.x
