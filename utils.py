# *******************************************************************************
# Copyright (C) 2022 INAF
#
# This software is distributed under the terms of the BSD-3-Clause license
#
# Authors:
# Ambra Di Piano <ambra.dipiano@inaf.it>
# *******************************************************************************

from re import compile, escape, DOTALL
import numpy as np
from os import system
from astropy.io import fits
from sagsci.tools.fits import Fits

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