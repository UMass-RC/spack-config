#!/usr/bin/env python3

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
import subprocess
import json
from typing import Tuple

TCL_OR_LMOD="lmod" # spack module tcl find, or spack module lmod find

def red(x: str) -> str:
    return "\033[91m" + x + "\033[0m"

def lua_comment(x: str):
    x = "-- " + x.strip().replace('\n', "\n-- ")
    return x

def shell_command(command: str, timeout_s: int) -> Tuple[str, str]:
    process = subprocess.run(command,timeout=timeout_s,capture_output=True,shell=True,check=True)
    return str(process.stdout, 'UTF-8'), str(process.stderr, 'UTF-8')

if len(sys.argv) != 2:
    print(red(lua_comment("invalid arguments!")))
    exit(1)
ARCH=sys.argv[1]

print(red(lua_comment("this is the output from Unity's hide-implicit-modules.py")))
print(red(lua_comment("https://github.com/UMass-RC/spack-config/tree/main/unity/installers")))
print(red(lua_comment(shell_command("which spack", 1)[0])))
find_cmd=f"spack find --json --implicit arch={ARCH}"
print(red(lua_comment(find_cmd)))
stdout, stderr = shell_command(find_cmd, 60)
modules_json_parser = json.loads(stdout)
for module in modules_json_parser:
    try:
        # I think it might be faster to look for name@version/hash rather than just /hash
        spec_str = f"{module['name']}@{module['version']}/{module['hash'][:10]}"
        find_module_cmd = f"spack module lmod find --full-path {spec_str}"
        stdout, stderr = shell_command(find_module_cmd, 60)
        module_location = stdout.strip()
    except subprocess.CalledProcessError:
        print(red(lua_comment(f"ERROR: command failed: {find_module_cmd}")))
        continue
    if not os.path.exists(module_location):
        print(red(lua_comment("output of search is something other than the location of a modulefile!")))
        print(red(lua_comment(module_location)))
        continue
    print(f"hide_modulefile(\"{module_location}\")")
