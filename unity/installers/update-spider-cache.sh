#!/bin/bash
prepend_modulepath() {
    if [ ! -d "$1" ]; then
        echo "\"$1\" does not exist!"
        return 1
    fi
    # if $1 is already present in modulepath
    if [[ $MODULEPATH =~ (^|:)"$1"($|:) ]] ; then
        return 1
    fi
    if [ -z $MODULEPATH ]; then
        export MODULEPATH="$1"
    else
        export MODULEPATH="$1:$MODULEPATH"
    fi
}

MODULEPATH="/modules/modulefiles"
# the microarch modules no longer cover production spack
# add each architecture's Core directory to modulepath
for arch in $(ls ../../share/spack/lmod/ | grep ^linux-ubuntu); do
    prepend_modulepath($(dirname $(dirname $PWD))/share/spack/lmod/$arch/Core)
done

# -D debug
source /usr/share/lmod/lmod/libexec/update_lmod_system_cache_files -D $MODULEPATH
