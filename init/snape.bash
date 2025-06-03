#!/bin/bash

if ! (return 0 2>/dev/null); then
	echo "snape: The initialization script must be sourced to work properly" 1>&2
	return 100
fi

if test -z "$SNAPE_PYTHON"; then
	export SNAPE_PYTHON="/usr/bin/python3"
fi

if ! "$SNAPE_PYTHON" -c "import venv" >/dev/null 2>&1; then
	echo "snape: Python installation or venv package not found" 1>&2
	return 2
fi

if test -z "$SNAPE_ROOT"; then
	export SNAPE_ROOT="$HOME/.snape"
fi

if test -z "$SNAPE_VENV"; then
	export SNAPE_VENV=".venv"
fi

export _SNAPE_SCRIPT=$(realpath "$(dirname "${BASH_SOURCE[0]}")/../src/snape/__main__.py")
export _SNAPE_SCRIPT_CMD="help --help -h new touch delete rm env setup status possess attach detach clean exec"

_find_snape_venv() {
	RESULT="$(realpath "$(pwd)")"
	while test "$RESULT" != "/"; do
		if test -f "$RESULT/$SNAPE_VENV/bin/activate" -a -f "$RESULT/$SNAPE_VENV/bin/python"; then
			echo "$RESULT"
			unset RESULT
			return 0
		fi
		RESULT=$(dirname "$RESULT")
	done
	unset RESULT
	return 1
}

function snape {
	mkdir -p "$SNAPE_ROOT"

	if ! test -d "$SNAPE_ROOT"; then
		echo "snape: Unable to create root directory" 1>&2
		return 1
	fi

	# No environment given
	if test $# -eq 0; then
		# venv is active => deactivate
		if test -n "$VIRTUAL_ENV"; then
			deactivate
			return 0
		fi

		# Check if valid local environment exists
		LOCAL_VENV=$(_find_snape_venv)
		if test "$?" -ne 0; then
			echo "No snape environment found (nor in any parent directory)" >&2
			echo "Run snape new to create one" >&2
			unset LOCAL_VENV
			return 2
		fi

		# Activate local environment
		source "$LOCAL_VENV/$SNAPE_VENV/bin/activate"
		unset LOCAL_VENV
		return 0
	fi

	# This seems like a python problem
	if echo "$_SNAPE_SCRIPT_CMD" | grep -wq -- "$1"; then
		"$SNAPE_PYTHON" "$_SNAPE_SCRIPT" "$@"
		return $?
	fi

	# Environment given which should be activated
	if test $# -eq 1; then
		if test -f "$SNAPE_ROOT/$1/bin/activate" -a -f "$SNAPE_ROOT/$1/bin/python"; then
			# Deactivate the current environment before activating the new one
			if test -n "$VIRTUAL_ENV"; then
				deactivate
			fi

			if source "$SNAPE_ROOT/$1/bin/activate"; then
				return 0
			else
				return 3
			fi
		else
			echo "No environment named \"$1\""
			return 4
		fi
	fi

	# This script cannot handle more than one argument,
	# anything else is passed to the python script
	"$SNAPE_PYTHON" "$_SNAPE_SCRIPT" "$@"
}

export -f snape

# Autocompletion cannot handle environment names with spaces in it
function _snape_autocomplete() {
	# If not autocompleting the first argument, default to file autocompletion
	if [ "$COMP_CWORD" -ne 1 ]; then
		COMPREPLY=($(compgen -A file -- "${COMP_WORDS[$COMP_CWORD]}"))
		return
	fi

	local ENVS=()

	# Check for existing global environments
	for ENV in $(ls "$SNAPE_ROOT"); do
		local SNAPE_ENV="${SNAPE_ROOT%/}/$ENV"
		if [ -d "$SNAPE_ENV" -a -f "$SNAPE_ENV/bin/activate" -a -f "$SNAPE_ENV/bin/python" ]; then
			ENVS+=("$ENV")
		fi
	done

	# Check for local environment
	if [ -d "$SNAPE_VENV" ]; then
		ENVS+=("--local")
	fi

	# autocomplete commands
	ENVS+=($_SNAPE_SCRIPT_CMD)

	# Complete with all found environments
	COMPREPLY+=($(compgen -W "${ENVS[*]}" -- "${COMP_WORDS[1]}"))
}

complete -F _snape_autocomplete snape
