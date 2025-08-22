"""
Miscellaneous utilities for PaperPlot.

API (selected):
Exceptions & Raising:
- DeprecationError(Exception): Custom deprecation exception.
- raise_exception(msg: str) -> NoReturn: Raise PaperPlotException.
- raise_exception_from(msg: str, cause: Exception|None) -> NoReturn: Raise with chained cause.

Context Managers:
- redirect_libc_stderr(fd): Temporarily redirect low-level C/C++ stderr (file descriptor 2) to provided file-like.

Decorators:
- assert_initialized(cls): Ensure ppplt._initialized before object construction.
- assert_style_unset(method): Guard methods that require style not yet set.
- assert_style_set(method): Guard methods that require style already set.

Platform & Path Helpers:
- get_platform() -> str: One of {macOS, Windows, Linux, Unix}.
- get_src_dir() -> str: Directory of ppplt package.
- get_style_dir() -> str: Directory containing style definitions under package.
- get_debug_log_dir() -> str: Unique per-run debug log directory path.

Behavior:
- redirect_libc_stderr uses platform-specific libc / msvcrt calls; on Windows is skipped under pytest due to handle issues.
- Style decorators rely on ppplt global state flags (_initialized, etc.).
"""

import ctypes
import datetime
import functools
import logging
import platform
import random
import types
import shutil
import sys
import os
from dataclasses import dataclass
from collections import OrderedDict
from typing import Any, Type, NoReturn, Optional

import numpy as np
import cpuinfo
import psutil

import ppplt

LOGGER = logging.getLogger(__name__)


class DeprecationError(Exception):
    pass


def raise_exception(msg="Something went wrong.") -> NoReturn:
    raise ppplt.PaperPlotException(msg)


def raise_exception_from(msg="Something went wrong.", cause=None) -> NoReturn:
    raise ppplt.PaperPlotException(msg) from cause


class redirect_libc_stderr:
    """
    Context-manager that temporarily redirects C / C++ std::cerr (i.e. the C `stderr` file descriptor 2) to a given
    Python file-like object's fd.

    Works on macOS, Linux (glibc / musl), and Windows (MSVCRT / Universal CRT ≥ VS2015).
    """

    def __init__(self, fd):
        self.fd = fd
        self.stderr_fileno = None
        self.original_stderr_fileno = None

    # --------------------------------------------------
    # Enter: duplicate stderr → tmp, dup2(target) → stderr
    # --------------------------------------------------
    def __enter__(self):
        self.stderr_fileno = sys.stderr.fileno()
        self.original_stderr_fileno = os.dup(self.stderr_fileno)
        sys.stderr.flush()

        if os.name == "posix":  # macOS, Linux, *BSD, …
            libc = ctypes.CDLL(None)
            libc.fflush(None)
            libc.dup2(self.fd.fileno(), self.stderr_fileno)
        elif os.name == "nt":  # Windows
            # FIXME: Do not redirect stderr on Windows OS when running pytest, otherwise it will raise this exception:
            # "OSError: [WinError 6] The handle is invalid"
            if "PYTEST_VERSION" not in os.environ:
                msvcrt = ctypes.CDLL("msvcrt")
                kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

                msvcrt.fflush(None)
                msvcrt._dup2(self.fd.fileno(), self.stderr_fileno)

                STDERR_HANDLE = -12
                new_os_handle = msvcrt._get_osfhandle(self.fd.fileno())
                kernel32.SetStdHandle(STDERR_HANDLE, new_os_handle)
        else:
            ezsim.logger.warning(f"Unsupported platform for redirecting libc stderr: {sys.platform}")

        return self

    # --------------------------------------------------
    # Exit: restore previous stderr, close the temp copy
    # --------------------------------------------------
    def __exit__(self, exc_type, exc_value, traceback):
        if self.stderr_fileno is None:
            return

        if os.name == "posix":
            libc = ctypes.CDLL(None)
            sys.stderr.flush()
            libc.fflush(None)
            libc.dup2(self.original_stderr_fileno, self.stderr_fileno)
        elif os.name == "nt":
            if "PYTEST_VERSION" not in os.environ:
                msvcrt = ctypes.CDLL("msvcrt")
                kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

                sys.stderr.flush()
                msvcrt.fflush(None)
                msvcrt._dup2(self.original_stderr_fileno, self.stderr_fileno)

                STDERR_HANDLE = -12
                orig_os_handle = msvcrt._get_osfhandle(self.original_stderr_fileno)
                kernel32.SetStdHandle(STDERR_HANDLE, orig_os_handle)

        os.close(self.original_stderr_fileno)
        self.stderr_fileno = None
        self.original_stderr_fileno = None


def assert_initialized(cls):
    original_init = cls.__init__

    def new_init(self, *args, **kwargs):
        if not ppplt._initialized:
            raise RuntimeError("PaperPlot hasn't been initialized. Did you call `ppplt.init()`?")
        original_init(self, *args, **kwargs)

    cls.__init__ = new_init
    return cls


def assert_style_unset(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.is_style_set:
            ppplt.raise_exception(f"PaperPlot style is already set as {self.current_style}.")
        return method(self, *args, **kwargs)

    return wrapper


def assert_style_set(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.is_style_set:
            ppplt.raise_exception(f"{type(self).__name__} style is not set yet.")
        return method(self, *args, **kwargs)

    return wrapper


def get_platform():
    name = platform.platform()
    # in python 3.8, platform.platform() uses mac_ver() on macOS
    # it will return 'macOS-XXXX' instead of 'Darwin-XXXX'
    if name.lower().startswith("darwin") or name.lower().startswith("macos"):
        return "macOS"

    if name.lower().startswith("windows"):
        return "Windows"

    if name.lower().startswith("linux"):
        return "Linux"

    if "bsd" in name.lower():
        return "Unix"

    assert False, f"Unknown platform name {name}"


def get_src_dir():
    return os.path.dirname(ppplt.__file__)


def get_style_dir():
    return os.path.join(get_src_dir(), "styles")


def get_debug_log_dir():
    current_time = datetime.datetime.now()
    unique_id = current_time.strftime("%Y%m%d_%H%M%S_%f")
    return os.path.join(os.path.dirname(ppplt.__file__), "debug", "logs", unique_id)
