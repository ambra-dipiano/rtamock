# *******************************************************************************
# Copyright (C) 2021 INAF
#
# This software is distributed under the terms of the BSD-3-Clause license
#
# Authors:
# Ambra Di Piano <ambra.dipiano@inaf.it>
# *******************************************************************************

import csv
import numpy as np
import argparse
import logging
import xml.etree.ElementTree as ET
from os import listdir
from os.path import join, isdir, basename
from sagsci.tools.utils import get_absolute_path
from sagsci.tools.myxml import MyXml


parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dataset", default="$DATA/analysis_archive", help="directory to dataset")
parser.add_argument("-r", "--run", type=str, required=True, help="runid")
args = parser.parse_args()

# set logging level
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# get all time bins in run
log.info(f'Collect timebins in run {args.run}')
datapath = join(get_absolute_path(args.dataset))
subdirs = np.sort([join(datapath, d) for d in listdir(datapath) if isdir(join(datapath, d))])
datafile = join(datapath, f'run{args.run}_lightcurve_{len(subdirs)}bins.csv')

# create and clear file
f = open(datafile, 'w+')
hdr = "time time_err excess excess_err sigma sigma_err flux flux_err on_counts off_counts alpha emin emax\n"
f.writelines([hdr])

# loop all time bins
for idx, d in enumerate(subdirs):

    # get from job configuration
    job = join(datapath, d, 'job.xml')
    xml = open(job)
    jobconf = ET.parse(xml)
    tmin = float(jobconf.find('parameter[@name="TimeIntervals"]').attrib['tmin'])
    tmax = float(jobconf.find('parameter[@name="TimeIntervals"]').attrib['tmax'])
    tmean = (tmin + tmax)/2
    terror = (tmax - tmin)/2
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
    row = f"{tmean} {terror} {excess} {excess_err} {sigma} {sigma_err} {flux} {flux_err} {on_counts} {off_counts} {alpha} {emin} {emax}\n"
    print(row)
    f.writelines([row])

f.close()
log.info(f'Results collected in: {datafile}')
