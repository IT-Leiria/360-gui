
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QResizeEvent
from PyQt5.QtWidgets import QWidget, QToolButton

from aroundvision.config.config_manager import CONF
from aroundvision.views.displayer import ImageWidget
from aroundvision.views.roi_settings import RoiSettings


class RegionOfInterest(QWidget):
    """RegionOfInterest: is the video player for region of interest.

    :param model: application model
    :type model: Model
    """
    def __init__(self, model):
        """Constructor for region of interest."""
        super().__init__()

        # variables
        self.model = model
        self.settings_toolButton = QToolButton()
        self.configuration_tools()
        self.roi_settings_window = None

        # Create image widget to display roi images
        self.roi_displayer = ImageWidget(self, None, self.settings_toolButton)
        self.installEventFilter(self)
        uic.loadUi(CONF.roi_filename, self)

        # Connects
        self.settings_toolButton.clicked.connect(self.open_roi_settings)

        # Add displayer to layout
        self.verticalLayout.addWidget(self.roi_displayer)

    def configuration_tools(self):
        """Configure settings button."""
        icon = QIcon()
        icon.addPixmap(QPixmap(CONF.settings_icon), QIcon.Normal, QIcon.Off)
        self.settings_toolButton.setIcon(icon)

        p_size = self.settings_toolButton.font().pointSize() * 3
        self.settings_toolButton.setIconSize(QSize(p_size, p_size))

        self.settings_toolButton.setStyleSheet("background-color: rgba(122, 122, 122, 0);"
                                               "border: 0px;")

    def resizeEvent(self, event: QResizeEvent) -> None:
        """resizeEvent: used to resize image when window changes.
        """
        # yes, is the image is ok?
        if self.model.roi_image is not None:
            # yes, let's resize, at the moment we resize without "KeepAspectRatio"
            self.model.roi_image = self.model.roi_image.scaled(
                self.roi_displayer.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.roi_displayer.set_image(self.model.roi_image)

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
