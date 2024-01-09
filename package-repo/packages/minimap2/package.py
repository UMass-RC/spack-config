from spack.package import *
from spack.pkg.builtin.minimap2 import Minimap2 as Minimap2Base

class Minimap2(Minimap2Base):
    version("2.26", sha256="6a588efbd273bff4f4808d5190957c50272833d2daeb4407ccf4c1b78143624c")
