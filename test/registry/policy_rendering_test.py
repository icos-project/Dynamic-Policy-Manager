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

from polman.common.model import PolicyCreate, PolicySpecTelemetry
from polman.registry.render import render_policy_spec
from pytest_mock import MockerFixture
from polman.common.model import Policy, PolicyEventType, PolicyPhase, PolicySubjectApplication
from polman.registry.main import PolmanRegistry
from polman.watcher.prometheus_rule_engine import PrometheusRuleEngine

def test_policy_3_rendering(policy_3_create):
    rendered_spec = render_policy_spec(policy_3_create)

    assert (
        isinstance(rendered_spec, PolicySpecTelemetry) and rendered_spec.expr
        == 'tlum_workload_info{ icos_app_component="component1", icos_app_instance="compss-example-app-002", icos_app_name="compss-example-app" } *on(icos_host_id) group_left avg without (cpu) (1 - rate(node_cpu_seconds_total{mode="idle"}[2m])) > 0.8'
    )

def test_policy_list(mocker: MockerFixture, test_registry: PolmanRegistry, policy_1_create, policy_2_create, policy_3_create, policy_4_create):
  
  p1 = test_registry.process_policy_create_request(policy_1_create, activate_created_policy=False)
  assert test_registry.get_policy_by_id(p1.id).status.phase == PolicyPhase.Inactive
  rp: Policy = test_registry.get_policy_by_id(p1.id)
  assert rp.status.phase == PolicyPhase.Inactive

  assert type(rp.status.renderedSpec) == PolicySpecTelemetry
  assert rp.status.renderedSpec.expr == 'avg without (mode,cpu) (1 - rate(node_cpu_seconds_total{mode="idle", icos_agent_id="icos-agent-1", icos_host_id=~".+" }[2m])) > 0.8'




def test_render_during_creation(policy_app_container_cpu_create: PolicyCreate) -> None:
    """Test rendering of app_container_cpu policy."""
    p = render_policy_spec(policy_app_container_cpu_create)
