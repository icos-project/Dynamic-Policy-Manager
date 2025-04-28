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
from abc import ABC, abstractmethod

from polman.common.config import DBType, PolmanConfig
from polman.common.logging import log_object
from polman.common.model import Policy, PolicyEvent, PolicyPhase, PolicySpec, PolicyVariableType
from polman.common.service import PolmanService
from polman.meter.main import PolmanMeter
from polman.storage.backend.main import PolmanStorageBackend
from polman.storage.backend.memory import InMemoryPolmanStorage
from polman.storage.backend.file import FilePolmanStorage
from polman.storage.backend.mongo import MongodbPolicyStore

logger = logging.getLogger(__name__)

#
#
#

class PolmanStorage(PolmanService, ABC):
    """The PolmanStorage service."""

    def __init__(self, config: PolmanConfig, pm: PolmanMeter, backend: PolmanStorageBackend | None = None) -> None:
        super().__init__(config)

        self._backend: PolmanStorageBackend
        self._pm = pm

        if backend:
            self._backend = backend
            return

        if config.db.type is DBType.IN_MEMORY:
            self._backend = InMemoryPolmanStorage(config)

        if config.db.type is DBType.MONGODB:
            self._backend = MongodbPolicyStore(config)

        if config.db.type is DBType.FILE:
            self._backend = FilePolmanStorage(config)

    async def start(self) -> None:
        """Start the service."""

    def insert(self, db_policy: Policy):
        res = self._backend.insert(db_policy)
        logger.info('New Policy added\n%s', log_object(res))
        return res

    def get(self, policy_id: str):
        return self._backend.get(policy_id)

    def add_policy_event(self, policy: Policy, event: PolicyEvent) -> None:
        self._backend.add_policy_event(policy.id, event)
        logger.debug(f"Policy \"{policy.name}\" event: {event}")

    def set_policy_phase(self, policy: Policy, phase: PolicyPhase) -> None:
        old_phase = policy.status.phase
        self._backend.set_policy_phase(policy.id, phase)
        logger.info(f"Policy \"{policy.name}\" phase changed: {old_phase} -> {phase}")
        self._pm.set_policy_enforced(policy)

    def set_rendered_spec(self, policy: Policy, rendered_spec: PolicySpec) ->  None:
        self._backend.set_rendered_spec(policy.id, rendered_spec)

    def update_variable(self, policy: Policy, variable_name: str, variable_value: PolicyVariableType | None) ->  None:
        self._backend.set_variable(policy.id, variable_name, variable_value)

    def update_measurement_backend(self, policy: Policy, name: str, status: dict) -> None:
        self._backend.update_measurement_backend(policy.id, name, status)

    def delete_measurement_backend(self, policy: Policy, name: str) -> None:
        """Delete a measurement backend status."""
        self._backend.delete_measurement_backend(policy.id, name)

    def list(self, filters={}) -> list[Policy]:
        return self._backend.list(filters=filters)

    def delete(self, policy_id: str) -> Policy:
        """Delete a policy by id

        Args:
        ----
            id (str): the id of the policy to remote

        Returns:
        -------
            Policy: the policy deleted

        """
        return self._backend.delete(policy_id)
