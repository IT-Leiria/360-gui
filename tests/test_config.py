
"""
    Testing configuration manager: here we are validation the load yaml file
    and if we are loading correctly variables from configuration. For tests
    we are using the config_teste.yaml..
    - test_api_configs()
    - test_ui_configs()
    - test_log_configs()
    - test_icons_config()
    - test_general_vars_config()
"""

from datetime import datetime
import pytest

from aroundvision.config.config_manager import ConfigurationManager


@pytest.fixture
def config():
    """Create fixture to create configuration manager.."""
    return ConfigurationManager("config_teste.yaml")


def test_api_configs(config):
    """Testing values related with api.."""
    assert config.api_endpoint == "http://0.0.0.0:5000/"
    assert config.api_get_stream_list_path == "get_stream_list"
    assert config.api_select_stream_path == "select_stream"
    assert config.api_get_frame_info == "get_frame_info"
    assert config.api_get_frame_raw_path == "get_frame_raw"
    assert config.api_get_viewport_info == "get_viewport_info"
    assert config.api_get_viewport_raw == "get_viewport_raw"
    assert config.api_selected_stream_idx == "0"


def test_ui_configs(config):
    """Testing values related with ui files.."""
    assert config.stylesheet_filename.split("/")[-1] == "aroundvision.css"
    assert config.mainwindow_filename.split("/")[-1] == "mainwindow.ui"
    assert config.loadsource_filename.split("/")[-1] == "load_source.ui"
    assert config.popup_filename.split("/")[-1] == "popup.ui"
    assert config.roi_filename.split("/")[-1] == "region_of_interest.ui"
    assert config.roi_settings_filename.split("/")[-1] == "roi_settings.ui"
    assert config.about_filename.split("/")[-1] == "about.ui"


def test_log_configs(config):
    """Testing values related with logs.."""
    d = datetime.today().strftime('%Y-%m-%d')

    assert config.log_level == "DEBUG"
    assert config.log_format == "[%(asctime)s - %(filename)s:%(lineno)s -  %(funcName)s() - %(levelname)s ] %(message)s"
    assert config.log_filename == "/tmp/aroundvision/AROUNDVISION-" + d + ".log"


def test_icons_config(config):
    """Testing values related with icons.."""
    assert config.play_icon.split("/")[-1] == "play-circle-solid_ok.png"
    assert config.pause_icon.split("/")[-1] == "pause-circle-solid_ok.png"
    assert config.settings_icon.split("/")[-1] == "settings-solid_ok.png"
    assert config.about_logo.split("/")[-1] == "csw_logo.png"
    assert config.loading_gif.split("/")[-1] == "loading.gif"


def test_general_vars_config(config):
    """Testing general values read from configuration.."""
    # projections
    assert config.projections[0]["proj_name"] == "Equi-rectangular"
    assert config.projections[0]["proj_id"] == 0
    assert config.projections[0]["proj_api_name"] == "ERP"
    assert config.projections[1]["proj_name"] == "Cube-Map"
    assert config.projections[1]["proj_id"] == 1
    assert config.projections[1]["proj_api_name"] == "CMP"
    assert config.projections[2]["proj_name"] == "Compact OHP"
    assert config.projections[2]["proj_id"] == 2
    assert config.projections[2]["proj_api_name"] == "COHP"
    assert config.projections[3]["proj_name"] == "Rectilinear"
    assert config.projections[3]["proj_id"] == 3
    assert config.projections[3]["proj_api_name"] == "RECT"
    assert config.projections[4]["proj_name"] == "Compact ISP"
    assert config.projections[4]["proj_id"] == 4
    assert config.projections[4]["proj_api_name"] == "CISP"
    # properties
    assert config.qualities == ['1', '2', '3', '4']
    assert config.faces_cube == ['1', '2', '3', '4', '5', '6']
    assert config.frame_rate == 30
    assert config.docs_url.split("/")[-1] == "index.html"
    assert config.loading_gif_time == 3000
    # roi settings
    assert config.roi_bitrate == "22"
    assert config.roi_bitrate_units == "Mbits/s"
    assert config.roi_qualities == ['1', '2', '3', '4']
    assert config.roi_quality == "4"
