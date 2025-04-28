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

from polman.common.model import PolicySpec, PolicyVariableType
from polman.common.errors import PolicyNotFoundError
from polman.common.model import Policy, PolicyEvent, PolicyPhase, Violation
from polman.common.service import PolmanService

logger = logging.getLogger(__name__)


class PolmanStorageBackend:

    @abstractmethod
    def insert(self, policy: Policy) -> Policy:
        pass

    @abstractmethod
    def get(self, policy_id: str) -> Policy:
        pass

    @abstractmethod
    def list(self, filters={}) -> list[Policy]:
        pass

    @abstractmethod
    def delete(self, policy_id: str) -> Policy:
        pass

    @abstractmethod
    def add_policy_event(self, policy_id: str, event: PolicyEvent) -> None:
        pass

    @abstractmethod
    def set_policy_phase(self, policy_id: str, phase: PolicyPhase) -> None:
        pass

    @abstractmethod
    def update_measurement_backend(self, policy_id: str, name: str, status: dict) -> None:
        pass

    @abstractmethod
    def delete_measurement_backend(self, policy_id: str, name: str) -> None:
        """Delete a measurement backend status."""

    @abstractmethod
    def set_rendered_spec(self, policy_id: str, spec: PolicySpec) -> None:
        ...

    @abstractmethod
    def set_variable(self, policy_id: str, name: str, value: PolicyVariableType|None) -> None:
        ...