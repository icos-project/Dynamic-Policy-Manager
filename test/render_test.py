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

import unittest
from polman.common.model import Policy, PolicyAction, PolicySpec, PolicySubject
from polman.registry.render import render_policy
from .utils import build



class TestSubject(unittest.TestCase):
  

    s1 = build(PolicySubject, {'appName': 'test', 'appInstance': '111', 'appComponent': 'c1'})
    s3 = build(PolicySubject, {'hostId': 'host123', 'agentId': 'ag1'})
  
    c1 = build(PolicySpec, {
      "expr": "sum by ({{subject_label_list}}) (compss_avgTime_ratio{CoreSignature=\"{{ compssTask }}\", {{subject_label_selector}}} * compss_pendTasks_ratio{CoreSignature=\"{{ compssTask }}\", {{subject_label_selector}}}) / sum by ({{subject_label_list}}) (compss_node_info{property=\"computing_units\", {{subject_label_selector}}}) / 1000",
      "violatedIf":  "> {{thresholdTimeSeconds}}",
      "thresholds": {
        "warning": 200,
        "critical": 500
      }})
    
    c2 = build(PolicySpec, {
        "templateName":"compss-under-allocation"})
    
    a1 = build(PolicyAction, {
        "type": "webhook",
        "url": "https://ded8-94-33-209-155.ngrok-free.app/",
        "httpMethod": "POST",
      })
    
    p1 = build(Policy, {
        "id": "1000",
        "name": "compss-low-performance-20",
        "subject": s1,
        "spec": c2,
        "variables": {
          "compssTask": "provesOtel.example_task",
          "thresholdTimeSeconds": "120"
        },
        "action": a1
      })
    

    def test_render(self):
      
      rp = render_policy(self.p1)
      
      print(rp)      
      
      
if __name__ == '__main__':
    unittest.main()
