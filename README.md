# Snape Virtual Environment Manager

Snape is a shell-python wrapper for the [`venv`](https://docs.python.org/3/library/venv.html) package to manage python virtual environments (aka. venvs) easily.
Of course, the name comes from the awesome Harry Potter universe.

Snape can manage environments for a single project (called *local* venvs) or for your whole system (called *global venvs*).
It can

- (de)activate environments
- create new environments
- delete existing environments

## Installation

`snape` requires you to have Python 3.7 or higher to be installed on your system.
That installation must have the `venv` package installed (usually named `python3-virtualenv` by package managers).
By default, that installation is assumed to be located at `/usr/bin/python3`.
To change that behavior, set the `SNAPE_PYTHON` variable to point to the python executable of your choice.

To install `snape`, clone the repository into a directory of your choice (e.g. `~/.local`) and run the setup script.
This can be achieved using the following commands:

```shell
git clone https://github.com/KirbyNel0/snape.git ~/.local/snape
cd ~/.local/snape
sh setup.sh
```

This will modify your shell initialization file to load the `snape` alias/function on shell startup.
Restart your shell to finish installation.

Snape will infer what shell you are using by reading the `$SHELL` variable.
If you want to install snape for a different shell (e.g. `zsh`), use `sh setup.sh -s zsh` instead.

## Deinstallation

To remove snape, run the following commands:

```shell
snape setup remove --all
rm -r ~/.local/snape
```

If you installed snape for multiple shells, be sure to remove snape for all those shells using `snape -s`.

## Usage

After installation, `snape` is available as a normal shell command. To list all available commands, run

```shell
snape help
```

## Autocompletion

Currently, autocompletion is only supported for the `bash` shell.
It will complete available environments to activate.

To enable autocompletion for the `bash` shell, put the following line into your `~/.bashrc` file, where `~/.local/snape`
is the path to the `snape` repository:

```bash
source ~/.local/snape/autocomplete/snape-complete.bash
```
