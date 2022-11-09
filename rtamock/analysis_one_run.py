# *******************************************************************************
# Copyright (C) 2022 INAF
#
# This software is distributed under the terms of the BSD-3-Clause license
#
# Authors:
# Ambra Di Piano <ambra.dipiano@inaf.it>
# *******************************************************************************

import yaml
import argparse
import numpy as np
from os import listdir, system
from os.path import join, isdir, isfile, basename
from sagsci.tools.utils import get_absolute_path
from rtamock.tools.utils import set_logger

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--configfile", default="myconfig.yml", help="configuration file")
args = parser.parse_args()

# get YAML configuration
with open(args.configfile) as configuration:
    config = yaml.load(configuration, Loader=yaml.FullLoader)
dataset = config['dirlist']['data']
runid = config['run']['runid']
wrapper = config['wrapper'].upper()

# logging
logname = join(config["dirlist"]["archive"].replace("XXX", str(config["run"]["runid"])), basename(__file__).replace('.py','.log'))
log = set_logger(filename=logname, level=config['loglevel'])
log.info('Logging: ' + logname)

# get all time bins in run
log.info(f'Collect timebins in run {runid}')
datapath = join(get_absolute_path(dataset), str(runid))
subdirs = np.sort([join(datapath, d) for d in listdir(datapath) if isdir(join(datapath, d))])

# loop all time bins
new_dir = join(datapath, f"analysis_{config['run']['nbins']}_bins_{config['run']['type']}")
system(f'mkdir {new_dir}')
for d in subdirs:
    # check all files are there
    system(f'cd {datapath}')
    if not isfile(join(d, 'obs.xml')):
        log.error(f'Missing obs.xml in: {d}')
    elif not isfile(join(d, 'job.xml')):
        log.error(f'Missing job.xml in: {d}')
    elif not isfile(join(d, 'target.xml')):
        log.error(f'Missing target.xml in: {d}')
    elif not isfile(join(d, basename(d)+'.fits')):
        log.error(f'Missing {basename(d)}.fits in: {d}')
    
    # run time bin analysis
    log.info(f'Execute analysis of: {basename(d)}')
    system(f'python ${wrapper.upper()}/execute.py -obs {d}/obs.xml -job {d}/job.xml -target {d}/target.xml -evt {d}/{basename(d)}.fits')

    # move bin in new_dir
    system(f'mv {d} {new_dir}')

# move new_dir in archive
archive_dir = config["dirlist"]["archive"].replace("XXX", str(config["run"]["runid"]))
system(f'mv {new_dir} {archive_dir}')

# close
log.info(f'Analysis of run {runid} completed with {wrapper.upper()} science tool.')



