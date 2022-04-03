# *******************************************************************************
# Copyright (C) 2021 INAF
#
# This software is distributed under the terms of the BSD-3-Clause license
#
# Authors:
# Ambra Di Piano <ambra.dipiano@inaf.it>
# *******************************************************************************

from genericpath import isdir
import os
import yaml
import argparse
from datetime import datetime
from os.path import join, isfile, expandvars
from sagsci.tools.utils import get_absolute_path

# get line command options
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--configfile", required=True, default="myconfig.yml", help="configuration YAML file")
args = parser.parse_args()

# get YAML configuration
configuration = open(args.configfile)
config = yaml.load(configuration, Loader=yaml.FullLoader)

# loop wobbles
for i in range(int(config['run']['wobble'])):
    # get number of bins in each run
    bins_in_run = int(float(config['source']['trun'])/float(config['source']['tstep']))
    for j in range(bins_in_run):
        # get time start and stop of each bin
        tstart = float(config['source']['tmin']) + j*float(config['source']['tstep'])
        tstop = float(config['source']['tmin']) + (j+1)*float(config['source']['tstep'])
        # compile data path
        datapath = join(get_absolute_path(config['dirlist']['data']), config['source']['name'].lower(), f"run{i+int(config['run']['idstart'])}", f"{tstart}_{tstop}_{config['source']['emin']}_{config['source']['emax']}")
        if isdir(datapath):
            os.removedirs(datapath)
        os.makedirs(datapath)
        # compile results path
        respath = join(get_absolute_path(config['dirlist']['results']), config['source']['name'].lower(), f"run{i+int(config['run']['idstart'])}", f"{tstart}_{tstop}_{config['source']['emin']}_{config['source']['emax']}")
        if isdir(respath):
            os.removedirs(respath)
        os.makedirs(respath)
