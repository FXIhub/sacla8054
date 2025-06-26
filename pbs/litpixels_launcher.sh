#!/bin/bash

run=$1
qfname=/home/kayyer/2025A8054/ana/pbs/litpixels_array.sh
sed -i "s/run=.*/run=${run}/" $qfname
qsub $qfname
