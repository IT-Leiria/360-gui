
"""

"""

import time
import logging

import requests

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

    def get_frame_from_api(self):
        start_time = time.time()

        while self.model.capturing.value:
            logger.info("Get frame from API : " + self.model.api_endpoint)

            seconds_delay = self.model.frame_delay / 1000.  # convert m seconds to seconds
            time.sleep(seconds_delay - ((time.time() - start_time) % seconds_delay))

            # Get frame
            r = requests.get(self.model.api_endpoint, stream=True)
            logger.info("Request Status: {}!".format(str(r.status_code)))

            # Is the content empty?
            if len(r.content) > 0:
                logger.info("The frame isn't empty, let's insert it in the images queue!")
                self.model.image_queue.put(r.content)

