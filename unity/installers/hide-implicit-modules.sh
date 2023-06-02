#!/bin/bash
#SBATCH -c 1
#SBATCH -t 4:00:00
#SBATCH -p cpu-preempt

# I don't want hide-implicit-modules.py to account for microarch modules
# there is no spack spec (so I'm told) that includes multiple architectures (x86_64, aarch64, ppc64le)
# instead, I run hide-implicit-modules.py for each arch that I want to include
# and then put them in a .modulerc.lua in the Core module directory for that architecture

set -e
set -x

source ../../share/spack/setup-env.sh

spack_module_dir="$(dirname $(dirname $PWD))/share/spack/lmod" # ../../share/spack/lmod
for arch in $(ls $spack_module_dir | grep ^linux-ubuntu); do
    ./hide-implicit-modules-arch.py $arch | sed "s|$spack_module_dir|/modules/spack_modulefiles|g" > ../../share/spack/lmod/$arch/Core/.modulerc.lua
done
