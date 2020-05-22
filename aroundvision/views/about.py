
import os

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, Qt, QUrl
from PyQt5.QtGui import QPixmap, QDesktopServices
from PyQt5.QtWidgets import QDialog

from aroundvision.config.config_manager import CONF


class About(QDialog):
    """
    A class used to build the About QDialog.

    This loads the ui file "about.ui" (this has a label with
    project description and a label to display the logo image).
    Then, we call set_link_to_label() to create a link to
    company website and, we call the set_logo() to display the logo image.

    Methods
    -------
    set_link_to_label()
        Setting link to Developed by ....
    set_logo()
        Setting logo from configuration
    """
    def __init__(self):
        super().__init__()

        self.current_dir = os.path.dirname(__file__)
        self.about_filename = os.path.join(self.current_dir, CONF.about_filename)

        # load ui
        uic.loadUi(self.about_filename, self)
        self.setWindowFlags(Qt.CustomizeWindowHint)

        # set logo and link label..
        self.set_logo()
        self.set_link_to_label()

    def set_link_to_label(self):
        """Setting link to Developed by ...."""
        self.label.linkActivated.connect(self.link)
        self.label.setText(
            self.label.text() +
            '<a href="http://www.criticalsoftware.com/" style="color: #DEDEDE">Critical Software!<a>')

    def set_logo(self):
        """Setting about logo!"""
        logo_image = QPixmap(CONF.about_logo)
        self.logo_label.setPixmap(logo_image)

    def link(self, link: str):
        QDesktopServices.openUrl(QUrl(link))

    @pyqtSlot()
    def open_about(self):
        self.exec_()

    @pyqtSlot()
    def cancel_slot(self):
        self.close()
