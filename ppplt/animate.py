"""
Media helpers (animation & image saving) for PaperPlot.

API:
- animate(imgs: list[np.ndarray|PIL.Image|path], filename: str|None = None, fps: int = 60) -> None
    Build an MP4 video from a list of image frames (in-memory arrays or paths) using moviepy.
    If filename is None: derives base name from caller file + timestamp.
- save_img_arr(arr: np.ndarray, filename: str = "img.png") -> None
    Save a single numpy array as an image file.

Utility Classes:
- Timer: Lightweight hierarchical timing / profiling helper with pretty console output.
- Rate: Sleep helper to maintain a target loop frequency.
- FPSTracker: Exponential moving average FPS estimator emitting logs.
- create_timer(name: str|None, new: bool=False, level:int=0, ti_sync:bool=False, skip_first_call: bool=False)
    Factory returning (and caching) Timer instances; unnamed timers are always new.

Behavior:
- Video writing uses libx264 ultrafast preset for development speed.
- Logging integrates with ppplt.logger to provide uniform styled output.
- Future TODO markers kept for potential watermark / audio / subtitle extensions.
"""

import inspect
import os
import threading
import time

import numpy as np
from PIL import Image

import ppplt


def animate(imgs, filename=None, fps=60):
    """
    Create a video from a list of images.

    Args:
        imgs (list): List of input images.
        filename (str, optional): Name of the output video file. If not provided, the name will be default to the name of the caller file, with a timestamp and '.mp4' extension.
    """
    assert isinstance(imgs, list)
    if len(imgs) == 0:
        ppplt.logger.warning("No image to save.")
        return

    if filename is None:
        caller_file = inspect.stack()[-1].filename
        # caller file + timestamp + .mp4
        filename = os.path.splitext(os.path.basename(caller_file))[0] + f'_{time.strftime("%Y%m%d_%H%M%S")}.mp4'
    os.makedirs(os.path.abspath(os.path.dirname(filename)), exist_ok=True)

    ppplt.logger.info(f'Saving video to ~<"{filename}">~...')
    from moviepy import ImageSequenceClip

    imgs = ImageSequenceClip(imgs, fps=fps)
    imgs.write_videofile(
        filename,
        fps=fps,
        logger=None,
        codec="libx264",
        preset="ultrafast",
        # ffmpeg_params=["-crf", "0"],
    )
    ppplt.logger.info("Video saved.")


def save_img_arr(arr, filename="img.png"):
    assert isinstance(arr, np.ndarray)
    os.makedirs(os.path.abspath(os.path.dirname(filename)), exist_ok=True)
    img = Image.fromarray(arr)
    img.save(filename)
    ppplt.logger.info(f"Image saved to ~<{filename}>~.")


class Timer:
    def __init__(self, skip=False, level=0):
        self.accu_log = dict()
        self.skip = skip
        self.level = level
        self.msg_width = 0
        self.reset()

    def reset(self):
        self.just_reset = True
        if self.level == 0 and not self.skip:
            print("─" * os.get_terminal_size()[0])
        self.prev_time = self.init_time = time.perf_counter()

    def _stamp(self, msg="", _ratio=1.0):
        if self.skip:
            return

        self.cur_time = time.perf_counter()
        self.msg_width = max(self.msg_width, len(msg))
        step_time = 1000 * (self.cur_time - self.prev_time) * _ratio
        accu_time = 1000 * (self.cur_time - self.init_time) * _ratio

        if msg not in self.accu_log:
            self.accu_log[msg] = [1, step_time, accu_time]
        else:
            self.accu_log[msg][0] += 1
            self.accu_log[msg][1] += step_time
            self.accu_log[msg][2] += accu_time

        if self.level > 0:
            prefix = " │  " * (self.level - 1)
            if self.just_reset:
                prefix += " ╭──"
            else:
                prefix += " ├──"
        else:
            prefix = ""

        print(
            f"{prefix}[{msg.ljust(self.msg_width)}] step: {step_time:5.3f}ms | accu: {accu_time:5.3f}ms | step_avg: {self.accu_log[msg][1]/self.accu_log[msg][0]:5.3f}ms | accu_avg: {self.accu_log[msg][2]/self.accu_log[msg][0]:5.3f}ms"
        )

        self.prev_time = time.perf_counter()
        self.just_reset = False


timers = dict()


def create_timer(name=None, new=False, level=0, ti_sync=False, skip_first_call=False):
    if name is None:
        return Timer()
    else:
        if name in timers and not new:
            timer = timers[name]
            timer.skip = False
            timer.reset()
            return timer
        else:
            timer = Timer(skip=skip_first_call, level=level, ti_sync=ti_sync)
            timers[name] = timer
            return timer


class Rate:
    def __init__(self, rate):
        self.rate = rate
        self.last_time = time.perf_counter()

    def sleep(self):
        current_time = time.perf_counter()
        sleep_duration = 1.0 / self.rate - (current_time - self.last_time)
        if sleep_duration > 0:
            time.sleep(sleep_duration)
        self.last_time = time.perf_counter()


class FPSTracker:
    def __init__(self, alpha=0.95):
        self.last_time = None
        self.dt_ema = None
        self.alpha = alpha

    def step(self):
        current_time = time.perf_counter()

        if self.last_time:
            dt = current_time - self.last_time
        else:
            self.last_time = current_time
            return

        if self.dt_ema:
            self.dt_ema = self.alpha * self.dt_ema + (1 - self.alpha) * dt
        else:
            self.dt_ema = dt
        fps = 1 / self.dt_ema
        self.total_fps = fps
        ppplt.logger.info(f"FPS: ~<{fps:.2f}>~ .")
        self.last_time = current_time
