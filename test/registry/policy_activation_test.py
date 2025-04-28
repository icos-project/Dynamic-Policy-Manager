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

from pytest_mock import MockerFixture
from polman.common.model import Policy, PolicyEventType, PolicyPhase, PolicySubjectApplication
from polman.registry.main import PolmanRegistry
from polman.watcher.prometheus_rule_engine import PrometheusRuleEngine

def test_policy_list(mocker: MockerFixture, test_registry: PolmanRegistry, policy_1_create, policy_2_create, policy_3_create, policy_4_create):
 
  m1 = mocker.patch.object(PrometheusRuleEngine, "add_rule", return_value="test-rule.yml")
  m2 = mocker.patch.object(PrometheusRuleEngine, "delete_rule", return_value="test-rule.yml")
  
  p1 = test_registry.process_policy_create_request(policy_1_create, activate_created_policy=False)
  assert test_registry.get_policy_by_id(p1.id).status.phase == PolicyPhase.Inactive
  
  test_registry.activate_policy(p1)
  rp: Policy = test_registry.get_policy_by_id(p1.id)
  assert rp.status.phase == PolicyPhase.Enforced
  assert len(rp.status.events) == 3
  assert rp.status.events[-1].type == PolicyEventType.Activated

  test_registry.deactivate_policy(rp)
  rp: Policy = test_registry.get_policy_by_id(p1.id)
  assert rp.status.phase == PolicyPhase.Inactive
  assert len(rp.status.events) == 4
  assert rp.status.events[-1].type == PolicyEventType.Deactivated
