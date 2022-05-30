# *******************************************************************************
# Copyright (C) 2021 INAF
#
# This software is distributed under the terms of the BSD-3-Clause license
#
# Authors:
# Ambra Di Piano <ambra.dipiano@inaf.it>
# *******************************************************************************

import csv
import argparse
from turtle import bk
import numpy as np
import xml.etree.ElementTree as ET
from os import listdir, makedirs
from os.path import join, isdir, expandvars, isfile
from sagsci.tools.utils import str2bool
from sagsci.tools.myxml import MyXml

# get line command options
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--directories', default=['data/crab/run1/job1', 'data/crab/run2/job1', 'data/crab/run3/job1', 'data/crab/run4/job1'], help='list of folders of wobble runs to display results from')
parser.add_argument('-s', '--source', type=str, default='Crab', help='target of the observation')
parser.add_argument('-lc', '--lightcurve', type=str, default='true', choices=['true', 'false'], help='collect the lightcurve from results files of single bins')
parser.add_argument('-c', '--cumulative', type=str, default='true', choices=['true', 'false'], help='collect the lightcurve from results files of single bins')
parser.add_argument('-o', '--output', type=str, default='output', help='output folder')
args = parser.parse_args()

if type(args.directories) is not list:
    args.directories = [args.directories]
print(f'Directories: {args.directories}')

if str2bool(args.lightcurve):
    if not isdir(args.output):
        makedirs(args.output)
    f = open(join(args.output, 'lightcurve.txt'), 'w')
    w = csv.writer(f, delimiter=' ')
    hdr = ['time', 'time_err', 'excess', 'excess_err', 'sigma', 'sigma_err', 'flux', 'flux_err', 'bkg', 'bkg_err', 'emin', 'emax']
    w.writerow(hdr)
    f.close()

if str2bool(args.lightcurve):
    if not isdir(args.output):
        makedirs(args.output)
    f = open(join(args.output, 'cumulative.txt'), 'w+')
    w = csv.writer(f, delimiter=' ')
    hdr = ['time', 'time_err', 'excess', 'excess_err', 'sigma', 'sigma_err', 'flux', 'flux_err', 'bkg', 'bkg_err', 'emin', 'emax']
    w.writerow(hdr)
    f.close()

# loop directories
if args.lightcurve:
    for d in args.directories:
        bins = [join(d, b) for b in listdir(d) if isdir(join(d, b))]
        for b in bins:
            # get from results
            try:
                results = [join(b, f) for f in listdir(b) if isfile(join(b, f)) and '_results.xml' in f][0]
            except IndexError:
                continue
            xml = MyXml(results)
            excess = xml.get_job_results(source=args.source, parameter='Photometric', attribute='excess')
            excess_err = xml.get_job_results(source=args.source, parameter='Photometric', attribute='excess_err')
            bkg = xml.get_job_results(source=args.source, parameter='Photometric', attribute='off_counts')
            bkg_err = np.sqrt(bkg)
            sigma = xml.get_job_results(source=args.source, parameter='Significance', attribute='value')
            sigma_err = xml.get_job_results(source=args.source, parameter='Significance', attribute='error')
            flux = xml.get_job_results(source=args.source, parameter='IntegratedFlux', attribute='value')
            flux_err = xml.get_job_results(source=args.source, parameter='IntegratedFlux', attribute='error')
            xml.close_xml()
            # get from job configuration
            job = [join(b, f) for f in listdir(b) if isfile(join(b, f)) and 'job.xml' in f][0]
            xml = open(job)
            jobconf = ET.parse(xml)
            tmin = float(jobconf.find('parameter[@name="TimeIntervals"]').attrib['tmin'])
            tmax = float(jobconf.find('parameter[@name="TimeIntervals"]').attrib['tmax'])
            tmean = (tmin + tmax)/2
            terror = (tmax - tmin)/2
            emin = float(jobconf.find('parameter[@name="Energy"]').attrib['emin'])
            emax = float(jobconf.find('parameter[@name="Energy"]').attrib['emax'])
            xml.close()
            # write row to file
            f = open(join(args.output, 'lightcurve.txt'), 'a')
            w = csv.writer(f, delimiter=' ')
            row = [tmean, terror, excess, excess_err, sigma, sigma_err, flux, flux_err, bkg, bkg_err, emin, emax]
            w.writerow(row)
            f.close()

