from spack.package import *
from spack.pkg.builtin.mummer4 import Mummer4 as Mummer4Base

class Mummer4(Mummer4Base):
    depends_on("gnuplot", type=("build","run"))
