
"""

"""

import argparse
import logging
import sys

from aroundvision.utils.app_utils import setup_logging
from aroundvision.views.mainwindow import MainWindow
from aroundvision.models.models import Model
from aroundvision.controllers.controller import Controller
from aroundvision.config.config_manager import CONF

from PyQt5.QtWidgets import QApplication


def input_arguments():
    """Argparse with help description and input args!"""
    parser = argparse.ArgumentParser(
        description="The AROUNDVISION is a tool to visualize 360 images from an API "
                    "in different projections. Additionally, it allows the user to "
                    "select some region of interest to visualize that area in more "
                    "detail!")

    # parser.add_argumemt('-var', '--variable', help='help')
    return parser.parse_args()


def run_app():
    app = QApplication(sys.argv)
    model = Model()
    window = MainWindow(model, Controller(model))
    window.show()
    window.raise_()
    app.exit(app.exec_())


def main():
    """Main Function: setup logging and run_app!"""
    args = input_arguments()
    setup_logging(CONF.log_filename, getattr(logging, CONF.log_level), CONF.log_format)
    run_app()


if __name__ == "__main__":
    main()
