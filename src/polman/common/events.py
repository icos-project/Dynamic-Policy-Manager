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

import datetime

from polman.common.model import PolicyVariableType, PolicyEvent, PolicyEventType, PolicySpec, Violation


class PolicyEventsFactory:
    @staticmethod
    def policy_created():
        return PolicyEvent(type=PolicyEventType.Created, timestamp=datetime.datetime.now())

    @staticmethod
    def policy_activated():
        return PolicyEvent(type=PolicyEventType.Activated, timestamp=datetime.datetime.now())

    @staticmethod
    def policy_deactivated():
        return PolicyEvent(type=PolicyEventType.Deactivated, timestamp=datetime.datetime.now())

    @staticmethod
    def policy_rendered(renderedSpec: PolicySpec):
        return PolicyEvent(
            type=PolicyEventType.Rendered,
            timestamp=datetime.datetime.now(),
            details={
                "renderedSpec": str(renderedSpec.model_dump())
            })

    @staticmethod
    def policy_rendering_error(orig_spec: PolicySpec, error: str):
        return PolicyEvent(
            type=PolicyEventType.RenderingError,
            timestamp=datetime.datetime.now(),
            details={
                "spec": str(orig_spec.model_dump()),
                "error": error
            })


    @staticmethod
    def variable_set(name: str, previousValue: PolicyVariableType|None, newValue: PolicyVariableType|None):
        return PolicyEvent(
            type=PolicyEventType.VariableSet,
            timestamp=datetime.datetime.now(),
            details={
                "name": name, "previousValue": previousValue, "newValue": newValue
            })

    @staticmethod
    def policy_violated(violation: Violation):
        return PolicyEvent(
            type=PolicyEventType.Violated,
            timestamp=datetime.datetime.now(),
            details={
                "id": violation.id,
                "currentValue": violation.currentValue,
                "threshold": violation.threshold,
                "extraLabels": violation.extraLabels,
            },
        )

    @staticmethod
    def policy_resolved():
        return PolicyEvent(type=PolicyEventType.Resolved, timestamp=datetime.datetime.now())
