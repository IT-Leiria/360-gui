
"""

"""


class Model(object):
    """Model values saved"""
    def __init__(self):
        self.selected_projection = ""
        self.selected_quality = ""
        self.selected_cube_face = ""
        self.api_endpoint = ""
        # region of interest vars
        self._roi_activated = False
        self._callbacks = []
        self.roi_image = None
        self.roi_geometry = None
        # region of interest settings
        self.selected_roi_bitrate = ""
        self.selected_roi_quality = ""

    def clean_roi_model(self):
        self._roi_activated = False
        self.roi_image = None
        self.roi_geometry = None

    @property
    def roi_activated(self):
        return self._roi_activated

    @roi_activated.setter
    def roi_activated(self, new_value):
        self._roi_activated = new_value
        self._notify_observers(new_value)

    def _notify_observers(self, new_value):
        for callback in self._callbacks:
            callback(new_value)

    def register_callback(self, callback):
        self._callbacks.append(callback)
