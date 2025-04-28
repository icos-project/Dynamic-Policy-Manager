#
# ICOS Dynamic Policy Manager
# Copyright © 2022 - 2025 Engineering Ingegneria Informatica S.p.A.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 
# This work has received funding from the European Union's HORIZON research
# and innovation programme under grant agreement No. 101070177.
#

import datetime
import logging

from keycloak import KeycloakOpenID

logger = logging.getLogger(__name__)


class KeycloakClient:
  
  
  def __init__(self, config) -> None:

    self.__plm_token = None
    self.__plm_token_expire_time = datetime.datetime.now()
        
    self.keycloak_openid = KeycloakOpenID(server_url=config.authn.server,
                                 client_id=config.authn.client_id,
                                 realm_name=config.authn.realm,
                                 client_secret_key=config.authn.client_secret.get_secret_value())

    logger.info("KeycloakClient initialized for client \"%s\"", config.authn.client_id)

  def validate_token(self, token) -> dict:
    """_summary_

    Args:
        token (str): the token to validate

    Returns:
        dict: token_info
    """
    KEYCLOAK_PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\n" + self.keycloak_openid.public_key() + "\n-----END PUBLIC KEY-----"
    options = {"verify_signature": True, "verify_aud": False, "verify_exp": True}
    return self.keycloak_openid.decode_token(token, key=KEYCLOAK_PUBLIC_KEY, options=options)      
  

  def is_authorized(self, token, permissions):
    logger.debug('Checking token uma permissions for permissions "%s"', permissions)
    res = self.keycloak_openid.has_uma_access(token, permissions=permissions)
    logger.debug('Server returned %s', res)
    if not res.is_authorized:
      logger.warn("Authorization denied, missing permissions: %s", res.missing_permissions)
      return False
    else:
      logger.info("Authorization granted")
      return True
  
  def get_plm_token(self):
    
    if not self.__plm_token or datetime.datetime.now() >= self.__plm_token_expire_time:
      token = self.keycloak_openid.token(grant_type=['client_credentials'])
      self.__plm_token = token['access_token']
      self.__plm_token_expire_time = datetime.datetime.now() + datetime.timedelta(seconds=float(token['expires_in']))
      logger.debug('New DPM access token acquired. Expires at %s', self.__plm_token_expire_time)
    else:
      logger.debug('Valid DPM access token found, reusing it')
    return self.__plm_token