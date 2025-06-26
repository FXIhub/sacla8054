#!/bin/bash

PREFIX=/home/kayyer/2025A8054/ana
run=$1
qfname=${PREFIX}/pbs/proc_dark_array.sh
sed -i "s/run=.*/run=${run}/" $qfname
qsub $qfname
