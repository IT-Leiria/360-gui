
from PyQt5.QtGui import QPainter, QIcon, QPixmap, QImage, QResizeEvent, QPaintEvent
from PyQt5.QtWidgets import QWidget, QApplication, QRubberBand, QToolButton, QVBoxLayout
from PyQt5.QtCore import QPoint, QRect, QSize, Qt, pyqtSlot

from aroundvision.config.config_manager import CONF
from aroundvision.views.loading_screen import LoadingScreen


class ImageWidget(QWidget):
    """ImageWidget: display images using setImage and paintEvent.
    The configure_tools are used to set play/pause buttons.
    The methods related with mouse are used to Region of Interest..

    :param parent: who calls this
    :type parent: VideoPlayer
    :param model: application model
    :type model: Model (MVC)
    """
    def __init__(self, parent=None, model=None):
        """Constructor for ImageWidget."""
        super(ImageWidget, self).__init__(parent)
        self.parent = parent
        self.image = None
        self.model = model
        self.loading = None  # Loading Screen
        # select area
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()
        self.setLayout(QVBoxLayout())
        self.model.roi_activated.register_callback(self.ended_roi)

        # play/pause
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

    def set_image(self, image: QImage) -> None:
        """Set image and refreshing the event queue.

        :param image: image to be displayer
        :type image: QImage
        """
        self.image = image
        self.update()
        QApplication.processEvents()  # refreshing the event queue

    def paintEvent(self, event: QPaintEvent) -> None:
        """Override paint event to draw image."""
        qp = QPainter()
        qp.begin(self)
        if self.image:
            qp.drawImage(QPoint(0, 0), self.image)
        qp.end()

    def mousePressEvent(self, event) -> None:
        """mousePressEvent used start draw a polygon with the left button (mouse)."""
        if event.button() == Qt.LeftButton:
            if self.model.roi_selection_activated.value:
                self.origin = QPoint(event.pos())
                self.rubber_band.setGeometry(QRect(self.origin, QSize()))
                self.rubber_band.show()

    def mouseMoveEvent(self, event) -> None:
        """mouseMoveEvent: here we already have a starting point of the polygon and we will draw the polygon."""
        if not self.origin.isNull() and self.model.roi_selection_activated.value:
            self.rubber_band.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event) -> None:
        """mouseReleaseEvent: to finalize the polygon.."""
        if event.button() == Qt.LeftButton:
            # Do we have model and image?
            if self.model:
                if self.image and self.model.roi_selection_activated.value:
                    # yes, let's get region of interest geometry and activate region of interest..
                    self.model.roi_geometry = self.rubber_band.geometry()  # x, y, w, h
                    self.model.roi_activated.value = True
        return super(ImageWidget, self).mouseReleaseEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """If we have the loading screen activated and if we resize the main window
        we have to adjust the loading position."""
        if self.loading:
            self.loading.adjust_loading_position(self.geometry())

    def set_loading_screen(self) -> None:
        """Setting the loading screen showing an animation gif."""
        self.loading = LoadingScreen(self, CONF.loading_gif, CONF.loading_gif_time)
        self.loading.close_signal.connect(self.start_displaying)
        self.loading.show()
        # disable play button, the user cannot pause when we are loading..
        self.play_toolButton.setEnabled(False)

    def ended_roi(self, activated: bool) -> None:
        """ROI active value changed."""
        if not activated:
            self.rubber_band.hide()

    @pyqtSlot()
    def start_displaying(self) -> None:
        """This slot will start timer in parent."""
        # play?
        if self.play_toolButton.isChecked():
            # yes, let's start timer worker..
            self.parent.start_timer.emit()
            # enable again the play button..
            self.play_toolButton.setEnabled(True)
