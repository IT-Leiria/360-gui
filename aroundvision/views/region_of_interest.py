
import os

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, QEvent, Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QToolButton

from config.config_manager import CONF
from aroundvision.views.displayer import ImageWidget
from aroundvision.views.roi_settings import RoiSettings


class RegionOfInterest(QWidget):
    """
    RegionOfInterest:
    """
    def __init__(self, model):
        super().__init__()

        # variables
        self.model = model
        self.current_dir = os.path.dirname(__file__)
        self.roi_filename = os.path.join(self.current_dir, CONF.roi_filename)
        self.settings_toolButton = QToolButton()
        self.configure_tools()
        self.roi_settings_window = None

        # Create image widget to display roi images
        self.roi_displayer = ImageWidget(self, None, self.settings_toolButton)
        self.installEventFilter(self)
        uic.loadUi(self.roi_filename, self)

        # Connects
        self.settings_toolButton.clicked.connect(self.open_roi_settings)

        # Add displayer to layout
        self.roi_verticalLayout.addWidget(self.roi_displayer)

    def configure_tools(self):
        """Configure settings button."""
        icon = QIcon()
        icon.addPixmap(QPixmap(CONF.settings_icon), QIcon.Normal, QIcon.Off)
        self.settings_toolButton.setIcon(icon)

        p_size = self.settings_toolButton.font().pointSize() * 3
        self.settings_toolButton.setIconSize(QSize(p_size, p_size))

        self.settings_toolButton.setStyleSheet("background-color: rgba(122, 122, 122, 0);"
                                               "border: 0px;")

    def eventFilter(self, obj, event):
        """evetFilter: used to resize image when window changes.
        TODO: improve this behaviour in further devs
        """
        # resize event?
        if event.type() == QEvent.Resize:
            # yes, is the image is ok?
            if self.model.roi_image is not None:
                # yes, let's resize
                # TODO: check -at the moment we resize without "KeepAspectRatio", if we want it please use
                #  self.image.scaled(self.main_displayer.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.model.roi_image = self.model.roi_image.scaled(self.roi_displayer.size(),
                                                                   Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
                self.roi_displayer.setImage(self.model.roi_image)

        return super().eventFilter(obj, event)

    def closeEvent(self, event) -> None:
        self.model.clean_roi_model()
        super(RegionOfInterest, self).closeEvent(event)

    @pyqtSlot()
    def open_roi_window(self):
        self.exec_()

    @pyqtSlot()
    def open_roi_settings(self):
        """Open roi settings panel.."""
        self.roi_settings_window = RoiSettings(self.model)
        self.roi_settings_window.show()
