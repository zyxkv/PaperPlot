"""
Logging utilities for PaperPlot with colored, compact output.

API:
Functions:
- get_clock(t: float, speed: int = 10) -> str: Return a clock emoji frame based on elapsed time.

Classes:
- TimeElapser: Context manager-like helper (used via logger.timer) to show live elapsed time updates.
- PaperPlotFormatter(logging.Formatter): Color + time formatting, inline emphasis markers (~<text>~ variants).
- Logger: Facade wrapping Python logging with ANSI styling, timer integration, and raw writes.

Logger Methods (selected):
- debug/info/warning/error/critical(msg): Standard level logging with styling.
- raw(message: str): Write raw (optionally styled) text without level/time prefix.
- timer(msg, refresh_rate=10, end_msg=""): Start a TimeElapser for live progress time display.
- lock_timer(): Internal context manager coordinating timer vs. normal log output.

Styling Markers:
- Replace sequences: ~< ... >~, ~~< ... >~~, etc. to apply color + emphasis (bold / italic / underline) layers.

Behavior:
- TimeElapser periodically rewrites same line until completion, then prints a success mark.
- Formatter shortens level names to single letters, aligns with minimal console footprint.
"""

import sys
import time
import logging
import threading
import numpy as np
from contextlib import contextmanager

from ppplt.style import colors, formats


def get_clock(t, speed=10):
    return "🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚🕛"[int(t * speed) % 12]


