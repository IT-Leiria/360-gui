
"""
    Testing the AroundivisionClient from controller.
    Here we are mocking a requests api with requests_mock.

    - test_aroundvision_client_get_200()
    - test_aroundvision_client_get_500()
    - test_aroundvision_client_get_empty_msg()
"""

import pytest
import requests_mock

from aroundvision.controllers.controller import AroundvisionClient

mock_api_url = "http://arvapy_api/"


@pytest.fixture
def aroundvision_client():
    """Returns around client session!"""
    return AroundvisionClient()


def test_aroundvision_client_get_200(aroundvision_client):
    """Testing a good response!"""
    with requests_mock.Mocker() as m:
        m.get(mock_api_url, text="CONTENT")
        resp = aroundvision_client.create_request("get", mock_api_url)

        assert resp["content"] == b'CONTENT'
        assert resp["errors"] == ''
        assert resp['status_code'] == 200
        assert resp['success']


def test_aroundvision_client_get_500(aroundvision_client):
    """Testing a internal error where we shall receive a status code
    a 500 and a success False.."""
    with requests_mock.Mocker() as m:
        m.get(mock_api_url, text="CONTENT", status_code=500)
        resp = aroundvision_client.create_request("get", mock_api_url)

        assert resp["content"] == b'CONTENT'
        assert resp["errors"] == ''
        assert resp['status_code'] == 500
        assert not resp['success']


def test_aroundvision_client_get_empty_msg(aroundvision_client):
    """Testing receiving empty message."""
    with requests_mock.Mocker() as m:
        m.get(mock_api_url)
        resp = aroundvision_client.create_request("get", mock_api_url)

        assert resp["content"] == b''
        assert resp["errors"] == ''
        assert resp['status_code'] == 200
        assert resp['success']
