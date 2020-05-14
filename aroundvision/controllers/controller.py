
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
    def __init__(self, model, frames=None, frame=None):
        self.model = model
        self.frames = frames
        self.frame = frame

        self.get_stream_list()
        r = requests.get(CONF.api_select_stream_path + "?idx=" + CONF.api_selected_stream_idx, stream=True)

    def get_frame_from_api(self):
        start_time = time.time()
        # TODO: improve
        while self.model.capturing.value:
            logger.info("Get frame from API : " + self.model.api_endpoint)

            seconds_delay = self.model.frame_delay / 1000.  # convert m seconds to seconds
            time.sleep(seconds_delay - ((time.time() - start_time) % seconds_delay))

            # Get frame
            r = requests.get(CONF.api_get_frame_raw_path, stream=True)
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

    def get_stream_list(self):
        # get stream list from API
        r = requests.get(CONF.api_get_stream_list_path, stream=True)

        # update our model with values
        for i, s in enumerate(literal_eval(r.content.decode())):
            self.model.stream_list.value["stream" + str(i)] = {"name": s[0], "width": s[1], "height": s[2],
                                                               "bytes_per_pixel": s[3], "number_of_layers": s[4]}
            self.model.stream_list.value["stream1"] = {"name": "TESTE", "width": s[1], "height": s[2],
                                                       "bytes_per_pixel": s[3], "number_of_layers": s[4]}
