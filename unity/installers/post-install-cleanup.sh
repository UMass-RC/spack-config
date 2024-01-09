#!/bin/bash
#SBATCH -c 4
#SBATCH --mem=16G
#SBATCH -p cpu-preempt
#SBATCH -t 8:00:00

SPACK_PREFIX=/modules/spack/0.20.0/

if [ -z "$SLURM_JOB_ID" ]; then
    echo "this script takes a long time, you probably want to \`sbatch\` me!"
    echo "sleeping for 3 seconds in case you want to ctrl+c..."
    sleep 3
fi
set -x
source $SPACK_PREFIX/share/spack/setup-env.sh
cd $SPACK_PREFIX/unity/installers
spack gc -y # uninstall packages that were needed only at build time
./update-spider-cache.sh # update Lmod spider cache
