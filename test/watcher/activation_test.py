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

# ruff: noqa: S101

"""Tests for the PolmanWatcher."""

from pytest_mock import MockerFixture

from polman.common.model import Policy, PolicyPhase
from polman.storage.backend.mongo import MongodbPolicyStore, PolicyDB
from polman.storage.main import PolmanStorage
from polman.watcher.main import PolmanWatcher
from polman.watcher.prometheus_rule_engine import PrometheusRuleEngine


def test_policy_activation(
    policy_2_db: PolicyDB, test_storage_with_mongo_backend: PolmanStorage,
    test_watcher: PolmanWatcher,
    mocker: MockerFixture
) -> None:
    """Test the activation and de-activation of policies."""
    m1 = mocker.patch.object(PrometheusRuleEngine, "add_rule", return_value="test-rule.yml")
    m2 = mocker.patch.object(PrometheusRuleEngine, "delete_rule", return_value="test-rule.yml")

    p = test_storage_with_mongo_backend.insert(policy_2_db)
    assert len(test_storage_with_mongo_backend.list()) == 1

    test_watcher.set_measurement_backends(p)
    p: Policy = test_storage_with_mongo_backend.get(p.id)
    m1.assert_called_once()
    assert "prom-1" in p.status.measurementBackends

    test_watcher.unset_measurement_backends(p)
    p = test_storage_with_mongo_backend.get(p.id)
    m2.assert_called_once()
    assert "prom-1" not in p.status.measurementBackends
