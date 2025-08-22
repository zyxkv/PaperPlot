"""
Terminal color & text formatting utilities for PaperPlot.

API:
Classes / Singletons:
- COLORS: Provides color escape sequences adapted to current theme (ppplt._theme in {"dark","light","dumb"}).
- FORMATS: Provides style escape sequences (BOLD, ITALIC, UNDERLINE, RESET) also theme-aware.

Functions:
- styless(text: str) -> str: Remove ANSI escape sequences from text.

Instances:
- colors: Singleton instance of COLORS.
- formats: Singleton instance of FORMATS.

Behavior:
- When theme is "dumb" all escape sequences become empty strings (no color control characters in output).
- Designed for logger / console pretty printing without leaking escape sequences into captured logs.
"""

import re
import ppplt


class COLORS:
    # Reference:
    # https://talyian.github.io/ansicolors/
    # https://bixense.com/clicolors/
    def __init__(self) -> None:
        pass

    @property
    def GREEN(self):
        if ppplt._theme == "dark":
            return "\x1b[38;5;119m"
        elif ppplt._theme == "light":
            return "\x1b[38;5;2m"
        elif ppplt._theme == "dumb":
            return ""

    @property
    def BLUE(self):
        if ppplt._theme == "dark":
            return "\x1b[38;5;159m"
        elif ppplt._theme == "light":
            return "\x1b[38;5;17m"
        elif ppplt._theme == "dumb":
            return ""

    @property
    def YELLOW(self):
        if ppplt._theme == "dark":
            return "\x1b[38;5;226m"
        elif ppplt._theme == "light":
            return "\x1b[38;5;3m"
        elif ppplt._theme == "dumb":
            return ""

    @property
    def RED(self):
        if ppplt._theme == "dark":
            return "\x1b[38;5;9m"
        elif ppplt._theme == "light":
            return "\x1b[38;5;1m"
        elif ppplt._theme == "dumb":
            return ""

    @property
    def CORN(self):
        if ppplt._theme == "dark":
            return "\x1b[38;5;11m"
        elif ppplt._theme == "light":
            return "\x1b[38;5;178m"
        elif ppplt._theme == "dumb":
            return ""

    @property
    def GRAY(self):
        if ppplt._theme == "dark":
            return "\x1b[38;5;247m"
        elif ppplt._theme == "light":
            return "\x1b[38;5;239m"
        elif ppplt._theme == "dumb":
            return ""

    @property
    def MINT(self):
        if ppplt._theme == "dark":
            return "\x1b[38;5;121m"
        elif ppplt._theme == "light":
            return "\x1b[38;5;23m"
        elif ppplt._theme == "dumb":
            return ""


class FORMATS:
    def __init__(self) -> None:
        pass

    @property
    def BOLD(self):
        if ppplt._theme == "dumb":
            return ""
        else:
            return "\x1b[1m"

    @property
    def ITALIC(self):
        if ppplt._theme == "dumb":
            return ""
        else:
            return "\x1b[3m"

    @property
    def UNDERLINE(self):
        if ppplt._theme == "dumb":
            return ""
        else:
            return "\x1b[4m"

    @property
    def RESET(self):
        if ppplt._theme == "dumb":
            return ""
        else:
            return "\x1b[0m"


def styless(text):
    pattern = re.compile(r"\x1b\[(\d+)(?:;\d+)*m")
    return pattern.sub("", text)


colors = COLORS()
formats = FORMATS()
