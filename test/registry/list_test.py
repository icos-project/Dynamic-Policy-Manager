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


def test_policy_list(test_registry, policy_2_create, policy_3_create):
  
  p1 = test_registry.process_policy_create_request(policy_2_create, activate_created_policy=False)
  p2 = test_registry.process_policy_create_request(policy_3_create, activate_created_policy=False)

  assert len(test_registry._ps.list()) == 2
  
  policies_asc = test_registry.list_all_policies(sort_by="creation_time", order="asc")
  
  assert policies_asc[0].id == p1.id
  

  policies_desc = test_registry.list_all_policies(sort_by="creation_time", order="desc")
  
  assert policies_desc[0].id == p2.id
  