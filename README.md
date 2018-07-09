# C3171_Reduction

This is code to reduce ATCA data for the C3171 project. 

The idea that each day will have its own calibration script. Using a base reduction example, each day will have its own reduction script built. Any day specific configuration/calibration steps will be implemented in that days script. For instance, if a CABB block goes down then a corresponding time range should be specific to that day. 

In this repository I will aim to add a folder for each day. The example script in the main directory will be the base reduction strategy.