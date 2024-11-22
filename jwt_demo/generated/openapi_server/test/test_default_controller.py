import unittest

from flask import json

from openapi_server.models.login_request import LoginRequest  # noqa: E501
from openapi_server.models.login_response import LoginResponse  # noqa: E501
from openapi_server.models.protected_data import ProtectedData  # noqa: E501
from openapi_server.models.register_request import RegisterRequest  # noqa: E501
from openapi_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_login_post(self):
        """Test case for login_post

        Authenticate and get a JWT token
        """
        login_request = {"password":"password","username":"username"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/login',
            method='POST',
            headers=headers,
            data=json.dumps(login_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_protected_get(self):
        """Test case for protected_get

        Access protected data
        """
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/protected',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_register_post(self):
        """Test case for register_post

        Register a new user
        """
        register_request = {"password":"password","username":"username"}
        headers = { 
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/register',
            method='POST',
            headers=headers,
            data=json.dumps(register_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
