
import functools
import logging

from PyQt5.QtGui import QDesktopServices, QImage, QResizeEvent
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
        self.projections = self.model.projections_list.value
        self.load_source_window = None

        # initialize ui's
        self.video_player = VideoPlayer(self.model, self.controller)             # video player
        self._initialize_ui(CONF.mainwindow_filename, CONF.stylesheet_filename)  # initialize main window
        self.fill_bottom_bar(self.model.projections_list.value, CONF.faces_cube)  # fill comboboxes

        # Register callback for projections because we just enable
        # face_cube combobox when the projection is "Cube Map"
        self.model.selected_projection.register_callback(self.face_cube)

        # register callbacks to sync between model and view
        self.model.stream_qualities.register_callback(self.stream_qualities)
        self.model.projections_list.register_callback(self.projections_list)
        self.model.main_capturing.register_callback(self.main_capture)
        self.model.main_bitrate.register_callback(self.bitrate_changed)

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

        self.track_button.hide()

        # Add displayer to layout
        self.frame_verticalLayout.addWidget(self.video_player.main_displayer)

    def _set_connects(self) -> None:
        """Setting connects here"""
        # top bar
        self.actionLoad_Source.triggered.connect(self.open_load_source)
        self.actionHelp.triggered.connect(functools.partial(self.open_help, CONF.docs_url))
        self.actionAbout.triggered.connect(self.open_about)
        # bottom bar
        self.proj_comboBox.currentIndexChanged[str].connect(self.change_projection)
        self.quality_comboBox.activated.connect(self.change_quality)
        self.cube_comboBox.currentIndexChanged[str].connect(self.change_cube_face)
        self.roi_button.clicked.connect(self.roi_button_clicked)

        # For video player resize
        self.resize_img.connect(self.video_player.resize_image)

    def fill_bottom_bar(self, projections: list, faces_cube: list) -> None:
        """Fill bottom bar comboboxes with values defined in config file.
        Comboboxes: Projections, Quality, Faces Cube (just enabled when Cube-Map projection is selected).

        :param projections: list with projections from configuration
        :type projections: list
        :param faces_cube: list with faces cube from configuration
        :type faces_cube: list
        """
        self.proj_comboBox.addItems([proj["proj_name"] for proj in projections])
        self.cube_comboBox.addItems(faces_cube)
        self.quality_comboBox.setEnabled(False)
        self.bitrate_label.setText("Bitrate: -")

        # Assign default values to model
        self.model.selected_projection.value = self.proj_comboBox.currentText()
        self.model.selected_quality.value = -1
        self.model.selected_cube_face.value = self.cube_comboBox.currentText()
        self.model.selected_roi_quality.value = -1

        if projections:
            self.model.selected_projection_api.value = \
                [p["proj_api_name"] for p in projections if p["proj_name"] == self.model.selected_projection.value][0]
        else:
            self.model.selected_projection_api.value = ""
        # check face cube
        self.face_cube(self.model.selected_projection.value)

    def face_cube(self, projection: str) -> None:
        """When projection is "Cube Map" we have to enable the combobox face_cube!

        :param projection: selected projection
        :type projection: str"""
        is_cube = projection == CONF.cube_proj_name["name"]
        self.cube_comboBox.setEnabled(is_cube)
        
    def stream_qualities(self, qualities) -> None:
        """Set quality combobox items
        
        :param qualities: list with qualities to be displayed
        :type qualities: list"""
        # clear existing entries and apend the new
        self.quality_comboBox.clear()
        self.quality_comboBox.addItems(qualities)
        enabled = True if qualities else False
        self.quality_comboBox.setEnabled(enabled)

        if enabled:
            self.quality_comboBox.setCurrentIndex(len(qualities) - 1)
            self.model.selected_quality.value = self.quality_comboBox.currentIndex()
            self.model.selected_roi_quality.value = self.model.selected_quality.value

    def projections_list(self, projections) -> None:
        """Update quality combobox items
        
        :param projections: dict with qualities to be displayed
        :type projections: dict"""
        # update available projections. it won't be used regularly since the projections are only received when starting the application
        self.projections = projections
        self.proj_comboBox.clear()
        self.proj_comboBox.addItems([proj["proj_name"] for proj in projections])

    def main_capture(self, capturing) -> None:
        """Enable or disable projections and quality combo boxes when capturing or not
        
        :param capturing: capturing frames
        :type capturing: bool"""
        # disable projections combobox while capturing
        self.proj_comboBox.setEnabled(not capturing)
        self.quality_comboBox.setEnabled(not capturing)

    def bitrate_changed(self, bitrate) -> None:
        """Update bitrate label
        
        :param bitrate: bitrate of current projection/quality
        :type bitrate: int"""
        self.bitrate_label.setText("Bitrate: " + str(bitrate))

    def resizeEvent(self, event: QResizeEvent) -> None:
        """resizeEvent: emit signal (resize_img) to video_player
         resize the image when window resized. And save the main
         displayer in model"""
        # let's emit a signal to video_player resize the image
        self.resize_img.emit()
        self.model.main_displayer_size.value = self.video_player.main_displayer.size()

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
        # guarantee projection is not empty
        if projection:
            self.model.selected_projection.value = projection
            self.model.selected_projection_api.value = \
                str([p["proj_api_name"] for p in self.projections if p["proj_name"] == projection][0])
            # get_frame_info from API in order to update the frame info
            if self.model.selected_projection_api.value != CONF.cube_proj_name["api_name"]:
                self.model.selected_cube_face.value = ""
                self.controller.get_frame_info()
            else:
                self.model.selected_cube_face.value = self.cube_comboBox.currentText()
                self.controller.get_projection_face_info()
            # clear queue when projection is changed
            with self.model.image_queue.mutex:
                self.model.image_queue.queue.clear()
    
    @pyqtSlot(int)
    def change_quality(self, quality):
        """slot: change quality in model when user change quality in combobox."""
        self.model.selected_quality.value = quality

    @pyqtSlot(str)
    def change_cube_face(self, cube_face):
        """slot: change cube face in model when user change cube face in combobox."""
        self.model.selected_cube_face.value = cube_face
        self.controller.get_projection_face_info()

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

    @pyqtSlot()
    def roi_button_clicked(self):
        """Slot: roi selection clicked"""
        # set or clear displayer tooltip
        tooltip = ""
        if(self.roi_button.isChecked()):
            tooltip = "Select Region of Interest"
        self.video_player.main_displayer.setToolTip(tooltip)
        self.model.roi_selection_activated.value = self.roi_button.isChecked()