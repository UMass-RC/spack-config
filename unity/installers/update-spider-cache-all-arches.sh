#!/bin/bash
TARGETS="x86_64 aarch64 ppc64le"
for target in $TARGETS; do
    sbatch --constraint=$target update-spider-cache.sh
done

