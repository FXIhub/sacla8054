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

if args.mask is not None:
    mask = np.load(args.mask)
else:
    mask = np.ones(DET_SHAPE, dtype='bool')

if args.dark_run is None:
    args.dark_run = utils.get_nearest_dark(args.run, past=True)
    print('Using dark run %d'%args.dark_run)
with h5py.File(PREFIX + 'dark/r%d_dark.h5'%args.dark_run, 'r') as f:
    dark = f['data/mean'][:]

tags = dbpy.read_taglist_byrun(BL_NUM, args.run)
nframes = len(tags)
print('%d frames in run %d'%(nframes, args.run))

litpix = np.zeros(nframes, dtype='i4')
integral = np.zeros(DET_SHAPE)
objs = [stpy.StorageReader(DET_NAME+'-%d'%i, BL_NUM, (args.run,)) for i in range(1,3)]
buffs = [stpy.StorageBuffer(obj) for obj in objs]
stime = time.time()
for i in range(nframes):
    for m in range(2):
        try:
            objs[m].collect(buffs[m], tags[i])
            mod = buffs[m].read_det_data(0) - dark[m]
        except stpy.APIError:
            mod = np.zeros((1024,512))
        litpix[i] += (mod[mask[m]] > ADU_THRESHOLD).sum()
        mod[mod <= ADU_THRESHOLD] = 0
        integral[m] += np.clip(np.rint(mod/ADU_PER_PHOTON), 0, np.inf)
    sys.stderr.write('\r%d/%d: %.2f Hz    ' % (i+1, nframes, (i+1)/(time.time()-stime)))
sys.stderr.write('\n')
integral /= nframes

out_fname = PREFIX + '/events/r%d_events.h5'%args.run
with h5py.File(out_fname, 'w') as f:
    f['entry_1/tags'] = tags
    f['entry_1/litpixels'] = litpix
    f['entry_1/mask_litpixels'] = mask
    f['entry_1/integral'] = integral
os.chmod(out_fname, 0o664)
