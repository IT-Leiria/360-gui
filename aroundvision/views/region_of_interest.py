import threading
import logging

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, Qt, QSize, pyqtSignal, QThread
from PyQt5.QtGui import QResizeEvent, QImage
from PyQt5.QtWidgets import QWidget

from aroundvision.config.config_manager import CONF
from aroundvision.views.displayer import ImageWidget
from aroundvision.views.qtimer_worker import TimerWorker

logger = logging.getLogger(__name__)

class RegionOfInterest(QWidget):
    """RegionOfInterest: is the video player for region of interest.

    :param model: application model
    :type model: Model
    """

    start_timer = pyqtSignal()
    stop_timer = pyqtSignal()

    def __init__(self, model, controller, play):
        """Constructor for region of interest."""
        super().__init__()

        # variables
        self.model = model
        self.controller = controller

        # get the roi info from API
        self.controller.get_viewport_roi_info()

        # Create image widget to display roi images
        self.roi_displayer = ImageWidget(self, self.model)
        self.installEventFilter(self)
        uic.loadUi(CONF.roi_filename, self)

        # initialize timer
        self._create_timer_thread()

        # Connects
        self._set_connects()

        # Add displayer to layout
        self.frame_layout.addWidget(self.roi_displayer)

        self.quality_combobox.addItems(self.model.stream_qualities.value)
        self.bitrate_label.setText("Bitrate: " + str(self.model.roi_bitrate.value))
        self.quality_combobox.setCurrentIndex(len(self.model.stream_qualities.value) - 1)
        self.model.selected_roi_quality.value = self.quality_combobox.currentIndex()

        # start with the same state as the main player
        if play:
            self.roi_displayer.play_toolButton.setChecked(play)
        # else:
        #     self.controller.get_viewport_roi(single_run = True)
        #     while self.model.roi_image_queue.empty():
        #         pass
        #     self.show_roi_frame()

    def _create_timer_thread(self):
        """Creating TimerWorker and timer for ROI frame display"""
        self.roi_timer_thread = QThread()
        self.roi_timer = TimerWorker(self.model.frame_rate.value, self.show_roi_frame)
        self.roi_timer.moveToThread(self.roi_timer_thread)

        self.stop_timer.connect(self.roi_timer.stop)
        self.start_timer.connect(self.roi_timer.start)

        self.roi_timer_thread.start()

    def _set_connects(self):
        """Setting connect for region of interest:
            - play_toolButton -> play_button_slot"""
        self.roi_displayer.play_toolButton.toggled.connect(self.play_button_slot)  # connect play/pause button

    def _start_capturing(self):
        """Starting capture thread for ROI"""
        # create thread roi to capture viewport from api
        self.model.capturing_roi.value = True
        self.capture_thread_roi = threading.Thread(name="capturing_roi", target=self.controller.get_viewport_roi)
        self.capture_thread_roi.start()

    def show_roi_frame(self):
        """Show region of interest frame: get roi image from the roi_image_queue,
        ->if exists, scale and set image in roi_displayer!"""
        try:
            # get roi image from queue
            img = self.model.roi_image_queue.get(False)
            self.model.roi_image = QImage(img.data, self.model.roi_width.value, self.model.roi_height.value,
                                          self.model.roi_bytes_per_line.value, QImage.Format_RGB888)

            # scale the image to main_displayer size with "KeepAspectRatio"
            self.roi_displayer.set_image(self.model.roi_image.scaled(self.roi_displayer.size(),
                                                               Qt.KeepAspectRatio, Qt.SmoothTransformation))

        except Exception as e:
            logger.warning("ROI Queue empty: " + str(e))

    def resizeEvent(self, event: QResizeEvent) -> None:
        """resizeEvent: used to resize image when window changes.
        """
        # yes, is the image is ok?
        if self.model.roi_image is not None:
            # yes, let's resize
            self.roi_displayer.set_image(self.model.roi_image.scaled(
                self.roi_displayer.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))

    def closeEvent(self, event) -> None:
        self.model.clean_roi_model()
        self.stop_timer.emit()
        super(RegionOfInterest, self).closeEvent(event)

    @pyqtSlot()
    def open_roi_window(self):
        self.exec_()

    @pyqtSlot()
    def play_button_slot(self):
        """Slot: when user press play, let's pause or display the frames."""
        # play?
        if self.roi_displayer.play_toolButton.isChecked():

            self._start_capturing()

            # start showing images
            self.start_timer.emit()

        else:
            # no, pause the display..
            self.model.capturing_roi.value = False
            self.stop_timer.emit()
