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

from jinja2 import BaseLoader, Environment
from polman.common.model import PolicyCreate, PolicySpecTelemetry, PolicySpecTemplate
from polman.registry.templates_catalog import POLICY_SPEC_TEMPLATES_CATALOG
from polman.watcher.prometheus_rule_engine import subject_to_labels_list, subject_to_labels_selector


def render_policy(orig_policy: PolicyCreate):
  
  policy = orig_policy.model_copy()
  
  if isinstance(policy.spec, PolicySpecTemplate):
    policy.spec = POLICY_SPEC_TEMPLATES_CATALOG[policy.spec.templateName].model_copy()
    
  # rendering specific to telemetry specs
  if isinstance(policy.spec, PolicySpecTelemetry):
    fullExprTpl = policy.spec.expr
    if policy.spec.violatedIf:
      fullExprTpl += f' {policy.spec.violatedIf}'
      policy.spec.violatedIf = None

    ctxt = {
      "subject": policy.subject.model_dump(mode="python"),
      "subject_label_selector": subject_to_labels_selector(policy.subject),
      "subject_label_list": subject_to_labels_list(policy.subject)
    }

    ctxt = ctxt | policy.variables
    
    rtemplate = Environment(loader=BaseLoader).from_string(fullExprTpl)
    policy.spec.expr = rtemplate.render(**ctxt)    

  
  return policy