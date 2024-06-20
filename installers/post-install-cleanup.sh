#!/bin/bash
#SBATCH -c 4
#SBATCH --mem=16G
#SBATCH -p cpu-preempt
#SBATCH -t 8:00:00
#SBATCH -o logs/cleanup-%j.log

echo "jobid $SLURM_JOB_ID on host $(hostname) by user $(whoami) on $(date)"

if [ ! -f "$PWD/post-install-cleanup.sh" ]; then
    echo "please change your current working directory to \$spack/unity/installers/" >&2
    echo "where \$spack is the spack directory for whatever spack instance you are using" >&2
    echo "/modules/spack/<whatever>" >&2
    exit 1
fi
SPACK_PREFIX=$(dirname $(dirname "$PWD"))

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

echo "done!"
