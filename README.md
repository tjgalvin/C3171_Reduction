# C3171_Reduction

This is code to reduce ATCA data for the C3171 project. 

The idea that each day will have its own calibration script. Using a base reduction example, each day will have its own reduction script built. Any day specific configuration/calibration steps will be implemented in that days script. For instance, if a CABB block goes down then a corresponding time range should be specific to that day. 

In this repository I will aim to add a folder for each day. The example script in the main directory will be the base reduction strategy.

## mir_utils.py

These are some miriad utilities used throughout the calibration stages. It contains known rfi channels to flag across both IFs/time and hard codes the primary and secondary flux calibrator names. 

It also implements a class to help run and manage miriad tasks. It subclasses string and adds a few methods to make it callable and return attribute properties of the miriad task (eg. invert.map or invert.beam)


## rpfits_struct.txt

Contains the rpfits file names and their directory structure so that the repository can be regenerated again easily if a complete redownload of raw data is needed. 


## model.py 

This suffix on teh reduction_7 and reduction_9 python files will attempt to use the uvfmeas spectrum outputs from the initial calibration to produce a consistent spectrum for the secondary and subsequent science data. 

The `Plots_Model`, `f7700_Model` and `f9500_Model` folders contain the outputs from these processing scripts

I am almost certain that these are not the correct way to reduce the data. I think in principal the idea of calibrating via a model of the secondary is OK, the only way I was able to get it to calibrate well was to specify NFBIN=1. I am not sure if this is really the right thing to do over a large bandwidth. The leakages are frequency dependent which this is not really handling. When NFBIN>1, the spectrum would not line up between the two IFs, even though they reference frequency and normalisation was set so they would. There may be something I am not seeing in the use of a flux model in gpcal, and the reference frequency is being set incorrectly. Will revisit this at some point.  

## notsys.py

Similar to the `model.py` suffix, the `notsys` suffix is used to denote scripts and plots that issued the `options=notsys` property of `atlod`. It seems as though due to RFI in the tvchan range, the absolute scaling applied by the online Tsys correction can be wrong, and this can carry on throughout the run, even after a `gpboot` with `1934-638`. Since the RFI is generally not persistent, then the Tsys can be a bit misbehaved. 

When using this command in `atlod` though there is a problem where for instances where ATCA has not settled onto a new pointing for an entire integration cycle, there is a corresponding elevated Tsys measurement. This fudge factor gets brought into the data aswell. So for these data, we will flag all visibilities whose `inttime` property is less then some threshold. 

Initial looks suggest the secondary spectrum across the two IFs aligns a lot better now, to a fraction of a percent. the bandpass ripple is still persistent though. 