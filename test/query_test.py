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

from polman.common.model import PolicyCreate, PolicySubject
from polman.watcher.prometheus_rule_engine import get_telemetry_expr, subject_to_labels_list, subject_to_labels_selector
from .utils import build
from .models_test import p1 as p1_orig

s1 = build(PolicySubject, {'appName': 'test', 'appInstance': '111', 'appComponent': 'c1'})
s2 = build(PolicySubject, {'type': 'custom', 'appName': 'test', 'appInstance': '111', 'appComponent': 'c1'})
s3 = build(PolicySubject, {'hostId': 'host123', 'agentId': 'ag1'})
s4 = build(PolicySubject, {'appName': 'test', 'appComponent': '*', 'appInstance': '123'})
s5 = build(PolicySubject, {'appName': 'test', 'appComponent': '/comp-.+/', 'appInstance': '123'})
s6 = build(PolicySubject, {'appName': '/test|foo/', 'appComponent': '/^component-\d\d$/', 'appInstance': '123'})
s7 = build(PolicySubject, {'appName': '/test/', 'appComponent': '^component-\d\d$', 'appInstance': '1\d\d'})

def test_subject_labels_selector():
  r = subject_to_labels_selector(s1)
  assert r == 'icos_app_component="c1", icos_app_instance="111", icos_app_name="test"'
  
  r = subject_to_labels_selector(s2)
  assert r == 'icos_app_component="c1", icos_app_instance="111", icos_app_name="test"'
  
  r = subject_to_labels_selector(s3)
  assert r == 'icos_agent_id="ag1", icos_host_id="host123"'
  
  r = subject_to_labels_selector(s4)
  assert r == 'icos_app_component=~".+", icos_app_instance="123", icos_app_name="test"'
  
  r = subject_to_labels_selector(s5)
  assert r == 'icos_app_component=~"comp-.+", icos_app_instance="123", icos_app_name="test"'
  
  r = subject_to_labels_selector(s6)
  assert r == 'icos_app_component=~"^component-\d\d$", icos_app_instance="123", icos_app_name=~"test|foo"'
  
  r = subject_to_labels_selector(s7)
  assert r == 'icos_app_component="^component-\d\d$", icos_app_instance="1\d\d", icos_app_name=~"test"'
  
def test_subject_labels_list():
  r = subject_to_labels_list(s1)
  assert r == 'icos_app_component, icos_app_instance, icos_app_name'

  r = subject_to_labels_list(s2)
  assert r == 'icos_app_component, icos_app_instance, icos_app_name'

  r = subject_to_labels_list(s3)
  assert r == 'icos_agent_id, icos_host_id'

  r = subject_to_labels_list(s2)
  assert r == 'icos_app_component, icos_app_instance, icos_app_name'


def test_query_expansion(policy_c1):
  
  p1 = p1_orig.model_copy()
  
  p1.subject = s1
  q = get_telemetry_expr(p1)
  assert q == 'sum by (icos_app_component, icos_app_instance, icos_app_name) (compss_avgTime_ratio{CoreSignature="provesOtel.example_task", icos_app_component="c1", icos_app_instance="111", icos_app_name="test"} * compss_pendTasks_ratio{CoreSignature="provesOtel.example_task", icos_app_component="c1", icos_app_instance="111", icos_app_name="test"}) / sum by (icos_app_component, icos_app_instance, icos_app_name) (compss_node_info{property="computing_units", icos_app_component="c1", icos_app_instance="111", icos_app_name="test"}) / 1000 > 120'

  p1.subject = s2
  q = get_telemetry_expr(p1)
  assert q == 'sum by (icos_app_component, icos_app_instance, icos_app_name) (compss_avgTime_ratio{CoreSignature="provesOtel.example_task", icos_app_component="c1", icos_app_instance="111", icos_app_name="test"} * compss_pendTasks_ratio{CoreSignature="provesOtel.example_task", icos_app_component="c1", icos_app_instance="111", icos_app_name="test"}) / sum by (icos_app_component, icos_app_instance, icos_app_name) (compss_node_info{property="computing_units", icos_app_component="c1", icos_app_instance="111", icos_app_name="test"}) / 1000 > 120'

  p1.subject = s4
  q = get_telemetry_expr(p1)
  assert q == 'sum by (icos_app_component, icos_app_instance, icos_app_name) (compss_avgTime_ratio{CoreSignature="provesOtel.example_task", icos_app_component=~".+", icos_app_instance="123", icos_app_name="test"} * compss_pendTasks_ratio{CoreSignature="provesOtel.example_task", icos_app_component=~".+", icos_app_instance="123", icos_app_name="test"}) / sum by (icos_app_component, icos_app_instance, icos_app_name) (compss_node_info{property="computing_units", icos_app_component=~".+", icos_app_instance="123", icos_app_name="test"}) / 1000 > 120'

  p1.subject = s7
  q = get_telemetry_expr(p1)
  assert q == 'sum by (icos_app_component, icos_app_instance, icos_app_name) (compss_avgTime_ratio{CoreSignature="provesOtel.example_task", icos_app_component="^component-\d\d$", icos_app_instance="1\d\d", icos_app_name=~"test"} * compss_pendTasks_ratio{CoreSignature="provesOtel.example_task", icos_app_component="^component-\d\d$", icos_app_instance="1\d\d", icos_app_name=~"test"}) / sum by (icos_app_component, icos_app_instance, icos_app_name) (compss_node_info{property="computing_units", icos_app_component="^component-\d\d$", icos_app_instance="1\d\d", icos_app_name=~"test"}) / 1000 > 120'


  p2 = build(PolicyCreate, policy_c1)

  q2 = get_telemetry_expr(p2)
  assert q2 == 'avg without (mode,cpu) (1 - rate(node_cpu_seconds_total{mode="idle", icos_agent_id="icos-agent-1", icos_host_id=~".+"}[2m])) > 0.8'
