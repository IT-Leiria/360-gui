
"""

"""

import os
import logging
import threading

from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QMainWindow, QAction
from PyQt5.QtCore import pyqtSlot, Qt, QEvent, QThread, pyqtSignal
from PyQt5 import uic

from aroundvision.views.load_source import LoadSource
from aroundvision.views.region_of_interest import RegionOfInterest
from aroundvision.views.displayer import ImageWidget
from aroundvision.views import qtimer_worker
from config.config_manager import CONF

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """AroundVision main window :: improve description"""
    # Signals
    start_timer = pyqtSignal()
    stop_timer = pyqtSignal()

    def __init__(self, model, controller):
        logger.info("Starting building main window!")
        super().__init__()

        # variables
        self.model = model
        self.controller = controller
        self.current_dir = os.path.dirname(__file__)
        self.mainwindow_filename = os.path.join(self.current_dir, CONF.mainwindow_filename)
        self.stylesheet_filename = os.path.join(self.current_dir, CONF.stylesheet_filename)
        self.main_displayer = ImageWidget(self, self.model)  # main images displayer
        self.image = None
        self.roi_window = None
        self.load_source_window = None
        self.installEventFilter(self)

        # load ui's
        uic.loadUi(self.mainwindow_filename, self)
        self.setStyleSheet(self.load_stylesheet())

        # Register callback when roi_activated value in model is changed..
        # when this value changed we call: display_roi
        self.model.roi_activated.register_callback(self.display_roi)

        # Register callback for projections because we just enable
        # face_cube combobox when the projection is "Cube Map"
        self.model.selected_projection.register_callback(self.face_cube)

        # Configurations
        self.fill_bottom_bar()
        self.model.selected_roi_bitrate = CONF.roi_bitrate
        self.model.selected_roi_quality = CONF.roi_quality
        self.model.frame_rate = CONF.frame_rate

        # Add displayer to layout
        self.frame_verticalLayout.addWidget(self.main_displayer)

        # Connects
        self.menuLoad_Source.triggered[QAction].connect(self.open_load_source)
        self.main_displayer.play_toolButton.toggled.connect(self.display_frames)  # connect play/pause button
        self.proj_comboBox.activated[str].connect(self.change_projection)
        self.quality_comboBox.activated[str].connect(self.change_quality)
        self.cube_comboBox.activated[str].connect(self.change_cube_face)

        # thread and timer to display images
        self.capture_thread = None
        self.timer_thread = QThread()
        self.timer = qtimer_worker.TimerWorker(self.model.frame_rate, self.show_frame)
        self.timer.moveToThread(self.timer_thread)
        self.stop_timer.connect(self.timer.stop)
        self.start_timer.connect(self.timer.start)
        self.timer_thread.start()

        logger.info("Main window was built!")

    def fill_bottom_bar(self):
        """Fill bottom bar comboboxes with values defined in config file.
        Comboboxes: Projections, Quality, Faces Cube.
        """
        self.proj_comboBox.addItems(CONF.projections)
        self.quality_comboBox.addItems(CONF.qualities)
        self.cube_comboBox.addItems(CONF.faces_cube)

        # Assign default values to model
        self.model.selected_projection.value = self.proj_comboBox.currentText()
        self.model.selected_quality.value = self.quality_comboBox.currentText()
        self.model.selected_cube_face.value = self.cube_comboBox.currentText()

    def eventFilter(self, obj, event):
        """evetFilter: used to resize image when window changes.
        """
        # resize event?
        if event.type() == QEvent.Resize:
            # yes, is the image is ok?
            if self.image is not None:
                # yes, let's resize
                # at the moment we resize without "KeepAspectRatio", if we want it please use
                # self.image.scaled(self.main_displayer.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.main_displayer.setImage(self.image.scaled(self.main_displayer.size(),
                                                               Qt.IgnoreAspectRatio, Qt.SmoothTransformation))

        return super().eventFilter(obj, event)

    def load_stylesheet(self):
        """Load stylesheet and return a string"""
        with open(self.stylesheet_filename) as f:
            return f.read()

    @pyqtSlot(str)
    def change_projection(self, projection):
        """slot: change projection in model when user change projection in combobox."""
        self.model.selected_projection.value = projection

    @pyqtSlot(str)
    def change_quality(self, quality):
        """slot: change quality in model when user change quality in combobox."""
        self.model.selected_quality.value = quality

    @pyqtSlot(str)
    def change_cube_face(self, cube_face):
        """slot: change cube face in model when user change cube face in combobox."""
        self.model.selected_cube_face.value = cube_face

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

            # Start timer to show image from queue every x seconds
            self.start_timer.emit()
        else:
            # no, pause the display..
            logger.info("Pause display 360.")
            self.model.capturing.value = False
            self.stop_timer.emit()

    @pyqtSlot()
    def show_frame(self):
        # get image from thread
        try:
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

    @pyqtSlot()
    def open_load_source(self):
        """slot: display the load source window to set api endpoint.."""
        self.load_source_window = LoadSource(self.model, self.controller)
        self.load_source_window.show()

    def display_roi(self, roi_activated):
        """Display Region of interest: create roi window and set image from saved in model.."""
        if roi_activated:
            self.roi_window = RegionOfInterest(self.model)
            self.roi_window.roi_displayer.setImage(self.model.roi_image)
            self.roi_window.show()

    def face_cube(self, projection):
        """when projection is "Cube Map" we enable the combobox face_cube!"""
        is_cube = True if projection == "Cube Map" else False
        self.cube_comboBox.setEnabled(is_cube)
