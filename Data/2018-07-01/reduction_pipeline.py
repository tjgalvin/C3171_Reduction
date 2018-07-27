import mir_utils as mu
from pymir import mirstr as m
from multiprocessing import Pool

NFBIN = 2
FREQS = ['7700', '9500']

def run(a):
    a.run()
    print(a)


# Initial pass of the data loads in without the Tsys correction to produce a
# robust spectrum of the secondary calibrator
for index, freq in enumerate(FREQS):
    ifsel = index + 1
    primary = f"{mu.primary}.{freq}"
    secondary = f"{mu.secondary}.{freq}"
    mosaic = f"{mu.science}.{freq}"

    # Load in the data
    atlod = m(f"atlod in=raw/*C3171 options=notsys,rfiflag,birdie,xycorr,noauto "\
              f"ifsel={ifsel} out=data{ifsel}.uv").run()
    print(atlod)

    # Flag the known bad channels out
    if ifsel == 1:
        mu.uvflag(atlod.out, mu.flags_7)
    else:
        mu.uvflag(atlod.out, mu.flags_9)

    # Split the data up
    uvsplit = m(f"uvsplit vis={atlod.out} options=mosaic "\
                f"select=source({mu.primary}),source({mu.secondary})").run()
    print(uvsplit)

    mfcal = m(f"mfcal vis={primary} interval=0.1").run()
    gpcal = m(f"gpcal vis={primary} interval=0.1 nfbin={NFBIN} "\
              f"options=xyvary").run()
    print(mfcal)
    print(gpcal)

    mu.calibrator_pgflag(primary)


    mfcal = m(f"mfcal vis={primary} interval=0.1").run()
    gpcal = m(f"gpcal vis={primary} interval=0.1 nfbin={NFBIN} "\
              f"options=xyvary").run()
    print(mfcal)
    print(gpcal)

    gpcopy = m(f"gpcopy vis={primary} out={secondary}").run()
    print(gpcopy)

    gpcal = m(f"gpcal vis={secondary} interval=0.1 nfbin={NFBIN} "\
              f"options=xyvary,qusolve").run()
    print(gpcal)

    mu.calibrator_pgflag(secondary)

    gpcal = m(f"gpcal vis={secondary} interval=0.1 nfbin={NFBIN} "\
              f"options=xyvary,qusolve").run()
    print(gpcal)

    gpboot = m(f"gpboot vis={secondary} cal={primary}").run()
    print(gpboot)

    plt = [m(f'uvplt vis={primary} axis=time,amp options=nob,nof stokes=i device=primary_timeamp_{freq}.png/PNG'),
           m(f'uvplt vis={primary} axis=re,im options=nob,nof,eq stokes=i,q,u,v device=primary_reim_{freq}.png/PNG'),
           m(f'uvplt vis={primary} axis=uc,vc options=nob,nof stokes=i  device=primary_ucvc_{freq}.png/PNG'),
           m(f'uvplt vis={primary} axis=freq,amp options=nob,nof stokes=i  device=primary_freqamp_{freq}.png/PNG'),
           m(f'uvplt vis={secondary} axis=time,amp options=nob,nof stokes=i device=secondary_timeamp_{freq}.png/PNG'),
           m(f'uvplt vis={secondary} axis=re,im options=nob,nof,eq stokes=i,q,u,v device=secondary_reim_{freq}.png/PNG'),
           m(f'uvplt vis={secondary} axis=uc,vc options=nob,nof stokes=i  device=secondary_ucvc_{freq}.png/PNG'),
           m(f'uvplt vis={secondary} axis=freq,amp options=nob,nof stokes=i device=secondary_freqamp_{freq}.png/PNG'),
           m(f'uvfmeas vis={secondary} stokes=i log=secondary_uvfmeas_{freq}_log.txt device=secondary_uvfmeas_{freq}.png/PNG')]
    pool = Pool(7)
    result = pool.map(run, plt)
    pool.close()
    pool.join()

