import sys
import os
import argparse
import time

import numpy as np
import h5py
import dbpy, stpy

import utils
from constants import PREFIX, BL_NUM
from constants import DET_SHAPE, DET_NAME, ADU_THRESHOLD, ADU_PER_PHOTON

parser = argparse.ArgumentParser(description='Count lit pixels per frame')
parser.add_argument('run', type=int, help='Run number')
parser.add_argument('-d', '--dark_run', type=int, help='Dark run number')
parser.add_argument('-m', '--mask', help='Good pixel mask file (boolean npy)')
args = parser.parse_args()

#load mask if given, otherwise, let all pixels through (np.ones)
if args.mask is not None:
    mask = np.load(args.mask)
else:
    mask = np.ones(DET_SHAPE, dtype='bool')


#load the dark data if given, otherwise grab the most recent.
if args.dark_run is None:
    args.dark_run = utils.get_nearest_dark(args.run, past=True)
    print('Using dark run %d'%args.dark_run)
with h5py.File(PREFIX + 'dark/r%d_dark.h5'%args.dark_run, 'r') as f:
    dark = f['data/mean'][:] #average pixel values over a dark run

# get the tags of this run
tags = dbpy.read_taglist_byrun(BL_NUM, args.run)
nframes = len(tags)
print('%d frames in run %d'%(nframes, args.run))


#initialize arrays for the number of lit pixels on the detector for every tag in this run,
# and the average intensity on the detector over the run
litpix = np.zeros(nframes, dtype='i4')
integral = np.zeros(DET_SHAPE)
#get storage readers and buffers for the modules (DET_NAME-[1/2])
objs = [stpy.StorageReader(DET_NAME+'-%d'%i, BL_NUM, (args.run,)) for i in range(1,3)]
buffs = [stpy.StorageBuffer(obj) for obj in objs]
stime = time.time()


#for each tag, for both modules...
for i in range(nframes):
    for m in range(2):
        #try and read the module data, but if you can't, throw a bunch of 0s
        try:
            objs[m].collect(buffs[m], tags[i])
            mod = buffs[m].read_det_data(0) - dark[m] #ADU module values, subtracting the dark values.
        except stpy.APIError:
            mod = np.zeros((1024,512))

        # in the positions where the mask is, and where the values are greater then the adu threshold,
        # sum those positions and save the value in the lit pixel array
        litpix[i] += (mod[mask[m]] > ADU_THRESHOLD).sum()

        # remove the values where the module is lower then the ADU threshold
        mod[mod <= ADU_THRESHOLD] = 0
        # convert the ADU values to photons, rounding th value to 0 if it's negative
        # then add the pixel values to the running total
        integral[m] += np.clip(np.rint(mod/ADU_PER_PHOTON), 0, np.inf)
    sys.stderr.write('\r%d/%d: %.2f Hz    ' % (i+1, nframes, (i+1)/(time.time()-stime)))
sys.stderr.write('\n')

#divide sum for the average
integral /= nframes

#save the output
out_fname = PREFIX + '/events/r%d_events.h5'%args.run
with h5py.File(out_fname, 'w') as f:
    f['entry_1/tags'] = tags
    f['entry_1/litpixels'] = litpix
    f['entry_1/mask_litpixels'] = mask
    f['entry_1/integral'] = integral
os.chmod(out_fname, 0o664)
