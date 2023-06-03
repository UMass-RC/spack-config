#!/bin/bash
#SBATCH -c 1
#SBATCH -p cpu-preempt

# -D debug
source /usr/share/lmod/lmod/libexec/update_lmod_system_cache_files -D $MODULEPATH
