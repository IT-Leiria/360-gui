
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog

from aroundvision.config.config_manager import CONF


class PopUp(QDialog):
    """This is a generic Popup where the user just have to provide the text message!

    :param text_message: message to be displayed in popup
    :type text_message: str
    """
    def __init__(self, text_message):
        super().__init__()
        # variables
        self.text_message = text_message

        # initialize ui
        uic.loadUi(CONF.popup_filename, self)

        # Assign value to label..
        self.text_label.setText(self.text_message)

        # Connects
        self.confirm_pushButton.clicked.connect(self.confirm_slot)

    @pyqtSlot()
    def confirm_slot(self):
        """Slot to close the popup window!"""
        self.close()
