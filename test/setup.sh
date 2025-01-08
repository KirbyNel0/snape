if [ "$(basename "$(dirname "$(realpath "$0")")")" != "test" ]
then
	echo "Not running in directory snape/test"
	exit 1
fi

if ! python3 -c "import venv" >/dev/null 2>&1
then
	echo "The venv package is not installed at $(which python3)"
	exit 2
fi

if [ -d ".venv" -a -f ".venv/bin/python3" -a -f ".venv/bin/pip3" -a -f ".venv/bin/activate" ]
then
	echo "\033[36;1m+ Virtual environment exists, skipping\033[0m"
else
	echo "\033[36;1m+ Creating virtual environment for testing\033[0m"
	python3 -m venv ".venv/" --upgrade-deps --clear
fi

echo "\033[36;1m+ Installing requirements\033[0m"
.venv/bin/pip3 install -r requirements.txt
