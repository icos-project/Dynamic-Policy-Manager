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


import pytest

from polman.common.config import APIConfig, AuthenticationConfig, ICOSConfig, PolmanConfig, PrometheusConfig
from polman.enforcer.main import PolmanEnforcer
from polman.registry.main import PolmanRegistry
from polman.watcher.main import PolmanWatcher


@pytest.fixture
def test_config():
  return PolmanConfig(
    api=APIConfig(),
    authn=AuthenticationConfig(
      server="http://localhost/",
      realm="fake"),
    prometheus=PrometheusConfig(),
    icos=ICOSConfig(job_manager_base_url='http://job-manager-url:8082'))

@pytest.fixture
def test_watcher(test_config, test_mongo_storage):
  return PolmanWatcher(test_config, test_mongo_storage, PolmanEnforcer(test_config))

@pytest.fixture
def test_registry(test_config, test_mongo_storage, test_watcher) -> PolmanRegistry:
  return  PolmanRegistry(test_config, test_mongo_storage, test_watcher)





