from spack.pkg.builtin.miniconda3 import Miniconda3 as Miniconda3Base
from spack.pkg.builtin.miniconda3 import _versions as _versions_base

_versions = {
    "22.11.1": {
        "Linux-x86_64": (
            "00938c3534750a0e4069499baf8f4e6dc1c2e471c86a59caa0dd03f4a9269db6",
            "https://repo.anaconda.com/miniconda/Miniconda3-py310_22.11.1-1-Linux-x86_64.sh",
        ),
        "Linux-ppc64le": (
            "4c86c3383bb27b44f7059336c3a46c34922df42824577b93eadecefbf7423836",
            "https://repo.anaconda.com/miniconda/Miniconda3-py310_22.11.1-1-Linux-ppc64le.sh",
        )
    }
}

_versions.update(_versions_base)

class Miniconda3(Miniconda3Base):
    pass
