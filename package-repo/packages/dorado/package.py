# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
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
#     spack install dorado
#
# You can edit this file again by typing:
#
#     spack edit dorado
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack.package import *
import os


class Dorado(CMakePackage,CudaPackage):
    """Oxford Nanopore's Basecaller"""

    homepage = "https://nanoporetech.com/"
    url = "https://github.com/nanoporetech/dorado/archive/refs/tags/v0.3.1.tar.gz"
    git = "https://github.com/nanoporetech/dorado/"

    #version("0.3.1", sha256="586b0a2ea1a8d72233a6716235f75e8cefe3a8ca9005d116f532b3f8d0c186aa")
    version("0.3.1", tag="v0.3.1", submodules=True)


    depends_on("cuda")
    depends_on("htslib")
    depends_on("hdf5")
    depends_on("zstd")
    depends_on("openssl")

    sanity_check_is_file = ["bin/dorado"]

    def install(self, spec, prefix):
        with working_dir(self.build_directory):
          make("install")
          #install.tree("../dist", self.prefix)
          mkdir(join_path(prefix, "bin"))
          mkdir(join_path(prefix, "lib"))
          copy("../dist/bin/dorado", join_path(prefix, "bin"))
          install_tree("../dist/lib", join_path(prefix, "lib"))

    def patch(self):
        with open(join_path(self.stage.source_path,"dorado/3rdparty/htslib/htscodecs/htscodecs/version.h"), "a") as fd:
            fd.write('#define HTSCODECS_VERSION_TEXT "1.16"')
        with open(join_path(self.stage.source_path,"dorado/3rdparty/htslib/version.h"), "a") as fd:
            fd.write("#define HTSCODECS_VERSION_TEXT HTS_VERSION_TEXT")

    def cmake_args(self):
        cudatoolkitdir = self.spec["cuda"].prefix
        htsdir = self.spec["htslib"].prefix
        args = [f"-DCUDA_TOOLKIT_ROOT_DIR={cudatoolkitdir}",  "-DCMAKE_C_FLAGS=-DHTS_VERSION_TEXT=1.16",
                self.define("CMAKE_CXX_COMPILER", self.spec["mpi"].mpicxx),
                ]
        return args
