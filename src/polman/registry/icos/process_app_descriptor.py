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

import logging
from polman.common.model import PolicyAction, PolicyActionWebhook, PolicyCreate, PolicySpecTemplate, PolicySubjectApplication
from deepmerge import always_merger

from polman.registry.icos.models import ICOSAppDescriptor, ICOSAppDescriptorComponent, ICOSPolicyBase, ICOSPolmanSpecPolicy, ICOSPolmanTemplatePolicy, ICOSSecurityPolicy, ICOSSecurityPolicyShort

logger = logging.getLogger(__name__)

def build_policy_json_from_app_descr_model(app_descr_model):


  
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


def security_level_to_thrshold(level) -> int:
  return {
    "low": 0,
    "medium": 34,
    "high": 67
  }[level]

def build_policy(ad_policy: ICOSPolicyBase, ad: ICOSAppDescriptor, ad_component: ICOSAppDescriptorComponent|None, app_instance: str, common_action: PolicyActionWebhook, counter):

  name = f'{ad.name}-{app_instance}-{ad_policy.name or (counter + 1)}'
  
  component_name = ad_component.name if ad_component else "*"
  if len(ad_policy.applyTo) == 1:
    component_name = ad_policy.applyTo[0]
  if len(ad_policy.applyTo) > 1:
    component_name = f'/{"|".join(ad_policy.applyTo)}/'

  subject = PolicySubjectApplication(appName=ad.name, appInstance=app_instance, appComponent=component_name)

  action = common_action.model_copy(deep=True)
  if ad_policy.remediation:
    action.extraParams["remediation"] = ad_policy.remediation

  partial_policy = {
    "name": name,
    "subject": subject,
    "action": action,
    "properties": ad_policy.properties
  }

  if isinstance(ad_policy, ICOSPolmanTemplatePolicy):
    logger.debug("Building policy from template %s", ad_policy.fromTemplate)
    return PolicyCreate(
      **partial_policy,
      spec=PolicySpecTemplate(templateName=ad_policy.fromTemplate),
      variables=ad_policy.variables
    )

  if isinstance(ad_policy, ICOSPolmanSpecPolicy):
    logger.debug("Building policy from spec %s", ad_policy.spec)
    return PolicyCreate(
      spec=ad_policy.spec,
      **partial_policy,
      variables=ad_policy.variables,
    )

  if isinstance(ad_policy, ICOSSecurityPolicy):
    logger.debug("Building security policy: %s", ad_policy)
    return PolicyCreate(
      spec=PolicySpecTemplate(templateName="app-sca-score"),
      **partial_policy,
      variables=ad_policy.variables | {"threshold": ad_policy.threshold if ad_policy.threshold else security_level_to_thrshold(ad_policy.level)}
    )

  if isinstance(ad_policy, ICOSSecurityPolicyShort):
    logger.debug("Building short security policy: %s", ad_policy)
    return PolicyCreate(
      spec=PolicySpecTemplate(templateName="app-sca-score"),
      **partial_policy,
      variables=ad_policy.variables | {"threshold": security_level_to_thrshold(ad_policy.security)}
    )
    
def process_app_descriptor(app_descr, app_instance, common_action):
  
  policies = []

  for pd in app_descr.policies:
    if isinstance(pd, ICOSPolicyBase):
      p = build_policy(pd, app_descr, None, app_instance, common_action, len(policies))
      policies.append(p)
    else:
      logger.debug("Discarding app descriptor policy %s because it is not a valid Polman policy", pd)

  
  for c in app_descr.components:
    for pd in c.policies:
      if isinstance(pd, ICOSPolicyBase):
        p = build_policy(pd, app_descr, c, app_instance, common_action, len(policies))
        policies.append(p)
      else:
        logger.debug("Discarding app descriptor policy %s because it is not a valid Polman policy", pd)

  return policies

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
    if common_action:
      p['action'] = always_merger.merge(p['action'], common_action.model_dump())

    if not p['name']:
      p['name'] = f'{app_descr.name}-{app_instance}-policy-{idx}'
    else:
       p['name'] = f'{app_descr.name}-{app_instance}-{p["name"]}'
    policies.append(PolicyCreate.model_validate(p))
    
  return policies