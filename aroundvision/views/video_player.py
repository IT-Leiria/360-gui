
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
    """VideoPlayer control all the video flow. Basically will do:
        - initialize the ImageWidget: where the images are visualized, the play button is\
        created, allows the region of interest..
        - create the capture thread in order to get frames from api (controller)\
        and store them in queue (Play activated)
        - create a qtimer thread in order to every frame_rate (fps) get a frame\
        from the queue and display it in ImageWidget.. (Play activated)
        - create a loading screen with animation gif defined in configuration file,\
        this is displayed during x seconds (loading_gif_time in config..) (Play activated)

    :param model: application model
    :type model: Model (MVC)
    :param controller: application controller
    :type controller: Controller (MVC)
    """
    # Signals
    start_timer = pyqtSignal()
    stop_timer = pyqtSignal()

    def __init__(self, model=None, controller=None):
        """Constructor for Video Player!"""
        super().__init__()
        self.model = model
        self.controller = controller
        self.main_displayer = ImageWidget(self, self.model)  # main images displayer
        self.image = None
        self.roi_window = None
        self.capture_thread = None  # Thread to call get frames in controller
        self.capture_thread_roi = None  # Thread to call get roi viewport in controller

        self._create_timer_thread()
        self._set_connects()

        # Register callback when roi_activated value in model is changed..
        # when this value changed we call: display_roi
        self.model.roi_activated.register_callback(self.display_roi)

    def _create_timer_thread(self):
        """Create the timer thread and the capture thread. Those processes are in different threads
        in order to not blocking the main thread.
            - QTimer thread: run the QTimer loop every frame_rate and when the timeout is reached -> call
            the show_frame method (get frame from queue and display it..)
            - Capture thread: get frames from api and insert them in queue (controller)
        """
        # Thread to run QTimer and initialize QTimer
        self.timer_thread = QThread()
        self.timer = TimerWorker(self.model.frame_rate.value, self.show_frame)
        self.timer.moveToThread(self.timer_thread)

        # connects for timer
        self.stop_timer.connect(self.timer.stop)
        self.start_timer.connect(self.timer.start)

        # let's start timer_thread..
        self.timer_thread.start()

    def _set_connects(self):
        """Setting connect for video player:
            - play_toolButton -> play_button_slot"""
        self.main_displayer.play_toolButton.toggled.connect(self.play_button_slot)  # connect play/pause button

    @pyqtSlot()
    def resize_image(self):
        """Slot: used to resize image when window changes."""
        # yes, Is the image ok?
        if self.image is not None:
            # yes, let's resize
            # at the moment we resize without "KeepAspectRatio", if we want it please use
            # self.image.scaled(self.main_displayer.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.main_displayer.set_image(self.image.scaled(self.main_displayer.size(),
                                                            Qt.IgnoreAspectRatio, Qt.SmoothTransformation))

    @pyqtSlot()
    def play_button_slot(self):
        """Slot: when user press play, let's pause or display the frames."""
        # play?
        if self.main_displayer.play_toolButton.isChecked():
            # yes, wow let's get the frames and display them.
            logger.info("Display frames.")

            # Start capturing frames
            self.model.main_capturing.value = True
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
            self.model.main_capturing.value = False
            self.stop_timer.emit()

    @pyqtSlot()
    def show_frame(self):
        """Slot: Show frame: get image from the queue -> if exists, scale and set image in displayer!"""
        try:
            # get image from queue
            img = self.model.image_queue.get(False)
            self.image = QImage(img.data, self.model.main_width.value, self.model.main_height.value,
                                self.model.main_bytes_per_line.value, QImage.Format_RGB888)

            # scale the image to main_displayer size without "KeepAspectRatio"
            self.image = self.image.scaled(self.main_displayer.size(), Qt.IgnoreAspectRatio)
            self.main_displayer.set_image(self.image)

            # is the region of interest activated?
            if self.model.roi_activated.value:
                # yes, let's set roi image
                self.show_roi_frame()
        except Exception as e:
            logger.info("Queue empty " + str(e))

    def show_roi_frame(self):
        """Show region of interest frame: get roi image from the roi_image_queue,
        ->if exists, scale and set image in roi_displayer!"""
        try:
            # get roi image from queue
            img = self.model.roi_image_queue.get(False)
            self.model.roi_image = QImage(img.data, self.model.roi_width.value, self.model.roi_height.value,
                                          self.model.roi_bytes_per_line.value, QImage.Format_RGB888)

            # scale the image to main_displayer size with "KeepAspectRatio"
            self.model.roi_image = self.model.roi_image.scaled(self.roi_window.roi_displayer.size(),
                                                               Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.roi_window.roi_displayer.set_image(self.model.roi_image)
            # resize roi window accordingly with roi_image size
            self.roi_window.resize(self.model.roi_image.size())

        except Exception as e:
            logger.warning("ROI Queue empty: " + str(e))

    def display_roi(self, roi_activated):
        """Display Region of interest: create roi window and set image from saved in model.."""
        # Do we already have a ROI window?
        if not self.roi_window and roi_activated:
            # clearing queue using thread safe, we are clearing queue because
            # we can have a new region of interest, than we need to save and
            # display images with new area..
            with self.model.roi_image_queue.mutex:
                self.model.roi_image_queue.queue.clear()

            # no, let's create one..
            # Get viewport info
            self.controller.get_viewport_roi_info()

            # create thread roi to capture viewport from api
            self.model.capturing_roi.value = True
            self.capture_thread_roi = threading.Thread(name="capturing_roi", target=self.controller.get_viewport_roi)
            self.capture_thread_roi.start()

            # create region of intereste..
            self.roi_window = RegionOfInterest(self.model)
            self.roi_window.show()
            self.show_roi_frame()

        # Is the roi window was deactivated?
        if not roi_activated:
            # yes, let's set a roi window as none..
            self.roi_window = None
