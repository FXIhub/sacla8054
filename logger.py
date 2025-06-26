import os
import time
import argparse
import subprocess

import pandas as pd
import dbpy

from constants import PREFIX, BL_NUM, RUN_INIT, COLUMNS

parser = argparse.ArgumentParser(description='Autologging/processing')
parser.add_argument('-p', '--process', help='Process new runs', action='store_true')
args = parser.parse_args()

if args.process:
    print('Will autoprocess new runs')
runs_fname = PREFIX + '/runs.csv'
# Initialize with existing DB if exists
try:
    runs_df = pd.read_csv(runs_fname, index_col=0)
    run = runs_df.index.max() + 1
except FileNotFoundError:
    print('Starting from the beginning')
    run = RUN_INIT
    runs_df = pd.DataFrame(columns=COLUMNS)

# Wait for new runs to arrive
#latest = dbpy.read_runnumber_newest(BL_NUM)
while True:
    try:
        rinfo = dbpy.read_runinfo(BL_NUM, run)
    except dbpy.APIError:
        print('Waiting for run %d' % run)
        time.sleep(5)
        continue
    if rinfo['runstatus'] != 0:
        print('%d running'%run)
        time.sleep(5)
        continue
    runs_df.loc[run] = [rinfo[k] for k in COLUMNS]
    runs_df.to_csv(runs_fname)
    os.chmod(runs_fname, 0o664)
    print('%d logged'%run)

    if args.process:
        comment = rinfo['comment'].lower()
        if 'dark' in comment and not os.path.isfile('data/dark/r%d_dark.h5'%run):
            #subprocess.Popen(('python proc_dark.py %d'%run).split())
            subprocess.Popen(('./pbs/proc_dark_launcher.sh %d'%run).split())
        elif not os.path.isfile('data/events/r%d_events.h5'%run):
            #subprocess.Popen(('python litpixels.py %d -m data/geom/goodpix_highq.npy'%run).split())
            subprocess.Popen(('./pbs/litpixels_launcher.sh %d'%run).split())
        else:
            print('Litpixels already run')
    run += 1
