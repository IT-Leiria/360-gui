
"""

"""

import logging
from ast import literal_eval
import urllib

from aroundvision.config.config_manager import CONF

import requests
import numpy as np
import cv2

logger = logging.getLogger(__name__)


class Controller(object):
    """
    Application Controller:
    - our iteraction with api client..
    """
    def __init__(self, model):
        self.model = model

        # Assign values from configurations
        self.session = requests.Session()
        self.model.api_endpoint.value = CONF.api_endpoint
        self.model.stream_index.value = CONF.api_selected_stream_idx

        # Request initial data from configuration
        self.get_stream_list()
        self.select_stream()

    def get_frame_from_api(self):
        while self.model.capturing.value:
            logger.info("Get frame from API : " + self.model.api_endpoint.value)

            # Get frame
            r = urllib.request.urlopen(self.model.api_endpoint.value + CONF.api_get_frame_raw_path + "?projection=" +
                                       self.model.selected_projection_api.value)
            content = r.read()
            size_content = len(content)
            logger.info("Request Status: {}!".format(str(r.status)))

            # Is the content has the expected size?
            if size_content == self.model.frame_len.value:
                logger.info("The frame has the expected size, let's insert it in the images queue!")
                self.model.image_queue.put(self.get_rgb_from_yuv(content))

    def select_stream(self):
        """Select Stream index in API"""
        select_stream_path = self.model.api_endpoint.value + CONF.api_select_stream_path + \
            "?idx=" + self.model.stream_index.value
        logger.info("Selecting stream in API {0}".format(select_stream_path))

        try:
            r = self.session.get(select_stream_path, stream=True)
            self.get_frame_info()

            logger.info("Select stream status {0}!".format(r.status_code))
        except requests.exceptions.RequestException as err:
            logger.warning("Connection Error {0}".format(str(err)))

    def get_frame_info(self):
        """Get frame info from selected stream on API"""
        get_frame_info_path = self.model.api_endpoint.value + CONF.api_get_frame_info + \
                              "?projection=" + self.model.selected_projection_api.value
        logger.info("Getting frame info in API {0}".format(get_frame_info_path))

        try:
            r = self.session.get(get_frame_info_path, stream=True)

            if r.status_code == 200:
                # build frame info
                frame_info = literal_eval(r.content.decode())
                self.model.width.value = frame_info["width"]
                self.model.height.value = frame_info["height"]
                self.model.shape.value = (int(self.model.height.value * 1.5), self.model.width.value)
                self.model.frame_len.value = int(self.model.width.value * self.model.height.value * 3 / 2)
                self.model.bytes_per_line.value = 3 * self.model.width.value

                logger.info("Get frame info status {0}!".format(r.status_code))
        except requests.exceptions.RequestException as err:
            logger.warning("Connection Error {0}".format(str(err)))

    def get_stream_list(self):
        """Get Stream List from API:
           - try to connect to API
           - return message: exception error or successfully status code
        """
        logger.info("Connecting to {0}".format(self.model.api_endpoint.value + CONF.api_get_stream_list_path))

        try:
            # get stream list from API
            r = self.session.get(self.model.api_endpoint.value + CONF.api_get_stream_list_path, stream=True)

            # update our model with values
            for i, s in enumerate(literal_eval(r.content.decode())):
                self.model.stream_list.value["stream" + str(i)] = {"name": s[0], "width": s[1], "height": s[2],
                                                                   "bytes_per_pixel": s[3], "number_of_layers": s[4]}

            self.model.api_connected.value = True
            logger.info("Connection Status {0} and our stream list {1}!".format(
                r.status_code, self.model.stream_list.value))

            return "Connection Status {0}!".format(str(r.status_code))

        except requests.exceptions.RequestException as err:
            logger.warning("Connection error: {0}".format(str(err)))
            self.model.api_connected.value = False
            self.model.stream_list.value.clear()
            return str(err)

    def get_rgb_from_yuv(self, raw):
        yuv = np.frombuffer(raw, dtype=np.uint8).reshape(self.model.shape.value)
        return cv2.cvtColor(yuv, cv2.COLOR_YUV420P2BGR)  # YV12)