#!/bin/sh

#PBS -q serial
#PBS -o .litpix.out
#PBS -e .litpix.out
#PBS -N litpix
#PBS -l select=1:ncpus=2:mem=8gb

cd ${PBS_O_WORKDIR}

module load python
PREFIX=/home/kayyer/2025A8054/ana

run=1561885
#python ${PREFIX}/litpixels.py $run -m ${PREFIX}/data/geom/goodpix_highq.npy
#python ${PREFIX}/litpixels.py $run -m ${PREFIX}/data/geom/goodpix_highq_v2.npy
python ${PREFIX}/litpixels.py $run -m ${PREFIX}/data/geom/goodpix_highq_v3.npy
python ${PREFIX}/add_motors.py $run
