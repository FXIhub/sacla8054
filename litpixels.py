import argparse

import numpy as np
import h5py

from constants import DET_SHAPE, BATCH_SIZE, ADU_THRESHOLD
import utils

parser = argparse.ArgumentParser(description='Count lit pixels per frame')
parser.add_argument('run', type=int, help='Run number')
parser.add_argument('-m', '--mask', help='Mask file (boolean npy)')
args = parser.parse_args()

if args.mask is not None:
    mask = np.load(args.mask)
else:
    mask = np.ones(DET_SHAPE, dtype='bool')

tags = utils.get_tags(args.run)
nframes = len(tags)
print('%d frames in run %d'%(nframes, args.run))

nbatches = int(np.ceil(nframes / BATCH_SIZE))
litpix = np.zeros(nframes, dtype='i4')
for b in range(nbatches):
    st = b * BATCH_SIZE
    en = min((b+1)*BATCH_SIZE, nframes)
    frames = utils.get_frames(args.run, np.arange(st, en), taglist=tags)
    litpix[st:en] = (frames[:,mask] > ADU_THRESHOLD).sum(1)
    sys.stderr.write('\r%d/%d' % (en, nframes))
sys.stderr.write('\n')

with h5py.File(PREFIX + 'events/r%d_events.h5'%args.run, 'w') as f:
    f['entry_1/litpixels'] = litpix
    f['entry_1/tags'] = tags
