
"""

"""

from PyQt5.QtGui import QPainter, QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QApplication, QRubberBand, QToolButton, QVBoxLayout
from PyQt5.QtCore import QPoint, QRect, QSize, Qt

from config.config_manager import CONF


class ImageWidget(QWidget):
    """
    ImageWidget: display images using setImage and paintEvent.
    The configure_tools is used to set play/pause buttons.
    The methods related with mouse are prepared to ROI task.
    """
    def __init__(self, parent=None):
        super(ImageWidget, self).__init__(parent)
        self.image = None
        # select area
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()

        # play/pause
        self.setLayout(QVBoxLayout())
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
        self.setMinimumSize(image.size())
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
            self.rubber_band.hide()

        return super(ImageWidget, self).mouseReleaseEvent(event)
