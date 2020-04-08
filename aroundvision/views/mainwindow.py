
"""

"""

import os
import logging
import queue

import cv2
from PyQt5.QtWidgets import QMainWindow, QAction
from PyQt5.QtCore import pyqtSlot, Qt, QEvent
from PyQt5 import uic
from PyQt5.QtGui import QImage

from aroundvision.controllers.controller import Controller
from aroundvision.models.models import Model
from aroundvision.views.load_source import LoadSource
from aroundvision.views.displayer import ImageWidget
from config.config_manager import CONF

logger = logging.getLogger(__name__)
image_queue = queue.Queue()     # Queue to hold images


class MainWindow(QMainWindow):
    """AroundVision main window :: improve description"""

    # Signals

    def __init__(self):
        logger.info("Starting building main window!")
        super().__init__()

        # variables
        self.current_dir = os.path.dirname(__file__)
        self.mainwindow_filename = os.path.join(self.current_dir, CONF.mainwindow_filename)
        self.stylesheet_filename = os.path.join(self.current_dir, CONF.stylesheet_filename)
        self.main_displayer = ImageWidget(self)  # main images displayer
        self.image = None
        self.installEventFilter(self)

        # load ui's
        uic.loadUi(self.mainwindow_filename, self)
        self.setStyleSheet(self.load_stylesheet())

        # Configurations
        self.fill_bottom_bar()
        Model.api_endpoint = CONF.api_endpoint

        # Add displayer to layout
        self.frame_verticalLayout.addWidget(self.main_displayer)

        # Connects
        self.menuLoad_Source.triggered[QAction].connect(self.open_load_source)
        self.main_displayer.play_toolButton.toggled.connect(self.display_frames)  # connect play/pause button
        self.proj_comboBox.activated[str].connect(self.change_projection)
        self.quality_comboBox.activated[str].connect(self.change_quality)
        self.cube_comboBox.activated[str].connect(self.change_cube_face)

        logger.info("Main window was built!")

    def fill_bottom_bar(self):
        """Fill bottom bar comboboxes with values defined in config file.
        Comboboxes: Projections, Quality, Faces Cube.
        """
        self.proj_comboBox.addItems(CONF.projections)
        self.quality_comboBox.addItems(CONF.qualities)
        self.cube_comboBox.addItems(CONF.faces_cube)

        # Assign default values to model
        Model.selected_projection = self.proj_comboBox.currentText()
        Model.selected_quality = self.quality_comboBox.currentText()
        Model.selected_cube_face = self.cube_comboBox.currentText()

    def eventFilter(self, obj, event):
        """evetFilter: used to resize image when window changes.
        TODO: improve this behaviour in further devs
        """
        # resize event?
        if event.type() == QEvent.Resize:
            # yes, is the image is ok?
            if self.image is not None:
                # yes, let's resize
                # TODO: check -at the moment we resize without "KeepAspectRatio", if we want it please use
                #  self.image.scaled(self.main_displayer.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
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
        Model.selected_projection = projection

    @pyqtSlot(str)
    def change_quality(self, quality):
        """slot: change quality in model when user change quality in combobox."""
        Model.selected_quality = quality

    @pyqtSlot(str)
    def change_cube_face(self, cube_face):
        """slot: change cube face in model when user change cube face in combobox."""
        Model.selected_cube_face = cube_face

    @pyqtSlot()
    def display_frames(self):
        """slot: when user press play, let's display the frames."""
        # play?
        if self.main_displayer.play_toolButton.isChecked():
            # yes, wow let's get the frames and display them.
            logger.info("Display frames.")
            for image_file in Controller.get_frames():
                self.image = cv2.imread(image_file)
                self.image = QImage(self.image.data, self.image.shape[1], self.image.shape[0],
                                    QImage.Format_RGB888).rgbSwapped()

                # TODO: check - at the moment we scaled the image to main_displayer size without
                #  "KeepAspectRatio", than if you want it please use the following:
                #  self.image.scaled(self.main_displayer.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.main_displayer.setImage(self.image.scaled(self.main_displayer.size(),
                                                               Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        else:
            # no, pause the display..
            logger.info("Pause display 360.")

    @pyqtSlot()
    def open_load_source(self):
        """slot: display the load source window to set api endpoint.."""
        self.load_source_window = LoadSource()
        self.load_source_window.show()
