# *******************************************************************************
# Copyright (C) 2022 INAF
#
# This software is distributed under the terms of the BSD-3-Clause license
#
# Authors:
# Ambra Di Piano <ambra.dipiano@inaf.it>
# *******************************************************************************

from os import system
import yaml
import argparse
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sagsci.tools.utils import get_absolute_path, str2bool

# get line command options
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--configfile", default="myconfig.yml", help="configuration YAML file")
parser.add_argument("-cp", "--copyfiles", default="false", help="copy plot files in repository dir")
args = parser.parse_args()

# get YAML configuration
configuration = open(args.configfile)
config = yaml.load(configuration, Loader=yaml.FullLoader)

def plot_significance(data):
    plt.errorbar(x=data['time'], y=data['sigma'], xerr=data['time_err'], fmt='bo', barsabove=True, label='Li&Ma Significance')    
    plt.ylabel(r'$\sigma$', fontsize=fs)

def plot_excess(data):
    plt.errorbar(x=data['time'], y=data['excess'], xerr=data['time_err'], yerr=data['excess_err'], fmt='bo', barsabove=True, label='excess counts')
    plt.ylabel('counts', fontsize=fs)

def plot_flux(data):
    plt.yscale('log')
    plt.errorbar(x=data['time'], y=data['flux'], xerr=data['time_err'], yerr=data['flux_err'], fmt='bo', barsabove=True, label='integrated flux')
    plt.ylabel('F (ph/cm2/s)', fontsize=fs)

def plot_background(data):
    plt.errorbar(x=data['time'], y=data['off_counts'], xerr=data['time_err'], yerr=np.sqrt(data['off_counts']), fmt='bo', barsabove=True, label='background')
    plt.ylabel('counts', fontsize=fs)

def plot_counts(data):
    plt.errorbar(x=data['time'], y=data['off_counts']/3, xerr=data['time_err'], yerr=np.sqrt(data['off_counts']/3), fmt='bo', barsabove=True, label=r'$\alpha\cdot$Noff')
    plt.errorbar(x=data['time'], y=data['on_counts'], xerr=data['time_err'], yerr=np.sqrt(data['on_counts']), fmt='g^', barsabove=True, label='Non')
    plt.ylabel('counts', fontsize=fs)

data = pd.DataFrame()
for f in config['plot']['data']:
    datafile = get_absolute_path(f)
    data.join(pd.read_csv(datafile, sep=' ', header=0))

data['time'] = data['time'] - data['time'].min()

which = config['plot']['which']
fs = 16
for w in which:
    fig = plt.figure(figsize=(10, 4))
    plt.title(f"RUN{config['run']['runid']}: {config['source']} E({data['emin'][0]} - {data['emax'][0]}) TeV", fontsize=fs)
    plt.tick_params(axis='both', labelsize=fs)
    plt.xlabel('time (s)', fontsize=fs)

    if w.lower() == 'background':
        plot_background(data=data)
    elif w.lower() == 'counts':
        plot_counts(data=data)
    elif w.lower() == 'excess':
        plot_excess(data=data)
    elif w.lower() == 'significance':
        plot_significance(data=data)
    elif w.lower() == 'flux':
        plot_flux(data=data)

    plt.grid()
    plt.legend()

    plt.tight_layout()
    outname = get_absolute_path(config['plot']['data']).replace('.csv', f'_{w}.png') 
    plt.savefig(outname)

    if str2bool(args.copyfiles):
        system(f'cp {outname} .')
        system(f'cp {datafile} .')










