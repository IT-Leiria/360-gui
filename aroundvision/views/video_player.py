import logging
import threading

from PyQt5.QtCore import Qt, QThread, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QWidget

from aroundvision.views.displayer import ImageWidget
from aroundvision.views.qtimer_worker import TimerWorker
from aroundvision.views.region_of_interest import RegionOfInterest

logger = logging.getLogger(__name__)


class VideoPlayer(QWidget):
    """
    VideoPlayer:
        - initialize ImageWidget, TimeWorker and RegionOfInterest
        - this control all video flow
    """
    # Signals
    start_timer = pyqtSignal()
    stop_timer = pyqtSignal()

    def __init__(self, parent=None, model=None, controller=None):
        super().__init__()
        self.model = model
        self.controller = controller
        self.main_displayer = ImageWidget(self, self.model)  # main images displayer
        self.image = None
        self.roi_window = None

        self._create_timer_thread()
        self._set_connects()

        # Register callback when roi_activated value in model is changed..
        # when this value changed we call: display_roi
        self.model.roi_activated.register_callback(self.display_roi)

    def _create_timer_thread(self):
        """Create the timer thread and the capture thread. Those processes are in different threads
           in order to not blocking the main thread.
           - QTimer thread: run QTimer loop every frame_rate and when timeout -> call show_frame (get frame from queue)
           - Capture thread: get frames from api and insert them in queue (controller)
           """
        # Thread to call get frames in controller
        self.capture_thread = None

        # Thread to run QTimer and initialize QTimer
        self.timer_thread = QThread()
        self.timer = TimerWorker(self.model.frame_rate, self.show_frame)
        self.timer.moveToThread(self.timer_thread)
        self.stop_timer.connect(self.timer.stop)
        self.start_timer.connect(self.timer.start)
        self.timer_thread.start()

    def _set_connects(self):
        self.main_displayer.play_toolButton.toggled.connect(self.display_frames)  # connect play/pause button

    @pyqtSlot()
    def resize_image(self):
        """resize image slot used to resize image when window changes.
        """
        # yes, is the image is ok?
        if self.image is not None:
            # yes, let's resize
            # at the moment we resize without "KeepAspectRatio", if we want it please use
            # self.image.scaled(self.main_displayer.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.main_displayer.setImage(self.image.scaled(self.main_displayer.size(),
                                                           Qt.IgnoreAspectRatio, Qt.SmoothTransformation))

    @pyqtSlot()
    def display_frames(self):
        """slot: when user press play, let's display the frames."""
        # play?
        if self.main_displayer.play_toolButton.isChecked():
            # yes, wow let's get the frames and display them.
            logger.info("Display frames.")

            # Start capturing frames
            self.model.capturing.value = True
            self.capture_thread = threading.Thread(name="capturing", target=self.controller.get_frame_from_api)
            self.capture_thread.start()

            # Do we already have images in the queue?
            if self.model.image_queue.empty():
                # No, let's Loading frames ... when timeout is reached, the main displayer
                # will emit the signal (start_timer), then the Start timer will start showing
                # a image from queue every x seconds
                self.main_displayer.set_loading_screen()
            else:
                # yes, we just pause the video let's start again..
                self.start_timer.emit()
        else:
            # no, pause the display..
            logger.info("Pause display 360.")
            self.model.capturing.value = False
            self.stop_timer.emit()

    @pyqtSlot()
    def show_frame(self):
        """Show frame: get image form queue -> if exists, scale and set image in displayer!"""
        try:
            # get image from thread
            img = self.model.image_queue.get(False)
            self.image = QImage(img.data, self.model.width.value, self.model.height.value,
                                self.model.bytes_per_line.value, QImage.Format_RGB888)

            # scale the image to main_displayer size without "KeepAspectRatio"
            self.image = self.image.scaled(self.main_displayer.size(), Qt.IgnoreAspectRatio)
            self.main_displayer.setImage(self.image)

            # is the region of interest activated?
            if self.model.roi_activated.value:
                # yes, let's set roi image
                self.model.roi_image = self.image.copy(self.model.roi_geometry).scaled(
                    self.roi_window.roi_displayer.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
                self.roi_window.roi_displayer.setImage(self.model.roi_image)
        except Exception as e:
            logger.info("Queue empty " + str(e))

    def display_roi(self, roi_activated):
        """Display Region of interest: create roi window and set image from saved in model.."""
        if roi_activated:
            self.roi_window = RegionOfInterest(self.model)
            self.roi_window.roi_displayer.setImage(self.model.roi_image)
            self.roi_window.show()
