
import os
import inspect
import confuse
from datetime import datetime
from pathlib import Path


class ConfigurationManager:
    """Configuration Manager: reading configuration values from config.yaml."""

    def __init__(self, config_file=None):
        """Constructor for configuration manager."""
        self.base_config_path = os.path.dirname(os.path.realpath(inspect.getfile(self.__class__)))
        self.parent_path = os.path.abspath(os.path.join(self.base_config_path, os.pardir))
        self.configuration_file = config_file if config_file else os.path.join(self.base_config_path, "config.yaml")
        self.current_date = datetime.today().strftime('%Y-%m-%d')
        self.config = self.load_config_file()

        # let's start storing variables
        self.log_config = self.config.get("log_configs")
        self.api_config = self.config.get("api_configs")
        self.ui_config = self.config.get("ui_configs")
        self.icons = self.config.get("icons")
        self.cube_proj_name = self.config.get("cube_projection")
        self.faces_cube = self.config.get("faces_cube")
        self.frame_rate = self.config.get("frame_rate")
        self.docs_url = os.path.join(self.parent_path, self.config.get("doc_url"))
        self.loading_gif_time = self.config.get("loading_time_mseconds")

        # roi settings
        self.roi_bitrate = self.config.get("roi_bitrate_value")
        self.roi_bitrate_units = self.config.get("roi_bitrate_units")

        # API configs
        self.api_endpoint = self.api_config.get("api_endpoint")
        self.api_get_stream_list_path = self.api_config.get("api_stream_list_path")
        self.api_select_stream_path = self.api_config.get("api_select_stream_path")
        self.api_get_frame_info = self.api_config.get("api_get_frame_info")
        self.api_get_frame_raw_path = self.api_config.get("api_get_frame_raw_path")
        self.api_get_face_raw_path = self.api_config.get("api_get_face_raw_path")
        self.api_get_viewport_info = self.api_config.get("api_get_viewport_info")
        self.api_get_viewport_raw = self.api_config.get("api_get_viewport_raw")
        self.api_selected_stream_idx = self.api_config.get("api_selected_stream_idx")
        self.api_get_layer_info = self.api_config.get("api_get_layer_info")
        self.api_get_projection_list_path = self.api_config.get("api_get_projection_list")

        # Log variables
        self.log_filename = self.log_config.get("log_filename") + self.current_date + \
            self.log_config.get("log_extension")
        self.log_dir = os.path.dirname(self.log_filename)
        self.log_format = self.log_config.get("log_format")
        self.log_level = self.log_config.get("log_level")

        # stylesheet
        self.stylesheet_filename = self.parent_path + "/views/" + self.ui_config.get("stylesheet")

        # ui
        self.mainwindow_filename = self.parent_path + "/views/" + self.ui_config.get("ui_mainwindow")
        self.loadsource_filename = self.parent_path + "/views/" + self.ui_config.get("ui_loadsource")
        self.popup_filename = self.parent_path + "/views/" + self.ui_config.get("ui_popup")
        self.roi_filename = self.parent_path + "/views/" + self.ui_config.get("roi_window")
        self.roi_settings_filename = self.parent_path + "/views/" + self.ui_config.get("roi_settings")
        self.about_filename = self.parent_path + "/views/" + self.ui_config.get("about_window")

        # Create dir for log if not exists
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)

        # path icons
        self.play_icon = self.parent_path + "/images/" + self.icons.get("play_icon")
        self.pause_icon = self.parent_path + "/images/" + self.icons.get("pause_icon")
        self.settings_icon = self.parent_path + "/images/" + self.icons.get("settings_icon")
        self.loading_gif = self.parent_path + "/images/" + self.icons.get("loading_gif")

    def load_config_file(self):
        return confuse.load_yaml(self.configuration_file)

    def get(self, value):
        return self.config[value]


CONF = ConfigurationManager()
