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

import pytest
from polman.common.model import Policy, PolicyAction, PolicyCreate, PolicySpec, PolicySpecTelemetry, PolicySubject, PolicySubjectApplication, PolicySubjectCustom, PolicySubjectHost
from polman.watcher.prometheus_rule_engine import subject_to_labels_dict, subject_to_labels_list, subject_to_labels_selector
from .utils import build

from pydantic_core._pydantic_core import ValidationError


s1 = build(PolicySubject, {'appName': 'test', 'appInstance': '111', 'appComponent': 'c1'})
s2 = build(PolicySubject, {'type': 'custom', 'appName': 'test', 'appInstance': '111', 'appComponent': 'c1'})
s3 = build(PolicySubject, {'hostId': 'host123', 'agentId': 'ag1'})
s4 = build(PolicySubject, {'appName': 'test', 'appComponent': 'c1'})

c1 = build(PolicySpec, {
    "expr": "sum by ({{subject_label_list}}) (compss_avgTime_ratio{CoreSignature=\"{{ compssTask }}\", {{subject_label_selector}}} * compss_pendTasks_ratio{CoreSignature=\"{{ compssTask }}\", {{subject_label_selector}}}) / sum by ({{subject_label_list}}) (compss_node_info{property=\"computing_units\", {{subject_label_selector}}}) / 1000",
    "violatedIf":  "> {{thresholdTimeSeconds}}",
    "thresholds": {
      "warning": 200,
      "critical": 500
    }})

a1 = build(PolicyAction, {
    "type": "webhook",
    "url": "https://ded8-94-33-209-155.ngrok-free.app/",
    "httpMethod": "POST",
  })

p1 = build(Policy, {
    "id": "1000",
    "name": "compss-low-performance-20",
    "subject": s1,
    "spec": c1,
    "variables": {
      "compssTask": "provesOtel.example_task",
      "thresholdTimeSeconds": "120"
    },
    "action": a1
  })


def test_subject(policy_c1):
  p2 = build(PolicyCreate, policy_c1)

  assert isinstance(s1, PolicySubjectApplication)
  assert isinstance(s2, PolicySubjectCustom)
  assert isinstance(s3, PolicySubjectHost)
  assert isinstance(s4, PolicySubjectCustom)
  
  with pytest.raises(ValidationError):
    build(PolicySubject, {'type': 'app', 'appName': 'test', 'appComponent': 'c1'})
    
  assert isinstance(p2.subject, PolicySubjectHost)
  
def test_spec():
  assert isinstance(c1, PolicySpecTelemetry)

def test_subject_to_label(policy_2_db):
  res = subject_to_labels_dict(policy_2_db.subject)
  
  assert len(res) == 3