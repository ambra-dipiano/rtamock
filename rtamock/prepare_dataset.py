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
import xml.etree.ElementTree as ET
from os import listdir, system
from os.path import join, isdir, expandvars, isfile, basename
from sagsci.tools.utils import get_obs_pointing
from tools.utils import get_obs_GTI, split_observation, bool2int, set_logger

# get line command options
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--configfile", default="myconfig.yml", help="configuration YAML file")
args = parser.parse_args()

# get YAML configuration
configuration = open(args.configfile)
config = yaml.load(configuration, Loader=yaml.FullLoader)
runid = config["run"]["runid"]

# logging
logname = join(config["dirlist"]["data"], basename(__file__).replace('.py','.log'))
log = set_logger(filename=logname, level=config['loglevel'])
log.info('Logging: ' + logname)

# set datapath
datapath = join(expandvars(config['dirlist']['data']), str(runid))

# remove all subfolders in $DATA directory
log.info(f'Remove all subdirs in run directory')
bins = [join(datapath, f) for f in listdir(datapath) if isdir(join(datapath, f))]
for b in bins:
    system(f'rm -r {b}')

# list all fits inside $DATA directory
log.info(f'Preparing dataset: {datapath}')
bins = [join(datapath, f) for f in listdir(datapath) if isfile(join(datapath, f)) and '.fits' in f]

# if only one fits in $DATA directory split observation otherwise skip
if len(bins) == 1:
    nbins = int(config['run']['nbins'])
    log.info(f'Splitting observation in {nbins} time bins')
    bins = split_observation(fitsfile=bins[0], nbins=nbins, type=config['run']['type'])

# create single folders per each fits in $DATA and copy xml files within
for b in bins:
    directory = join(datapath, basename(b).replace('.fits', ''))
    if not isdir(directory):
        system(f'mkdir {directory}')
    system(f'mv {b} {directory}')
    system(f'cp {join(datapath, "target.xml")} {directory}/.')
    system(f'cp data/templates/job.xml {directory}/.')
    system(f'cp data/templates/obs.xml {directory}/.')

# modify job.xml per each bin in $DATA
bins = np.sort([join(datapath, d) for d in listdir(datapath) if isdir(join(datapath, d))])
log.info('Prepare job.xml files')
for b in bins:
    fitsfile = join(b, basename(b)+'.fits')
    tstart, tstop = get_obs_GTI(fitsfile=fitsfile)
    pointing = get_obs_pointing(filename=fitsfile)
    jobfile = join(b, 'job.xml')
    with open(jobfile) as job:
        jobconf = ET.parse(job)
    root = jobconf.getroot()
    prm = root.find('parameter[@name="TimeIntervals"]')
    prm.set('tmin', str(tstart))
    prm.set('tmax', str(tstop))
    prm = root.find('parameter[@name="DirectoryList"]')
    prm.set('job', datapath)  
    respath = join(b, 'results') 
    prm.set('results', respath)   
    prm.set('jobprefix', f"{basename(b)}")   
    prm = root.find('parameter[@name="RegionOfInterest"]')
    prm.set('ra', str(pointing['ra']))
    prm.set('dec', str(pointing['dec']))
    prm = root.find('parameter[@name="Energy"]')
    prm.set('emin', str(config['run']['emin']))
    prm.set('emax', str(config['run']['emax']))
    prm = root.find('parameter[@name="Stack"]')
    prm.set('value', str(bool2int(config['run']['stack'])))
    prm.set('depth', str(config['run']['maxdepth']))
    prm = root.find('parameter[@name="Logging"]')
    prm.set('level', config['loglevel'])
    jobconf.write(jobfile)

# modify obs.xml per each bin in $DATA
log.info('Prepare obs.xml files')
for b in bins:
    obsfile = join(b, 'obs.xml')
    with open(obsfile) as obs:
        obsconf = ET.parse(obs)
    root = obsconf.getroot()
    root.set('name', config['source'])
    root.set('instrument', 'LST-1')
    root.set('id', str(runid))
    prm = root.find('parameter[@name="GoodTimeIntervals"]')
    prm.set('tstartreal', str(tstart))
    prm.set('tendreal', str(tstop))
    prm.set('tstartplanned', str(tstart))
    prm.set('tendplanned', str(tstart))
    prm = root.find('parameter[@name="RegionOfInterest"]')
    prm.set('ra', str(pointing['ra']))
    prm.set('dec', str(pointing['dec']))
    prm = root.find('parameter[@name="Pointing"]')
    prm.set('ra', str(pointing['ra']))
    prm.set('dec', str(pointing['dec']))
    prm = root.find('parameter[@name="Energy"]')
    prm.set('emin', str(config['run']['emin']))
    prm.set('emax', str(config['run']['emax']))
    prm = root.find('parameter[@name="Calibration"]')
    prm.set('database', config['run']['prod'])
    prm.set('response', config['run']['irf'])
    obsconf.write(obsfile)

# modify target.xml per each bin in $DATA
log.info('Prepare target.xml files')
for b in bins:
    targetfile = join(b, 'target.xml')
    with open(targetfile) as t:
        tconf = ET.parse(t)
    root = obsconf.getroot()
    prm = root.find('source')
    root.set('name', config['source'])
    tconf.write(targetfile)
