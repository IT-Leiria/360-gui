
import queue

from aroundvision.config.config_manager import CONF


class Model(object):
    """Model: this class defines all values shared in all application (like a database)!"""
    def __init__(self):
        # from config values
        self.selected_projection = FieldValue("")
        self.selected_projection_api = FieldValue("")
        self.selected_quality = FieldValue("")
        self.selected_cube_face = FieldValue("")
        self.api_endpoint = FieldValue(CONF.api_endpoint)
        self.frame_rate = FieldValue(CONF.frame_rate)
        # region of interest vars
        self.roi_activated = FieldValue(False)
        self.roi_image = None
        self.roi_geometry = None
        self.selected_roi_bitrate = FieldValue(CONF.roi_bitrate)
        self.selected_roi_quality = FieldValue(CONF.roi_quality)

        # main display: queue and capturing..
        self.image_queue = queue.Queue()
        self.capturing = FieldValue(False)

        # Streams
        self.api_connected = FieldValue(True)
        self.stream_list = FieldValue({})
        self.stream_index = FieldValue(CONF.api_selected_stream_idx)

        # Frame variables
        self.width = FieldValue(None)
        self.height = FieldValue(None)
        self.shape = FieldValue(None)
        self.frame_len = FieldValue(None)
        self.bytes_per_line = FieldValue(None)

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
        - self.teste.register_callback( function ) :: function is\
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
