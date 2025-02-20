import sys
import os
import subprocess
import argparse
from pathlib import Path

from snape import env_var
from snape.config import SHELLS
from snape.util import log, info
from snape.cli._parser import subcommands
from snape.virtualenv import get_snape_env_path, ensure_virtual_env

def snape_exec(
        *,
        cmd: list[str],
        env: str | None,
        local: bool,
        working_dir: str | None,
        quote: str,
        py_script: bool,
        as_python: bool
) -> int | None:
    """
    Execute some command using a specific snape environment.

    For argument documentation, see ``snape_exec_parser``.
    """
    snape_env = get_snape_env_path(env, local)
    log("Using snape environment:", snape_env)

    ensure_virtual_env(snape_env)

    python = str(snape_env / "bin/python")

    if working_dir is not None and not Path(working_dir).is_dir():
        raise NotADirectoryError(f"Invalid working directory specified: {working_dir}")

    # Enter working directory
    old_working_dir = os.getcwd()
    if working_dir is not None:
        log("Entering", working_dir)
        os.chdir(working_dir)
    
    process: subprocess.Popen | subprocess.CompletedProcess
    try:
        if as_python:
            # specify all arguments for python
            python_commands = ";".join(cmd)
            log("$", python, "-c", python_commands)
            info("$ " + "\n$ ".join(cmd))
            process = subprocess.run([python, "-c", python_commands])
        else:
            # Run in sub-shell
            shell: str = env_var.SHELL
            if shell is None:
                info("No shell specified")
                return

            shell_info = SHELLS[shell]
            activate_file = snape_env / shell_info["activate_file"]
            activate_command = f"source '{activate_file}'"
            command = " ".join(map(lambda s: quote + s.replace(quote, '\\' + quote) + quote, cmd))

            if py_script:
                log(f"Running script {cmd[0]} using {python}")
                command = quote + python + quote + " " + command

            log(f"Using {shell} in sub-shell")

            process = subprocess.Popen(shell, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr, text=True)
            info("$", activate_command)
            info("$", command)
            process.communicate(activate_command + "\n" + command)
            info("$", "deactivate")
    except BaseException as e:
        raise e
    finally:
        if working_dir is not None:
            log("Exiting", working_dir)
            os.chdir(old_working_dir)

    if process.returncode != 0:
        raise ChildProcessError(f"Command failed with exit code {process.returncode}")

    return process.returncode

snape_exec_parser = subcommands.add_parser(
    "exec",
    usage="snape exec [-e ENV | -l] [-d DIR] [-q SYMBOL] [-p | -s] -- cmd",
    description="""\
  Execute some command using a specific environment.

  Creates a sub-shell of the current shell ($SHELL or -s option),
  activates the specified environment in that shell and runs the specified command.
  
  By default, each part of the command is quoted in single quotation marks (') before being passed to the shell executable.
  To use double or no quotation marks, see -q.

  -- is not required if cmd does not contain any dashed options.\
    """,
    help="execute some command using a specific snape environment",
    formatter_class=argparse.RawDescriptionHelpFormatter
)

snape_exec_parser.add_argument(
    "cmd", nargs="+",
    help="the command to execute"
)
snape_exec_parser.add_argument(
    "-e", "--env", "--inside",
    help="the name of the environment to execute the command in",
    action="store", default=None, dest="env", metavar="ENV"
)
snape_exec_parser.add_argument(
    "-l", "--local", "--here",
    help="use a local environment instead of a global one. overrides --env.",
    action="store_true", default=False, dest="local"
)
snape_exec_parser.set_defaults(func=snape_exec)

snape_exec_parser_execution = snape_exec_parser.add_argument_group("execution behavior")
snape_exec_parser_execution.add_argument(
    "-d", "--working-dir",
    help="the working directory to use when executing the command. "
         "if not specified, uses the current working directory.",
    action="store", default=None, dest="working_dir", metavar="DIR"
)
snape_exec_parser_execution.add_argument(
    "-q", "--quote",
    help="specify a symbol to enclose each part of the command with (default: '). "
         r"the specified symbol is escaped inside each part using a backslash (e.g. \').",
    action="store", default="'", dest="quote", metavar="SYMBOL"
)
snape_exec_parser_execution.add_argument(
    "-s", "--script",
    help="run a python script using the specified environment. cmd must contain the script's path and its arguments.",
    action="store_true", default=False, dest="py_script"
)
snape_exec_parser_execution.add_argument(
    "-p", "--python",
    help="run cmd as a series of python commands instead of shell commands. will not open a sub-shell. ignores -q and -s.",
    action="store_true", default=False, dest="as_python"
)
