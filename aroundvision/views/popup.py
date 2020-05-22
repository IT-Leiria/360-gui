
import os

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog

from aroundvision.config.config_manager import CONF


class PopUp(QDialog):
    """
    PopUp
    """
    def __init__(self, text_message):
        super().__init__()

        # variables
        self.current_dir = os.path.dirname(__file__)
        self.popup_filename = os.path.join(self.current_dir, CONF.popup_filename)
        self.text_message = text_message

        uic.loadUi(self.popup_filename, self)

        # Assign value to label..
        self.text_label.setText(self.text_message)

        # Connects
        self.confirm_pushButton.clicked.connect(self.confirm_slot)

    @pyqtSlot()
    def confirm_slot(self):
        self.close()
