"""Utilities to help with the execution of miriad tasks and C3171 project data. 
"""

import subprocess as sp
from scipy.optimize import curve_fit
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pymir as pymir
from pymir import mirstr as m
from astropy.time import Time
import astropy.units as u
import os

# Added the mirstr as a package from github tjgalvin
# Hack until reduction scripts are updated
mirstr = pymir.mirstr

primary = '1934-638'
secondary = '0327-241'
science = 'c3171'

chan_ref_7 = 6676 
flags_7 = {'chan_start':[7866-chan_ref_7, 8058-chan_ref_7, 8177-chan_ref_7, 7747-chan_ref_7, 1058, 670, 851, 788],
           'chan_end'  :[7896-chan_ref_7, 8088-chan_ref_7, 8207-chan_ref_7, 7777-chan_ref_7, 1065, 680, 857, 810]}

flags_9 = {'chan_start':[850],
           'chan_end'  :[900]}


def uvflag(vis, flag_def):
    if len(flag_def['chan_start']) != len(flag_def['chan_end']):
        raise ValueError('Chanels star and end should have the same length')
        
    for start, end in zip(flag_def['chan_start'], flag_def['chan_end']):
        line = f"chan,{end-start},{start},1"
        print(line)
        proc = mirstr(f"uvflag vis={vis} line={line} flagval=flag").run()
        print(proc)

def mfcal_flux(fit, ifcal=1):
    nu_0 = fit[2]
    fact = fit[3]

    if ifcal == 1:
        flux_str = f"{10.**(fit[1][0]):.4f},{nu_0:.1f},{fit[0][1]:.4f}"
        # flux_str = f"{10.**(fit[0][0]+fact):.4f},{nu_0:.1f},{fit[0][1]:.4f}"
        # flux_str = f"{10.**(fit[0][0]):.4f},{nu_0:.1f},{fit[0][1]:.4f}"
    else:
        flux_str = f"{10.**fit[1][0]:.4f},{nu_0:.1f},{fit[1][1]:.4f}"
        
    return flux_str

def pl(nu, *p):
    """Polynomial model to fit to spectra. To be consistent
    with uvfmeas options=log, data should be logged when given
    to the fitting method (i.e. curve_fit)
    
    Arguments:
        nu {numpy.ndarray} -- Frequency of the data. Divide data by nu_0 outsid eof method
    
    Returns:
       spec {numpy.ndarray} -- Modelled spectrum
    """
    spec = np.zeros_like(nu)
    for index, val in enumerate(p):
        spec += val * nu ** index

    return spec


def model_secondary(plot=False, nu_0=8.6):
    """Function to scale IF1 onto IF2. 

    Assumes that it is being called from a `Date` folder with an
    initial calibration
    """

    df7 = pd.read_csv(f'Plots_notsys/secondary_uvfmeas_7700_log.txt', names=('nu','s_nu','s_model'), delim_whitespace=True)
    df9 = pd.read_csv(f'Plots_notsys/secondary_uvfmeas_9500_log.txt', names=('nu','s_nu','s_model'), delim_whitespace=True)
    
    nu7, snu7 = np.log10(df7['nu'].values/nu_0), np.log10(df7['s_nu'].values)
    nu9, snu9 = np.log10(df9['nu'].values/nu_0), np.log10(df9['s_nu'].values)
    
    p0 = (np.log10(1.), -0.3)
    fit7 = curve_fit(pl, nu7, snu7, p0)
    fit9 = curve_fit(pl, nu9, snu9, p0)
    
    # fact = fit7[0][0] - fit9[0][0]
    # fact = 0
    nom7 = np.median(pl(nu7[-50:], *fit7[0]))
    nom9 = np.median(pl(nu9[:50], *fit9[0]))
    fact = nom7 - nom9

    if plot:
        fig, (ax,ax1) = plt.subplots(2,1, figsize=(10,8))

        ax.plot(10**nu7, 10**snu7)
        ax.plot(10**nu7, 10**pl(nu7, *fit7[0]))

        ax.plot(10**nu9, 10**snu9)
        ax.plot(10**nu9, 10**pl(nu9, *fit9[0]))

        ax1.plot(10**nu7, 10**(snu7-fact))
        ax1.plot(10**nu7, 10**(pl(nu7, *fit7[0])-fact))

        ax1.plot(10**nu9, 10**snu9)
        ax1.plot(10**nu9, 10**pl(nu9, *fit9[0]))

        fig.show()
    
    return (fit7[0], fit9[0], nu_0, fact)


def flag_cycle(s: pd.Series, selection: str='flagging.txt', delta: int=2):
    """Construct a miriad selection time() statement to flag out a integration cycle
    assuming a `cain cycle` of 10
    
    Arguments:
        s {pd.Series} -- A row of a pandas dataframe produced using `uvdump`
    
    Keyword Arguments:
        selection {str} -- The file to place select time()'s into (default: {'flagging.txt'})
        delta {int} -- Time range to flag around (default: {5})
    """

    t1 = (Time(s['time'], format='jd')-delta*u.second).datetime.strftime('%y%b%d:%H:%M:%S')
    t2 = (Time(s['time'], format='jd')+delta*u.second).datetime.strftime('%y%b%d:%H:%M:%S')
    
    select = f"time({t1},{t2})"
    
    with open(selection, 'a') as out_file:
        print(select, file=out_file)
    

def flag_inttime(uv: str, threshold: int=9, logfile: str='dump.txt', selection: str='flagging.txt', 
                 delete: bool=False):
    """Flag out short integration cycles from a uv-file
    
    Arguments:
        uv {str} -- uv-file to flag
    
    Keyword Arguments:
        threshold {int} -- Minimum length of time for each cycle (default: {9})
        logfile {str} -- File to `uvdump` to (default: {'dump.txt'})
        selection {str} -- File to place select statements in (default: {'flagging.txt'})
        delete {bool} -- Clean up log files (default: {False})
    """

    uvdump = m(f"uvdump vis={uv} vars=inttime,ant1,ant2,time,source log={logfile}").run()
    print(uvdump)
    
    var = pd.read_csv(logfile, names=('inttime','ant1','ant2','time','source'))
    var = var[(var['ant1'].values==1)&(var['ant2'].values==2)] # Smaller list of selects
    
    var[var['inttime']<threshold].apply(flag_cycle, axis=1, selection=selection)
    
    uvflag = m(f"uvflag vis={uv} select=@{selection} flagval=flag").run()
    print(uvflag)
    
    if delete:
        os.remove(logfile)
        os.remove(selection)        
