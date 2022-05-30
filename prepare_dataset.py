# *******************************************************************************
# Copyright (C) 2021 INAF
#
# This software is distributed under the terms of the BSD-3-Clause license
#
# Authors:
# Ambra Di Piano <ambra.dipiano@inaf.it>
# *******************************************************************************

import yaml
import argparse
import logging
import numpy as np
import xml.etree.ElementTree as ET
from os import listdir, system
from os.path import join, isdir, expandvars, isfile, basename
from sagsci.tools.utils import get_obs_pointing
from utils import get_obs_GTI, split_observation

# get line command options
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--configfile", default="myconfig.yml", help="configuration YAML file")
args = parser.parse_args()

# get YAML configuration
configuration = open(args.configfile)
config = yaml.load(configuration, Loader=yaml.FullLoader)
runid = config["run"]["runid"]

# set logging leve
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# list all fits inside $DATA directory
datapath = join(expandvars(config['dirlist']['data']), str(runid))
log.info(f'Preparing dataset: {datapath}')
bins = [join(datapath, f) for f in listdir(datapath) if isfile(join(datapath, f)) and '.fits' in f]

# if only one fits in $DATA directory split observation otherwise skip
if len(bins) == 1:
    nbins = int(config['run']['nbins'])
    log.info(f'Splitting observation in {nbins}')
    bins = split_observation(fitsfile=bins[0], nbins=nbins)

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
bins = [join(datapath, d) for d in listdir(datapath) if isdir(join(datapath, d))]
log.info('Prepare job.xml files')
for b in bins:
    fitsfile = join(b, basename(b)+'.fits')
    tstart, tstop = get_obs_GTI(fitsfile=fitsfile)
    pointing = get_obs_pointing(filename=fitsfile)
    jobfile = join(b, 'job.xml')
    job = open(jobfile)
    jobconf = ET.parse(job)
    prm = jobconf.find('parameter[@name="TimeIntervals"]')
    prm.set('tmin', str(tstart))
    prm.set('tmax', str(tstop))
    prm = jobconf.find('parameter[@name="DirectoryList"]')
    prm.set('job', datapath)  
    respath = join(b, 'results') 
    prm.set('results', respath)   
    prm.set('prefix', f"analysis")   
    prm = jobconf.find('parameter[@name="RegionOfInterest"]')
    prm.set('ra', str(pointing['ra']))
    prm.set('dec', str(pointing['dec']))
    jobconf.write(join(datapath, 'job.xml'), encoding="UTF-8", xml_declaration=True)
    job.close()

# modify obs.xml per each bin in $DATA
bins = [join(datapath, d) for d in listdir(datapath) if isdir(join(datapath, d))]
log.info('Prepare obs.xml files')
for b in bins:
    obsfile = join(b, 'obs.xml')
    obs = open(obsfile)
    obsconf = ET.parse(obs)
    prm = obsconf.find('parameter[@name="GoodTimeIntervals"]')
    prm.set('tstartreal', str(tstart))
    prm.set('tendreal', str(tstop))
    prm.set('tstartplanned', str(tstart))
    prm.set('tendplanned', str(tstart))
    prm = obsconf.find('parameter[@name="RegionOfInterest"]')
    prm.set('ra', str(pointing['ra']))
    prm.set('dec', str(pointing['dec']))
    prm = obsconf.find('parameter[@name="Pointing"]')
    prm.set('ra', str(pointing['ra']))
    prm.set('dec', str(pointing['dec']))
    obsconf.write(join(datapath, 'obs.xml'), encoding="UTF-8", xml_declaration=True)
    job.close()
