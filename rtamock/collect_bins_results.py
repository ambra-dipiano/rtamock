# *******************************************************************************
# Copyright (C) 2021 INAF
#
# This software is distributed under the terms of the BSD-3-Clause license
#
# Authors:
# Ambra Di Piano <ambra.dipiano@inaf.it>
# *******************************************************************************

import yaml
import numpy as np
import argparse
import xml.etree.ElementTree as ET
from os import listdir
from os.path import join, isdir, basename
from sagsci.tools.utils import get_absolute_path
from sagsci.tools.myxml import MyXml
from rtamock.tools.utils import set_logger


parser = argparse.ArgumentParser()
parser.add_argument("-f", "--configfile", default="myconfig.yml", help="configuration file")
args = parser.parse_args()

# get YAML configuration
configuration = open(args.configfile)
config = yaml.load(configuration, Loader=yaml.FullLoader)

# logging
logname = join(get_absolute_path(config["logging"]["folder"]), basename(__file__).replace('.py','.log'))
log = set_logger(filename=logname, level=config["logging"]['level'])
log.info('Logging: ' + logname)

# get all time bins in run
log.info(f'Collect timebins in run {config["run"]["runid"]}')
datapath = join(get_absolute_path(config["dirlist"]["archive"]).replace('XXX', str(config['run']['runid'])), f"analysis_{config['run']['nbins']}_bins_{config['run']['type']}")
subdirs = np.sort([join(datapath, d) for d in listdir(datapath) if isdir(join(datapath, d))])

datafile = join(datapath, f'run{config["run"]["runid"]}_{config["run"]["type"]}_{config["run"]["nbins"]}bins.csv')

# create and clear file
f = open(datafile, 'w+')
hdr = "tmin tmax time time_err excess excess_err sigma sigma_err flux flux_err on_counts off_counts alpha emin emax\n"
f.writelines([hdr])

# loop all time bins
for idx, d in enumerate(subdirs):

    # get from job configuration
    job = join(datapath, d, 'job.xml')
    xml = open(job)
    jobconf = ET.parse(xml)
    tmin = float(jobconf.find('parameter[@name="TimeIntervals"]').attrib['tmin'])
    tmax = float(jobconf.find('parameter[@name="TimeIntervals"]').attrib['tmax'])
    #tmean = (tmin + tmax)/2
    tmean = tmax
    terror = (tmax - tmin)/2
    log.debug(f'time = [{tmin}, {tmax}], exposure = {tmax-tmin}')
    log.debug(f'bin center = [{tmean}]')
    emin = float(jobconf.find('parameter[@name="Energy"]').attrib['emin'])
    emax = float(jobconf.find('parameter[@name="Energy"]').attrib['emax'])
    xml.close()

    # get from results.xml file
    results = join(datapath, d, 'results', basename(d)+'_results.xml')
    xml = MyXml(results)
    source = xml.get_source_name()
    excess = xml.get_job_results(source=source, parameter='Photometric', attribute='excess')
    excess_err = xml.get_job_results(source=source, parameter='Photometric', attribute='excess_err')
    off_counts = xml.get_job_results(source=source, parameter='Photometric', attribute='off_counts')
    off_err = np.sqrt(off_counts)
    alpha = xml.get_job_results(source=source, parameter='Photometric', attribute='alpha')
    on_counts = xml.get_job_results(source=source, parameter='Photometric', attribute='on_counts')
    on_err = np.sqrt(on_counts)
    sigma = xml.get_job_results(source=source, parameter='Significance', attribute='value')
    sigma_err = xml.get_job_results(source=source, parameter='Significance', attribute='error')
    flux = xml.get_job_results(source=source, parameter='IntegratedFlux', attribute='value')
    flux_err = xml.get_job_results(source=source, parameter='IntegratedFlux', attribute='error')
    xml.close_xml()

    # write to file
    row = f"{tmin} {tmax} {tmean} {terror} {excess} {excess_err} {sigma} {sigma_err} {flux} {flux_err} {on_counts} {off_counts} {alpha} {emin} {emax}\n"
    f.writelines([row])

f.close()
log.info(f'Results collected in: {datafile}')
