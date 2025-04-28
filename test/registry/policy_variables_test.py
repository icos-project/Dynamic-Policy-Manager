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

from polman.common.model import PolicyEventType, PolicyPhase, PolicySpecTelemetry
from polman.registry.main import PolmanRegistry
from polman.watcher.prometheus_rule_engine import PrometheusRuleEngine

def test_policy_deactivated(test_registry: PolmanRegistry, policy_2_create):
  
  # compssTask: "provesOtel.example_task",
  # thresholdTimeSeconds": "120"
  
  p2 = test_registry.process_policy_create_request(policy_2_create, activate_created_policy=False)

  renderedExpr_1 = 'sum by (icos_app_instance, icos_app_component, icos_app_name) (compss_avgTime_ratio{CoreSignature="provesOtel.example_task", icos_app_name="compss-example-app", icos_app_instance="compss-example-app-002", icos_app_component="component1"} * compss_pendTasks_ratio{CoreSignature="provesOtel.example_task", icos_app_name="compss-example-app", icos_app_instance="compss-example-app-002", icos_app_component="component1"}) / sum by (icos_app_instance, icos_app_component, icos_app_name) (compss_node_info{property="computing_units", icos_app_name="compss-example-app", icos_app_instance="compss-example-app-002", icos_app_component="component1"}) > 120'
  renderedExpr_2 = 'sum by (icos_app_instance, icos_app_component, icos_app_name) (compss_avgTime_ratio{CoreSignature="provesOtel.example_task", icos_app_name="compss-example-app", icos_app_instance="compss-example-app-002", icos_app_component="component1"} * compss_pendTasks_ratio{CoreSignature="provesOtel.example_task", icos_app_name="compss-example-app", icos_app_instance="compss-example-app-002", icos_app_component="component1"}) / sum by (icos_app_instance, icos_app_component, icos_app_name) (compss_node_info{property="computing_units", icos_app_name="compss-example-app", icos_app_instance="compss-example-app-002", icos_app_component="component1"}) > 800'
  renderedExpr_3 = 'sum by (icos_app_instance, icos_app_component, icos_app_name) (compss_avgTime_ratio{CoreSignature="provesOtel.test123_task", icos_app_name="compss-example-app", icos_app_instance="compss-example-app-002", icos_app_component="component1"} * compss_pendTasks_ratio{CoreSignature="provesOtel.test123_task", icos_app_name="compss-example-app", icos_app_instance="compss-example-app-002", icos_app_component="component1"}) / sum by (icos_app_instance, icos_app_component, icos_app_name) (compss_node_info{property="computing_units", icos_app_name="compss-example-app", icos_app_instance="compss-example-app-002", icos_app_component="component1"}) > 800'

  assert type(p2.status.renderedSpec) == PolicySpecTelemetry
  assert p2.status.renderedSpec.expr == renderedExpr_1

  p2 = test_registry.process_set_policy_variable(p2, "thresholdTimeSeconds", 800)

  assert type(p2.status.renderedSpec) == PolicySpecTelemetry
  assert p2.status.renderedSpec.expr == renderedExpr_2


  p2 = test_registry.process_set_policy_variable(p2, "compssTask", "provesOtel.test123_task")

  assert type(p2.status.renderedSpec) == PolicySpecTelemetry
  assert p2.status.renderedSpec.expr == renderedExpr_3




def test_policy_active(mocker: MockerFixture, test_registry: PolmanRegistry, policy_1_create):

  m1 = mocker.patch.object(PrometheusRuleEngine, "add_rule", return_value="test-rule.yml")
  m2 = mocker.patch.object(PrometheusRuleEngine, "delete_rule", return_value="test-rule.yml")

  # maxCpu: 0.8

  renderedExpr_1 = 'avg without (mode,cpu) (1 - rate(node_cpu_seconds_total{mode="idle", icos_agent_id="icos-agent-1", icos_host_id=~".+" }[2m])) > 0.8'
  renderedExpr_2 = 'avg without (mode,cpu) (1 - rate(node_cpu_seconds_total{mode="idle", icos_agent_id="icos-agent-1", icos_host_id=~".+" }[2m])) > 0.6'

  p1 = test_registry.process_policy_create_request(policy_1_create, activate_created_policy=True)


  assert type(p1.status.renderedSpec) == PolicySpecTelemetry
  assert p1.status.renderedSpec.expr == renderedExpr_1
  assert p1.status.phase == PolicyPhase.Enforced

  p1 = test_registry.process_set_policy_variable(p1, "maxCpu", 0.6)

  assert type(p1.status.renderedSpec) == PolicySpecTelemetry
  assert p1.status.renderedSpec.expr == renderedExpr_2
  assert p1.status.phase == PolicyPhase.Enforced

  # check that the policy has been first deactivated, then rendered and finally reactivated
  assert [p.type for p in p1.status.events] == [
    PolicyEventType.Created,
    PolicyEventType.Rendered,
    PolicyEventType.Activated,
    PolicyEventType.Deactivated,
    PolicyEventType.VariableSet,
    PolicyEventType.Rendered,
    PolicyEventType.Activated
    ]


def test_variable_set_events(test_registry: PolmanRegistry, policy_1_create):
  p1 = test_registry.process_policy_create_request(policy_1_create, activate_created_policy=False)
  
  p1 = test_registry.process_set_policy_variable(p1, "maxCpu", 0.6)

  assert p1.status.events[-2].type == PolicyEventType.VariableSet
  assert p1.status.events[-2].details == {'name': 'maxCpu', 'newValue': 0.6, 'previousValue': 0.8}

  p1 = test_registry.process_set_policy_variable(p1, "newVar", "testVal")
  assert p1.status.events[-2].type == PolicyEventType.VariableSet
  assert p1.status.events[-2].details == {'name': "newVar", 'newValue': "testVal", 'previousValue': None}
  assert p1.variables["newVar"] == "testVal"

  p1 = test_registry.process_set_policy_variable(p1, "newVar", "newVAL")
  assert p1.status.events[-2].type == PolicyEventType.VariableSet
  assert p1.status.events[-2].details == {'name': "newVar", 'newValue': "newVAL", 'previousValue': "testVal"}
  assert p1.variables["newVar"] == "newVAL"

  p1 = test_registry.process_set_policy_variable(p1, "newVar", None)
  assert p1.status.events[-2].type == PolicyEventType.VariableSet
  assert p1.status.events[-2].details == {'name': "newVar", 'newValue': None, 'previousValue': "newVAL"}
  assert "newVar" not in p1.variables