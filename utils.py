import dbpy, stpy
import numpy as np

from constants import BL_NUM, DET_NAME

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

