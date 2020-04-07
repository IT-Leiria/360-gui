
"""

"""

import os

import cv2
import queue

image_queue = queue.Queue()     # Queue to hold images


class Controller:
    """
    Application Controller:
    - our iteraction with api client..
    """
    def __init__(self, frames=None, frame=None):
        self.frames = frames
        self.frame = frame

    @staticmethod
    def get_frames():
        image_folder = "/home/na-simoes/Desktop/NunoSimoes/py_projects/pre_aroundvision/tests/imgs/"
        images = [os.path.join(image_folder, img) for img in sorted(os.listdir(image_folder)) if img.endswith(".jpeg")]
        return images

    def get_frame(self, filename):
        return cv2.imread(filename)
