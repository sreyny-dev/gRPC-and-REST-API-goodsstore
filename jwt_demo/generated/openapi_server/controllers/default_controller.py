import connexion
from typing import Dict
from typing import Tuple
from typing import Union
from pprint import pprint

from openapi_server.models.login_request import LoginRequest  # noqa: E501
from openapi_server.models.login_response import LoginResponse  # noqa: E501
from openapi_server.models.protected_data import ProtectedData  # noqa: E501
from openapi_server.models.register_request import RegisterRequest  # noqa: E501
from openapi_server import util

from openapi_server.controllers.security_controller import generate_token
from werkzeug.security import generate_password_hash, check_password_hash

# simplified user DB: username => password_hash
users = {}


def login_post():  # noqa: E501
    """Authenticate and get a JWT token

     # noqa: E501

    :param login_request: 
    :type login_request: dict | bytes

    :rtype: Union[LoginResponse, Tuple[LoginResponse, int], Tuple[LoginResponse, int, Dict[str, str]]
    """
    if connexion.request.is_json:
      login_request = LoginRequest.from_dict(connexion.request.get_json())  # noqa: E501
    if login_request.username not in users:
      return {'message': f'User {login_request.username} does not exist.'}, 404
    if check_password_hash(users[login_request.username], login_request.password):
      token = generate_token(user_name=login_request.username)
      return {'token': token}, 200
    else:
      return {'message': 'Invalid credentials'}, 401


def protected_get():  # noqa: E501
    """Access protected data

     # noqa: E501


    :rtype: Union[ProtectedData, Tuple[ProtectedData, int], Tuple[ProtectedData, int, Dict[str, str]]
    """
    # https://connexion.readthedocs.io/en/3.0.5/context.html#context-context
    user_name = connexion.context['token_info']['user_name']
    return {'message': f'Congratulations! Authentication passed! You are {user_name}.'}, 200


def register_post():  # noqa: E501
    """Register a new user

     # noqa: E501

    :param register_request: 
    :type register_request: dict | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    if connexion.request.is_json:
      register_request = RegisterRequest.from_dict(connexion.request.get_json())  # noqa: E501
    # check unique username
    if register_request.username in users:
      return {'message': f'User {register_request.username} already exists.'}, 400
    # generate password hash
    pwd_hash = generate_password_hash(register_request.password)
    # register
    users[register_request.username] = pwd_hash
    pprint(users)
    return {'message': f'User {register_request.username} registered successfully!'}, 201
