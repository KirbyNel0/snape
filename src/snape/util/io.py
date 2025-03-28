__all__ = [
    "info",
    "log",
    "ask",
    "toggle_io"
]

INFO: bool = True
DEBUG: bool = False


def toggle_io(informational: bool, debug: bool) -> None:
    """
    Toggles whether the ``info`` and ``log`` methods output anything.
    """
    global INFO, DEBUG
    INFO = informational
    DEBUG = debug

    if debug:
        log("Debug output enabled")


def info(*message, **kwargs) -> None:
    """
    Output informational messages.

    Prints all specified objects to standard output using the ``print`` function.

    :param message: Messages to print.
    :param kwargs: Arguments to pass to ``print``.
    """
    if INFO:
        print(*message, **kwargs)


def log(*message, **kwargs) -> None:
    """
    Output debug log messages.

    Prints all specified objects to standard output using the ``print`` function.

    :param message: Messages to print.
    :param kwargs: Arguments to pass to ``print``.
    """
    if DEBUG:
        print("\033[33m+", *message, "\033[0m", **kwargs)


def ask(prompt: str, default: bool | None) -> bool:
    """
    Prompts the user to enter either yes (``y``/``Y``) or no (``n``/``N``).
    If a default is specified, no input will result into that output.
    Only single letter input will be accepted (case-insensitive).

    :param prompt: The thing to ask the user. Will be printed to standard output together with ``[y/n]`` question.
    :param default: The default result to return if the user enters nothing.
        If `None`, the user is required to enter something.
    :return: The user's selection as ``bool``.
    """
    if default is None:
        default_str = "[y/n]"
    else:
        default_str = "[Y/n]" if default else "[y/N]"

    while True:
        answer = input(f"{prompt} {default_str} ")
        if answer in ("y", "Y"):
            return True
        elif answer in ("n", "N"):
            return False
        elif answer == "" and default is not None:
            return default
