import dbpy, stpy
import numpy as np

from constants import BL_NUM, DET_NAME
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
    assert frame.shape == DET_SHAPE
    assem = np.zeros(ASSEM_SHAPE, dtype='f4')
    s1, s2 = ASSEM_SHIFTS
    assem[s1[0]:s1[0]+DET_SHAPE[1], s1[1]:s1[1]+DET_SHAPE[2]] = frame[0]
    assem[s2[0]:s2[0]+DET_SHAPE[1], s2[1]:s2[1]+DET_SHAPE[2]] = frame[1]
    return assem
