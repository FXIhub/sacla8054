import sys
import os
import argparse

import numpy as np
import h5py
import dbpy

import utils
from constants import PREFIX, BL_NUM, MOTOR_DICT, I0_KEY

parser = argparse.ArgumentParser(description='Add motor positions to events file')
parser.add_argument('run', type=int, help='Run number')
parser.add_argument('-f', '--force', help='Overwrite', action='store_true')
args = parser.parse_args()


# if the events file doesn't exist, exit
events_fname = PREFIX + '/events/r%d_events.h5' % args.run
if not os.path.isfile(events_fname):
    print('Create events file first')
    sys.exit()



# get tags for this run
taglist = dbpy.read_taglist_byrun(BL_NUM, args.run)
hightag, starttag = dbpy.read_start_tagnumber(BL_NUM, args.run)

#initialse flag if the motor positions have been added
added = False
#open the events files
with h5py.File(events_fname, 'a') as f:

    #for each of the xyz motors
    for motornum, event_key in MOTOR_DICT.items():
        if 'entry_1/motors/'+event_key in f: #check if motors have been added to the file alread
            if args.force: #overwrite command
                del f['entry_1/motors/'+event_key]
            else:
                print('%s already present' % event_key)
                continue

        # if motor hasn't been added...
        data_key = 'xfel_bl_3_st_4_motor_%d/position'%motornum
        vals = np.array(dbpy.read_syncdatalist_float(data_key, hightag, taglist)) #get the motor position for each tag
        f['entry_1/motors/'+event_key] = vals #add it to the h5
        added = True

    # Adding pulse energy
    if 'entry_1/pulse_energy_au' not in f or ('entry_1/pulse_energy_au' in f and args.force):
        if args.force:
            del f['entry_1/pulse_energy_au']
        vals = np.array(dbpy.read_syncdatalist_float(I0_KEY, hightag, taglist)) #get the pulse energy for each tag
        f['entry_1/pulse_energy_au'] = vals #add it to the h5
        added = True
    else:
        print('pulse_energy_au already present')
if added:
    print('Added motor positions to run %d events file'%args.run)
