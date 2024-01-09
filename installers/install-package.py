#!/usr/bin/env python3
import os
import re
import sys
import atexit
import tempfile
import argparse
import datetime
import subprocess

if os.geteuid() == 0:
    print("Do not run this as root!")
    sys.exit(1)

parser = argparse.ArgumentParser(description="""
    I submit batch jobs to run `spack install [spack package spec]` with sensible defaults.
    examples:
        ./install-package.py zlib
        ./install-package.py "netlib-scalapack ^openblas ^openmpi"
        ./install-package.py -y -a "x86_64,ppc64le" zlib
        EXTRA_SPACK_ARGS="--use-buildcache never" ./install-package.py zlib
        EXTRA_SBATCH_ARGS="-G 1" ./install-package.py zlib
    environment variables:
        EXTRA_SPACK_INSTALL_ARGS: `spack install $EXTRA_SPACK_ARGS [spack package spec]`
        EXTRA_SBATCH_ARGS: `sbatch $EXTRA_SBATCH_ARGS batch-script.sh`
        SPACK_PREFIX: path to spack

    spack package spec -> https://spack.readthedocs.io/en/latest/basic_usage.html#sec-specs
    spack install args -> https://spack.readthedocs.io/en/latest/command_index.html#spack-install
    sbatch args -> https://slurm.schedmd.com/sbatch.html
""", formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-a", "--arches", type=str, default="x86_64,ppc64le,aarch64", help='\n'.join([
                    "comma separated list of architectures",
                    "`... spack install [package_spec] target=[ARCH]`",
                    "`sbatch --constraint=[ARCH] ...`"
                    ]))
parser.add_argument("-c", "--cpus-per-task", type=int, default=4,
                    help="sbatch --cpus-per-task={} ...")
parser.add_argument("-d", "--debug", default="", action="store_const", const="--debug",
                    help="spack --debug install ...")
parser.add_argument("--export", type=str, default="",
                    help="sbatch --export={} ...")
parser.add_argument("package_spec", type=str,
                    help="https://spack.readthedocs.io/en/latest/basic_usage.html#sec-specs")
parser.add_argument("--mem", type=str, default="32G",
                    help="sbatch --mem={} ...")
parser.add_argument("-p", "--partition", type=str, default="building",
                    help="sbatch --partition={} ...")
parser.add_argument("-t", "--time", type=str, default="1-0",
                    help="sbatch --time={} ...")
parser.add_argument("-y", "--yes", action="store_true",
                    help="skip prompt y/n")
args = parser.parse_args()

PREFIX = os.path.dirname(os.path.abspath(sys.argv[0])) # parent directory of this script
SPACK_PREFIX = os.getenv("SPACK_PREFIX", None)
if not SPACK_PREFIX:
    SPACK_PREFIX = os.path.dirname(os.path.dirname(PREFIX)) # PREFIX/../..
BATCH_SCRIPT_CONTENT=f"""\
#!/bin/bash -l
set -e
set -o pipefail
# TMPDIR is overwrittten during slurm prolog
if [ ! -z "$TMPDIR_NAME" ]; then
    export TMPDIR=$TMPDIR_NAME
fi
echo "jobid $SLURM_JOB_ID on host $(hostname) by user $(whoami) on $(date)"
echo "you can find my source files and build logs in $TMPDIR"
echo source {SPACK_PREFIX}/share/spack/setup-env.sh
source {SPACK_PREFIX}/share/spack/setup-env.sh
echo $@
eval $@

"""
batch_script_path = tempfile.mktemp(suffix=".sh")
with open(batch_script_path, 'w', encoding="utf8") as batch_script_file:
    batch_script_file.write(BATCH_SCRIPT_CONTENT)
atexit.register(os.remove, batch_script_path) # no longer needed after job submission

now = str(datetime.datetime.now().timestamp()).split('.')[0] # integer number of seconds since epoch

EXTRA_SPACK_INSTALL_ARGS = os.environ.get('EXTRA_SPACK_INSTALL_ARGS', "")
EXTRA_SBATCH_ARGS = os.environ.get('EXTRA_SBATCH_ARGS', "")

tmpdir_path = os.path.join(PREFIX, "install-tmp")
if not os.path.isdir(tmpdir_path):
    tmpdir_path = tempfile.mkdtemp()
    print(f"./install-tmp is not a directory! Temp files will instead be placed under {tmpdir_path}.")
logdir_path = os.path.join(PREFIX, "logs")
if not os.path.isdir(logdir_path):
    logdir_path = os.path.join(tmpdir_path, "logs")
    print(f"./logs is not a directory! logs will instead be placed under {logdir_path}.")
    os.mkdir(logdir_path)

package_spec_one_word = re.sub(r"[\s]+", "-", args.package_spec)
package_spec_filename = package_spec_one_word.replace('/', '-').replace('^', '-')

jobs = []
for arch in args.arches.split(','):
    job_tmpdir_path = os.path.join(tmpdir_path, f"{now}-{package_spec_filename}-{arch}")
    os.mkdir(job_tmpdir_path)
    log_file_path = os.path.join(logdir_path, f"{now}-{package_spec_filename}-{arch}.log")
    if len(args.export) > 0:
        _export=f"--export='{args.export},TMPDIR_NAME={job_tmpdir_path}'"
    else:
        _export=f"--export='TMPDIR_NAME={job_tmpdir_path}'"
    job = f" \
        sbatch --job-name={package_spec_one_word}-{arch} --output={log_file_path} \
        --partition={args.partition} --cpus-per-task={args.cpus_per_task} \
        --mem={args.mem} --time={args.time} --nodes=1 --constraint={arch} \
        {_export} {EXTRA_SBATCH_ARGS} {batch_script_path} \
        unbuffer spack --color=never --timestamp {args.debug} install --yes --fail-fast --keep-stage \
        --source {EXTRA_SPACK_INSTALL_ARGS} \"{args.package_spec} target={arch}\" \
    "
    job = re.sub(r"[\s]+", ' ', job)
    job = job.strip()
    jobs.append(job)

def print_job_highlighted(job_str:str):
    ansi_start = '\033[96m'
    ansi_end = '\033[0m'
    try:
        before_spack, after_spack = job_str.split(" spack ")
        print(before_spack + ansi_start + " spack " + after_spack + ansi_end)
    except ValueError: # failed to split job string by " spack " into two halves
        print(job_str)

print()
for job in jobs:
    print_job_highlighted(job)
    print()

if not args.yes and sys.stdin.isatty():
    while(True):
        print("would you like to submit these jobs? (y/n) ", end='')
        response = input("").lower() # case insensitive
        if len(response) == 0:
            continue
        if response[0] == 'y':
            break
        if response[0] == 'n':
            print("goodbye")
            sys.exit(0)
        continue

for job in jobs:
    subprocess.run(job, check=True, shell=True)
