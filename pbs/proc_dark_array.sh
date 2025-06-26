#!/bin/sh

#PBS -q serial
#PBS -o .pdark.out
#PBS -e .pdark.out
#PBS -N dark
#PBS -l select=1:ncpus=2

cd ${PBS_O_WORKDIR}

module load python
PREFIX=/home/kayyer/2025A8054/ana

run=1560000
python ${PREFIX}/proc_dark.py $run
