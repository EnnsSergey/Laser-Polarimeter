#!/bin/bash
export LD_LIBRARY_PATH=/ceph/sw/gcc/13.2.0/x86_64-el8/lib64:$LD_LIBRARY_PATH
thr_num=$1
sx=$2
sy=$3

/home/enns/LaserPolarimeter/build/./main /home/enns/LaserPolarimeter/run.mac $thr_num  --P 1.0 --Q 0.5 --beta 0.7 --sx $sx --sy $sy
