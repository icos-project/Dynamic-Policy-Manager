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


from http import HTTPMethod
from typing import Literal, Optional, Union
from pydantic import BaseModel, field_validator
import yaml

from polman.common.model import PolicyActionBase, PolicyProperties, PolicySpec


class ICOSPolicyBase(BaseModel):
  type: str
  name: Optional[str] = None
  component: Optional[str] = None
  remediation: Optional[str] = None

class ICOSPolmanTemplatePolicy(ICOSPolicyBase):
  type: Literal['polmanTemplate'] = 'polmanTemplate'
  fromTemplate: str
  variables: dict = {}
  properties: Optional[PolicyProperties] = {}
  
class ICOSPolmanSpecPolicy(ICOSPolicyBase):
  type: Literal['polmanSpec'] = 'polmanSpec'
  spec: PolicySpec
  variables: dict = {}
  properties: Optional[PolicyProperties] = {}
  
class ICOSSecurityPolicy(ICOSPolicyBase):
  type: Literal['security'] = 'security'
  security: str

ICOSAppDescriptorPolicy =  Union[ICOSPolmanTemplatePolicy, ICOSPolmanSpecPolicy, ICOSSecurityPolicy]

class ICOSAppDescriptorComponent(BaseModel):
  name: str
  type: str
  policies: Optional[list[ICOSAppDescriptorPolicy]] = []

class ICOSAppDescriptor(BaseModel):
  name: str
  description: str
  components: list[ICOSAppDescriptorComponent] = []
  policies: list[ICOSAppDescriptorPolicy] = []


class PolicyActionICOSService(PolicyActionBase):
  type: Literal['icos-service'] = 'icos-service'
  uri: str
  http_method: HTTPMethod
  extra_params: dict[str, str] = {}
  include_access_token: bool = False
  

class ICOSAppDeployedRequest(BaseModel):
  #app_descriptor: ICOSAppDescriptor
  app_descriptor: ICOSAppDescriptor
  app_instance: str
  common_action: PolicyActionICOSService
  service: str
  
  @field_validator('app_descriptor', mode='before')
  @classmethod
  def parse_from_string(cls, v: str) -> ICOSAppDescriptor:
    for doc in yaml.safe_load_all(v):
      if 'name' in doc and 'components' in doc:
        return ICOSAppDescriptor.model_validate(doc)
    