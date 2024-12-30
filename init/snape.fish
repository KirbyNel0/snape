#!/usr/bin/env fish

# if not test '$_' = source -o '$_' = .
#     echo "snape: The initialization script must be sourced to work properly" 1>&2
#     exit 100
# end

if [ -z "$SNAPE_PYTHON" ]
	set -x SNAPE_PYTHON "/usr/bin/python3"
end

if ! "$SNAPE_PYTHON" -c "import venv" >/dev/null 2>&1
	echo "snape: Python installation or venv package not found" 1>&2
	exit 2
end

if [ -z "$SNAPE_ROOT" ]
	set -x SNAPE_ROOT $HOME/.snape
end

if [ -z "$SNAPE_VENV" ]
	set -x SNAPE_VENV snape
end

if [ -z "$SNAPE_LOCAL_VENV" ]
	set -x SNAPE_LOCAL_VENV .snape
end

set SNAPE_SCRIPT (realpath (dirname (status current-filename))/../snape/run.py)
set SNAPE_SCRIPT_CMD "help --help -h new touch delete rm env setup status possess attach detach clean"

function snape
	mkdir -p "$SNAPE_ROOT"

	if ! [ -d "$SNAPE_ROOT" ]
		echo "snape: Unable to create root directory" 1>&2
		exit 1
	end

	# No environment given
	if [ (count $argv) -eq 0 ]
		# venv is active => deactivate
		if [ -n "$VIRTUAL_ENV" ]
			deactivate
			exit 0
		end

		# Snape is inactive => activate default environment
		if ! [ -f "$SNAPE_ROOT/$SNAPE_VENV/bin/activate.fish" -a -f "$SNAPE_ROOT/$SNAPE_VENV/bin/python" ]
			# The default environment does not exist, create it
			if ! /usr/bin/python3 "$SNAPE_SCRIPT" new "$SNAPE_VENV"
				exit 2
			end
		end

		# activate
		source "$SNAPE_ROOT/$SNAPE_VENV/bin/activate.fish"
		exit 0
	end

	# This seems like a python problem
	if echo "$SNAPE_SCRIPT_CMD" | grep -wq -- "$argv[1]"
		/usr/bin/python3 "$SNAPE_SCRIPT" $argv
		exit $status
	end

	# Environment given which should be activated
	if [ (count $argv) -eq 1 ]
		# Manage local environment
		if [ "$argv[1]" = "here" -o "$argv[1]" = "--here" -o "$argv[1]" = "--local" ]
			# Environment is active, deactivate
			if [ -n "$VIRTUAL_ENV" ]
				deactivate
			end

			if ! [ -f "$SNAPE_LOCAL_VENV/bin/activate.fish" -a -f "$SNAPE_LOCAL_VENV/bin/python" ]
				echo "No snape environment found in the current directory" >&2
				echo "Run snape new --here to create one" >&2
				exit 1
			end

			source "$SNAPE_LOCAL_VENV/bin/activate.fish"
			exit 0
		end

		if [ -f "$SNAPE_ROOT/$argv[1]/bin/activate.fish" -a -f "$SNAPE_ROOT/$argv[1]/bin/python" ]
			# Deactivate the current environment before activating the new one
			if [ -n "$VIRTUAL_ENV" ]
				deactivate
			end

			if source "$SNAPE_ROOT/$argv[1]/bin/activate.fish"
				exit 0
			else
				exit 3
			end
		else
			echo "No environment named $argv[1]"
			exit 4
		end
	end

	# This script cannot handle more than one argument,
	# anything else is passed to the python script
	/usr/bin/python3 "$SNAPE_SCRIPT" $argv
end
