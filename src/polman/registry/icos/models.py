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

from http import HTTPMethod
from typing import Annotated, List, Literal, Optional, Self, Union, get_args
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
import yaml

from polman.common.model import PolicyActionBase, PolicyProperties, PolicySpec


#
#  POLICIES
#

class ICOSPolicyBase(BaseModel):
  name: Optional[str] = None
  #component: Optional[str] = None
  applyTo: List[str] = Field(default=[], alias="apply-to")
  remediation: Optional[str] = "none"
  variables: dict = {}
  properties: PolicyProperties = {}

  @field_validator('applyTo', mode='before')
  @classmethod
  def parse_from_string(cls, v: str|List[str]) -> List[str]:
    if isinstance(v, str):
      return [v]
    else:
      return v

class ICOSPolmanTemplatePolicy(ICOSPolicyBase):
  type: Literal['custom'] = 'custom'
  fromTemplate: str

  
class ICOSPolmanSpecPolicy(ICOSPolicyBase):
  type: Literal['custom'] = 'custom'
  spec: PolicySpec

class ICOSSecurityPolicyShort(ICOSPolicyBase):
  security: str
  remediation: Optional[str] = "redeploy"

class ICOSSecurityPolicy(ICOSPolicyBase):
  type: Literal['security'] = 'security'
  threshold: Optional[int] = None
  level: Optional[Literal["low", "medium", "high"]] = None
  remediation: Optional[str] = "redeploy"

  @model_validator(mode='after')
  def check_passwords_match(self) -> Self:
    if (self.threshold is not None) and (self.level is not None):
      raise ValueError('Only one between "threshold" and "level" can be set')
    return self

ICOSAppDescriptorPolicy =  Union[
  ICOSSecurityPolicyShort, 
  ICOSSecurityPolicy, 
  ICOSPolmanTemplatePolicy, 
  ICOSPolmanSpecPolicy
]

# fallback object to parse all policies that are not for Polman
# they will be discarded
class NoPolmanPolicy(BaseModel):
  type: str

  @field_validator('type', mode='before')
  @classmethod
  def parse_from_string(cls, v: str) -> str:
    # if the type is one of the other known policies, fail
    for t in get_args(ICOSAppDescriptorPolicy):
      if "type" in t.model_fields and t.model_fields["type"].default == v:
        raise ValueError(f"type ({t.model_fields['type'].default}) is for a Polman policy, but the other fields do not match")
    return v


#
#  APP DESCRIPTOR MODEL
#

class ICOSAppDescriptorComponent(BaseModel):
  name: str
  type: str
  policies: Optional[list[Union[ICOSAppDescriptorPolicy, NoPolmanPolicy]]] = []

class ICOSAppDescriptor(BaseModel):
  name: str
  description: str
  components: list[ICOSAppDescriptorComponent] = []
  policies: list[Union[ICOSAppDescriptorPolicy, NoPolmanPolicy]] = []


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
  def parse_from_string(cls, v: str) -> ICOSAppDescriptor|None:
    for doc in yaml.safe_load_all(v):
      if 'name' in doc and 'components' in doc:
        return ICOSAppDescriptor.model_validate(doc)


class GenericICOSAppLifecycleEvent(BaseModel):
  #event: str
  app_instance: str
  app_descriptor: Optional[ICOSAppDescriptor] = None
  callback: Optional[PolicyActionICOSService] = None
  service: str

  @field_validator('app_descriptor', mode='before')
  @classmethod
  def parse_from_string(cls, v: str) -> ICOSAppDescriptor|None:
    for doc in yaml.safe_load_all(v):
      if 'name' in doc and 'components' in doc:
        return ICOSAppDescriptor.model_validate(doc)

class ICOSAppCreatedEvent(GenericICOSAppLifecycleEvent):
  event: Literal['created'] = 'created'

class ICOSAppStoppedEvent(GenericICOSAppLifecycleEvent):
  event: Literal['stopped'] = 'stopped'

class ICOSAppStartedEvent(GenericICOSAppLifecycleEvent):
  event: Literal['started'] = 'started'

class ICOSAppDeletedEvent(GenericICOSAppLifecycleEvent):
  event: Literal['deleted'] = 'deleted'


ICOSAppEvent = Union[ICOSAppCreatedEvent, ICOSAppStartedEvent, ICOSAppStoppedEvent, ICOSAppDeletedEvent]