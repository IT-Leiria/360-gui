
import pytest
import pytestqt.qtbot
from PyQt5 import QtCore

from aroundvision.views.load_source import LoadSource
from aroundvision.models.models import Model
from aroundvision.controllers.controller import Controller

m = Model()
c = Controller(m)


def test_load_source(qtbot):
    """Testing functionalities in load source like save button actions.."""
    w = LoadSource(m, c)
    assert m.api_endpoint.value == w.api_endpoint_lineEdit.text()
    assert m.stream_index.value == w.stream_index_lineEdit.text()

    m.api_connected.value = True
    w.stream_index_lineEdit.setText("4")

    qtbot.mouseClick(w.save_pushButton, QtCore.Qt.LeftButton)

    assert m.api_endpoint.value == w.api_endpoint_lineEdit.text()
    assert m.stream_index.value == "4"

# Add more tests





