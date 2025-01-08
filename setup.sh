#!/bin/sh

SNAPE_SHELL=$(basename $SHELL)

while getopts "hvs:" OPT
do
	case $OPT in
		h)
			cat <<EOF
usage: sh setup.sh"

  Sets up snape for the current shell
  After setup, restart your shell to use snape.
  With snape setup, run 'snape setup' for further information.

arguments (only one at a time):
	-h	show this help and exit
	-v	enable debug output
  	-s	set up snape for the specified shell (current: $SHELL)
EOF
			exit 0
			;;
		s)
			SNAPE_SHELL=$OPTARG
			;;
		v)
			SNAPE_OPT=-v
			;;
		?)
			exit 1
			;;
	esac
done

if [ -z "$SNAPE_PYTHON" ]
then
	export SNAPE_PYTHON="/usr/bin/python3"
fi

if [ -f "$(dirname "$SNAPE_PYTHON")/activate" ]
then
  cat <<WARN
Warning: It seems like your python executable is contained within a virtual environment.
         You should select a different installation to run snape.
         This can be done by setting the \$SNAPE_PYTHON variable.
WARN
fi

if ! "$SNAPE_PYTHON" --version >/dev/null
then
	echo "Python not found at $SNAPE_PYTHON (\$SNAPE_PYTHON variable)" >&2
	exit 2
fi

if ! "$SNAPE_PYTHON" -c "import venv" >/dev/null
then
	echo "python-venv is not installed for $SNAPE_PYTHON" >&2
	exit 3
fi

"$SNAPE_PYTHON" run.py $SNAPE_OPT -s "$SNAPE_SHELL" setup init
