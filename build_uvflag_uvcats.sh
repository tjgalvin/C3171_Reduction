#!/bin/bash

# Dirty script to build uvcat files across all days. Need to go about
# making it a proper build script with options for modes of calibrated
# folders and paths. For the moment have to hand tweak values

num_points=195
outs=./Semester_2
for ((p=1;p<=num_points;p++))
do
	uvflag vis=Data/*/f7700/c3171_$p.7700 line=chan,60,1898 flagval=flag options=noapply &
done

wait

for ((p=1;p<=num_points;p++))
do
	in7=Data/*/f7700/c3171_$p.7700
	in9=Data/*/f9500/c3171_$p.9500
	# in9=''
	ins="$in7,$in9"
	# for ((i=1;i<=num_days;i++))
	# do
	# 	ins=$ins,Night$i/Pointings/c3171_$p.7700,Night$i/Pointings/c3171_$p.9500
	# done
	echo $ins
	uvcat vis=$ins out=$outs/c3171_$p.uv  &
done
