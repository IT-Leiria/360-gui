
"""

"""


class Model(object):
    """Model values saved"""
    def __init__(self):
        self.selected_projection = ""
        self.selected_quality = ""
        self.selected_cube_face = ""
        self.api_endpoint = ""
        self._roi_activated = False
        self._callbacks = []

    @property
    def roi_activated(self):
        return self._roi_activated

    @roi_activated.setter
    def roi_activated(self, new_value):
        old_value = self._roi_activated
        self._roi_activated = new_value
        self._notify_observers(old_value, new_value)

    def _notify_observers(self, old_value, new_value):
        for callback in self._callbacks:
            callback(old_value, new_value)

    def register_callback(self, callback):
        self._callbacks.append(callback)
