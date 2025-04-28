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

import json
import logging

from polman.common.errors import PolicyNotFoundError
from polman.common.model import Policy, PolicyEvent, PolicyPhase, PolicySpec, PolicyVariableType
from .memory import InMemoryPolmanStorage

logger = logging.getLogger(__name__)


class FilePolmanStorage(InMemoryPolmanStorage):
    def __init__(self, config) -> None:
        super().__init__(config)

        self._file = config.db.url
        self._read_from_file()

    def _read_from_file(self):
        with open(self._file, "r") as infile:
            json_list = json.load(infile)
            models = [Policy.model_validate(o) for o in json_list]
            self._store = {m.id: m for m in models}

    def _write_to_file(self):
        models = list(self._store.values())
        json_list = [m.model_dump(mode="json") for m in models]
        with open(self._file, "w") as outfile:
            json.dump(json_list, outfile)

    def insert(self, policy: Policy) -> Policy:
        res = super().insert(policy)
        self._write_to_file()
        return res

    def get(self, policy_id: str) -> Policy:
        return super().get(policy_id)

    def list(self, filters={}) -> list[Policy]:
        return super().list(filters=filters)

    def delete(self, policy_id: str) -> Policy:
        res = super().delete(policy_id)
        self._write_to_file()
        return res     

    def add_policy_event(self, policy_id: str, event: PolicyEvent) -> None:
        super().add_policy_event(policy_id, event)
        self._write_to_file()

    def set_policy_phase(self, policy_id: str, phase: PolicyPhase) -> None:
        super().set_policy_phase(policy_id, phase)
        self._write_to_file()

    def update_measurement_backend(self, policy_id: str, name: str, status: dict) -> None:
        super().update_measurement_backend(policy_id, name, status)
        self._write_to_file()

    def delete_measurement_backend(self, policy_id: str, name: str) -> None:
        super().delete_measurement_backend(policy_id, name)
        self._write_to_file()

    def set_rendered_spec(self, policy_id: str, spec: PolicySpec) -> None:
        super().set_rendered_spec(policy_id, spec)
        self._write_to_file()

    def set_variable(self, policy_id: str, name: str, value: PolicyVariableType|None) -> None:
        super().set_variable(policy_id, name, value)
        self._write_to_file()