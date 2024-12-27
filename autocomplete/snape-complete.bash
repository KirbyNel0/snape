#!/usr/bin/env bash

if [ -z "$SNAPE_ROOT" ]; then
	export SNAPE_ROOT="$HOME/.snape"
fi

if [ -z "$SNAPE_VENV" ]; then
	export SNAPE_VENV="snape"
fi

if [ -z "$SNAPE_LOCAL_VENV" ]; then
	export SNAPE_LOCAL_VENV=".venv"
fi

function _snape_autocomplete() {
	# If not autocompleting the first argument, default to file autocompletion
	if [ "$COMP_CWORD" -ne 1 ]; then
		COMPREPLY=($(compgen -A file -- "${COMP_WORDS[$COMP_CWORD]}"))
		return
	fi

	local ENVS=()

	# Check for existing global environments
	for ENV in $(ls "$SNAPE_ROOT")
	do
		local SNAPE_ENV="${SNAPE_ROOT%/}/$ENV"
		if [ -d "$SNAPE_ENV" -a -f "$SNAPE_ENV/bin/activate" -a -f "$SNAPE_ENV/bin/python" ]; then
			ENVS+=("$ENV")
		fi
	done

	# Check for local environment
	if [ -d "$SNAPE_LOCAL_VENV" ]; then
		ENVS+=("--here")
	fi

	# Complete with all found environments
	COMPREPLY+=($(compgen -W "${ENVS[*]}" -- "${COMP_WORDS[1]}"))
}

complete -F _snape_autocomplete snape
