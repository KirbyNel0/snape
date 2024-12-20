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

if ! command -v /usr/bin/python3 >/dev/null
then
	echo "Python not found at /usr/bin/python3" >&2
	exit 2
fi

if ! /usr/bin/python3 -c "import venv" >/dev/null
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
	/usr/bin/python3 py/snape.py -s "$2" setup init
	exit $?
fi

/usr/bin/python3 py/snape.py setup init
