
import os
import inspect
import confuse
from datetime import datetime
from pathlib import Path


class ConfigurationManager:
    """Configuration Manager"""

    def __init__(self):
        self.base_config_path = os.path.dirname(os.path.realpath(inspect.getfile(self.__class__)))
        self.configuration_file = os.path.join(self.base_config_path, "config.yaml")
        self.current_date = datetime.today().strftime('%Y-%m-%d')
        self.config = self.load_config_file()
        self.log_config = self.config.get("log_configs")

        # Log variables
        self.log_filename = self.log_config.get("log_filename") + self.current_date + \
            self.log_config.get("log_extension")
        self.log_dir = os.path.dirname(self.log_filename)
        self.log_format = self.log_config.get("log_format")
        self.log_level = self.log_config.get("log_level")

        # stylesheet
        self.stylesheet_filename = self.config.get("stylesheet")

        # ui
        self.mainwindow_filename = self.config.get("ui_mainwindow")

        # Create dir for log if not exists
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)

    def load_config_file(self):
        return confuse.load_yaml(self.configuration_file)

    def get(self, value):
        return self.config[value]


CONF = ConfigurationManager()
