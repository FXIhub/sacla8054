import os.path as op
import glob

import numpy as np
import dbpy, stpy

from constants import PREFIX, BL_NUM, DET_NAME
from constants import DET_SHAPE, ASSEM_SHAPE, ASSEM_SHIFTS

def get_tags(run):
    return dbpy.read_taglist_byrun(BL_NUM, run)

def get_frames(run, indices, taglist=None):
    if taglist is None:
        taglist = get_tags(run)
    if len(taglist) <= max(indices):
        raise IndexError('Only %d events in run %d' % (len(taglist), run))
    obj = stpy.StorageReader(DET_NAME, BL_NUM, (run,))
    buff = stpy.StorageBuffer(obj)
    frames = []
    for i in indices:
        obj.collect(buff, taglist[i])
        frames.append(buff.read_det_data(0))
    return frames


def assemble(frame):
    '''
    Combine 2 detector modules into single image.
    frame must be shape (2, 1024, 512)
    '''
    assert frame.shape == DET_SHAPE
    assem = np.zeros(ASSEM_SHAPE, dtype='f4')
    s1, s2 = ASSEM_SHIFTS
    assem[s1[0]:s1[0]+DET_SHAPE[1], s1[1]:s1[1]+DET_SHAPE[2]] = frame[0]
    assem[s2[0]:s2[0]+DET_SHAPE[1], s2[1]:s2[1]+DET_SHAPE[2]] = frame[1]
    return assem

def get_nearest_dark(run, past=True):
    '''
    Search for the most recent dark run
    '''
    dfiles = sorted(glob.glob(PREFIX+'dark/r*_dark.h5'))
    druns = np.array([int(op.basename(fname).split('_')[0][1:]) for fname in dfiles])
    if past:
        return druns[np.where((druns <= run))[0][-1]]
    else:
        return druns[np.abs(druns-run).argmin()]

def make_pixmap(dx=-34, dy=101):
    '''Get pixel coordinates
    dx and dy refer to the shift of the center compared to 
    the center of module 1
    '''
    m, x, y = np.meshgrid(np.arange(2), np.arange(-512,512.), np.arange(-256,256.), indexing='ij')
    x[0] += dx+0.01; x[1] -= dx + 0.71
    y[0] += dy+0.01; y[1] += dy + 533.326
    return x, y
