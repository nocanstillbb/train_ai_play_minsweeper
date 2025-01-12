#!/bin/bash
set -x

currentpath=$(pwd)



cd third-party/prism_all
./clear.sh
cd ../..

rm -rf $currentpath/build

