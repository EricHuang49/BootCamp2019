NOTE: These functions need to be put in an environment with IPOPT. Please copy them into the same directory that had the original growth_model folder for them to work properly. There are visualizations if no model will be run.

This folder contains four different subfolders that made certain modifications to the original growth model:

- static: this is the plain vanilla original folder

- stochastic: this is the stocastic version with theta values of 0.9, 0.95, 1, 1.05, 1.10 with equal probabilities.

- stochastic_parallel: this is the stocastic version with MPI4PY implementation for parallelizing.

- new_stochastic: this is the stocastic version with MPI4PY but the structure of the original version is changed for it to be more readable (at least for myself).