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

from enum import Enum
from pydantic import BaseModel, Field, SecretStr, model_validator

from typing_extensions import Self
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PrometheusConfig(BaseModel):
  rules_api_url: str = ""  


class DBType(str, Enum):
    IN_MEMORY = "inmemory"
    FILE = "file"
    MONGODB = "mongodb"


class DBConfig(BaseModel):
  type: DBType = DBType.IN_MEMORY
  host: str = ""
  port: int = 0
  user: str = ""
  password: SecretStr = SecretStr("")
  name: str = ""
  url: str = ""

  @model_validator(mode='after')
  def custom_default(self) -> Self:
    if self.type == 'mongodb' and not self.url:
      if not self.host:
        logger.warning("Database type 'mongodb' but 'host' parameter not set: using default 'localhost'")
        self.host = "localhost"
      if not self.port:
        logger.warning("Database type 'mongodb' but 'port' parameter not set: using default '27017'")
        self.port = 27017
      if not self.name:
        logger.warning("Database type 'mongodb' but 'name' parameter not set: using default 'polman'")
        self.name = "polman"
    return self


class AuthenticationConfig(BaseModel):
  skip: bool = False
  server: str = "https://localhost/"
  realm: str = "icos"
  client_id: str = ""
  client_secret: SecretStr = SecretStr("")
  verify_audience: bool = False
  
class AuthorizationConfig(BaseModel):
  skip: bool = False
  fallback_scope: str = ""

class APIConfig(BaseModel):
  host: str = "127.0.0.1"
  port: int = 8000
  root: str = '/polman'
  allowed_cors_origins: list[str] = Field(default=None)
  enable_debug_calls: bool = False
  
class ICOSConfig(BaseModel):
  job_manager_base_url: str = ""
  
class PolmanConfig(BaseModel):
  
  quiet: bool = False
  verbosity: int = 2
  rich_output: bool = False
  
  db: DBConfig = Field(default=None)
  authn: AuthenticationConfig = Field(default=None)
  authz: AuthorizationConfig  = Field(default=None)
  api: APIConfig = Field(default=None)
  prometheus: PrometheusConfig = Field(default=None)

  icos: ICOSConfig = Field(default=None)
