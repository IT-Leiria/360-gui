
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

    The about_filename and about_logo are defined in configuration file.
    """
    def __init__(self):
        """Constructor method for about!"""
        super().__init__()
        # load ui
        uic.loadUi(CONF.about_filename, self)
        self.setWindowFlags(Qt.CustomizeWindowHint)

        # set logo and link label..
        self.set_logo(CONF.about_logo)
        self.set_link_to_label()

    def set_link_to_label(self) -> None:
        """Setting link to Developed by ...."""
        self.label.linkActivated.connect(self.link)
        self.label.setText(
            self.label.text() +
            '<a href="http://www.criticalsoftware.com/" style="color: #DEDEDE">Critical Software!<a>')

    def set_logo(self, logo_filename: str) -> None:
        """Setting about logo!

        :param logo_filename: logo filename
        :param logo_filename: str"""
        logo_image = QPixmap(logo_filename)
        self.logo_label.setPixmap(logo_image)

    @staticmethod
    def link(link: str) -> None:
        """Uses QDesktop Services to open the url!"""
        QDesktopServices.openUrl(QUrl(link))

    @pyqtSlot()
    def open_about(self):
        """Slot to open the about window!"""
        self.exec_()

    @pyqtSlot()
    def cancel_slot(self):
        """Slot to close the about window!"""
        self.close()
