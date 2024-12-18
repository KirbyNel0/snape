#!/bin/bash

# The SNAPE_ENV variable checks whether the current python environment is managed by snape
# The SNAPE_ROOT variable contains the path to all snape environments (default: ~/.snape)
# The SNAPE_VENV variable defines the name of the default environment (default: snape)
# The SNAPE_PY variable points to the python script to execute as fallback

if ! (return 0 2>/dev/null)
then
	echo "This script must be sourced to work properly" 1>&2
	exit 100
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

SNAPE_PY=$(dirname "$BASH_SOURCE")/snape.py

function is-snape-venv() {
	[[ -f "$SNAPE_ROOT/$1/bin/activate" && "$SNAPE_ROOT/$1/bin/python" ]]
}

mkdir -p "$SNAPE_ROOT"

if ! test -d "$SNAPE_ROOT"
then
	echo "Unable to create snape directory" 1>&2
	return 1
fi

# No environment given
if [[ $# -eq 0 ]]
then
	# venv is active => deactivate
	if [[ -n "$VIRTUAL_ENV" ]]
	then
		deactivate
		unset SNAPE_ENV
		return 0
	fi
	
	# Snape is inactive => activate default environment
	if ! [[ -f "$SNAPE_ROOT/$SNAPE_VENV/bin/activate" && "$SNAPE_ROOT/$SNAPE_VENV/bin/python" ]]
	then
		# The default environment does not exist, create it
		if ! /usr/bin/python "$SNAPE_PY" new "$SNAPE_VENV"
		then
			return 2
		fi
	fi
	
	# activate
	snape "$SNAPE_VENV"
	return 0
fi

# This seems like a python problem
if [[ "$1" == "help" || "$1" == "--help" || "$1" == "-h"\
   || "$1" == "new" || "$1" == "delete" || "$1" == "list" || "$1" == "setup" || "$1" == "status" ]]
then
	/usr/bin/python "$SNAPE_PY" $@
	return $?
fi

# Environment given which should be activated
if [[ "$#" == 1 ]]
then
	# Manage local environment
	if [[ "$1" == "here" || "$1" == "--here" ]]
	then
		# Environment is active, deactivate
		if [[ -n "$VIRTUAL_ENV" ]]
		then
			deactivate
			unset SNAPE_ENV
			return 0
		fi
		
		if ! [[ -f "$SNAPE_LOCAL_VENV/bin/activate" && "$SNAPE_LOCAL_VENV/bin/python" ]]
		then
			echo "No snape environment found in the current directory" >&2
			echo "Run snape new --here to create one" >&2
			return 1
		fi
		
		source "$SNAPE_LOCAL_VENV/bin/activate"
		return 0
	fi
	
	if [[ -f "$SNAPE_ROOT/$1/bin/activate" && "$SNAPE_ROOT/$1/bin/python" ]]
	then
		# Deactivate the current environment before activating the new one
		if [[ -n "$VIRTUAL_ENV" ]]
		then
			deactivate
			unset SNAPE_ENV
		fi
		
		if source "$SNAPE_ROOT/$1/bin/activate"
		then
			export SNAPE_ENV=$1
			return 0
		else
			return 3
		fi
	else
		echo "No environment named $1"
		return 4
	fi
fi

# This script cannot handle more than one argument,
# anything else is passed to the python script
/usr/bin/python "$SNAPE_PY" $@
