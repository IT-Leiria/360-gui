
import logging
from ast import literal_eval
import urllib
from socket import timeout

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

        self.get_projection_list()


    def get_frame_from_api(self):
        """While we are capturing values (model.capturing = True) we will
        get frames from API and store them in model.image.queue.
        Here we are using urllib because it has a better performance than requests."""
        while self.model.main_capturing.value:
            logger.info("Get frame from API : " + self.model.api_endpoint.value)

            path = CONF.api_get_frame_raw_path if self.model.selected_cube_face.value == CONF.faces_cube[0] else CONF.api_get_face_raw_path

            # Build request
            request = self.model.api_endpoint.value + path + "?projection=" + \
                                       self.model.selected_projection_api.value

            if self.model.selected_quality.value != -1:
                request = request + "&layer=" + str(self.model.selected_quality.value)

            if self.model.selected_projection_api.value != CONF.faces_cube[0]:
                request = request + "&face=" + str(self.get_cube_face_idx())

            # Get frame
            r = urllib.request.urlopen(request)
            content = r.read()
            size_content = len(content)
            logger.info("Request Status: {}!".format(str(r.status)))

            # Is the content has the expected size?
            if size_content == self.model.main_frame_len.value:
                logger.info("The frame has the expected size, let's insert it in the images queue!")
                self.model.image_queue.put(self.get_rgb_from_yuv(content, self.model.main_shape.value))

    def get_projection_list(self):
        """Get Projections List from API
        """
        request = self.model.api_endpoint.value + CONF.api_get_projection_list_path
        r = self.api_client.create_request("get", request)

        if r["status_code"] == 200:

            projections = literal_eval(r["content"].decode())

            projection_list = []
            for p in projections:
                projection_list.append({'proj_api_name' : p[0], 'proj_name' : p[1]})

            self.model.projections_list.value = projection_list

            logger.info("Get projections list status {0}!".format(r["status_code"]))

    def _get_url_for_roi(self, specific_endpoint):
        """Get the url for region of interest: here we are getting the x,y,width,height
        and assigning those values to the url..

        :param specific_endpoint: for example get_viewport or get_viewport_info
        :type specific_endpoint: str
        """
        # get size of the resized image
        img_size = self.model.main_displayer_size.value

        # get x, y, width, height: as we have the main image resized we have to get the
        # coordinates taking into account the original values (model.width and model.height)
        # just using the rule of three..
        width = int((self.model.roi_geometry.width() * self.model.main_width.value) / img_size.width())
        height = int((self.model.roi_geometry.height() * self.model.main_height.value) / img_size.height())
        x = int((self.model.roi_geometry.center().x() * self.model.main_width.value) / img_size.width())
        y = int((self.model.roi_geometry.center().y() * self.model.main_height.value) / img_size.height())
        layer = self.model.selected_roi_quality.value

        # build the url ..
        url = self.model.api_endpoint.value + specific_endpoint + "?coord=pixel&" + \
               "x=" + str(x) + "&y=" + str(y) + "&width=" + str(width) + "&height=" + str(height)

        if layer != -1:
            url = url + "&layer=" + str(layer)

        return url
    def get_viewport_roi(self, single_run = False):
        """Get viewport region of interest."""
        # get url for get viewport raw
        url = self._get_url_for_roi(CONF.api_get_viewport_raw)

        while self.model.capturing_roi.value or single_run:
            single_run = False
            logger.info("Get viewport region of interest from API : " + self.model.api_endpoint.value)

            # Get viewport
            try:
                r = urllib.request.urlopen(url, timeout=2)
                content = r.read()
                size_content = len(content)
                logger.info("Request Status: {}!".format(str(r.status)))
                # Is the content has the expected size?
                if size_content == self.model.roi_frame_len.value:
                    logger.info("The roi frame has the expected size, let's insert it in the images queue!")
                    self.model.roi_image_queue.put(self.get_rgb_from_yuv(content, self.model.roi_shape.value))
            except timeout as e:
                logger.info("ROI frame request timeout. Stopping capture.")
                self.model.capturing_roi.value = False

    def get_viewport_roi_info(self):
        """Get viewport regiont of interest info"""
        url = self._get_url_for_roi(CONF.api_get_viewport_info)
        logger.info("Getting viewport info in API {0}".format(url))

        # get viewport roi info
        r = self.api_client.create_request("get", url)

        if r["status_code"] == 200:
            # build frame info
            frame_info = literal_eval(r["content"].decode())
            self.model.roi_width.value = frame_info["width"]
            self.model.roi_height.value = frame_info["height"]
            self.model.roi_shape.value = (int(self.model.roi_height.value * 1.5), self.model.roi_width.value)
            self.model.roi_frame_len.value = int(self.model.roi_width.value * self.model.roi_height.value * 3 / 2)
            self.model.roi_bytes_per_line.value = 3 * self.model.roi_width.value
            self.model.roi_bitrate.value = round(frame_info["bitrate"], 2)  # round roi bitrate to 2 decimal points

            logger.info("Get viewport info status {0}!".format(r["status_code"]))

    def select_stream(self):
        """Select Stream index in API"""
        select_stream_path = self.model.api_endpoint.value + CONF.api_select_stream_path + \
            "?idx=" + self.model.stream_index.value
        logger.info("Selecting stream in API {0}".format(select_stream_path))

        r = self.api_client.create_request("get", select_stream_path)
        self.get_frame_info()
        self.get_stream_qualities()

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

            self.model.main_width.value = frame_info["width"]
            self.model.main_height.value = frame_info["height"]
            self.model.main_shape.value = (int(self.model.main_height.value * 1.5), self.model.main_width.value)
            self.model.main_frame_len.value = int(self.model.main_width.value * self.model.main_height.value * 3 / 2)
            self.model.main_bytes_per_line.value = 3 * self.model.main_width.value
            self.model.main_bitrate.value = frame_info["bitrate"]
            logger.info("Get frame info status {0}!".format(r["status_code"]))

    def get_cube_face_idx(self) -> int:
        idx = -1
        for face in CONF.faces_cube:
            if face == self.model.selected_cube_face.value:
                return idx
            idx += 1
        return -1

    def get_projection_face_info(self):
        get_frame_info_path = self.model.api_endpoint.value + "get_projection_face_info" + \
            "?projection=" + self.model.selected_projection_api.value + "&face=" + str(self.get_cube_face_idx()) + "&layer=" + str(self.model.selected_quality.value)
        logger.info("Getting frame info in API {0}".format(get_frame_info_path))

        r = self.api_client.create_request("get", get_frame_info_path)
        if r["status_code"] == 200:
            # build frame info
            frame_info = literal_eval(r["content"].decode())

            self.model.main_width.value = frame_info["width"]
            self.model.main_height.value = frame_info["height"]
            self.model.main_shape.value = (int(self.model.main_height.value * 1.5), self.model.main_width.value)
            self.model.main_frame_len.value = int(self.model.main_width.value * self.model.main_height.value * 3 / 2)
            self.model.main_bytes_per_line.value = 3 * self.model.main_width.value
            self.model.main_bitrate.value = frame_info["bitrate"]

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

    def get_stream_qualities(self):
        """Get Stream Qualities List from API to be displayed in the Quality combobox
        """
        layer_info_path = self.model.api_endpoint.value + CONF.api_get_layer_info + \
            "?idx=" + self.model.stream_index.value
        logger.info("Getting stream qualities in API {0}".format(layer_info_path))
        # get stream list from API
        r = self.api_client.create_request("get", layer_info_path)

        self.model.stream_qualities.value = {}

        # successful request?
        if r['status_code'] == 200:
            # yes, update the values in the model
            qualities = []
            for i, s in enumerate(literal_eval(r["content"].decode())):
                # manipulate content which is formatted like:
                qualities.append(s[1])
            self.model.stream_qualities.value = qualities
        else:
            self.model.selected_quality.value = -1
        logger.info("Get stream qualities status {0}!".format(r["status_code"]))

    @staticmethod
    def get_rgb_from_yuv(raw, shape):
        """Convert YUV420 to RGB array!

        :param raw: bytearray received by API
        :type raw: bytearray
        :param shape: shape (width, height)
        :type shape: tuple
        :return: cv2 array converted from yuv420 to bgr
        :rtype: bgr array
        """
        yuv = np.frombuffer(raw, dtype=np.uint8).reshape(shape)
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
                r = self.dict_request[request_type](url, stream=True, timeout=5)
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
