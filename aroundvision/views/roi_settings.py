
import os

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget

from config.config_manager import CONF
from aroundvision.views.popup import PopUp


class RoiSettings(QWidget):
    """
    RoiSettings: settings panel with bitrate and quality.
    """
    def __init__(self, model):
        super().__init__()

        # variables
        self.model = model
        self.current_dir = os.path.dirname(__file__)
        self.roi_settings_filename = os.path.join(self.current_dir, CONF.roi_settings_filename)

        uic.loadUi(self.roi_settings_filename, self)
        self.fill_ui()

        # Connects
        self.cancel_pushButton.clicked.connect(self.cancel_slot)
        self.save_pushButton.clicked.connect(self.save_values_slot)
        self.quality_comboBox.activated[str].connect(self.change_roi_quality)

    def fill_ui(self):
        """Fill ui with model values.
        bitrate and quality.
        """
        # bitrate
        self.bitrate_lineEdit.setText(self.model.selected_roi_bitrate)
        self.bitrate_units_label.setText(CONF.roi_bitrate_units)

        # quality
        self.quality_comboBox.addItems(CONF.roi_qualities)
        self.quality_comboBox.setCurrentIndex(self.quality_comboBox.findText(self.model.selected_roi_quality))

    @pyqtSlot(str)
    def change_roi_quality(self, quality):
        """slot: change roi quality in model and in ui when user change roi quality in combobox."""
        self.model.selected_roi_quality = quality
        self.quality_comboBox.setCurrentIndex(self.quality_comboBox.findText(quality))

    @pyqtSlot()
    def save_values_slot(self):
        roi_bitrate_current_text = self.bitrate_lineEdit.text()
        if roi_bitrate_current_text != "":
            self.model.selected_roi_bitrate = roi_bitrate_current_text
            self.close()
        else:
            popup = PopUp("Your bitrate is empty! Please insert a valid bitrate.")
            popup.exec_()

    @pyqtSlot()
    def cancel_slot(self):
        self.close()
