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

from http import HTTPMethod
import json

from polman.common.model import PolicyActionWebhook
from polman.registry.icos.process_app_descriptor import process_app_descriptor
from polman.watcher.prometheus_rule_engine import PrometheusRuleEngine
from test.utils import get_storage_from_http_client


def test_post_icos_app_descriptor_compss_2(test_http_client_mongo, app_deployed_request_compss_2_json, mocker):
 
  response = test_http_client_mongo.post('/polman/registry/api/v1/icos/', json=json.loads(app_deployed_request_compss_2_json))
  assert response.status_code == 200
  assert len(response.json()) == 1

def test_post_icos_app_descriptor_compss_1(test_http_client_mongo, app_deployed_request_compss_1_json, mocker):
 
  print(app_deployed_request_compss_1_json)
  response = test_http_client_mongo.post('/polman/registry/api/v1/icos/', json=json.loads(app_deployed_request_compss_1_json))
  assert response.status_code == 200
  assert len(response.json()) == 1
  
  #p = test_mongo_storage.list()[0]
  
  #assert p.name == 'mjpeg-ffmpeg-app-demo-app-002-policy-0'
  

  
def test_post_icos_app_descriptor_2(test_http_client_mongo, app_deployed_request_2_json, test_mongo_storage, mocker):
  
  response = test_http_client_mongo.post('/polman/registry/api/v1/icos/', json=json.loads(app_deployed_request_2_json))
  assert response.status_code == 200
  assert len(response.json()) == 1
  
  p = test_mongo_storage.list()[0]
  
  assert p.name == 'mjpeg-ffmpeg-app-demo-app-002-policy-0'
  


def test_post_icos_unknown_bad_action(test_http_client, app_deployed_request_1_json, mocker):
  
  new_app_deployment = app_deployed_request_1_json.replace("job-manager", "not-existing-service")

  response = test_http_client.post('/polman/registry/api/v1/icos/', json=json.loads(new_app_deployment))
  assert response.status_code == 500
  assert response.json()['detail'] == "Unknown service name in action: 'not-existing-service'"
  


def test_post_icos(test_http_client, app_deployed_request_1_json, mocker):

  mocker.patch.object(PrometheusRuleEngine, "add_rule", return_value="test-rule.yml")
      
  response = test_http_client.post('/polman/registry/api/v1/icos/', json=json.loads(app_deployed_request_1_json))
  assert response.status_code == 200
  assert len(response.json()) == 3
     
  for p in get_storage_from_http_client(test_http_client).list():
    
    assert p.action.url == 'http://job-manager-url:8082/jobmanager/policies/incompliance/create'
    assert p.action.extraParams['customParam'] == "test-1"
    
    if p.name == 'policy1':
      assert p.subject.appComponent == '*'
      assert p.action.extraParams['remediation'] == 'scale-up'

    if p.name == 'policyInside1':
      assert p.subject.appComponent == 'ffmpeg'
      assert p.spec.expr.startswith("sum by (icos_app_component, icos_app_instance, icos_app_name) ")
      assert p.action.extraParams['remediation'] == 'scale-down'
      assert p.action.extraParams['customParam'] == 'test-1'

def test_icos_app_descriptor(app_deployed_request_1_model):
  
  ps = process_app_descriptor(app_deployed_request_1_model.app_descriptor, app_deployed_request_1_model.app_instance, PolicyActionWebhook(url='http://localhost:1234/', httpMethod=HTTPMethod.GET))
    
  assert len(ps) == 3
  
  for p in ps:
    if p.name == 'policy1':
      assert p.subject.appComponent == '*'
      assert p.action.extraParams['remediation'] == 'scale-up'

    if p.name == 'policyInside1':
      assert p.subject.appComponent == 'ffmpeg'
      assert p.spec.templateName == 'compss-under-allocation'
