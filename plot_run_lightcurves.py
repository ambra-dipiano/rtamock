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
from sagsci.tools.utils import get_absolute_path

# get line command options
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--configfile", default="myconfig.yml", help="configuration YAML file")
args = parser.parse_args()

# get YAML configuration
configuration = open(args.configfile)
config = yaml.load(configuration, Loader=yaml.FullLoader)
datafile = get_absolute_path(config['plot']['data'])

def plot_significance(data):
    plt.errorbar(x=data['time'], y=data['sigma'], xerr=data['time_err'], yerr=data['sigma_err'], fmt='ro', barsabove=True, label='Li&Ma Significance')

def plot_excess(data):
    plt.errorbar(x=data['time'], y=data['excess'], xerr=data['time_err'], yerr=data['excess_err'], fmt='ro', barsabove=True, label='excess counts')

def plot_flux(data):
    plt.yscale('log')
    plt.errorbar(x=data['time'], y=data['flux'], xerr=data['time_err'], yerr=data['flux_err'], fmt='ro', barsabove=True, label='integrated flux')

def plot_background(data):
    plt.errorbar(x=data['time'], y=data['off_counts'], xerr=data['time_err'], yerr=np.sqrt(data['off_counts']), fmt='ro', barsabove=True, label='background')

def plot_counts(data):
    plt.errorbar(x=data['time'], y=data['off_counts'], xerr=data['time_err'], yerr=np.sqrt(data['off_counts']), fmt='ro', barsabove=True, label='off counts')
    plt.errorbar(x=data['time'], y=data['on_counts'], xerr=data['time_err'], yerr=np.sqrt(data['on_counts']), fmt='g^', barsabove=True, label='on counts')


df = pd.read_csv(datafile, sep=' ', header=0)
which = config['plot']['which']
fs = 16
for w in which:
    fig = plt.figure(figsize=(10, 4))
    plt.title(f"{config['source']} - {config['run']['runid']}", fontsize=fs)
    plt.tick_params(axis='both', labelsize=fs)
    plt.xlabel('MJD', fontsize=fs)
    plt.ylabel(w, fontsize=fs)

    if w.lower() == 'background':
        plot_background(data=df)
    elif w.lower() == 'counts':
        plot_counts(data=df)
    elif w.lower() == 'excess':
        plot_excess(data=df)
    elif w.lower() == 'significance':
        plot_significance(data=df)
    elif w.lower() == 'flux':
        plot_flux(data=df)

    plt.grid()
    plt.legend()

    plt.tight_layout()
    outname = get_absolute_path(config['plot']['data']).replace('.txt', f'_{w}.png') 
    plt.savefig(outname)










