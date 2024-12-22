#!/bin/sh

if test "$1" = "--help" -o "$1" = "-h"
then
	cat <<EOF
usage: sh setup.sh"

  Sets up snape for the current shell
  After setup, restart your shell to use snape.
  With snape setup, run 'snape setup' for further information.

arguments (only one at a time):
	-h, --help    show this help and exit
  	-s, --shell   set up snape for the specified shell
EOF
	exit 0
fi

if [ -z "$SNAPE_PYTHON" ]
then
	export SNAPE_PYTHON="/usr/bin/python3"
fi

if ! "$SNAPE_PYTHON" --version >/dev/null
then
	echo "Python not found at $SNAPE_PYTHON" >&2
	exit 2
fi

if ! "$SNAPE_PYTHON" -c "import venv" >/dev/null
then
	echo "python-venv is not installed" >&2
	exit 2
fi

if test "$1" = "--shell" -o "$1" = "-s"
then
	if test -z "$2"
	then
		echo "No shell name provided ($1)" >&2
		exit 2
	fi
	"$SNAPE_PYTHON" snape/run.py -s "$2" setup init
	exit $?
fi

"$SNAPE_PYTHON" snape/run.py setup init
