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
