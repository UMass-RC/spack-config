#!/bin/bash

PREFIX="/modules/spack-0.19.1/unity/installers"
ARCHITECTURES="x86_64,ppc64le,aarch64"
#ARCHITECTURES="$ARCHITEECTURES,cascadelake,haswell,icelake,skylake_avx512,zen,zen2"
CPUS_PER_TASK="4"
TIME="1-0"
PARTITION="building"
FRESH_OR_REUSE="--reuse"
GPU=""
MEMORY="32G"

read -r -d '' help <<- HELP
	I submit Slurm batch jobs which install things via spack.
	You can \`tail -f [log file]\` to watch it go.

	usage:
	install-package.sh [spack package spec]
	install-package.sh [-a arch] [-c cpus] [-p partition] [-t time] [-d|f|h|y] [spack package spec]

	examples:
		install-package.sh -yf -a ppc64le apptainer@1.1.5+suid
		EXTRA_SPACK_ARGS="--use-buildcache never" install-package.sh apptainer@1.1.5+suid
		EXTRA_SBATCH_ARGS="-G 1" install-package.sh apptainer@1.1.5+suid

	spack package spec -> https://spack.readthedocs.io/en/latest/basic_usage.html#sec-specs
	spack install args -> https://spack.readthedocs.io/en/latest/command_index.html#spack-install
	sbatch args -> https://slurm.schedmd.com/sbatch.html

	options:
		-a      comma separated list of architectures to be added to spack specs
		-d      debug
		-f      spack install --fresh (default --reuse)
		-h      display this message
		-y      yes

	options forwarded to sbatch (don't use EXTRA_SBATCH_ARGS for these):
		-c		cpus            default: "$CPUS_PER_TASK"
		-p		partition       default: "$PARTITION"
		-t		time            default: "$TIME"

	environment variables:
		EXTRA_SPACK_ARGS: \`spack install \$EXTRA_SPACK_ARGS [spack package spec]\`
		EXTRA_SBATCH_ARGS: \`sbatch \$EXTRA_SBATCH_ARGS slurm-install-batch.sh\`

HELP

set -e # exit if any command fails

prompt_yes_or_no() {
	echo $@
	read input
	yes_or_no $input
	result=$?
	if [ $result -eq 2 ]; then
		prompt_yes_or_no $@ # try again
		return $?
	else
		return $result
	fi
}

yes_or_no() {
	case $1 in
		[Yy]) return 0 ;;
		[Yy]es) return 0 ;;
		[Tt]rue) return 0;;
		[Nn]) return  1;;
		[Nn]o) return  1;;
		[Ff]alse) return  1;;
		*) return 2;;
	esac
}

if (( $EUID == 0 )); then
	echo "do not run this as root!"
	exit 1
fi

if [ ! -d "$PREFIX" ]; then
	echo "PREFIX \"$PREFIX\" does not exist!"
	exit 1
fi

if [ $# -eq 0 ]; then
	echo "not enough arguments!"
	echo "$help"
	exit 1
fi

PACKAGE_SPEC="${@: -1}" # get last argument
set -- "${@:1:$(($#-1))}" # remove last argument

while getopts "a:c:dfhp:t:y" option; do
	case $option in
		a) ARCHITECTURES=$OPTARG;;
		c) CPUS_PER_TASK=$OPTARG;;
		d) DEBUG="-d";;
		f) FRESH_OR_REUSE="--fresh";;
		h) echo "$help"; exit;;
		p) PARTITION=$OPTARG;;
		t) TIME=$OPTARG;;
		y) DO_SKIP_PROMPT="true"
	esac
done
shift $(($OPTIND - 1)) # remove processed arguments from the list

if (( $# > 0 )); then
	echo "too many arguments!"
	echo "$help"
	exit 1
fi

BATCH_SCRIPT_PATH=$(mktemp)
# just for peace of mind, shouldn't ever happen
if [ ! -e "$BATCH_SCRIPT_PATH" ]; then
	echo "mktemp was supposed to create file \"$BATCH_SCRIPT_PATH\" but it doesn't exist!"
	exit 1
fi
cat <<- BATCH_SCRIPT > $BATCH_SCRIPT_PATH
	#!/bin/bash
	echo "jobid \$SLURM_JOB_ID on host \$(hostname) by user \$(whoami) on \$(date)"
	source $PREFIX/../share/spack/setup-env.sh
	echo "spack $DEBUG install \$SPACK_INSTALL_ARGS"
	spack $DEBUG install \$SPACK_INSTALL_ARGS
	if [ ! \$? -eq 0 ]; then
		# copy spack-build-out and spack-build-env in case we need to make a github issue
		stage_dir=/scratch/\$(hostname)/\$SLURM_JOB_ID/\$(whoami)/spack-stage/
		if [ -d \$stage_dir ]; then
			ARGS_LIST=(\$SPACK_INSTALL_ARGS)
			# 2nd to last argument is the package name, last argument is the target architecture
			stage_copy_dir=$PREFIX/logs/failed-builds/\$(date +%s)-\${ARGS_LIST[-2]}-\${ARGS_LIST[-1]}
			mkdir -p \$stage_copy_dir
			cp \$stage_dir \$stage_copy_dir/
			cp \$stage_dir \$stage_copy_dir/
			echo "spack stage copied to \$stage_copy_dir/"
		else
			echo "spack stage directory \$stage_dir doesn't exist!"
		fi
	fi
BATCH_SCRIPT

IFS="," # comma separated list
for arch in $ARCHITECTURES; do
	if [ -z $(echo $arch | xargs) ]; then continue; fi # ignore blank
	SPACK_INSTALL_ARGS="\
$FRESH_OR_REUSE -y --keep-stage --fail-fast \
$EXTRA_SPACK_ARGS $PACKAGE_SPEC target=$arch"
	# include time so that `ls` sorts chronologically
	LOG_FILE="$PREFIX/logs/$(date +%s)-${PACKAGE_SPEC}-${arch}.out"
	touch $LOG_FILE # make sure we have permissions to the log file
	log_files+=("$LOG_FILE")
	this_job="\
sbatch --job-name=\"$PACKAGE_SPEC-$arch\" --output=\"$LOG_FILE\" --partition=\"$PARTITION\" \
--cpus-per-task=\"$CPUS_PER_TASK\" --mem=\"$MEMORY\" --time=\"$TIME\" -N 1 \
--export=\"SPACK_INSTALL_ARGS=$SPACK_INSTALL_ARGS\" --constraint=$arch \
$EXTRA_SBATCH_ARGS $BATCH_SCRIPT_PATH"
	echo "$this_job"
	echo
	JOBS+=("$this_job")
done
unset IFS

if [[ $DO_SKIP_PROMPT == "true" ]] || prompt_yes_or_no "do you want to submit these jobs?"; then
	echo
	IFS=$'\n'
	for i in ${!JOBS[@]}; do
		job=${JOBS[$i]}
		logfile=${log_files[$i]}
		eval "$job"
		echo $logfile
		echo
	done
	unset IFS
fi