class TimeElapser:
    """
    A tool that can be called with `with` statement, and starts a separate thread that continuously outputs logger message with elasped time.
    """

    def __init__(self, logger, refresh_rate, end_msg):
        self.logger = logger
        self.dt = 1.0 / refresh_rate
        self.n = np.ceil(np.log10(refresh_rate)).astype(int)
        self._stop = threading.Event()

        self.last_logger_output = self.logger.last_output
        # re-print the logger message without the reset character
        self.start_msg = self.last_logger_output[:-4]
        # adding back the reset character
        self.end_msg = end_msg + self.last_logger_output[-4:] + "\n"

    def __enter__(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._stop.set()
        self.thread.join()

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def run(self):
        # re-print logger msg from the beginning of the previous line
        self.logger.raw("\x1b[1F" + self.start_msg + " ")
        t_start = time.perf_counter()
        t_elapsed = time.perf_counter() - t_start
        self.logger.raw(f"~<{t_elapsed:.{self.n}f}s>~ {get_clock(t_elapsed)} ")
        prev_width = len(f"{t_elapsed:.{self.n}f}s ") + 3
        while not self._stop.is_set():
            time.sleep(self.dt)
            with self.logger.lock_timer():
                t_elapsed = time.perf_counter() - t_start
                # check if something in the main thread has moved the cursor to a new line
                if self.logger._is_new_line:
                    self.logger.raw(self.start_msg + " ")
                else:
                    self.logger.raw("\b" * prev_width)
                self.logger.raw(f"~<{t_elapsed:.{self.n}f}s>~ {get_clock(t_elapsed)} ")
                prev_width = len(f"{t_elapsed:.{self.n}f}s ") + 3
        self.logger.raw("\b\b\b✅ " + self.end_msg)


class PaperPlotFormatter(logging.Formatter):
    def __init__(self, log_time=True, verbose_time=True):
        super(PaperPlotFormatter, self).__init__()

        self.mapping = {
            logging.DEBUG: colors.GREEN,
            logging.INFO: colors.BLUE,
            logging.WARNING: colors.YELLOW,
            logging.ERROR: colors.RED,
            logging.CRITICAL: colors.RED,
        }
        self.log_time = log_time
        if verbose_time:
            self.TIME = "%(asctime)s.%(msecs)03d"
            self.TIMESTAMP = "%(created).3f"  # 使用统一的毫秒级时间戳
            self.TIMESTAMP_length = 17  # 例如：1717991234.123 (13位整数+1点+3位小数)
            # self.DATE_FORMAT = "%y-%m-%d %H:%M:%S"
            self.DATE_FORMAT = "%H:%M:%S"  # 包含毫秒
            self.INFO_length = 41
        else:
            self.TIME = "%(asctime)s"
            self.TIMESTAMP = "%(created).3f"  # 使用统一的毫秒级时间戳
            self.TIMESTAMP_length = 17  # 例如：1717991234.123 (13位整数+1点+3位小数)
            self.DATE_FORMAT = "%H:%M:%S"
            self.INFO_length = 28

        self.LEVEL = "%(levelname)s"
        self.MESSAGE = "%(message)s"

        self.last_output = ""
        self.last_color = ""

    def colored_fmt(self, color):
        self.last_color = color
        if self.log_time:
            return f"{color}[Pplt] [{self.TIME}] [{self.LEVEL}] {self.MESSAGE}{formats.RESET}"
        return f"{color}[Pplt] [{self.LEVEL}] {self.MESSAGE}{formats.RESET}"

    def extra_fmt(self, msg):
        msg = msg.replace("~~~~<", colors.MINT + formats.BOLD + formats.ITALIC)
        msg = msg.replace("~~~<", colors.MINT + formats.ITALIC)
        msg = msg.replace("~~<", colors.MINT + formats.UNDERLINE)
        msg = msg.replace("~<", colors.MINT)

        msg = msg.replace(">~~~~", formats.RESET + self.last_color)
        msg = msg.replace(">~~~", formats.RESET + self.last_color)
        msg = msg.replace(">~~", formats.RESET + self.last_color)
        msg = msg.replace(">~", formats.RESET + self.last_color)

        return msg

    def format(self, record):
        log_fmt = self.colored_fmt(self.mapping.get(record.levelno))
        record.levelname = record.levelname[0]
        formatter = logging.Formatter(log_fmt, datefmt=self.DATE_FORMAT)
        msg = self.extra_fmt(formatter.format(record))
        self.last_output = msg
        return msg


class Logger:
    def __init__(self, logging_level, log_time, verbose_time):
        if isinstance(logging_level, str):
            logging_level = logging_level.upper()

        self._logger = logging.getLogger("ppplot")
        self._logger.setLevel(logging_level)

        self._formatter = PaperPlotFormatter(log_time, verbose_time)

        self._handler = logging.StreamHandler(sys.stdout)
        self._handler.setLevel(logging_level)
        self._handler.setFormatter(self._formatter)
        self._logger.addHandler(self._handler)

        self._stream = self._handler.stream
        self._is_new_line = True

        self.timer_lock = threading.Lock()

    def addFilter(self, filter):
        self._logger.addFilter(filter)

    def removeFilter(self, filter):
        self._logger.removeFilter(filter)

    def removeHandler(self, handler):
        self._logger.removeHandler(handler)

    @property
    def INFO_length(self):
        return self._formatter.INFO_length

    @contextmanager
    def log_wrapper(self):
        self.timer_lock.acquire()

        # swap with timer output
        if not self._is_new_line and not self._stream.closed:
            self._stream.write("\r")
        try:
            yield
        finally:
            self._is_new_line = True
            self.timer_lock.release()

    @contextmanager
    def lock_timer(self):
        self.timer_lock.acquire()
        try:
            yield
        finally:
            self.timer_lock.release()

    def log(self, level, msg, *args, **kwargs):
        with self.log_wrapper():
            self._logger.log(level, msg, *args, **kwargs)

    def debug(self, message):
        with self.log_wrapper():
            self._logger.debug(message)

    def info(self, message):
        with self.log_wrapper():
            self._logger.info(message)

    def warning(self, message):
        with self.log_wrapper():
            self._logger.warning(message)

    def error(self, message):
        with self.log_wrapper():
            self._logger.error(message)

    def critical(self, message):
        with self.log_wrapper():
            self._logger.critical(message)

    def raw(self, message):
        self._stream.write(self._formatter.extra_fmt(message))
        self._stream.flush()
        if message.endswith("\n"):
            self._is_new_line = True
        else:
            self._is_new_line = False

    def timer(self, msg, refresh_rate=10, end_msg=""):
        self.info(msg)
        return TimeElapser(self, refresh_rate, end_msg)

    @property
    def handler(self):
        return self._handler

    @property
    def last_output(self):
        return self._formatter.last_output

    @property
    def level(self):
        return self._logger.level
