
"""

"""

import os
import logging

from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import pyqtSlot, QEvent, pyqtSignal, QUrl
from PyQt5 import uic

from aroundvision.views.load_source import LoadSource
from aroundvision.views.about import About
from aroundvision.views.video_player import VideoPlayer
from aroundvision.config.config_manager import CONF

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """AroundVision main window :: improve description"""
    # Signals
    resize_img = pyqtSignal()

    def __init__(self, model, controller):
        logger.info("Starting building main window!")
        super().__init__()

        # variables
        self.model = model
        self.controller = controller
        self.current_dir = os.path.dirname(__file__)
        self.mainwindow_filename = os.path.join(self.current_dir, CONF.mainwindow_filename)
        self.stylesheet_filename = os.path.join(self.current_dir, CONF.stylesheet_filename)

        self.installEventFilter(self)

        # load ui's
        uic.loadUi(self.mainwindow_filename, self)
        self.setStyleSheet(self.load_stylesheet())
        self.showMaximized()

        # Register callback for projections because we just enable
        # face_cube combobox when the projection is "Cube Map"
        self.model.selected_projection.register_callback(self.face_cube)

        # Configurations
        self.fill_bottom_bar()
        self.model.selected_roi_bitrate = CONF.roi_bitrate
        self.model.selected_roi_quality = CONF.roi_quality
        self.model.frame_rate = CONF.frame_rate

        # Add displayer to layout
        self.video_player = VideoPlayer(self, self.model, self.controller)
        self.frame_verticalLayout.addWidget(self.video_player.main_displayer)

        self._set_connects()

        logger.info("Main window was built!")

    def _set_connects(self):
        """Set connects here"""
        # top bar
        self.actionLoad_Source.triggered.connect(self.open_load_source)
        self.actionHelp.triggered.connect(self.open_help)
        self.actionAbout.triggered.connect(self.open_about)
        # bottom bar
        self.proj_comboBox.activated[str].connect(self.change_projection)
        self.quality_comboBox.activated[str].connect(self.change_quality)
        self.cube_comboBox.activated[str].connect(self.change_cube_face)
        # For video player resize
        self.resize_img.connect(self.video_player.resize_image)

    def fill_bottom_bar(self):
        """Fill bottom bar comboboxes with values defined in config file.
        Comboboxes: Projections, Quality, Faces Cube.
        """
        self.proj_comboBox.addItems([proj["proj_name"] for proj in CONF.projections])
        self.quality_comboBox.addItems(CONF.qualities)
        self.cube_comboBox.addItems(CONF.faces_cube)

        # Assign default values to model
        self.model.selected_projection.value = self.proj_comboBox.currentText()
        self.model.selected_quality.value = self.quality_comboBox.currentText()
        self.model.selected_cube_face.value = self.cube_comboBox.currentText()
        self.model.selected_projection_api.value = \
            [p["proj_api_name"] for p in CONF.projections if p["proj_name"] == self.model.selected_projection.value][0]

    def eventFilter(self, obj, event):
        """evetFilter: used to resize image when window changes.
        """
        # resize event?
        if event.type() == QEvent.Resize:
            # yes, let's emit a signal to video_player resize the image
            self.resize_img.emit()

        return super().eventFilter(obj, event)

    def load_stylesheet(self):
        """Load stylesheet and return a string"""
        with open(self.stylesheet_filename) as f:
            return f.read()

    @pyqtSlot(str)
    def change_projection(self, projection):
        """slot: change projection in model when user change projection in combobox."""
        self.model.selected_projection.value = projection
        self.model.selected_projection_api.value = \
            str([p["proj_api_name"] for p in CONF.projections if p["proj_name"] == projection][0])
        self.controller.get_frame_info()

    @pyqtSlot(str)
    def change_quality(self, quality):
        """slot: change quality in model when user change quality in combobox."""
        self.model.selected_quality.value = quality

    @pyqtSlot(str)
    def change_cube_face(self, cube_face):
        """slot: change cube face in model when user change cube face in combobox."""
        self.model.selected_cube_face.value = cube_face

    @pyqtSlot()
    def open_load_source(self):
        """slot: display the load source window to set api endpoint.."""
        self.load_source_window = LoadSource(self.model, self.controller)
        self.load_source_window.show()

    @pyqtSlot()
    def open_about(self):
        """Slot: display about window!"""
        self.about_window = About()
        self.about_window.show()

    @pyqtSlot()
    def open_help(self):
        """Open aroundvision docs in browser."""
        if not QDesktopServices.openUrl(QUrl(CONF.docs_url)):
            QMessageBox.warning(self, 'Open Url', 'Could not open url!')

    def face_cube(self, projection):
        """when projection is "Cube Map" we enable the combobox face_cube!"""
        is_cube = True if projection == "Cube-Map" else False
        self.cube_comboBox.setEnabled(is_cube)
