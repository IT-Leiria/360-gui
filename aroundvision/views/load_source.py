
import os

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QWidget

from config.config_manager import CONF
from aroundvision.views.popup import PopUp


class LoadSource(QWidget):
    """
    LoadSource: panel to read configurations, at the moment just used
                to set the api endpoint.
    """
    def __init__(self, model):
        super().__init__()

        # variables
        self.model = model
        self.current_dir = os.path.dirname(__file__)
        self.loadsource_filename = os.path.join(self.current_dir, CONF.loadsource_filename)

        uic.loadUi(self.loadsource_filename, self)
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)

        # Assign model value :: api endpoint
        self.api_endpoint_lineEdit.setText(self.model.api_endpoint)

        # Connects
        self.cancel_pushButton.clicked.connect(self.cancel_slot)
        self.save_pushButton.clicked.connect(self.save_sources_slot)

    @pyqtSlot()
    def open_load_source(self):
        self.exec_()

    @pyqtSlot()
    def save_sources_slot(self):
        end_point_current_text = self.api_endpoint_lineEdit.text()
        if end_point_current_text != "" and end_point_current_text != self.model.api_endpoint:
            self.model.api_endpoint = end_point_current_text
            self.close()
        else:
            popup = PopUp("Something wrong with your endpoint: " + end_point_current_text)
            popup.exec_()

    @pyqtSlot()
    def cancel_slot(self):
        self.close()
