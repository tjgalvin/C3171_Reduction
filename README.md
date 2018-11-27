# C3171_Reduction

This is code to reduce ATCA data for the C3171 project. 

The idea that each day will have its own calibration script. Using a base reduction example, each day will have its own reduction script built. Any day specific configuration/calibration steps will be implemented in that days script. For instance, if a CABB block goes down then a corresponding time range should be specific to that day. 

In this repository I will aim to add a folder for each day. The example script in the main directory will be the base reduction strategy.

## mir_utils.py

These are some miriad utilities used throughout the calibration stages. It contains known rfi channels to flag across both IFs/time and hard codes the primary and secondary flux calibrator names. 

There is also functionality to use the two CABB IFs to derive a model of the secondary calibrator to be used as a flux reference model, ensuring the two IFs are properly aligned. Initial reduction found that the online Tsys correction can introduce an amplitude offset, which was particuarly troublesome when RFI 'popped' into the tvchan range. This was more a problem for semester one. Semester two (and onwards) used the tvmedian command, making the Tsys more resilient to interference.

## rpfits_struct.txt

Contains the rpfits file names and their directory structure so that the repository can be regenerated again easily if a complete redownload of raw data is needed. 

## reduction_pipeline.py

The current version of the reduction pipeline applied to each day. During testing it was found that it was best to undo the online Tsys correction when loading data to better calibrate consistently the two CABB IFs. As the two IFs will be used simultaneously to make a single image, extra work is made to ensure that they are consistent. The secondary spectrum is initially calibrated without the online Tsys correction to derive a consistent reference flux model. Mosaic scans will inflate the Tsys measurement for integrations that were less then the desired cycle length (i.e. slewing to a new pointing). Hence, undoing the Tsys correction also means flagging out a significant fraction of the mosaic source data. 

To avoid this, we used the derived secondary spectrum as a flux model after first undoing the Tsys correction. Once a secondary spectrum has been constructed, data is reloaded with the Tsys correlation (which is applied online and required for the mosaic pointings) and calibrated against this model. This reduction_pipeline.py script implements this two stage procedure. Any day specific options/stages are also implemented in each days script. 

Calibrating in this manner also allows for a time dependent bandpass solution to be constrained (as the secondary now has a known model specific to that day and is sufficiently strong), eliminating the bandpass ripple seen in the original reductions.

## model.py 

This is a historical script and will be removed. 

This suffix on the reduction_7 and reduction_9 python files will attempt to use the uvfmeas spectrum outputs from the initial calibration to produce a consistent spectrum for the secondary and subsequent science data. 

The `Plots_Model`, `f7700_Model` and `f9500_Model` folders contain the outputs from these processing scripts

I am almost certain that these are not the correct way to reduce the data. I think in principal the idea of calibrating via a model of the secondary is OK, the only way I was able to get it to calibrate well was to specify NFBIN=1. I am not sure if this is really the right thing to do over a large bandwidth. The leakages are frequency dependent which this is not really handling. When NFBIN>1, the spectrum would not line up between the two IFs, even though they reference frequency and normalisation was set so they would. There may be something I am not seeing in the use of a flux model in gpcal, and the reference frequency is being set incorrectly. Will revisit this at some point.  

## notsys.py

This is a historical script will be removed.

Similar to the `model.py` suffix, the `notsys` suffix is used to denote scripts and plots that issued the `options=notsys` property of `atlod`. It seems as though due to RFI in the tvchan range, the absolute scaling applied by the online Tsys correction can be wrong, and this can carry on throughout the run, even after a `gpboot` with `1934-638`. Since the RFI is generally not persistent, then the Tsys can be a bit misbehaved. 

When using this command in `atlod` though there is a problem where for instances where ATCA has not settled onto a new pointing for an entire integration cycle, there is a corresponding elevated Tsys measurement. This fudge factor gets brought into the data aswell. So for these data, we will flag all visibilities whose `inttime` property is less then some threshold. 

Initial looks suggest the secondary spectrum across the two IFs aligns a lot better now, to a fraction of a percent. the bandpass ripple is still persistent though. 
