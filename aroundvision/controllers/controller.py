
"""

"""

import time
import logging
from ast import literal_eval
from config.config_manager import CONF

import requests
from PIL import Image

logger = logging.getLogger(__name__)


class Controller(object):
    """
    Application Controller:
    - our iteraction with api client..
    """
    def __init__(self, model):
        self.model = model

        # Assign values from configurations
        self.model.api_endpoint.value = CONF.api_endpoint
        self.model.stream_index.value = CONF.api_selected_stream_idx

        self.get_stream_list()
        self.select_stream()

    def get_frame_from_api(self):
        start_time = time.time()
        # TODO: improve
        while self.model.capturing.value:
            logger.info("Get frame from API : " + self.model.api_endpoint.value)

            seconds_delay = self.model.frame_delay / 1000.  # convert m seconds to seconds
            time.sleep(seconds_delay - ((time.time() - start_time) % seconds_delay))

            # Get frame
            r = requests.get(self.model.api_endpoint.value + CONF.api_get_frame_raw_path, stream=True)
            logger.info("Request Status: {}!".format(str(r.status_code)))

            # Is the content empty?
            if len(r.content) == 11059200: # > 0
                try:
                    logger.info("The frame isn't empty, let's insert it in the images queue!")
                    print("insert img ", len(r.content))
                    i = Image.frombytes("L", (3840, 1920), r.content, decoder_name="raw")
                    self.model.image_queue.put(i.toqimage())  # .tobytes())  # r.content)

                except Exception as e:
                    self.model.capturing.value = False
                    print("Exception :: ", e)
            else:
                print("Not Image ", r.status_code)

    def select_stream(self):
        """Select Stream index in API"""
        select_stream_path = self.model.api_endpoint.value + CONF.api_select_stream_path + \
            "?idx=" + self.model.stream_index.value
        logger.info("Selecting stream in API {0}".format(select_stream_path))

        try:
            r = requests.get(select_stream_path, stream=True)
            logger.info("Select stream status {0}!".format(r.status_code))
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
            r = requests.get(self.model.api_endpoint.value + CONF.api_get_stream_list_path, stream=True)

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
