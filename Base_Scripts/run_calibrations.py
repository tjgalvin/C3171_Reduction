"""Script to batch run calibration scripts across all days. 

At this point requires some manual tweaking to run on a specific script type
"""
import os
import sys
import glob
import pymir as mu
from multiprocessing import Pool
import subprocess as sp

def run(s):
    """Function to create mirstr and run
    
    Arguments:
        s {tuple} -- Element one is the miriad task to execute and
                     the second is the working directory to execute in
    """
    sp.run(s[0].split(), cwd=s[1])

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
    a =[("python3 reduction_7_notsys.py", day),
        ("python3 reduction_9_notsys.py", day)
        ]
    jobs.extend(a)



pool = Pool(12)
result = pool.map(run, jobs)
pool.close()
pool.join()