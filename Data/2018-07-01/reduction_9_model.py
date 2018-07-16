"""Script to reduce data from C3171 data, and rather then use 1934-638
to derive a passband solution and apply a absolute flux scale, we will
use a model derived from the secondary after an initial calibration.

The use of this model is done to:
- correct for the band pass ripple we see in the secondary spectrum
- improve the agreement of the overlaped regions of the IFs

We require there to be the
- `data` directory containing the previous atlod files
- `uvfmeas` spectrum logs from the make_plots.py script. Currently
   this has to be run manualy, but will be folded into the 
   processing of the normal reduction scripts
"""

import mir_utils as mu 
import shutil
import glob
import os
import sys

NFBIN = 4
IFSEL = 2
FREQ = '9500'

primary = f"{mu.primary}.{FREQ}"
secondary = f"{mu.secondary}.{FREQ}"
mosaic = f"{mu.science}.{FREQ}"

# Check for directories and files
if not os.path.exists('uv'):
    print('Data uv files do not exist')
    sys.exit(1)

# Load in the data
uv = f'uv/data{IFSEL}.uv'

# Split the data up
uvsplit = mu.mirstr(f"uvsplit vis={uv} options=mosaic").run()
print(uvsplit)

sec_model = mu.model_secondary()
mfflux = mu.mfcal_flux(sec_model, ifcal=2)

print(mfflux)

# Primary calibration
mfcal = mu.mirstr(f'mfcal vis={secondary} flux={mfflux} interval=0.1').run()
gpcal = mu.mirstr(f"gpcal vis={secondary} interval=0.1 nfbin={NFBIN} flux={mfflux.split(',')[0]} spec={mfflux.split(',')[1]},{mfflux.split(',')[2]} options=xyvary,qusolve").run()
# gpcal = mu.mirstr(f"gpcal vis={secondary} interval=0.1 nfbin={NFBIN} flux={mfflux.split(',')[0]} spec={','.join(mfflux.split(',')[1:])}  options=xyvary,qusolve").run()
# gpcal = mu.mirstr(f"gpcal vis={secondary} interval=0.1 nfbin={NFBIN} options=xyvary,qusolve").run()

print(mfcal)
print(gpcal)

# Automated flagging
pgflag = mu.mirstr(f"pgflag vis={secondary} command='<b' stokes=i,q,u,v flagpar=8,5,5,3,6,3 options=nodisp").run()
print(pgflag)

pgflag = mu.mirstr(f"pgflag vis={secondary} command='<b' stokes=i,v,q,u flagpar=8,2,2,3,6,3  options=nodisp").run()
print(pgflag)

pgflag = mu.mirstr(f"pgflag vis={secondary} command='<b' stokes=i,v,u,q flagpar=8,2,2,3,6,3  options=nodisp").run()
print(pgflag)

# Primary calibration
mfcal = mu.mirstr(f'mfcal vis={secondary} flux={mfflux} interval=0.1').run()
gpcal = mu.mirstr(f"gpcal vis={secondary} interval=0.1 nfbin={NFBIN} flux={mfflux.split(',')[0]} spec={mfflux.split(',')[1]},{mfflux.split(',')[2]} options=xyvary,qusolve").run()
# gpcal = mu.mirstr(f"gpcal vis={secondary} interval=0.1 nfbin={NFBIN} flux={mfflux.split(',')[0]} spec={','.join(mfflux.split(',')[1:])}  options=xyvary,qusolve").run()
# gpcal = mu.mirstr(f"gpcal vis={secondary} interval=0.1 nfbin={NFBIN} options=xyvary,qusolve").run()

print(mfcal)
print(gpcal)

plt = [mu.mirstr(f'uvplt vis={secondary} axis=time,amp options=nob,nof stokes=i device=secondary_timeamp_{FREQ}.png/PNG'),
       mu.mirstr(f'uvplt vis={secondary} axis=re,im options=nob,nof,eq stokes=i,q,u,v device=secondary_reim_{FREQ}.png/PNG'),
       mu.mirstr(f'uvplt vis={secondary} axis=uc,vc options=nob,nof stokes=i  device=secondary_ucvc_{FREQ}.png/PNG'),
       mu.mirstr(f'uvplt vis={secondary} axis=freq,amp options=nob,nof stokes=i device=secondary_freqamp_{FREQ}.png/PNG'),
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

import sys
sys.exit()

gpcopy = mu.mirstr(f"gpcopy vis={secondary} out={mosaic}").run()
print(gpcopy)

# Automated flagging
# pgflag = mu.mirstr(f"pgflag vis={mosaic} command='<b' stokes=i,q,u,v flagpar=8,5,5,3,6,3 options=nodisp").run()
# print(pgflag)

pgflag = mu.mirstr(f"pgflag vis={mosaic} command='<b' stokes=i,v,q,u flagpar=8,2,2,3,6,3  options=nodisp").run()
print(pgflag)

pgflag = mu.mirstr(f"pgflag vis={mosaic} command='<b' stokes=i,v,u,q flagpar=8,2,2,3,6,3  options=nodisp").run()
print(pgflag)


uvsplit = mu.mirstr(f'uvsplit vis={mosaic}').run()
print(uvsplit)

# Make output dirs
try:
    os.makedirs('Plots')
except Exception as e:
    print(e)

try:
    os.makedirs('uv')
except Exception as e:
    print(e)

try:
    os.makedirs(f'f{FREQ}')
except Exception as e:
    print(e)

shutil.move(atlod.attribute('out'), 'uv')
for i in glob.glob(f'*.{FREQ}'):
    shutil.move(i, f'f{FREQ}')

for i in glob.glob(f'*{FREQ}.png'):
    shutil.move(i, f'Plots')