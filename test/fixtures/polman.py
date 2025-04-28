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

import pytest

from pydantic import SecretStr
from polman.common.config import APIConfig, AuthenticationConfig, ICOSConfig, PolmanConfig, PrometheusConfig
from polman.enforcer.main import PolmanEnforcer
from polman.meter.main import PolmanMeter
from polman.registry.main import PolmanRegistry
from polman.storage.main import PolmanStorage
from polman.watcher.main import PolmanWatcher


@pytest.fixture
def test_config():
  return PolmanConfig(
    api=APIConfig(enable_debug_calls=True),
    authn=AuthenticationConfig(
      server="http://localhost/",
      realm="fake",
      client_secret=SecretStr("fake")),
    prometheus=PrometheusConfig(rules_api_url="http://localhost"),
    icos=ICOSConfig(job_manager_base_url='http://job-manager-url:8082'))

@pytest.fixture
def test_watcher(test_config, test_storage_with_mongo_backend) -> PolmanWatcher:
  return PolmanWatcher(test_config, test_storage_with_mongo_backend, PolmanEnforcer(test_config))


@pytest.fixture
def test_storage_with_mongo_backend(test_config, test_mongo_backend):
  return PolmanStorage(test_config, PolmanMeter(), backend=test_mongo_backend)


@pytest.fixture
def test_storage_with_in_memory_backend(test_config, test_in_memory_backend):
  return PolmanStorage(test_config, PolmanMeter(), backend=test_in_memory_backend)

@pytest.fixture
def test_registry(test_config, test_storage_with_mongo_backend, test_watcher) -> PolmanRegistry:
  return  PolmanRegistry(test_config, test_storage_with_mongo_backend, test_watcher)




