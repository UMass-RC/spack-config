import platform
from spack.package import *
from spack.pkg.builtin.ont_guppy import OntGuppy as OntGuppyBase

_versions = {
    "6.5.7-cuda": {
        "Linux-x86_64": (
            "c3dd8f8b7567061a155d1921586dd95540410b35b2ccb8a33a463d9db8642711",
            "https://cdn.oxfordnanoportal.com/software/analysis/ont-guppy_6.5.7_linux64.tar.gz",
        )
    }
}

class OntGuppy(OntGuppyBase):
    for ver, packages in _versions.items():
        key = "{0}-{1}".format(platform.system(), platform.machine())
        pkg = packages.get(key)
        if pkg:
            version(ver, sha256=pkg[0], url=pkg[1])
