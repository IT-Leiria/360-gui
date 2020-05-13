
"""

"""

import queue

class Model(object):
    """Model values saved"""
    def __init__(self):
        self.selected_projection = FieldValue("")
        self.selected_quality = FieldValue("")
        self.selected_cube_face = FieldValue("")
        self.api_endpoint = FieldValue("")
        self.frame_delay = FieldValue(1000)
        # region of interest vars
        self.roi_activated = FieldValue(False)
        self.roi_image = None
        self.roi_geometry = None

        # main display: queue and capturing..
        self.image_queue = queue.Queue()
        self.capturing = FieldValue(False)

    def clean_roi_model(self):
        self.roi_activated.value = False
        self.roi_image = None
        self.roi_geometry = None


class FieldValue:
    """
    Model variables must be FieldValue() because this object
    is already prepared to user register callbacks (observers)
    for this field.

    Example:
    - self.teste = field_value("TESTE") # initial value
    - self.teste.value # access variable and assign a new value
    - self.teste.register_callback( function ) :: function is
      called when the variable (teste) is modified..
    """
    def __init__(self, initial_value):
        self._value = initial_value
        self._callbacks = []

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value
        self._notify_observers(new_value)

    def _notify_observers(self, new_value):
        for callback in self._callbacks:
            callback(new_value)

    def register_callback(self, callback):
        self._callbacks.append(callback)
