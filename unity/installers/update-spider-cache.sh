#!/bin/bash
# assuming that all module directories are accessible by loading modules out of /modules/modulefiles
# spack directories: module load microarch, URI directories: module load uri, ...
MODULEPATH="/modules/modulefiles"
# -D debug
source /usr/share/lmod/lmod/libexec/update_lmod_system_cache_files -D $MODULEPATH
