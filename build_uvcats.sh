#!/bin/bash

num_points=195
outs=./Semester_2_notsys
for ((p=1;p<=num_points;p++))
do
	in7=Data/*/f7700_notsys/c3171_$p.7700
	in9=Data/*/f9500_notsys/c3171_$p.9500
	# in9=''
	ins="$in7,$in9"
	# for ((i=1;i<=num_days;i++))
	# do
	# 	ins=$ins,Night$i/Pointings/c3171_$p.7700,Night$i/Pointings/c3171_$p.9500
	# done
	echo $ins
	uvcat vis=$ins out=$outs/c3171_$p.uv  &
done
