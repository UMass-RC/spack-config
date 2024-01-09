#!/usr/bin/env python3
#!/bin/bash
#SBATCH -c 1
#SBATCH -t 4:00:00
#SBATCH -p cpu-preempt

"""
hide implicit spack modules from Lmod
makes output which should be written into a .modulerc.lua file
implicit modules are those that were not asked for, only included as a dependency

requires an arch (e.g. "linux-ubuntu20.04-x86_64") passed as an argument
that is, "arch" based on Spack terminology, which includes platform and OS version,
not to be confused with "target" (e.g. "x86_64").

I am badly bottlenecked by I/O, you might want to make me a batch job

when this comes out in a spack update, this script will be redundant
https://github.com/spack/spack/pull/36619
"""

import os
import sys
import json
import subprocess

SPACK_PREFIX="/modules/spack/0.20.0" # no trailing slash here
ARCH2OUTFILE={
        "x86_64": f"{SPACK_PREFIX}/share/spack/lmod/linux-ubuntu20.04-x86_64/Core/.modulerc.lua",
        "aarch64": f"{SPACK_PREFIX}/share/spack/lmod/linux-ubuntu20.04-aarch64/Core/.modulerc.lua",
        "ppc64le": f"{SPACK_PREFIX}/share/spack/lmod/linux-ubuntu20.04-ppc64le/Core/.modulerc.lua",
}
USE_SYMLINKS_INSTEAD={
    f"{SPACK_PREFIX}/share/spack/lmod": "/modules/spack_modulefiles"
}

def shell_cmd(*args, **kwargs):
    return subprocess.check_output(*args, **kwargs).decode("utf8").strip()

def hide_implicit_modules(arch: str) -> str:
    find_cmd = ["spack", "find", "--json", "--implicit", f"arch={arch}"]
    output_lines = [
        "-- this is the output from Unity's hide-implicit-modules.py"
        "-- https://github.com/UMass-RC/spack-config/tree/main/unity/installers"
        f"-- {' '.join(find_cmd)}"
    ]
    print(' '.join(find_cmd))
    implicit_modules_json_str = shell_cmd(find_cmd, timeout=60)
    modules_json_parser = json.loads(implicit_modules_json_str)
    for module in modules_json_parser:
        try:
            # I think it might be faster to look for name@version/hash rather than just /hash
            spec_str = f"{module['name']}@{module['version']}/{module['hash'][:10]}"
            find_module_cmd = ["spack", "module", "lmod", "find", "--full-path", spec_str]
            print(' '.join(find_module_cmd))
            module_location = shell_cmd(find_module_cmd, timeout=60)
        except subprocess.CalledProcessError:
            err_msg = f"-- ERROR: command failed: \"{' '.join(find_module_cmd)}\""
            print(err_msg)
            output_lines.append(err_msg)
            continue
        except subprocess.TimeoutExpired:
            err_msg = f"-- ERROR: command timed out: \"{' '.join(find_module_cmd)}\""
            print(err_msg)
            output_lines.append(err_msg)
            continue
        if not os.path.exists(module_location):
            print("output of search is something other than the location of a modulefile!")
            print(f"output: \"{module_location}\"")
            output_lines.append("-- ERROR: command returned invalid output: {' '.join(find_module_cmd}")
            continue
        for _dir, link in USE_SYMLINKS_INSTEAD.items():
            module_location = module_location.replace(_dir, link)
        hide_statement = f"hide_modulefile(\"{module_location}\")"
        print(hide_statement)
        output_lines.append(hide_statement)
    return '\n'.join(output_lines)

if os.geteuid() == 0:
    print("Do not run this as root!")
    sys.exit(1)

sys.stdout.reconfigure(line_buffering=True, write_through=True)

print(f"which spack? {shell_cmd(['which', 'spack'])}")

for arch,output_file_path in ARCH2OUTFILE.items():
    print(f"I will overwrite file \"{output_file_path}\"...")
    output = hide_implicit_modules(arch)
    print(f"overwriting file \"{output_file_path}\"...")
    with open(output_file_path, 'w', encoding="utf8") as out_file:
        out_file.write(output)

