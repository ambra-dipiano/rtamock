# *******************************************************************************
# Copyright (C) 2022 INAF
#
# This software is distributed under the terms of the BSD-3-Clause license
#
# Authors:
# Ambra Di Piano <ambra.dipiano@inaf.it>
# *******************************************************************************

import argparse
import logging
from os import listdir, system
from os.path import join, isdir, isfile, basename
from sagsci.tools.utils import get_absolute_path

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dataset", default="$DATA", help="directory to dataset")
parser.add_argument("-w", "--wrapper", type=str, default='rtaph', help="runid")
parser.add_argument("-r", "--run", type=str, required=True, help="runid")
args = parser.parse_args()

# set logging level
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# get all time bins in run
log.info(f'Collect timebins in run {args.run}')
datapath = join(get_absolute_path(args.dataset), args.run)
subdirs = [join(datapath, d) for d in listdir(datapath) if isdir(join(datapath, d))]

# loop all time bins
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
    system(f'python ${args.wrapper.upper()}/execute.py -obs $DATA/{args.run}/{basename(d)}/obs.xml -job $DATA/{args.run}/{basename(d)}/job.xml -target $DATA/{args.run}/{basename(d)}/target.xml -evt $DATA/{args.run}/{basename(d)}/{basename(d)}.fits')


log.info(f'Analysis of run {args.run} completed with {args.wrapper.upper()} science tool.')


