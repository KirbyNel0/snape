#!/bin/sh

if test "$1" = "--help" -o "$1" = "-h"
then
	echo "usage: sh setup.sh"
	echo
	echo "  Sets up snape for the current shell"
	echo "  After setup, restart your shell to use snape."
	echo "  With snape setup, run 'snape setup' for further information."
	echo
	echo "arguments (only one at a time):"
	echo "	-h, --help    show this help and exit"
	echo "  -s, --shell   set up snape for the specified shell"
	exit 0
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
