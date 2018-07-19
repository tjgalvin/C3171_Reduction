"""Example code to flag a dataset based on the `inttime` variable of each record. Although
`qvack` can flag the initial integration of each source, it does not consider the integration
time. 
"""

import os
import pandas as pd
from astropy.time import Time
import astropy.units as u
from pymir import mirstr as m


def flag_cycle(s: pd.Series, selection: str='flagging.txt', delta: int=5):
    """Construct a miriad selection time() statement to flag out a integration cycle
    assuming a `cain cycle` of 10
    
    Arguments:
        s {pd.Series} -- A row of a pandas dataframe produced using `uvdump`
    
    Keyword Arguments:
        selection {str} -- The file to place select time()'s into (default: {'flagging.txt'})
        delta {int} -- Time range to flag around (default: {5})
    """

    t1 = (Time(s['time'], format='jd')-5*u.second).datetime.strftime('%y%b%d:%H:%M:%S')
    t2 = (Time(s['time'], format='jd')+5*u.second).datetime.strftime('%y%b%d:%H:%M:%S')
    
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



flag_inttime('Data/data1_test.uv/', threshold=9, delete=True)

