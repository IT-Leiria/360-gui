
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QDialog

from aroundvision.config.config_manager import CONF


class About(QDialog):
    """
    A class used to build the About QDialog.

    This loads the ui file "about.ui".
    """
    def __init__(self):
        """Constructor method for about!"""
        super().__init__()
        # load ui
        uic.loadUi(CONF.about_filename, self)
        self.setWindowFlags(Qt.CustomizeWindowHint)

    @pyqtSlot()
    def open_about(self):
        """Slot to open the about window!"""
        self.exec_()

    @pyqtSlot()
    def cancel_slot(self):
        """Slot to close the about window!"""
        self.close()
