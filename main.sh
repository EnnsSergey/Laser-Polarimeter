#!/bin/bash
export LD_LIBRARY_PATH=/ceph/sw/gcc/13.2.0/x86_64-el8/lib64:$LD_LIBRARY_PATH
echo $1
/home/enns/LaserPolarimeter/build/./main /home/enns/LaserPolarimeter/run.mac $1  --P 1.0 --Q 0.99 --beta 0.7
