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

import datetime
from enum import Enum
from http import HTTPMethod
from typing import Literal, NotRequired, Optional, Union
from typing_extensions import TypedDict
from pydantic import BaseModel, ConfigDict

class BaseModelWithType(BaseModel):
  pass
  
class PolicySubjectBase(BaseModelWithType):
  type: str
     
class PolicySubjectCustom(PolicySubjectBase):
  type: Literal['custom'] = 'custom'
  
  model_config = ConfigDict(extra='allow')
  
class PolicySubjectApplication(PolicySubjectBase):
  type: Literal['app'] = 'app'
  appName: str
  appComponent: str
  appInstance: str

class PolicySubjectHost(PolicySubjectBase):
  type: Literal['host'] = 'host'
  hostId: str
  agentId: str

class PolicySpecBase(BaseModelWithType):
  description: str = ""
  pass

class PolicySpecTelemetry(PolicySpecBase):
  type: Literal['telemetryQuery'] = 'telemetryQuery'
  expr: str
  violatedIf: Optional[str] = None
  thresholds: Optional[dict[str, float]] = None

class PolicySpecTemplate(PolicySpecBase):
  type: Literal['template'] = 'template'
  templateName: str

class PolicySpecConstraints(PolicySpecBase):
  type: Literal['constraints']
  constraints: dict[str, str]


class PolicyActionBase(BaseModelWithType):
  pass

class PolicyActionWebhook(PolicyActionBase):
  type: Literal['webhook'] = 'webhook'
  url: str
  httpMethod: HTTPMethod
  extraParams: dict[str, str] = {}
  includeAccessToken: bool = False

class PolicyProperties(TypedDict):
  oneoff: NotRequired[bool]
  interval: NotRequired[str]
  pendingInterval: NotRequired[str]


PolicySubject = Union[PolicySubjectApplication, PolicySubjectHost, PolicySubjectCustom]  # keep Custom at the end!
PolicySpec = Union[PolicySpecTemplate, PolicySpecTelemetry, PolicySpecConstraints]
PolicyAction = Union[PolicyActionWebhook]

class PolicyCreate(BaseModel):
  name: str
  subject: PolicySubject
  spec: PolicySpec
  action: PolicyAction
  variables: dict[str, Union[str|int|float]] = {}
  properties: PolicyProperties = {}

class Violation(BaseModel):
  id: str
  currentValue: str
  threshold: Optional[str] = None
  policyName: str
  policyId: str
  measurementBackend: str
  extraLabels: dict[str, str]
  subject: Union[PolicySubjectCustom, PolicySubjectApplication, PolicySubjectHost]

class PolicyPhase(str, Enum):
  Enforced = 'enforced'
  Violated = 'violated'
  Inactive = 'inactive'
  Unknown = 'unknown'
  
class PolicyEventType(str, Enum):
    Activated = 'activated'
    Deactivated = 'deactivated'
    Violated = 'violated'
    Resolved = 'resolved'
    Created = 'created'
    Deleted = 'deleted'

class PolicyEvent(BaseModel):
  type: PolicyEventType
  timestamp: datetime.datetime
  details: dict[str,Optional[Union[str,int,float, dict[str, str]]]] = {}
  
class PolicyStatus(BaseModel):
  measurementBackends: dict[str, dict[str, Union[str, int]]] = {}
  events: list[PolicyEvent] = []
  phase: PolicyPhase = PolicyPhase.Unknown

class Policy(PolicyCreate):
  id: str = None
  status: PolicyStatus = PolicyStatus()

class PolicyRead(Policy):
  id: str

class User(BaseModel):
  name: str
  username: str
  email: str
  scopes: list[str]
