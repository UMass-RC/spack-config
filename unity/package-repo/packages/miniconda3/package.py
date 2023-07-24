import platform
from spack.package import version
from spack.pkg.builtin.miniconda3 import Miniconda3 as Miniconda3Base

class Miniconda3(Miniconda3Base):
    # add arm versions
    if platform.system() == "Linux" and platform.machine() == "aarch64":
        version("22.11.1",
                sha256="48a96df9ff56f7421b6dd7f9f71d548023847ba918c3826059918c08326c2017",
                url="https://repo.anaconda.com/miniconda/Miniconda3-py310_22.11.1-1-Linux-aarch64.sh",
                expand=False)
        version("23.3.1",
                sha256="6950c7b1f4f65ce9b87ee1a2d684837771ae7b2e6044e0da9e915d1dee6c924c",
                url="https://repo.anaconda.com/miniconda/Miniconda3-py310_23.3.1-0-Linux-aarch64.sh",
                expand=False)
