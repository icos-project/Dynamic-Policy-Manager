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

import logging
import uuid
from polman.common.config import PolmanConfig
from polman.common.events import PolicyEventsFactory
from polman.common.model import Policy, PolicyCreate, PolicyRead, PolicyPhase
from polman.common.service import PolmanService
from polman.registry.render import render_policy
from polman.storage.main import PolmanStorage
from polman.watcher.main import PolmanWatcher
logger = logging.getLogger(__name__)


class PolmanRegistry(PolmanService):

  def __init__(self, config: PolmanConfig, ps: PolmanStorage, pw: PolmanWatcher):
    logger.info('Initializing PolmanRegistry')
    self._ps = ps
    self._pw = pw

  def start(self):
    pass

  def get_policy_by_id(self, id: str) -> PolicyRead:
    p = self._ps.get(id)
    if not p:
      return None
    return PolicyRead(**p.model_dump())

  def list_all_policies(self, sort_by="creation_time", order="asc") -> list[PolicyRead]:
    policies = [PolicyRead(**db_policy.model_dump()) for db_policy in self._ps.list()]
    
    if sort_by == 'creation_time':
      policies.sort(key=lambda p: p.status.events[0].timestamp, reverse=True if order == "desc" else False)
    
    return policies

  def process_policy_create_request(self, policy: PolicyCreate, activate_created_policy=True) -> PolicyRead:
    logger.debug('Received request: %s', policy)
    rendered = render_policy(policy)
    logger.debug('Rendered policy: %s', rendered)
    
    db_policy = Policy(**rendered.model_dump(), id=str(uuid.uuid4()))
    
    db_policy = self._ps.insert(db_policy)
    
    self._ps.add_policy_event(db_policy, PolicyEventsFactory.policy_created())
    self._ps.set_policy_phase(db_policy, PolicyPhase.Inactive)


    
    logger.info('New Policy "%s" (id=%s) added', db_policy.name, db_policy.id)
    logger.debug('%s', db_policy.model_dump_json()) 


    if activate_created_policy:
      logger.debug("Activating policy because activate_created_policy=True")
      #
      # Call the watcher
      # 
      res = self._pw.set_measurement_backends(db_policy)
      for k, v in res.items():
        self._ps.update_measurement_backend(db_policy, k, v)
  
      # the status is considered enforced because we alway activate a policy when
      # we create it
      self._ps.set_policy_phase(db_policy, PolicyPhase.Enforced)
  
    return PolicyRead(**db_policy.model_dump())
    