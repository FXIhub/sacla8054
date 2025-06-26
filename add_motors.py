import sys
import os
import argparse

import numpy as np
import h5py
import dbpy

import utils
from constants import PREFIX, BL_NUM, MOTOR_DICT

parser = argparse.ArgumentParser(description='Add motor positions to events file')
parser.add_argument('run', type=int, help='Run number')
parser.add_argument('-f', '--force', help='Overwrite', action='store_true')
args = parser.parse_args()

events_fname = PREFIX + '/events/r%d_events.h5' % args.run
if not os.path.isfile(events_fname):
    print('Create events file first')
    sys.exit()

taglist = dbpy.read_taglist_byrun(BL_NUM, args.run)
hightag, starttag = dbpy.read_start_tagnumber(BL_NUM, args.run)

added = False
with h5py.File(events_fname, 'a') as f:
    for motornum, event_key in MOTOR_DICT.items():
        if 'entry_1/motors/'+event_key in f:
            if args.force:
                del f['entry_1/motors/'+event_key]
            else:
                print('%s already present' % event_key)
                continue
        data_key = 'xfel_bl_3_st_4_motor_%d/position'%motornum
        vals = np.array(dbpy.read_syncdatalist_float(data_key, hightag, taglist))
        f['entry_1/motors/'+event_key] = vals
        added = True
if added:
    print('Added motor positions to run %d events file'%args.run)
