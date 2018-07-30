"""Script to batch run calibration scripts across all days. 

At this point requires some manual tweaking to run on a specific script type

Need to add option to handle this. 
"""
import os
import sys
import glob
import pymir as mu
from multiprocessing import Pool
import subprocess as sp

def run(s):
    """Function to call python calibration script
    
    Arguments:
        s {tuple} -- Element one is the calibration script
                     the second is the working directory to execute in
    """
    p = sp.run(s[0].split(), cwd=s[1])
    print(p.stdout.decode())
    print(p.stderr.decode())

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
    # a =[("python3 reduction_7_model.py", day),
    #     ("python3 reduction_9_model.py", day)
    #     ]
    a =[("python3 reduction_pipeline.py", day),
        ]
    jobs.extend(a)



pool = Pool(10)
result = pool.map(run, jobs)
pool.close()
pool.join()