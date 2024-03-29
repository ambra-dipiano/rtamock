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
import matplotlib.pyplot as plt
import pandas as pd
from os import system
from os.path import join, basename
from sagsci.tools.utils import get_absolute_path, str2bool
from rtamock.tools.utils import set_logger

# get line command options
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--configfile", default="myconfig.yml", help="configuration YAML file")
parser.add_argument("-cp", "--copyfiles", default="false", help="copy plot files in repository dir")
args = parser.parse_args()

# get YAML configuration
configuration = open(args.configfile)
config = yaml.load(configuration, Loader=yaml.FullLoader)

# logging
logname = join(get_absolute_path(config["logging"]["folder"]), basename(__file__).replace('.py','.log'))
log = set_logger(filename=logname, level=config["logging"]['level'])
log.info('Logging: ' + logname)

def plot_significance(data, xerr=True):
    if xerr:
        plt.errorbar(x=data['time'], y=data['sigma'], xerr=data['time_err'], fmt='bo', barsabove=True, label='Li&Ma Significance')    
    else:
        plt.errorbar(x=data['time'], y=data['sigma'], fmt='bo', barsabove=True, label='Li&Ma Significance')    
    plt.ylabel(r'$\sigma$', fontsize=fs)

def plot_excess(data, xerr=True):
    if xerr:
        plt.errorbar(x=data['time'], y=data['excess'], xerr=data['time_err'], yerr=data['excess_err'], fmt='bo', barsabove=True, label='excess counts')
    else:
        plt.errorbar(x=data['time'], y=data['excess'], yerr=data['excess_err'], fmt='bo', barsabove=True, label='excess counts')
    plt.ylabel('counts', fontsize=fs)

def plot_flux(data, xerr=True):
    plt.yscale('log')
    if xerr:
        plt.errorbar(x=data['time'], y=data['flux'], xerr=data['time_err'], yerr=data['flux_err'], fmt='bo', barsabove=True, label='integrated flux')
    else:
        plt.errorbar(x=data['time'], y=data['flux'], yerr=data['flux_err'], fmt='bo', barsabove=True, label='integrated flux')
    plt.ylabel('F (ph/cm2/s)', fontsize=fs)

def plot_background(data, xerr=True):
    if xerr:
        plt.errorbar(x=data['time'], y=data['off_counts'], xerr=data['time_err'], yerr=np.sqrt(data['off_counts']), fmt='bo', barsabove=True, label='background')
    else:
        plt.errorbar(x=data['time'], y=data['off_counts'], yerr=np.sqrt(data['off_counts']), fmt='bo', barsabove=True, label='background')
    plt.ylabel('counts', fontsize=fs)

def plot_counts(data, xerr=True):
    if xerr:
        plt.errorbar(x=data['time'], y=data['off_counts']/3, xerr=data['time_err'], yerr=np.sqrt(data['off_counts']/3), fmt='bo', barsabove=True, label=r'$\alpha\cdot$Noff')
        plt.errorbar(x=data['time'], y=data['on_counts'], xerr=data['time_err'], yerr=np.sqrt(data['on_counts']), fmt='g^', barsabove=True, label='Non')
    else:
        plt.errorbar(x=data['time'], y=data['off_counts']/3, yerr=np.sqrt(data['off_counts']/3), fmt='bo', barsabove=True, label=r'$\alpha\cdot$Noff')
        plt.errorbar(x=data['time'], y=data['on_counts'], yerr=np.sqrt(data['on_counts']), fmt='g^', barsabove=True, label='Non')
    plt.ylabel('counts', fontsize=fs)

datafile = get_absolute_path(config['plot']['data']).replace('XXX', str(config['run']['runid'])).replace('YYY', config['run']['type']).replace('ZZZ', str(config['run']['nbins']))
data = pd.read_csv(datafile, sep=' ', header=0)
log.debug(f'bins = [{data["time"].min()}, {data["time"].max()}]')
data['time'] = data['time'] - data['time'].min()
log.debug(f'bins = [{data["time"].min()}, {data["time"].max()}]')
log.debug(f'time = [{data["tmin"].min()}, {data["tmax"].max()}]')
log.debug(f'Len table = {len(data)}')

which = config['plot']['which']
fs = 16
for w in which:
    fig = plt.figure(figsize=(10, 4))
    plt.title(f"RUN{config['run']['runid']}: {config['source']} E({data['emin'][0]} - {data['emax'][0]}) TeV", fontsize=fs)
    plt.tick_params(axis='both', labelsize=fs)
    plt.xlabel('time (s)', fontsize=fs)

    if config['run']['type'].lower() == 'cumulative':
        xerr = False
    else:
        xerr = True

    if w.lower() == 'background':
        plot_background(data=data, xerr=xerr)
    elif w.lower() == 'counts':
        plot_counts(data=data, xerr=xerr)
    elif w.lower() == 'excess':
        plot_excess(data=data, xerr=xerr)
    elif w.lower() == 'significance':
        plot_significance(data=data, xerr=xerr)
    elif w.lower() == 'flux':
        plot_flux(data=data, xerr=xerr)

    plt.grid()
    plt.legend()

    plt.tight_layout()
    outname = get_absolute_path(config['plot']['data']).replace('XXX', str(config['run']['runid'])).replace('YYY', config['run']['type']).replace('ZZZ', str(config['run']['nbins'])).replace('.csv', f'_{w}.png') 
    plt.savefig(outname)
    log.info(f'Saved {w} lightcurve: {outname}')

    if str2bool(args.copyfiles):
        log.info('Copy figure to workspace.')
        system(f'cp {outname} .')









