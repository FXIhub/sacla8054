import sys
import os
import argparse
import time

import numpy as np
import h5py
import dbpy, stpy

from constants import PREFIX, BL_NUM
from constants import DET_SHAPE, DET_NAME, ADU_THRESHOLD

parser = argparse.ArgumentParser(description='Process dark run')
parser.add_argument('run', type=int, help='Run number')
args = parser.parse_args()


tags = dbpy.read_taglist_byrun(BL_NUM, args.run) #tags within this run
nframes = len(tags)
print('%d frames in run %d'%(nframes, args.run))

#initiize mean and mean squared for each pixel over the run
mean = np.zeros(DET_SHAPE) # DET_SHAPE= (2, 1024, 512)
meansq = np.zeros(DET_SHAPE)

#get storage readers and buffers for the modules (DET_NAME-[1/2])
objs = [stpy.StorageReader(DET_NAME+'-%d'%i, BL_NUM, (args.run,)) for i in range(1,3)]
buffs = [stpy.StorageBuffer(obj) for obj in objs]
stime = time.time()

#for each tag, for both modules...
for i in range(nframes):
    for m in range(2):
        # get the data
        objs[m].collect(buffs[m], tags[i])
        mod = buffs[m].read_det_data(0)
        # add the values and values^2 to a running total
        mean[m] += mod
        meansq[m] += mod**2
    sys.stderr.write('\r%d/%d: %.2f Hz    ' % (i+1, nframes, (i+1)/(time.time()-stime)))
sys.stderr.write('\n')

# divide out by the tags in the run to get mean
mean /= nframes
meansq /= nframes

# save output
out_fname = PREFIX + 'dark/r%d_dark.h5'%args.run
with h5py.File(out_fname, 'w') as f:
    f['data/mean'] = mean
    f['data/sigma'] = np.sqrt(meansq - mean**2)
os.chmod(out_fname, 0o664)
