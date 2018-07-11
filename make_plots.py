"""Script to batch make all plots for all observing days on the calibrated data

It assumes that the reduction_7.py and reduction_9.py scripts have run.
"""
import os
import glob
import mir_utils as mu
from multiprocessing import Pool

def run(s):
    """Function to create mirstr and run
    
    Arguments:
        s {tuple} -- Element one is the miriad task to execute and
                     the second is the working directory to execute in
    """

    task = mu.mirstr(s[0])
    task.run(cwd=s[1])
    print(task)

primary = '1934-638'
secondary = '0327-241'

# Consider droping if1/if2
freqs = ['7700', '9500']

# Should be OK for the moment. No data in 2020's yet
days = glob.glob('Data/201*')

# Tuple of mirstr task to execute and the cwd to pass
# to subprocess.run()
jobs = []

for day in days:
    # Plots can be made if calibrated directories exist
    if os.path.exists(f"{day}/f{freqs[0]}") and os.path.exists(f"{day}/f{freqs[1]}"):
        # Should put checks here for appropriate Plot directories
        for f in freqs:
            a =[(f'uvplt vis=f{f}/{primary}.{f}   axis=time,amp options=nob,nof,2pass stokes=i       device=Plots/primary_timeamp_{f}.png/PNG', day),
                (f'uvplt vis=f{f}/{primary}.{f}   axis=re,im options=nob,nof,eq,2pass stokes=i,q,u,v device=Plots/primary_reim_{f}.png/PNG', day),
                (f'uvplt vis=f{f}/{primary}.{f}   axis=uc,vc options=nob,nof,2pass    stokes=i       device=Plots/primary_ucvc_{f}.png/PNG', day),
                (f'uvplt vis=f{f}/{primary}.{f}   axis=freq,amp options=nob,nof,2pass stokes=i       device=Plots/primary_freqamp_{f}.png/PNG', day),
                (f'uvplt vis=f{f}/{secondary}.{f} axis=time,amp options=nob,nof,2pass stokes=i       device=Plots/secondary_timeamp_{f}.png/PNG', day),
                (f'uvplt vis=f{f}/{secondary}.{f} axis=re,im options=nob,nof,eq,2pass stokes=i,q,u,v device=Plots/secondary_reim_{f}.png/PNG', day),
                (f'uvplt vis=f{f}/{secondary}.{f} axis=uc,vc options=nob,nof,2pass    stokes=i       device=Plots/secondary_ucvc_{f}.png/PNG', day),
                (f'uvplt vis=f{f}/{secondary}.{f} axis=freq,amp options=nob,nof,2pass stokes=i       device=Plots/secondary_freqamp_{f}.png/PNG', day),
              ]
            jobs.extend(a)

pool = Pool(15)
result = pool.map(run, jobs)
pool.close()
pool.join()