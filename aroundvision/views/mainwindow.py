
import functools
import logging

from PyQt5.QtGui import QDesktopServices, QResizeEvent
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QUrl
from PyQt5 import uic

from aroundvision.views.load_source import LoadSource
from aroundvision.views.about import About
from aroundvision.views.video_player import VideoPlayer
from aroundvision.config.config_manager import CONF

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """AroundVision main window :: it is a subclass of QMainWindow!
    We are starting the ui main window (bottom bar with comboboxes: projections,
    qualities and faces cube; creating the Video Player and add it to the frame
    layout; creating the menu actions: help, about and load source; and creating
    general connects like comboboxes).

    :param model: application model
    :type model: Model (MVC)
    :param controller: application controller
    :type controller: Controller (MVC)"""
    # Signals
    resize_img = pyqtSignal()

    def __init__(self, model=None, controller=None):
        """Constructor method for main window."""
        logger.info("Starting building main window!")
        super().__init__()
        # variables
        self.model = model
        self.controller = controller
        self.projections = CONF.projections
        self.load_source_window = None

        # initialize ui's
        self.video_player = VideoPlayer(self.model, self.controller)             # video player
        self._initialize_ui(CONF.mainwindow_filename, CONF.stylesheet_filename)  # initialize main window
        self.fill_bottom_bar(CONF.projections, CONF.qualities, CONF.faces_cube)  # fill comboboxes

        # Register callback for projections because we just enable
        # face_cube combobox when the projection is "Cube Map"
        self.model.selected_projection.register_callback(self.face_cube)

        self._set_connects()

        logger.info("Main window was built!")

    def _initialize_ui(self, mainwindow_file: str, stylesheet_file: str) -> None:
        """Initialize ui main window: load ui, set stylesheet, fill bottom bars, add video player to layout!"""
        # load ui's and set stylesheet
        uic.loadUi(mainwindow_file, self)
        self.setStyleSheet(self.load_stylesheet(stylesheet_file))

        # main settings
        self.installEventFilter(self)
        self.showMaximized()

        # Add displayer to layout
        self.frame_verticalLayout.addWidget(self.video_player.main_displayer)

    def _set_connects(self) -> None:
        """Setting connects here"""
        # top bar
        self.actionLoad_Source.triggered.connect(self.open_load_source)
        self.actionHelp.triggered.connect(functools.partial(self.open_help, CONF.docs_url))
        self.actionAbout.triggered.connect(self.open_about)
        # bottom bar
        self.proj_comboBox.activated[str].connect(self.change_projection)
        self.quality_comboBox.activated[str].connect(self.change_quality)
        self.cube_comboBox.activated[str].connect(self.change_cube_face)
        # For video player resize
        self.resize_img.connect(self.video_player.resize_image)

    def fill_bottom_bar(self, projections: list, qualities: list, faces_cube: list) -> None:
        """Fill bottom bar comboboxes with values defined in config file.
        Comboboxes: Projections, Quality, Faces Cube (just enabled when Cube-Map projection is selected).

        :param projections: list with projections from configuration
        :type projections: list
        :param qualities: list with qualities from configuration
        :type qualities: list
        :param faces_cube: list with faces cube from configuration
        :type faces_cube: list
        """
        self.proj_comboBox.addItems([proj["proj_name"] for proj in projections])
        self.quality_comboBox.addItems(qualities)
        self.cube_comboBox.addItems(faces_cube)

        # Assign default values to model
        self.model.selected_projection.value = self.proj_comboBox.currentText()
        self.model.selected_quality.value = self.quality_comboBox.currentText()
        self.model.selected_cube_face.value = self.cube_comboBox.currentText()
        self.model.selected_projection_api.value = \
            [p["proj_api_name"] for p in projections if p["proj_name"] == self.model.selected_projection.value][0]
        # check face cube
        self.face_cube(self.model.selected_projection.value)

    def face_cube(self, projection: str) -> None:
        """When projection is "Cube Map" we have to enable the combobox face_cube!

        :param projection: selected projection
        :type projection: str"""
        is_cube = True if projection == "Cube-Map" else False
        self.cube_comboBox.setEnabled(is_cube)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """resizeEvent: emit signal (resize_img) to video_player
         resize the image when window resized."""
        # let's emit a signal to video_player resize the image
        self.resize_img.emit()

    @staticmethod
    def load_stylesheet(stylesheet_filename: str) -> str:
        """Load stylesheet and return a string.

        :param stylesheet_filename: stylesheet filename (.css)
        :param stylesheet_filename: str"""
        with open(stylesheet_filename) as f:
            return f.read()

    @pyqtSlot(str)
    def change_projection(self, projection):
        """slot: change projection in model when user change projection in combobox
         and get_frame_info from API in order to update the frame info."""
        self.model.selected_projection.value = projection
        self.model.selected_projection_api.value = \
            str([p["proj_api_name"] for p in self.projections if p["proj_name"] == projection][0])
        # get_frame_info from API in order to update the frame info
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
        """slot: display the load source window to user set the application settings!"""
        self.load_source_window = LoadSource(self.model, self.controller)
        self.load_source_window.show()

    @pyqtSlot()
    def open_about(self):
        """Slot: display about window!"""
        about_window = About()
        about_window.open_about()

    @pyqtSlot(str)
    def open_help(self, docs_url: str):
        """Open aroundvision docs in browser (Sphinx docs)."""
        if not QDesktopServices.openUrl(QUrl(docs_url)):
            QMessageBox.warning(self, 'Open Url', 'Could not open url!')