uvfmeas = m(f"uvfmeas vis={','.join([f'{mu.secondary}.{freq}' for freq in FREQS])} "\
            f"stokes=i log=secondary_uvfmeas_both_log.txt "\
            f"device=secondary_uvfmeas_both.png/PNG").run()
print(uvfmeas)

# import sys
# sys.exit()

# Acquire information of the fit to the model of secondary
fit_pack = mu.model_secondary(if1='secondary_uvfmeas_7700_log.txt',
                              if2='secondary_uvfmeas_9500_log.txt')

# Now move things into a directory structure
mu.mv_uv('notsys')

# Reload the data with Tsys and use model as reference flux model
for index, freq in enumerate(FREQS):
    ifsel = index + 1
    primary = f"{mu.primary}.{freq}"
    secondary = f"{mu.secondary}.{freq}"
    mosaic = f"{mu.science}.{freq}"

    # Obtain mflux string from the fitpack information
    mfflux = mu.mfcal_flux(fit_pack, ifcal=ifsel)

    # Load in the data
    atlod = m(f"atlod in=raw/*C3171 options=rfiflag,birdie,xycorr,noauto "\
              f"ifsel={ifsel} out=data{ifsel}.uv").run()
    print(atlod)

    # Flag the known bad channels out
    if ifsel == 1:
        mu.uvflag(atlod.out, mu.flags_7)
    else:
        mu.uvflag(atlod.out, mu.flags_9)

    # Split the data up
    uvsplit = m(f"uvsplit vis={atlod.out} options=mosaic ").run()
    print(uvsplit)

    # Calibrate the secondary using the flux reference model
    mfcal = m(f"mfcal vis={secondary} flux={mfflux} interval=0.1").run()
    gpcal = m(f"gpcal vis={secondary} nfbin={NFBIN} interval=0.1 "\
               "options=xyvary,qusolve").run()
    print(mfcal)
    print(gpcal)

    mu.calibrator_pgflag(secondary)

    # Calibrate the secondary using the flux reference model
    mfcal = m(f"mfcal vis={secondary} flux={mfflux} interval=0.1").run()
    gpcal = m(f"gpcal vis={secondary} nfbin={NFBIN} interval=0.1 "\
               "options=xyvary,qusolve").run()
    print(mfcal)
    print(gpcal)

    mfboot = m(f"mfboot vis={secondary} select=source({mu.secondary}) "\
               f"flux={mfflux}").run()
    print(mfboot)

    plt = [m(f'uvplt vis={secondary} axis=time,amp options=nob,nof stokes=i device=secondary_timeamp_{freq}.png/PNG'),
           m(f'uvplt vis={secondary} axis=re,im options=nob,nof,eq stokes=i,q,u,v device=secondary_reim_{freq}.png/PNG'),
           m(f'uvplt vis={secondary} axis=uc,vc options=nob,nof stokes=i  device=secondary_ucvc_{freq}.png/PNG'),
           m(f'uvplt vis={secondary} axis=freq,amp options=nob,nof stokes=i device=secondary_freqamp_{freq}.png/PNG'),
           m(f'uvfmeas vis={secondary} stokes=i log=secondary_uvfmeas_{freq}_log.txt device=secondary_uvfmeas_{freq}.png/PNG')]
    pool = Pool(7)
    result = pool.map(run, plt)
    pool.close()
    pool.join()

    gpcopy = m(f"gpcopy vis={secondary} out={mosaic}").run()
    print(gpcopy)

    # Flag the actual science data
    mu.mosaic_pgflag(mosaic)

    uvsplit = m(f"uvsplit vis={mosaic}").run()
    print(uvsplit)

uvfmeas = m(f"uvfmeas vis={','.join([f'{mu.secondary}.{freq}' for freq in FREQS])} "\
            f"stokes=i log=secondary_uvfmeas_both_log.txt "\
            f"device=secondary_uvfmeas_both.png/PNG").run()
print(uvfmeas)

mu.mv_uv('normal')