PREFIX = '/work/kayyer/2025A8054/'
DET_NAME = 'MPCCD-2N0-M02-001'
DET_SHAPE = (2, 1024, 512) # 2 rectangular modules
BL_NUM = 3

# Auto-logging
RUN_INIT = 1561457 #first run of the experiment
COLUMNS = ['starttime', 'stoptime', 'total_tagnumber',
           'start_tagnumber', 'end_tagnumber', 'hightagnumber',
           'comment', 'runtype', 'stationnumber', 'runstatus']

# Hit finding
ADU_THRESHOLD = 50

# Assembly
ASSEM_SHAPE = (1100, 1200)
ASSEM_SHIFTS = ([38, 38], [39, 571])

# Photon conversion
MOD_GAINS = (25.2525, 25.8232)
ADU_PER_PHOTON = 96.5

# Motors
MOTOR_DICT = {
    49: 'nozzle_x',
    50: 'nozzle_y',
    55: 'nozzle_z',
}
I0_KEY = 'xfel_bl_3_st_4_bm_1_pd/charge'
