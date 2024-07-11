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

from polman.common.model import PolicyCreate
from deepmerge import always_merger

def build_policy_json_from_app_descr_model(app_descr_model):
  
  print('9999', app_descr_model)
  # ignoring at the moment
  if app_descr_model.type == "security":
    return None
  
  # Polman policies
  res = {
    "name": app_descr_model.name,
    "subject": {
      "type": "app",
      "appComponent": app_descr_model.component
    },
    "variables": app_descr_model.variables,
    "action" : {}
  }
  
  if app_descr_model.type == 'polmanTemplate':
    res['spec'] = {
      "type": "template",
      "templateName": app_descr_model.fromTemplate
    }
  
  if app_descr_model.type == 'polmanSpec':
    res['spec'] = app_descr_model.spec.model_dump()

  if app_descr_model.properties:
    res['properties'] = app_descr_model.properties.model_dump()

  if app_descr_model.remediation:
    res['action']['extraParams'] = {'remediation': app_descr_model.remediation}
  return res

def process_app_descriptor(app_descr, app_instance, common_action):
  
  # 1. Parse the App Descriptor
  
  
  policies_dicts = []
  # 2. Collct all policies in the component definitions
  for c in app_descr.components:
    for p in c.policies:
      m = build_policy_json_from_app_descr_model(p)
      if not m:
        continue
      m['subject']['appComponent'] = c.name      
      policies_dicts.append(m)
  
  for p in app_descr.policies:
      m = build_policy_json_from_app_descr_model(p)
      if not m:
        continue
      policies_dicts.append(m)
  
  policies = []
  for idx, p in enumerate(policies_dicts):
    p['subject']['appName'] = app_descr.name
    p['subject']['appInstance'] = app_instance
    p['action'] = always_merger.merge(p['action'], common_action.model_dump())

    if not p['name']:
      p['name'] = f'{app_descr.name}-{app_instance}-policy-{idx}'
    
    policies.append(PolicyCreate.model_validate(p))
    
  return policies