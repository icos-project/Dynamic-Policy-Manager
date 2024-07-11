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

from abc import ABC, abstractmethod
import logging
from polman.common.model import Policy, PolicyEvent, PolicyPhase, Violation
from polman.common.service import PolmanService

logger = logging.getLogger(__name__)

class PolmanStorage(PolmanService, ABC):
  
  @abstractmethod
  def insert(self, policy: Policy) -> Policy:
    pass

  @abstractmethod
  def get(self, id: str) -> Policy:
    pass

  @abstractmethod
  def list(self) -> list[Policy]:
    pass

  @abstractmethod
  def delete(self, id: str) -> bool:
    pass
 
  @abstractmethod
  def add_policy_event(self, policy: Policy, event: PolicyEvent):
    pass
  
  @abstractmethod
  def set_policy_phase(self, policy: Policy, phase: PolicyPhase):
    pass
  
  @abstractmethod
  def add_violation_to_history(self, policy: Policy, violation: Violation):
    pass

  @abstractmethod
  def update_measurement_backend(self, policy: Policy, name: str, status: dict):
    pass

class InMemoryPolmanStorage(PolmanStorage):
  
  def __init__(self, config, init_store={}) -> None:
    super().__init__(config)
    logger.info("Initializing InMemory Storage")
    self._store = init_store
    
  def start(self):
    pass
  
  def insert(self, db_policy: Policy):
    self._store[db_policy.id] = db_policy
    return db_policy

  def get(self, id: str):
    if id in self._store:
      return self._store[id]
    else:
      return None

  def add_policy_event(self, policy: Policy, event: PolicyEvent):
    policy.status.events.append(event)

  def set_policy_phase(self, policy: Policy, phase: PolicyPhase):
    policy.status.phase = phase
  
  def add_violation_to_history(self, policy: Policy, violation: Violation):
    policy.status.violationHistory.append(violation)
    
  def update_measurement_backend(self, policy: Policy, name: str, status: dict):
    policy.status.measurementBackends[name] = status
  
  def list(self):
    return list(self._store.values())


  def delete(self, id: str):
    pass