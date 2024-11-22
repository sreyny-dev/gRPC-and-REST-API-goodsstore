from typing import List
import os
import datetime

import jwt  # https://pypi.org/project/PyJWT/

SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your_secret_key')
ALGORITHM = 'HS256'
EXPIRATION_MINUTES = 2

# decode_token (this function signature is auto-generated)
def info_from_BearerAuth(token):
    """
    Check and retrieve authentication information from custom bearer token.
    Returned value will be passed in 'token_info' parameter of your operation function, if there is one.
    'sub' or 'uid' will be set in 'user' parameter of your operation function, if there is one.

    :param token Token provided by Authorization header
    :type token: str
    :return: Decoded token information or None if token is invalid
    :rtype: dict | None
    """
    try:
      decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
      return decoded
    except jwt.ExpiredSignatureError:
      return None   # Token has expired
    except jwt.InvalidTokenError:
      return None   # Invalid token
    
def generate_token(user_name):
  """ Generate a JWT token for a given user. """
  cur_ts = datetime.datetime.now(tz=datetime.timezone.utc)
  payload = {
    'user_name': user_name,
    # https://pyjwt.readthedocs.io/en/stable/usage.html#registered-claim-names
    'iat': cur_ts,                                                  # issued at
    'exp': cur_ts + datetime.timedelta(minutes=EXPIRATION_MINUTES)  # token expiration
  }
  token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
  return token
