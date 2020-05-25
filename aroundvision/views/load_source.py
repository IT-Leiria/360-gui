
import logging

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QWidget, QFormLayout, QLabel

from aroundvision.config.config_manager import CONF
from aroundvision.views.popup import PopUp

logger = logging.getLogger(__name__)


class LoadSource(QWidget):
    """LoadSource: it's like the main settings, the user has:
        - a panel to insert the endpoint and the stream index..
        - button to connect to the API with the inserted values
        - a layout to display a list of streams as the response from connect..
    Than, this module needs the model to get and save the endpoints and selected streams
    and, the controller to interact with the API.

    Example:
        - API Endpoint: http://0.0.0.0:5000/
        - Stream Index: 0
        - Stream List (accordingly with API response):
            - Stream Index: 0
            - Name: /datasets/Video.yuv
            - Size: 3840 x 1920
            - Bytes per pixel: 1
            - Number of layers: 1
    """
    def __init__(self, model, controller):
        """Constructor for load source window!"""
        super().__init__()
        logger.info("Creating load source window!")
        # variables
        self.model = model
        self.controller = controller

        # load ui
        uic.loadUi(CONF.loadsource_filename, self)
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)

        # Assign model values to ui :: api endpoint and stream index
        self.api_endpoint_lineEdit.setText(self.model.api_endpoint.value)
        self.stream_index_lineEdit.setText(self.model.stream_index.value)

        # Connects
        self.cancel_pushButton.clicked.connect(self.cancel_slot)
        self.save_pushButton.clicked.connect(self.save_sources_slot)
        self.connect_pushButton.clicked.connect(self.connect_slot)

        # Create stream list
        self.create_stream_list()

    def create_stream_list(self) -> None:
        """Create the stream list, depends from get_stream_list GET values."""
        # clear stream list layout in order to add or remove items (more easy)..
        self.clear_layout(self.stream_list_layout)

        self.stream_list_layout.addWidget(QLabel("Stream List:"))

        # if we have stream list with values, add them to the layout..
        for i, s in enumerate(self.model.stream_list.value):
            # Create Widget and formLayout
            wid = QWidget()
            wid.setStyleSheet("background-color: #222222;")
            form = QFormLayout()

            # add Row for values: index, name, size, bytes per pixel, number of layers
            stream = self.model.stream_list.value[s]
            form.addRow(QLabel("Stream Index: "), QLabel(str(i)))
            form.addRow(QLabel("Name: "), QLabel(stream["name"]))
            form.addRow(QLabel("Size: "), QLabel(str(stream["width"]) + " x " + str(stream["height"])))
            form.addRow(QLabel("Bytes per Pixel: "), QLabel(str(stream["bytes_per_pixel"])))
            form.addRow(QLabel("Number of layers: "), QLabel(str(stream["number_of_layers"])))

            # add to layout
            wid.setLayout(form)
            self.stream_list_layout.addWidget(wid)

            logger.info("Adding the following stream {0}".format(stream))

    @pyqtSlot()
    def connect_slot(self):
        """Slot: try to connect and display the returned message (from connection)"""
        # get api endpoint from lineedit..
        self.model.api_endpoint.value = self.api_endpoint_lineEdit.text()

        # let's connect and display popup with message
        connect_msg = self.controller.get_stream_list()
        popup = PopUp(connect_msg)
        popup.exec_()

        # update our stream list
        self.create_stream_list()

    @pyqtSlot()
    def save_sources_slot(self):
        """Slot for save button. Save inserted data in model and select_stream in API!"""
        end_point_current_text = self.api_endpoint_lineEdit.text()
        if not self.model.api_connected.value or end_point_current_text != self.model.api_endpoint.value:
            popup = PopUp("You are not connected with your endpoint: " + end_point_current_text)
            popup.exec_()
        else:
            self.model.api_endpoint.value = end_point_current_text
            self.controller.select_stream()
            self.close()

    @pyqtSlot()
    def cancel_slot(self):
        """Slot to close open source window!"""
        self.close()

    def clear_layout(self, layout) -> None:
        """Remove all content from the received layout."""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())
