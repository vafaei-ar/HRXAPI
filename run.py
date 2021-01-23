#!/usr/bin/env python

# === Start Python 2/3 compatibility
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future.builtins import *  # noqa  pylint: disable=W0401, W0614
from future.builtins.disabled import *  # noqa  pylint: disable=W0401, W0614
# === End Python 2/3 compatibility

import subprocess
import yaml
from copy import deepcopy
import numpy as np
from os import remove
from sys import argv

from utils import SimPipline

np.random.seed(0)

configfile = 'template.yaml'
prefix = argv[1]+'/'
klname = 'dk_5thresh_fg_10thresh'

test = 1
if test:
    nside = 32
    freqstart = 550
    freqend = 550+(660-550)
    nchannels = 4
    ndays = 2
    grid_size = 2
    lmax = 40
else:
    nside = 128
    freqstart = 550
    freqend = 550+(660-550)
    nchannels = 64
    ndays = 10
    grid_size = 3
    lmax = 130

pointing_start = 0.
pointing_stop = 1.
npointings = 2

#here one can list all thresholds
thresh_list = [[5,10,1]]


simp = SimPipline(prefix = prefix,
                  pointing_start = pointing_start,
                  pointing_stop = pointing_stop,
                  npointings = npointings,
                  lmax = lmax,
                  mmax = lmax,
                  nside = nside,
                  ndays = ndays,
                  grid_size = grid_size,
                  freqstart = freqstart,
                  freqend = freqend,
                  nchannels = nchannels,
                  thresh_list = thresh_list)


# One can run the initiation steps separately or all together using "telescope_init" method. 
#simp.beamtransfers()
#simp.kltransform()
#simp.psfisher()

simp.telescope_init()

#Then one can make map
simp.make_maps(mode='foreground')


# Generating visibilities 
#path = prefix+'drift_prod_hirax_survey/'
files = [prefix+'maps/foreground.h5'] #,prefix+'maps/foreground.h5']
output_root = prefix+'draco/sstream_fg_'
simp.gen_vis(files,output_root)

# And extract PS 
files = [prefix+'draco/sstream_fg_'+'group_0.h5']
simp.ps_extract(files)

















