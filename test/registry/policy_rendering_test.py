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



from polman.registry.render import render_policy


def test_policy_3_rendering(policy_3_create):

  rendered = render_policy(policy_3_create)

  assert rendered.spec.expr == 'tlum_workload_info{ icos_app_component="component1", icos_app_instance="compss-example-app-002", icos_app_name="compss-example-app" } *on(icos_host_id) group_left avg without (cpu) (1 - rate(node_cpu_seconds_total{mode="idle"}[2m])) > 0.8'  
  
      

  