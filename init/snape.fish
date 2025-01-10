#!/usr/bin/env fish

# if test "$_" != source -a "$_" != .
#     echo "snape: The initialization script must be sourced to work properly" 1>&2
#     exit 100
# end

if test -z "$SNAPE_PYTHON"
	set -x SNAPE_PYTHON /usr/bin/python3
end

if ! "$SNAPE_PYTHON" -c "import venv" >/dev/null 2>&1
	echo "snape: Python installation or venv package not found" 1>&2
	exit 2
end

if test -z "$SNAPE_ROOT"
	set -x SNAPE_ROOT $HOME/.snape
end

if test -z "$SNAPE_VENV"
	set -x SNAPE_VENV .venv
end

set _SNAPE_SCRIPT (realpath (dirname (status current-filename))/../run.py)
set _SNAPE_SCRIPT_CMD "help --help -h new touch delete rm env setup status possess attach detach clean"

function _find_snape_venv
    set -l RESULT (realpath (pwd))
    while test "$RESULT" != "/"
        if test -f "$RESULT/$SNAPE_VENV/bin/activate.fish"; and test -f "$RESULT/$SNAPE_VENV/bin/python"
            echo "$RESULT"

            return 0
        end
    end

    return 1
end

function snape
	mkdir -p "$SNAPE_ROOT"

	if not test -d "$SNAPE_ROOT"
		echo "snape: Unable to create root directory" 1>&2
		return 1
	end

	# No environment given
	if test (count $argv) -eq 0
		# venv is active => deactivate
		if test -n "$VIRTUAL_ENV"
			deactivate
			return 0
		end

		# Check if valid local environment exists
		set -l LOCAL_VENV (_find_snape_venv)
		if test $status -ne 0
			echo "No snape environment found (nor in any parent directory)" >&2
			echo "Run snape new to create one" >&2

			return 2
		end

		# Activate local environment
		source "$LOCAL_VENV/$SNAPE_VENV/bin/activate.fish"

		return 0
	end

	# This seems like a python problem
	if echo "$_SNAPE_SCRIPT_CMD" | grep -wq -- "$argv[1]"
		"$SNAPE_PYTHON" "$_SNAPE_SCRIPT" $argv
		return $status
	end

	# Environment given which should be activated
	if test (count $argv) -eq 1
		if test -f "$SNAPE_ROOT/$argv[1]/bin/activate.fish"; and test -f "$SNAPE_ROOT/$argv[1]/bin/python"
			# Deactivate the current environment before activating the new one
			if test -n "$VIRTUAL_ENV"
				deactivate
			end

			if source "$SNAPE_ROOT/$argv[1]/bin/activate.fish"
				return 0
			else
				return 3
			end
		else
			echo "No environment named \"$argv[1]\""
			return 4
		end
	end

	# This script cannot handle more than one argument,
	# anything else is passed to the python script
	"$SNAPE_PYTHON" "$_SNAPE_SCRIPT" $argv
end
