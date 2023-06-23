#!/bin/bash
#SBATCH -c 1
#SBATCH -p cpu-preempt
#SBATCH --export=none

set -e

arches="x86_64,ppc64le,aarch64"
IFS=','
for arch in $arches; do
    os_arch=linux-ubuntu20.04-$arch
    cmd="\
/usr/share/lmod/lmod/libexec/update_lmod_system_cache_files \
-D \
-d \"/modules/lmod/spider-cache/$arch\" \
-t \"/modules/lmod/spider-cache/$arch/system.txt\" \
\"/modules/modulefiles/noarch:/modules/modulefiles/$arch:/modules/spack_modulefiles/$os_arch/Core\"\
"
    echo "$cmd"
    eval $cmd
done
unset IFS
