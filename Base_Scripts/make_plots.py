"""Script to batch make all plots for all observing days on the calibrated data

It assumes that the reduction_7.py and reduction_9.py scripts have run.
"""
import os
import sys
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
if len(sys.argv) > 1:
    # Assume user knows what they are doing
    days = sys.argv[1:]
else:
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
                (f'uvplt vis=f{f}/{primary}.{f}   axis=time,amp options=nof,2pass     stokes=i       device=Plots/primary_timeamp_{f}_nxy.png/PNG nxy=4,4', day),
                (f'uvplt vis=f{f}/{primary}.{f}   axis=re,im options=nob,nof,eq,2pass stokes=i,q,u,v device=Plots/primary_reim_{f}.png/PNG', day),
                (f'uvplt vis=f{f}/{primary}.{f}   axis=uc,vc options=nob,nof,2pass    stokes=i       device=Plots/primary_ucvc_{f}.png/PNG', day),
                (f'uvplt vis=f{f}/{primary}.{f}   axis=freq,amp options=nob,nof,2pass stokes=i       device=Plots/primary_freqamp_{f}.png/PNG', day),
                (f'uvplt vis=f{f}/{primary}.{f}   axis=freq,amp options=nof,2pass     stokes=i       device=Plots/primary_freqamp_{f}_nxy.png/PNG nxy=4,4', day),
                (f'uvplt vis=f{f}/{secondary}.{f} axis=time,amp options=nob,nof,2pass stokes=i       device=Plots/secondary_timeamp_{f}.png/PNG', day),
                (f'uvplt vis=f{f}/{secondary}.{f} axis=time,amp options=nof,2pass     stokes=i       device=Plots/secondary_timeamp_{f}_nxy.png/PNG nxy=4,4', day),
                (f'uvplt vis=f{f}/{secondary}.{f} axis=re,im options=nob,nof,eq,2pass stokes=i,q,u,v device=Plots/secondary_reim_{f}.png/PNG', day),
                (f'uvplt vis=f{f}/{secondary}.{f} axis=uc,vc options=nob,nof,2pass    stokes=i       device=Plots/secondary_ucvc_{f}.png/PNG', day),
                (f'uvplt vis=f{f}/{secondary}.{f} axis=freq,amp options=nob,nof,2pass stokes=i       device=Plots/secondary_freqamp_{f}.png/PNG', day),
                (f'uvplt vis=f{f}/{secondary}.{f} axis=freq,amp options=nof,2pass     stokes=i       device=Plots/secondary_freqamp_{f}_nxy.png/PNG nxy=4,4', day),
                (f'uvfmeas vis=f{f}/{secondary}.{f} stokes=i log=Plots/secondary_uvfmeas_{f}_log.txt device=Plots/secondary_uvfmeas_{f}.png/PNG', day),
              
              ]
            jobs.extend(a)

        jobs.append((f'uvfmeas vis=f{freqs[0]}/{secondary}.{freqs[0]},f{freqs[1]}/{secondary}.{freqs[1]} stokes=i log=Plots/secondary_uvfmeas_both_log.txt device=Plots/secondary_uvfmeas_both.png/PNG', day))


pool = Pool(20)
result = pool.map(run, jobs)
pool.close()
pool.join()