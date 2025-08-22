from ppplt import Subplot
import numpy as np


def random_plot_data(data_point_length: int = 20):
    x = np.arange(data_point_length)
    y = np.c_[x, x**1.2, x**1.5]
    return x, y


def load_img(folder_path: str = "assets", fmt: str = "png"):
    import glob
    import os
    from PIL import Image

    img_paths = glob.glob(f"{folder_path}/*.{fmt}")
    img_dict = {}

    for img_path in img_paths:
        img_name = os.path.basename(img_path).split(".")[0]  # Get filename without extension
        img = Image.open(img_path)
        img_array = np.array(img)
        img_dict[img_name] = img_array

    return img_dict


def single_plot(
    row,
    col,
):
    """
    one-column figure (half page width)
    """
    with Subplot() as sp:
        sp.subplot(row, col)
