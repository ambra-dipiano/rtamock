# *******************************************************************************
# Copyright (C) 2022 INAF
#
# This software is distributed under the terms of the BSD-3-Clause license
#
# Authors:
# Ambra Di Piano <ambra.dipiano@inaf.it>
# *******************************************************************************

import logging
import numpy as np
from re import compile, escape, DOTALL
from os import system, makedirs, remove
from astropy.io import fits
from sagsci.tools.fits import Fits
from os.path import dirname, isdir, isfile

def get_level_code(level):
    if level.lower() == 'debug':
        level = 10
    elif level.lower() == 'info':
        level = 20
    elif level.lower() == 'warning':
        level = 30
    elif level.lower() == 'error':
        level = 40
    elif level.lower() == 'critical':
        level = 50
    else:
        level = 0
    return level

def set_logger(filename, level):
    if isfile(filename):
        remove(filename)
    if not isdir(dirname(filename)):
        makedirs(dirname(filename))
    log = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s|%(filename)s|l%(lineno)d|%(levelname)s| %(message)s')
    fileHandler = logging.FileHandler(filename)
    fileHandler.setFormatter(formatter)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    log.addHandler(fileHandler)
    log.addHandler(consoleHandler)
    if type(level) == str:
        level = get_level_code(level)
    log.setLevel(level)
    return log

def bool2int(val):
    if val is True:
        return 1
    else:
        return 0

def get_obj_pointing(fitsfile):
    with fits.open(fitsfile) as h:
        ra = h['EVENTS'].header['RA_OBJ']
        dec = h['EVENTS'].header['DEC_OBJ']
    return {'ra': ra, 'dec': dec}

def get_obs_GTI(fitsfile):
    with fits.open(fitsfile) as h:
        GTI = h['GTI'].data[0]
    return GTI

def split_observation(fitsfile, nbins, type='lightcurve'):
    GTI = get_obs_GTI(fitsfile=fitsfile)
    edges = np.linspace(GTI[0], GTI[1], num=nbins+1)
    bins = []
    for i in range(len(edges)-1):
        selection = fitsfile.replace(".fits", f"_{edges[i]}_{edges[i+1]}.fits")
        system(f'cp {fitsfile} {selection}')
        bins.append(selection)
    
        f = Fits()
        pointing = {'ra': f.get_dl3_hdr(selection)['RA_PNT'], 'dec': f.get_dl3_hdr(selection)['DEC_PNT']}
        dl3 = f.get_dl3_data(selection)
        if type.lower() == 'lightcurve':
            dl3_selected = f.selection_cuts(dl3, pointing, trange=[edges[i], edges[i+1]])
            f.set_dl3_data(selection, dl3_selected, GTI=[edges[i], edges[i+1]])
        elif type.lower() == 'cumulative':
            dl3_selected = f.selection_cuts(dl3, pointing, trange=[edges[0], edges[i+1]])
            f.set_dl3_data(selection, dl3_selected, GTI=[edges[0], edges[i+1]])
        else:
            raise ValueError(f'Type "{type.lower()}" not allowed.')

    return bins

def multiple_replace(string, rep_dict):
    pattern = compile("|".join([escape(k) for k in sorted(rep_dict,key=len,reverse=True)]), flags=DOTALL)
    return pattern.sub(lambda x: rep_dict[x.group(0)], string)