#!/bin/bash
set -x

currentpath=$(pwd)
project_install_dir=$currentpath/vcpkg_installed/arm64-osx
#qt_install_dir=/Users/hbb/Qt/5.15.2/clang_64
#qt_install_dir=/Users/hbb/Qt/5.15.2/clang_64
cmake_paramter="-DCMAKE_PREFIX_PATH=;$project_install_dir -DCMAKE_INSTALL_PREFIX=$project_install_dir  -DCMAKE_TOOLCHAIN_FILE=/Users/hbb/toolchain-arm64.cmake -DBUILD_PRISM_ALL=OFF"


cd $currentpath/third-party/prism_all
./build.sh $cmake_paramter

if [ $? -ne 0 ]; then
exit 1
fi

paths=( "DATA_COLLECTOR")
#paths=( "DATA_COLLECTOR"  "DV_TRAIN_SERVER" "DV_APP")
modules=''
cd $currentpath && mkdir -p build 
for module in ${paths[@]}; do
    cd $currentpath/build
    modules+=" -DBUILD_$module=ON "
    #bash -c "cmake -S '$currentpath' $cmake_paramter $modules"
    cmake .. $cmake_paramter $modules
    if [ $? -ne 0 ]; then
     exit 1
    fi
    lower_module_name=$(echo "$module" | tr '[:upper:]' '[:lower:]')
    cd $lower_module_name
    cmake --build . --target install --config release
    if [ $? -ne 0 ]; then
     exit 1
    fi
done

