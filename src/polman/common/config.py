# ICOS Dynamic Policy Manager
# Copyright © 2022-2024 Engineering Ingegneria Informatica S.p.A.
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

from pydantic import BaseModel


class PrometheusConfig(BaseModel):
  orig_api_url: str = ""
  mod_api_url: str = ""


class DBConfig(BaseModel):
  type: str = "sqlite"
  host: str = ""
  port: int = 0
  user: str = ""
  password: str = ""
  name: str = ""
  url: str = ""


class AuthenticationConfig(BaseModel):
  skip: bool = False
  server: str = "https://localhost/"
  realm: str = "icos"
  client_id: str = ""
  client_secret: str = ""
  verify_audience: bool = False
  
class AuthorizationConfig(BaseModel):
  skip: bool = False

class APIConfig(BaseModel):
  host: str = "127.0.0.1"
  port: int = 8000
  root: str = '/polman'
  allowed_cors_origins: list[str] = None
  enable_admin_api: bool = False
  
class ICOSConfig(BaseModel):
  job_manager_base_url: str = ""
  
class PolmanConfig(BaseModel):
  
  quiet: bool = False
  verbosity: int = 2
  
  db: DBConfig = None
  authn: AuthenticationConfig = None
  authz: AuthorizationConfig = None
  api: APIConfig = None
  prometheus: PrometheusConfig = None

  icos: ICOSConfig = None
