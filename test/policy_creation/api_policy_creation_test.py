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

from polman.common.model import PolicyEventType, PolicyPhase
from polman.watcher.prometheus_rule_engine import PrometheusRuleEngine
from test.utils import get_storage_from_http_client
  
def test_create_policies(mocker, test_http_client_mongo, policy_c1):

  response = test_http_client_mongo.post("/polman/registry/api/v1/policies", json=policy_c1)
  
  # test response code
  assert response.status_code == 200
  
  # test response is the json we expect
  assert response.json()["name"] == "cpu_usage-for-agent"
  assert response.json()["status"]["measurementBackends"]["prom-1"]["rule_file"] == 'test-rule.yml'
  
  storage = get_storage_from_http_client(test_http_client_mongo)
  # test we have exactly one policy in the storage
  assert len(storage.list()) == 1
  
  # get the policy from the storage
  p = storage.get(response.json()["id"])
  
  # test events
  assert len(p.status.events) == 2
  assert p.status.events[0].type == PolicyEventType.Created
  # true because currently we activate the policy when we create them
  assert p.status.events[1].type == PolicyEventType.Activated


def test_create_policy_no_activation(mocker, test_http_client_mongo, policy_c1):

  response = test_http_client_mongo.post("/polman/registry/api/v1/policies?do_not_activate=True", json=policy_c1)

  storage = get_storage_from_http_client(test_http_client_mongo)
  p = storage.get(response.json()["id"])
  
  # test events
  assert len(p.status.events) == 1
  assert p.status.phase == PolicyPhase.Inactive
  
def test_unprocessable_policy(mocker, test_http_client, policy_c1):
  
  del policy_c1['subject']
  
  mocker.patch.object(PrometheusRuleEngine, "add_rule", return_value="test-rule.yml")

  response = test_http_client.post("/polman/registry/api/v1/policies", json=policy_c1)
  assert response.status_code == 422
  assert response.json()['status_code'] == 422
  response.json()['detail'][0]['type'] == "missing"
  response.json()['detail'][0]['loc'][1] == "subject"
