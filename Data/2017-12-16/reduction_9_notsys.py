"""Script to reduce data from C3171 data
"""
import mir_utils as mu 
import shutil
import glob
import os

NFBIN = 2
IFSEL = 2
FREQ = '9500'

primary = f"{mu.primary}.{FREQ}"
secondary = f"{mu.secondary}.{FREQ}"
mosaic = f"{mu.science}.{FREQ}"

# Load in the data
atlod = mu.mirstr(f"atlod in=raw/*C3171 options=notsys,rfiflag,birdie,xycorr,noauto ifsel={IFSEL} out=data{IFSEL}.uv").run()
print(atlod)

# Flag the known bad channels out
mu.uvflag(atlod.out, mu.flags_9)

# Drop the first integration cycle is less then 8 seconds
mu.flag_inttime(atlod.out, threshold=8, logfile='dump9.txt', delete=True, selection='flagging9.txt')

# Split the data up
uvsplit = mu.mirstr(f"uvsplit vis={atlod.attribute('out')} options=mosaic").run()
print(uvsplit)

# Primary calibration
mfcal = mu.mirstr(f'mfcal vis={primary} interval=0.1').run()
gpcal = mu.mirstr(f'gpcal vis={primary} interval=0.1 nfbin={NFBIN} options=xyvary').run()

print(mfcal)
print(gpcal)

# Automated flagging
pgflag = mu.mirstr(f"pgflag vis={primary} command='<b' stokes=i,q,u,v flagpar=8,5,5,3,6,3 options=nodisp").run()
print(pgflag)

pgflag = mu.mirstr(f"pgflag vis={primary} command='<b' stokes=i,v,q,u flagpar=8,2,2,3,6,3  options=nodisp").run()
print(pgflag)

pgflag = mu.mirstr(f"pgflag vis={primary} command='<b' stokes=i,v,u,q flagpar=8,2,2,3,6,3  options=nodisp").run()
print(pgflag)

# Primary calibration
mfcal = mu.mirstr(f'mfcal vis={primary} interval=0.1').run()
gpcal = mu.mirstr(f'gpcal vis={primary} interval=0.1 nfbin={NFBIN} options=xyvary').run()

print(mfcal)
print(gpcal)

gpcopy = mu.mirstr(f"gpcopy vis={primary} out={secondary}").run()
print(gpcopy)

gpcal = mu.mirstr(f"gpcal vis={secondary} options=xyvary,qusolve nfbin={NFBIN} interval=0.1").run()
print(gpcal)

# Automated flagging
pgflag = mu.mirstr(f"pgflag vis={secondary} command='<b' stokes=i,q,u,v flagpar=8,5,5,3,6,3 options=nodisp").run()
print(pgflag)

pgflag = mu.mirstr(f"pgflag vis={secondary} command='<b' stokes=i,v,q,u flagpar=8,2,2,3,6,3  options=nodisp").run()
print(pgflag)

pgflag = mu.mirstr(f"pgflag vis={secondary} command='<b' stokes=i,v,u,q flagpar=8,2,2,3,6,3  options=nodisp").run()
print(pgflag)

gpcal = mu.mirstr(f"gpcal vis={secondary} options=xyvary,qusolve nfbin={NFBIN} interval=0.1").run()
print(gpcal)

gpboot = mu.mirstr(f'gpboot vis={secondary} cal={primary}').run()
print(gpboot)

plt = [mu.mirstr(f'uvplt vis={primary} axis=time,amp options=nob,nof,2pass stokes=i device=primary_timeamp_{FREQ}.png/PNG'),
       mu.mirstr(f'uvplt vis={primary} axis=re,im options=nob,nof,eq,2pass stokes=i,q,u,v device=primary_reim_{FREQ}.png/PNG'),
       mu.mirstr(f'uvplt vis={primary} axis=uc,vc options=nob,nof,2pass stokes=i  device=primary_ucvc_{FREQ}.png/PNG'),
       mu.mirstr(f'uvplt vis={primary} axis=freq,amp options=nob,nof,2pass stokes=i  device=primary_freqamp_{FREQ}.png/PNG'),
       mu.mirstr(f'uvplt vis={secondary} axis=time,amp options=nob,nof,2pass stokes=i device=secondary_timeamp_{FREQ}.png/PNG'),
       mu.mirstr(f'uvplt vis={secondary} axis=re,im options=nob,nof,eq,2pass stokes=i,q,u,v device=secondary_reim_{FREQ}.png/PNG'),
       mu.mirstr(f'uvplt vis={secondary} axis=uc,vc options=nob,nof,2pass stokes=i  device=secondary_ucvc_{FREQ}.png/PNG'),
       mu.mirstr(f'uvplt vis={secondary} axis=freq,amp options=nob,nof,2pass stokes=i device=secondary_freqamp_{FREQ}.png/PNG'),
    ]

print(plt)

def run(a):
    a.run()
    print(a)
    
from multiprocessing import Pool

pool = Pool(5)
result = pool.map(run, plt)
pool.close()
pool.join()

gpcopy = mu.mirstr(f"gpcopy vis={secondary} out={mosaic}").run()
print(gpcopy)

# Automated flagging
# pgflag = mu.mirstr(f"pgflag vis={mosaic} command='<b' stokes=i,q,u,v flagpar=8,5,5,3,6,3 options=nodisp").run()
# print(pgflag)

pgflag = mu.mirstr(f"pgflag vis={mosaic} command='<b' stokes=i,v,q,u flagpar=8,2,0,3,6,3  options=nodisp").run()
print(pgflag)

pgflag = mu.mirstr(f"pgflag vis={mosaic} command='<b' stokes=i,v,u,q flagpar=8,2,0,3,6,3  options=nodisp").run()
print(pgflag)


uvsplit = mu.mirstr(f'uvsplit vis={mosaic}').run()
print(uvsplit)
# Make output dirs
try:
    os.makedirs('Plots_notsys')
except Exception as e:
    print(e)

try:
    os.makedirs('uv_notsys')
except Exception as e:
    print(e)

try:
    os.makedirs(f'f{FREQ}_notsys')
except Exception as e:
    print(e)

shutil.move(atlod.attribute('out'), 'uv_notsys')
for i in glob.glob(f'*.{FREQ}'):
    shutil.move(i, f'f{FREQ}_notsys')

for i in glob.glob(f'*{FREQ}.png'):
    shutil.move(i, f'Plots_notsys')