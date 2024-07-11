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

from test.utils import get_registry_from_http_client


def test_status_page(test_http_client_mongo, policy_create_1):
  reg = get_registry_from_http_client(test_http_client_mongo)
  p = reg.process_policy_create_request(policy_create_1, activate_created_policy=False)
  
  response = test_http_client_mongo.get("/polman/status")
 
  assert response.status_code == 200
  assert f'<a href=#{p.id}' in response.text