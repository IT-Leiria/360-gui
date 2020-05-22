
"""

"""

import cv2
import numpy as np

from PyQt5.QtGui import QPainter, QIcon, QPixmap, QImage
from PyQt5.QtWidgets import QWidget, QApplication, QRubberBand, QToolButton, QVBoxLayout
from PyQt5.QtCore import QPoint, QRect, QSize, Qt

from aroundvision.config.config_manager import CONF


class ImageWidget(QWidget):
    """
    ImageWidget: display images using setImage and paintEvent.
    The configure_tools is used to set play/pause buttons.
    The methods related with mouse are prepared to ROI task.
    """
    def __init__(self, parent=None, model=None, settings=None):
        super(ImageWidget, self).__init__(parent)
        self.image = None
        self.model = model
        self.settings = settings
        # select area
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()
        self.setLayout(QVBoxLayout())

        # is settings?
        if self.settings:
            self.layout().addWidget(self.settings, 0, Qt.AlignTop | Qt.AlignLeft)

        # play/pause
        if self.model:
            self.play_toolButton = QToolButton(self)
            self.layout().addWidget(self.play_toolButton, 1, Qt.AlignBottom | Qt.AlignHCenter)
            self.configure_tools()

    def configure_tools(self):
        """Configure display tools: play and pause buttons."""
        icon = QIcon()
        icon.addPixmap(QPixmap(CONF.play_icon), QIcon.Normal, QIcon.Off)
        icon.addPixmap(QPixmap(CONF.pause_icon), QIcon.Normal, QIcon.On)
        self.play_toolButton.setIcon(icon)
        self.play_toolButton.setCheckable(True)

        p_size = self.play_toolButton.font().pointSize() * 4
        self.play_toolButton.setIconSize(QSize(p_size, p_size))

        self.play_toolButton.setStyleSheet("background-color: rgba(122, 122, 122, 0);"
                                           "border: 0px;")

    def setImage(self, image):
        self.image = image
        self.update()
        QApplication.processEvents()  # refreshing the event queue

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        if self.image:
            qp.drawImage(QPoint(0, 0), self.image)
        qp.end()

    # TODO: the following methods used to draw the region of interest
    #       in that task start from here..
    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.origin = QPoint(event.pos())
            self.rubber_band.setGeometry(QRect(self.origin, QSize()))
            self.rubber_band.show()

    def mouseMoveEvent(self, event) -> None:
        if not self.origin.isNull():
            self.rubber_band.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            # TODO: this must be improved, this is just an example..
            if self.model and self.image:
                img_crop = self.image.copy(self.rubber_band.geometry())
                self.model.roi_image = img_crop
                self.model.roi_geometry = self.rubber_band.geometry()
                self.model.roi_activated.value = True
                # cv2.imshow("ROI", self.convert_qimage_to_mat(img_crop))

        return super(ImageWidget, self).mouseReleaseEvent(event)

    # this was used in imshow with opencv example ..
    #@staticmethod
    #def convert_qimage_to_mat(in_image):
    #    """Converts a QImage into an opencv MAT format"""
    #    img = in_image.convertToFormat(QImage.Format_RGB32)
    #    ptr = img.bits()
    #    ptr.setsize(img.byteCount())
    #    return np.array(ptr).reshape(img.height(), img.width(), QImage.Format_RGB32)  # Copies the data
