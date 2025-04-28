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

import logging

from polman.common.errors import PolicyNotFoundError
from polman.common.model import Policy, PolicyEvent, PolicyPhase, PolicySpec, PolicyVariableType
from .main import PolmanStorageBackend

logger = logging.getLogger(__name__)


class InMemoryPolmanStorage(PolmanStorageBackend):
    """A backend that keeps policies in memory."""

    def __init__(self, config, init_store={}) -> None:
        self._store = init_store

    def insert(self, policy: Policy) -> Policy:
        self._store[policy.id] = policy
        return policy

    def get(self, policy_id: str):
        if policy_id in self._store:
            return self._store[policy_id]
        raise PolicyNotFoundError(policy_id)

    def add_policy_event(self, policy_id: str, event: PolicyEvent) -> None:
        p = self.get(policy_id)
        p.status.events.append(event)

    def set_policy_phase(self, policy_id: str, phase: PolicyPhase) -> None:
        p = self.get(policy_id)
        p.status.phase = phase

    def update_measurement_backend(self, policy_id: str, name: str, status: dict) -> None:
        p = self.get(policy_id)
        p.status.measurementBackends[name] = status

    def delete_measurement_backend(self, policy_id: str, name: str) -> None:
        p = self.get(policy_id)
        del p.status.measurementBackends[name]

    def list(self, filters={}) -> list[Policy]:
        # TODO: implement filtering
        return list(self._store.values())

    def delete(self, policy_id: str) -> Policy:
        p = self._store[policy_id]
        del self._store[policy_id]
        return p

    def set_rendered_spec(self, policy_id: str, spec: PolicySpec) -> None:
        p = self.get(policy_id)
        p.status.renderedSpec = spec

    def set_variable(self, policy_id: str, name: str, value: PolicyVariableType|None) -> None:
        p = self.get(policy_id)
        if not value:
            del p.variables[name]
        else:
            p.variables[name] = value