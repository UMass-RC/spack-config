# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# ----------------------------------------------------------------------------
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
# This is a template package file for Spack.  We've put "FIXME"
# next to all the things you'll want to change. Once you've handled
# them, you can save this file and test your package like this:
#
#     spack install bwa-mem2
#
# You can edit this file again by typing:
#
#     spack edit bwa-mem2
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from glob import glob
from spack.package import *


class BwaMem2(MakefilePackage):
    """The next version of bwa-mem"""

    homepage = "https://github.com/bwa-mem2/bwa-mem2"
    url = "https://github.com/bwa-mem2/bwa-mem2/releases/download/v2.2.1/Source_code_including_submodules.tar.gz"

    version("2.2.1", sha256="9b001bdc7666ee3f14f3698b21673714d429af50438b894313b05bc4688b1f6d")

    depends_on("zlib")

    def install(self, sepc, prefix):
        mkdir(prefix.bin)
        files= glob("bwa-mem2*")
        for file in files:
            install(file, prefix.bin)
