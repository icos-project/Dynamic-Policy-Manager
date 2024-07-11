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

import os
from typing import List
from jinja2 import BaseLoader, Environment
from pydantic import TypeAdapter
import requests

from polman.common.model import PolicySubject
from polman.watcher.model import PrometheusRuleGroup


SUBJECT_FIELDS_TO_ICOS_TELEMETRY_LABELS = {
  'appName': 'icos_app_name',
  'appInstance': 'icos_app_instance',
  'appComponent': 'icos_app_component',
  'hostId': 'icos_host_id',
  'agentId': 'icos_agent_id'
}

# TODO: move in common
def subject_field_value_from_labels(field_name, labels):
  label_name = SUBJECT_FIELDS_TO_ICOS_TELEMETRY_LABELS.get(field_name, None)
  if not label_name:
    raise Exception('field name not mapped to any label')
  return labels[label_name]

def subject_to_labels_dict(subject: PolicySubject):
  return {SUBJECT_FIELDS_TO_ICOS_TELEMETRY_LABELS[v]: getattr(subject, v) for v in subject.model_fields_set if v != 'type'}

# TODO: move in common
def subject_to_labels_list(subject: PolicySubject):
  return ', '.join(sorted([SUBJECT_FIELDS_TO_ICOS_TELEMETRY_LABELS[v] for v in subject.model_fields_set if v != 'type']))

# TODO: move in common
def subject_to_labels_selector(subject: PolicySubject):

  labels = []
  for field in subject.model_fields_set:
    field_value = getattr(subject, field)
    if field == 'type':
      continue
    
    label_name = SUBJECT_FIELDS_TO_ICOS_TELEMETRY_LABELS[field]
    
    # special case: treat "*" as ".+" regex
    if field_value == '*':
      labels.append(f'{label_name}=~".+"')
      continue
    
    if field_value.startswith('/') and field_value.endswith('/'):
      labels.append(f'{label_name}=~"{field_value[1:-1]}"')
      continue
      
    labels.append(f'{label_name}="{field_value}"')
  
  labels.sort()
    
  return ', '.join(labels)


def get_telemetry_expr(db_policy, spec_override=None):

  spec = spec_override or db_policy.spec

  fullExprTpl = spec.expr
  if spec.violatedIf:
    fullExprTpl += f' {spec.violatedIf}'

  dump = db_policy.model_dump(mode="python")
  ctxt = {
    "subject": db_policy.subject,
    "subject_label_selector": subject_to_labels_selector(db_policy.subject),
    "subject_label_list": subject_to_labels_list(db_policy.subject)
  }

  ctxt = ctxt | dump['variables']
  
  rtemplate = Environment(loader=BaseLoader).from_string(fullExprTpl)
  exprData = rtemplate.render(**ctxt)

  return exprData


class PrometheusRuleEngine:
    
  def __init__(self, prom_api_url=None, post_prom_api_url=None) -> None:
    self.prom_api = prom_api_url
    self.mod_prom_api = post_prom_api_url or prom_api_url
    
  def add_rule(self, policy_name, policy_id, expression, for_param=None, labels={}, annotations={}):
    
    annotations['plm_id'] = policy_id
    annotations['plm_expr_value'] = "{{ $value }}"
    
    body = {"data":{"groups":[{"name": policy_name, "rules":[
      {
      "alert": f"{policy_name}:rule-0",
      "expr": expression,
      "for": for_param,
      "labels": labels,
      "annotations": annotations
    }]}]}}
    
    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    
    res = requests.post(self.mod_prom_api, headers=headers, json = body)
    
    print(res.text)
    print(res.reason)
    return res.json()['file']
 
 
  def list_rules(self):
    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    res = requests.get(self.mod_prom_api, headers=headers)
    
    print(res.json()) 
    ta = TypeAdapter(List[PrometheusRuleGroup])
    m = ta.validate_python(res.json()['data']['groups'])
    return m
  
  def delete_all_rules(self):
    rules = self.list_rules()
    for rg in rules:
      file_rule = os.path.basename(rg.file)
      res = requests.delete(f'{self.mod_prom_api}/{file_rule}')
      print(res)
  
  def delete_rule(self):
    pass
  
  def is_rule_set(self):
    pass



  