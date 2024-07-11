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

import json
import logging
from polman.common.model import Policy, PolicyEvent, PolicyPhase, Violation
from polman.storage.main import PolmanStorage

logger = logging.getLogger(__name__)

class FilePolmanStorage(PolmanStorage):
  
  def __init__(self, config) -> None:
    super().__init__(config)
  
    logger.info("Initializing File Storage from file %s", config.db.url)
    self._file = config.db.url
    self._store = {}
    self._read_from_file()
    
  def _read_from_file(self):
    with open(self._file, "r") as infile:
      json_list=json.load(infile)
      models = [Policy.model_validate(o) for o in json_list]
      self._store = {m.id: m for m in models}

  def _write_to_file(self):
    models = list(self._store.values())
    json_list = [m.model_dump(mode="json") for m in models]
    with open(self._file, "w") as outfile:
        json.dump(json_list, outfile)

  def start(self):
    pass
  
  def insert(self, db_policy: Policy):
    self._store[db_policy.id] = db_policy
    self._write_to_file()
    return db_policy

  def get(self, id: str):
    if id in self._store:
      return self._store[id]
    else:
      return None

  def add_policy_event(self, policy: Policy, event: PolicyEvent):
    policy.status.events.append(event)
    self._write_to_file()

  def set_policy_phase(self, policy: Policy, phase: PolicyPhase):
    policy.status.phase = phase
    self._write_to_file()
  
  def add_violation_to_history(self, policy: Policy, violation: Violation):
    policy.status.violationHistory.append(violation)
    self._write_to_file()
    
  def update_measurement_backend(self, policy: Policy, name: str, status: dict):
    policy.status.measurementBackends[name] = status
    self._write_to_file()
  
  def list(self):
    return list(self._store.values())


  def delete(self, id: str):
    pass