import os
import time

import pandas as pd
import dbpy

from constants import PREFIX, BL_NUM, RUN_INIT, COLUMNS

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
    #print(run, rinfo.keys(), rinfo['start_tagnumber'], rinfo['end_tagnumber'])
    run += 1
