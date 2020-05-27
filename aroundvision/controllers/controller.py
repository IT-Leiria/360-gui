
import logging
from ast import literal_eval
import urllib

from aroundvision.config.config_manager import CONF

import requests
import numpy as np
import cv2

logger = logging.getLogger(__name__)


class Controller(object):
    """Application Controller: our interaction with api client.

    :param model: application model
    :type model: Model
    """
    def __init__(self, model):
        """Constructor for Controller."""
        logger.info("Starting building controller!")
        self.model = model

        # Start requests session..
        self.api_client = AroundvisionClient()

        # Request initial data from configuration
        self.get_stream_list()
        self.select_stream()

    def get_frame_from_api(self):
        """While we are capturing values (model.capturing = True) we will
        get frames from API and store them in model.image.queue.
        Here we are using urllib because has a better performance than requests."""
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

        r = self.api_client.create_request("get", select_stream_path)
        self.get_frame_info()

        logger.info("Select stream status {0}!".format(r["status_code"]))

    def get_frame_info(self):
        """Get frame info from selected stream on API. Here we are storing
        the following values in our model: frame width, height, shape, len and bytes per line."""
        get_frame_info_path = self.model.api_endpoint.value + CONF.api_get_frame_info + \
                              "?projection=" + self.model.selected_projection_api.value
        logger.info("Getting frame info in API {0}".format(get_frame_info_path))

        r = self.api_client.create_request("get", get_frame_info_path)

        if r["status_code"] == 200:
            # build frame info
            frame_info = literal_eval(r["content"].decode())
            self.model.width.value = frame_info["width"]
            self.model.height.value = frame_info["height"]
            self.model.shape.value = (int(self.model.height.value * 1.5), self.model.width.value)
            self.model.frame_len.value = int(self.model.width.value * self.model.height.value * 3 / 2)
            self.model.bytes_per_line.value = 3 * self.model.width.value

            logger.info("Get frame info status {0}!".format(r["status_code"]))

    def get_stream_list(self):
        """Get Stream List from API:
            - try to connect to API
            - return message: exception error or successfully status code
        """
        logger.info("Connecting to {0}".format(self.model.api_endpoint.value + CONF.api_get_stream_list_path))

        # get stream list from API
        r = self.api_client.create_request("get", self.model.api_endpoint.value + CONF.api_get_stream_list_path)

        # Success request?
        if r['status_code'] == 200:
            # yes, let's update our model with values
            for i, s in enumerate(literal_eval(r["content"].decode())):
                self.model.stream_list.value["stream" + str(i)] = \
                    {"name": s[0], "width": s[1], "height": s[2],
                     "bytes_per_pixel": s[3], "number_of_layers": s[4]}

            self.model.api_connected.value = True
            logger.info("Connection Status {0} and our stream list {1}!".format(
                r['status_code'], self.model.stream_list.value))

            return "Connection Status {0}!".format(str(r['status_code']))
        else:
            # no, let's return warning message
            self.model.api_connected.value = False
            self.model.stream_list.value.clear()
            return_msg = r["errors"] + r["content"].decode() if r["content"] != "" else r["errors"]
            return return_msg

    def get_rgb_from_yuv(self, raw):
        """Convert YUV420 to RGB array!

        :param raw: bytearray received by API
        :type raw: bytearray
        :return: cv2 array converted from yuv420 to bgr
        :rtype: bgr array
        """
        yuv = np.frombuffer(raw, dtype=np.uint8).reshape(self.model.shape.value)
        return cv2.cvtColor(yuv, cv2.COLOR_YUV420P2BGR)  # YV12)


class AroundvisionClient:
    """AroundvisionClient is used to simplify the requests and don't spread
    try/except all over the code. When we initialize this class, automatically
    a sessions is created.
    How to use: api_client = AroundvisionClient().
    """
    REQUEST_GET = "get"
    REQUEST_PUT = "put"
    REQUEST_DELETE = "delete"
    REQUEST_POST = "post"

    def __init__(self):
        self.session = requests.Session()
        self.dict_request = {self.REQUEST_GET: self.session.get,
                             self.REQUEST_PUT: self.session.put,
                             self.REQUEST_DELETE: self.session.delete,
                             self.REQUEST_POST: self.session.post}

    def create_request(self, request_type, url, *args):
        """This makes the requests more simplified and return always a dictionary
        with the following args: errors, content, status_code, success.

        :param request_type: "get", "put", "delete", "post"
        :type request_type: str
        :param url: url to make the request
        :type url: str
        :return: {"errors": errors_found, "content": content from response,
                  "status_code": status code, "success": value}
        :rtype: dictionary
        """
        response = {'errors': '', 'content': '', 'status_code': 0}

        try:
            if request_type in self.dict_request:
                r = self.dict_request[request_type](url, stream=True)
                response["content"] = r.content
                response['status_code'] = r.status_code

            logging.info("Request ", extra={
                "Type": request_type,
                "Url": url})

        except requests.exceptions.RequestException as e:
            # all request http exceptions
            response["errors"] = 'Connection Error: ' + str(e)
            logger.warning("Connection error: {0}".format(str(e)))

        except Exception as e:
            # exception api side
            response["errors"] = 'Client Error: ' + str(e)
            logger.warning("Client error: {0}".format(str(e)))

        # we just have success if we have status code with 200 ..
        response['success'] = True if response['status_code'] == 200 else False

        return response
