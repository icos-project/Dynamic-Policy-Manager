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
import os
import pytest
import test
from polman.registry.icos.models import ICOSAppDeployedRequest
from test.utils import build


@pytest.fixture(scope="session")
def app_descriptor_all_yaml():
  with open(os.path.join(test.__path__[0], "data/app_descriptor_all.yaml")) as f:  # type: ignore
    return f.read() 

@pytest.fixture(scope="session")
def app_descriptor_1_yaml():
  with open(os.path.join(test.__path__[0], "data/app_descriptor_1.yaml")) as f:  # type: ignore
    return f.read() 


@pytest.fixture(scope="function")
def app_deployed_request_1_json(app_descriptor_1_yaml):
  return json.dumps({
    "app_instance": "demo-app",
    "common_action": {
      "uri": "/jobmanager/policies/incompliance/create",
      "http_method": "POST",
      "extra_params": {
        "customParam": "test-1"
      }
    },
    "service": "job-manager",
    "app_descriptor": app_descriptor_1_yaml
  })
  
@pytest.fixture(scope="function")
def app_deployed_request_2_json(app_descriptor_2_yaml):
  return json.dumps({
    "app_instance": "demo-app-002",
    "common_action": {
      "uri": "/jobmanager/policies/incompliance/create",
      "http_method": "POST",
      "extra_params": {
        "customParam": "test-1"
      }
    },
    "service": "job-manager",
    "app_descriptor": app_descriptor_2_yaml
  })

@pytest.fixture(scope="function")
def app_deployed_request_3_json(app_descriptor_3_yaml):
  return json.dumps({
    "app_instance": "demo-app-003",
    "common_action": {
      "uri": "/jobmanager/policies/incompliance/create",
      "http_method": "POST",
      "extra_params": {
        "customParam": "test-x"
      }
    },
    "service": "job-manager",
    "app_descriptor": app_descriptor_3_yaml
  })


@pytest.fixture(scope="function")
def app_deployed_request_1_model(app_deployed_request_1_json):
  return build(ICOSAppDeployedRequest, json.loads(app_deployed_request_1_json))

  
@pytest.fixture(scope="session")
def app_descriptor_compss_1_yaml():
  with open(os.path.join(test.__path__[0], "data/app_descriptor_compss_1.yaml")) as f:  # type: ignore
    return f.read() 
  
@pytest.fixture(scope="session")
def app_descriptor_compss_2_yaml():
  with open(os.path.join(test.__path__[0], "data/app_descriptor_compss_2.yaml")) as f:  # type: ignore
    return f.read() 

@pytest.fixture(scope="function")
def app_deployed_request_compss_1_json(app_descriptor_compss_1_yaml):
  return json.dumps({
    "app_instance": "demo-compss-aaa",
    "common_action": {
      "uri": "/jobmanager/policies/incompliance/create",
      "http_method": "POST"
    },
    "service": "job-manager",
    "app_descriptor": app_descriptor_compss_1_yaml
  })
  
@pytest.fixture(scope="function")
def app_deployed_request_compss_2_json(app_descriptor_compss_2_yaml):
  return json.dumps({
    "app_instance": "demo-compss-2-xxx",
    "common_action": {
      "uri": "/jobmanager/policies/incompliance/create",
      "http_method": "POST"
    },
    "service": "job-manager",
    "app_descriptor": app_descriptor_compss_2_yaml
  })