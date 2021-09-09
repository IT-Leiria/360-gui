
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QWidget

from aroundvision.config.config_manager import CONF
from aroundvision.views.popup import PopUp


class RoiSettings(QWidget):
    """RoiSettings: settings panel with bitrate and quality.

    :param model: Model
    :type model: Model
    """
    def __init__(self, model):
        """Constructor for region of interest settings."""
        super().__init__()

        # variables
        self.model = model

        uic.loadUi(CONF.roi_settings_filename, self)
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        self.fill_ui()

        # Connects
        self.cancel_pushButton.clicked.connect(self.cancel_slot)
        self.save_pushButton.clicked.connect(self.save_values_slot)
        self.quality_comboBox.activated[str].connect(self.change_roi_quality)

        self.model.stream_qualities.register_callback(self.stream_qualities)

    def fill_ui(self):
        """Fill ui with model values.
        bitrate and quality.
        """
        # bitrate
        #self.bitrate_lineEdit.setText(self.model.selected_roi_bitrate.value)
        #self.bitrate_units_label.setText(CONF.roi_bitrate_units)

        # quality
        self.quality_comboBox.addItems(self.model.stream_qualities.value)
        self.quality_comboBox.setCurrentIndex(self.quality_comboBox.findText(self.model.selected_roi_quality.value))

    def stream_qualities(self, qualities) -> None:
        # clear existing entries and apend the new
        self.quality_comboBox.clear()
        self.quality_comboBox.addItems(qualities)

    @pyqtSlot(str)
    def change_roi_quality(self, quality):
        """slot: change roi quality in model and in ui when user change roi quality in combobox."""
        self.model.selected_roi_quality.value = quality
        self.quality_comboBox.setCurrentIndex(self.quality_comboBox.findText(quality))

    @pyqtSlot()
    def save_values_slot(self):
        """Save button clicked we will save those values in model..
        The roi_quality was already saved by combobox slot.."""
        self.close()
        #roi_bitrate_current_text = self.bitrate_lineEdit.text()
        #if roi_bitrate_current_text != "":
        #    self.model.selected_roi_bitrate.value = roi_bitrate_current_text
        #    self.close()
        #else:
        #    popup = PopUp("Your bitrate is empty! Please insert a valid bitrate.")
        #    popup.exec_()

    @pyqtSlot()
    def cancel_slot(self):
        self.close()
