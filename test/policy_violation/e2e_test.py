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

import requests
from polman.common.model import PolicyEventType, PolicyPhase
from test.utils import get_storage_from_http_client


def test_policy_creation_violation_resolve(policy_cpu144_dict, policy_cpu144_alerts_dict, policy_cpu144_resolve_dict, mocker, test_http_client_mongo):

  # 1. Create Policy 
  response = test_http_client_mongo.post("/polman/registry/api/v1/policies", json=policy_cpu144_dict)
  
  assert response.status_code == 200
  storage = get_storage_from_http_client(test_http_client_mongo)
  assert len(storage.list()) == 1
  
  p = storage.get(response.json()["id"])
  
  print(p.id)
  
  assert p.status.phase == PolicyPhase.Enforced
  
  # 2. Send Alert
  # setup a mock to requests.post to intercept the webhook sending
  res = requests.Response()
  setattr(res, "status_code", 200)
  m = mocker.patch.object(requests, "post", return_value=res)
  test_http_client_mongo.post("polman/watcher/api/v1/webhooks/alertmanager", json=policy_cpu144_alerts_dict(p.id))
  
  # ensure that a webhook has been sent
  assert len(m.mock_calls) == 1
  
  # ensure status is violated
  p = storage.get(response.json()["id"])
  assert p.status.phase == PolicyPhase.Violated
  
  # ensure event violation created
  assert p.status.events[len(p.status.events) - 1].type == PolicyEventType.Violated
  
  # 3. Send Resolve
  test_http_client_mongo.post("polman/watcher/api/v1/webhooks/alertmanager", json=policy_cpu144_resolve_dict(p.id))

  # ensure status is enforced
  p = storage.get(response.json()["id"])
  assert p.status.events[len(p.status.events) - 1].type == PolicyEventType.Resolved
  assert p.status.phase == PolicyPhase.Enforced