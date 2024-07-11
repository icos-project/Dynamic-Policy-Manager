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

from test.utils import get_storage_from_http_client


def test_get_existing_policy(test_http_client, test_policy_factory):
    
  person_instance = test_policy_factory.build()

  get_storage_from_http_client(test_http_client).insert(person_instance)
  
  response = test_http_client.get(f'/polman/registry/api/v1/policies/{person_instance.id}')
  assert response.status_code == 200
  assert response.json()['name'] == person_instance.name
  
  
def test_get_not_existing_policy(test_http_client):
  response = test_http_client.get('/polman/registry/api/v1/policies/123')
  assert response.status_code == 404