
import os

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QWidget, QFormLayout, QLabel

from config.config_manager import CONF
from aroundvision.views.popup import PopUp


class LoadSource(QWidget):
    """
    LoadSource:
        - panel to set endpoint and stream index..
        - connect with new endpoints
        - display list of stream in server..
    """
    def __init__(self, model, controller):
        super().__init__()

        # variables
        self.model = model
        self.controller = controller
        self.current_dir = os.path.dirname(__file__)
        self.loadsource_filename = os.path.join(self.current_dir, CONF.loadsource_filename)

        # load ui
        uic.loadUi(self.loadsource_filename, self)
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

    def create_stream_list(self):
        """Create stream list, depends from get_stream_list GET values."""
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

    @pyqtSlot()
    def open_load_source(self):
        self.exec_()

    @pyqtSlot()
    def connect_slot(self):
        """try connect and display the returned message (from connection)"""
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
        self.close()

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())
