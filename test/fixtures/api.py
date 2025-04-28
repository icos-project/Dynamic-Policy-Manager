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

from fastapi.testclient import TestClient
import pytest
from polman.api.main import PolmanApi
from polman.common.api import get_authorized_user

from polman.common.model import User
from polman.enforcer.main import PolmanEnforcer
from polman.registry.main import PolmanRegistry
from polman.watcher.main import PolmanWatcher
from polman.watcher.prometheus_rule_engine import PrometheusRuleEngine

async def get_authorized_user_override():
  return User(name="John", username="Doe", email="john.doe@acme.com", scopes=[])


@pytest.fixture
def test_http_client(test_config, test_storage_with_in_memory_backend):
    watcher = PolmanWatcher(test_config, test_storage_with_in_memory_backend, PolmanEnforcer(test_config))
    api = PolmanApi(test_config, PolmanRegistry(test_config, test_storage_with_in_memory_backend, watcher), watcher)
    api.app.routes[0].app.dependency_overrides[get_authorized_user] = get_authorized_user_override  # type: ignore
    return TestClient(api.app)


@pytest.fixture
def test_http_client_mongo(test_config, test_storage_with_mongo_backend, mocker):
  watcher = PolmanWatcher(test_config, test_storage_with_mongo_backend, PolmanEnforcer(test_config))
  api = PolmanApi(test_config, PolmanRegistry(test_config, test_storage_with_mongo_backend, watcher), watcher)
  api.app.routes[0].app.dependency_overrides[get_authorized_user] = get_authorized_user_override  # type: ignore
   
  mocker.patch.object(PrometheusRuleEngine, "add_rule", return_value="test-rule.yml")
  mocker.patch.object(PrometheusRuleEngine, "delete_rule", return_value="test-rule.yml")

  return TestClient(api.app)