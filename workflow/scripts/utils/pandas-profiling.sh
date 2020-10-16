#!/bin/sh

dir=$1
meta_id=$2
threads=$3

row_num=100000

#echo $dir $meta_id $threads

if [ $# -eq 3 ]
  then
    echo Profiling $meta_id with $threads threads, limiting to $row_num random rows
    t=$dir/$meta_id.tmp
    gunzip -c $dir/$meta_id.csv.gz | shuf -n $row_num > $t 
    cat $dir/$meta_id.header $t > $t.csv
    pandas_profiling -s --pool_size $threads $t.csv $dir/$meta_id.profile.html
    rm $t $t.csv
else
    echo "Not enough arguments supplied"
fi