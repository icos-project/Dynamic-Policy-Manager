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
import uuid

from typing import List
from polman.common.config import PolmanConfig
from polman.common.errors import PolicyRenderingError, PolicyVariableNotExist, PolmanError
from polman.common.events import PolicyEventsFactory
from polman.common.model import Policy, PolicyCreate, PolicyPhase, PolicyRead, PolicyVariableType
from polman.common.service import PolmanService
from polman.registry.render import render_policy_spec, test_spec_rendering
from polman.storage.main import PolmanStorage
from polman.watcher.main import PolmanWatcher

logger = logging.getLogger(__name__)


class PolmanRegistry(PolmanService):
    def __init__(self, config: PolmanConfig, ps: PolmanStorage, pw: PolmanWatcher):
        logger.info("Initializing PolmanRegistry")
        self._ps = ps
        self._pw = pw

    async def start(self):
        pass

    def get_policy_by_id(self, id: str) -> PolicyRead:
        p = self._ps.get(id)
        if not p:
            raise PolmanError("Policy Not Found")
        return PolicyRead(**p.model_dump())


    def find_policies(
        self, sort_by="creation_time", order="asc", filters={}
    ) -> List[PolicyRead]:
        policies = [
            PolicyRead(**db_policy.model_dump()) for db_policy in self._ps.list(filters=filters)
        ]

        if sort_by == "creation_time":
            policies.sort(
                key=lambda p: p.status.events[0].timestamp,
                reverse=True if order == "desc" else False,
            )

        return policies

    def list_all_policies(
        self, sort_by="creation_time", order="asc"
    ) -> list[PolicyRead]:
        return self.find_policies(sort_by=sort_by, order=order)

    def process_policy_delete_request(self, policy_id: str) -> Policy:
        """Delete a policy."""
        policy = self._ps.get(policy_id)
        self.deactivate_policy(policy)
        self._ps.delete(policy_id)
        return policy


    def activate_policy(self, policy: Policy) -> Policy:
        self._pw.set_measurement_backends(policy)
        # the status is considered enforced because we alway activate a policy when
        # we create it
        self._ps.set_policy_phase(policy, PolicyPhase.Enforced)
        return PolicyRead(**self._ps.get(policy.id).model_dump())

    def deactivate_policy(self, policy: Policy) -> Policy:
        self._pw.unset_measurement_backends(policy)
        self._ps.set_policy_phase(policy, PolicyPhase.Inactive)
        return PolicyRead(**self._ps.get(policy.id).model_dump())

    def render_policy_spec(self, policy: Policy) -> Policy:
        rendered = render_policy_spec(policy)
        logger.debug("Rendered policy: %s", rendered)
        self._ps.set_rendered_spec(policy, rendered)            
        self._ps.add_policy_event(policy, PolicyEventsFactory.policy_rendered(rendered))

        return PolicyRead(**self._ps.get(policy.id).model_dump())

    def set_policy_variable(self, policy: Policy, name: str, value: PolicyVariableType|None) -> Policy:
        prev_value = policy.variables.get(name, None)
        self._ps.update_variable(policy, name, value)
        self._ps.add_policy_event(policy, PolicyEventsFactory.variable_set(name, prev_value, value))
        return PolicyRead(**self._ps.get(policy.id).model_dump())


    def process_set_policy_variable(self, policy: Policy, name: str, value: PolicyVariableType|None) -> Policy:
        
        # if we want to delete a variable that does not exist, raise an exception
        if not value and name not in policy.variables:
            raise PolicyVariableNotExist(f"Variable {name} not found")

        test_spec_rendering(policy, {name: value})
        
        _reactivate = False

        # 1. deactivate if active
        if policy.status.phase == PolicyPhase.Enforced or policy.status.phase == PolicyPhase.Violated:
            self.deactivate_policy(policy)
            _reactivate = True

        # 2. set variable
        policy = self.set_policy_variable(policy, name, value)


        # 3. re-render the policy
        policy = self.render_policy_spec(policy)

        # 4. reactivate if it was active
        if _reactivate:
            self.activate_policy(policy)

        return PolicyRead(**self._ps.get(policy.id).model_dump())

    def process_policy_create_request(
        self, policy: PolicyCreate, activate_created_policy=True
    ) -> PolicyRead:
        logger.debug("Received request: %s", policy)


        db_policy = Policy(**policy.model_dump(), id=str(uuid.uuid4()))
        db_policy = self._ps.insert(db_policy)

        self._ps.add_policy_event(db_policy, PolicyEventsFactory.policy_created())
        self._ps.set_policy_phase(db_policy, PolicyPhase.Inactive)

        db_policy = self.render_policy_spec(db_policy)

        if activate_created_policy:
            logger.debug("Activating policy because activate_created_policy=True")

            self.activate_policy(db_policy)

        # return updated object
        return PolicyRead(**self._ps.get(db_policy.id).model_dump())
