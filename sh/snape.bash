#!/bin/bash

if ! (return 0 2>/dev/null); then
	echo "This script must be sourced to work properly" 1>&2
	return 100
fi

if [ -z "$SNAPE_PYTHON" ]; then
	export SNAPE_PYTHON="/usr/bin/python3"
fi

if ! "$SNAPE_PYTHON" -c "import venv" >/dev/null 2>&1; then
	echo "Python installation or venv package not found" 1>&2
	return 2
fi

if [ -z "$SNAPE_ROOT" ]; then
	export SNAPE_ROOT="$HOME/.snape"
fi

if [ -z "$SNAPE_VENV" ]; then
	export SNAPE_VENV="snape"
fi

if [ -z "$SNAPE_LOCAL_VENV" ]; then
	export SNAPE_LOCAL_VENV=".venv"
fi

SNAPE_SCRIPT=$(realpath "$(dirname "${BASH_SOURCE[0]}")/../snape/run.py")
SNAPE_SCRIPT_CMD="help --help -h new touch delete rm list setup status possess clean"

mkdir -p "$SNAPE_ROOT"

if ! test -d "$SNAPE_ROOT"; then
	echo "Unable to create snape directory" 1>&2
	return 3
fi

# No environment given
if [[ $# -eq 0 ]]; then
	# venv is active => deactivate
	if [[ -n "$VIRTUAL_ENV" ]]; then
		deactivate
		return 0
	fi
	
	# Snape is inactive => activate default environment
	if ! [[ -f "$SNAPE_ROOT/$SNAPE_VENV/bin/activate" && -f "$SNAPE_ROOT/$SNAPE_VENV/bin/python" ]]; then
		# The default environment does not exist, create it
		if ! "$SNAPE_PYTHON" "$SNAPE_SCRIPT" new "$SNAPE_VENV"; then
			return 4
		fi
	fi

	# activate
	source "$SNAPE_ROOT/$SNAPE_VENV/bin/activate"
	return 0
fi

# This seems like a python problem
if echo "$SNAPE_SCRIPT_CMD" | grep -wq -- "$1"; then
	"$SNAPE_PYTHON" "$SNAPE_SCRIPT" $@
	return $?
fi

# Environment given which should be activated
if [[ "$#" == 1 ]]; then
	# Manage local environment
	if [[ "$1" == "here" || "$1" == "--here" ]]; then
		# Environment is active, deactivate
		if [[ -n "$VIRTUAL_ENV" ]]; then
			deactivate
			return 0
		fi

		if ! [[ -f "$SNAPE_LOCAL_VENV/bin/activate" && -f "$SNAPE_LOCAL_VENV/bin/python" ]]; then
			echo "No snape environment found in the current directory" >&2
			echo "Run snape new --here to create one" >&2
			return 5
		fi

		source "$SNAPE_LOCAL_VENV/bin/activate"
		return 0
	fi

	if [[ -f "$SNAPE_ROOT/$1/bin/activate" && -f "$SNAPE_ROOT/$1/bin/python" ]]; then
		# Deactivate the current environment before activating the new one
		if [[ -n "$VIRTUAL_ENV" ]]; then
			deactivate
		fi

		if source "$SNAPE_ROOT/$1/bin/activate"; then
			return 0
		else
			return 6
		fi
	else
		echo "No environment named '$1'"
		return 7
	fi
fi

# This script cannot handle more than one argument,
# anything else is passed to the python script
"$SNAPE_PYTHON" "$SNAPE_SCRIPT" $@
