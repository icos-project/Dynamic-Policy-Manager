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
import pytest


@pytest.fixture(scope="function")
def app_create_event_compss_1_json(app_descriptor_compss_1_yaml):
  return json.dumps({
    "event": "created",
    "app_instance": "demo-compss-1-xxx",
    "callback": {
      "uri": "/jobmanager/policies/incompliance/create",
      "http_method": "POST"
    },
    "service": "job-manager",
    "app_descriptor": app_descriptor_compss_1_yaml
  })

@pytest.fixture(scope="function")
def app_start_compss_1_json():
  return json.dumps({
    "event": "started",
    "app_instance": "demo-compss-1-xxx",
    "service": "job-manager",
  })

@pytest.fixture(scope="function")
def app_create_event_compss_2_json(app_descriptor_compss_2_yaml):
  return json.dumps({
    "event": "created",
    "app_instance": "demo-compss-2-xxx",
    "callback": {
      "uri": "/jobmanager/policies/incompliance/create",
      "http_method": "POST"
    },
    "service": "job-manager",
    "app_descriptor": app_descriptor_compss_2_yaml
  })

@pytest.fixture(scope="function")
def app_start_compss_2_json():
  return json.dumps({
    "event": "started",
    "app_instance": "demo-compss-2-xxx",
    "service": "job-manager",
  })


@pytest.fixture(scope="function")
def app_stop_compss_2_json():
  return json.dumps({
    "event": "stopped",
    "app_instance": "demo-compss-2-xxx",
    "service": "job-manager",
  })

@pytest.fixture(scope="function")
def app_delete_compss_2_json():
  return json.dumps({
    "event": "deleted",
    "app_instance": "demo-compss-2-xxx",
    "service": "job-manager",
  })