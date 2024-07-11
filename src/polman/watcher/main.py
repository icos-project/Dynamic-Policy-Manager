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

import logging
from polman.common.config import PolmanConfig
from polman.common.events import PolicyEventsFactory
from polman.common.model import PolicyPhase, PolicySpecTelemetry
from polman.common.service import PolmanService
from polman.enforcer.main import PolmanEnforcer
from polman.storage.main import PolmanStorage
from polman.watcher.prometheus_rule_engine import PrometheusRuleEngine
from polman.watcher.violation import build_violation


logger = logging.getLogger(__name__)


class PolmanWatcher(PolmanService):
  
  def __init__(self, config: PolmanConfig, ps: PolmanStorage, pe: PolmanEnforcer):
    super().__init__(config)
    self._config = config
    self._ps = ps
    self._pe = pe

  def start(self):
    pass
 
  def process_alertmanager_alert(self, alert):
    if 'plm_id' not in alert.annotations:
      print('plm_id not found: this is not an alert for a policy!')
      return
    
    policy_id = alert.annotations['plm_id']
  
    policy = self._ps.get(policy_id)
    
    if not policy:  
      logger.error("No policy with id %s found", policy_id)
      return
      #raise HTTPException(status_code=404, detail="Policy not found")
  
    if alert.status == 'firing':
      violation = build_violation(alert, policy)
      
      self._ps.add_policy_event(policy, PolicyEventsFactory.policy_violated(violation))   
      self._ps.set_policy_phase(policy, PolicyPhase.Violated)
      
      self._pe.execute_violation_action(policy, violation)  
      return
    
    if alert.status == 'resolved':
      # TODO: trigger the action also for resolved?
      self._ps.add_policy_event(policy, PolicyEventsFactory.policy_resolved())   
      self._ps.set_policy_phase(policy, PolicyPhase.Enforced)
      return      
    
    logger.warn('Ignoring alert with status "%s"', alert.status)
    return
     

    
  def set_measurement_backends(self, policy):
    
    spec = policy.spec
    
    # set measurement backend for telemetry
    if isinstance(spec, PolicySpecTelemetry):
      
      prom_rule_engine = PrometheusRuleEngine(prom_api_url=self._config.prometheus.orig_api_url, post_prom_api_url=self._config.prometheus.mod_api_url)
    
      rule_file = prom_rule_engine.add_rule(
        policy_name=policy.name,
        policy_id=policy.id,
        expression=policy.spec.expr,
        annotations={'plm_measurement_backend': 'prom-1'},
        for_param=policy.properties.get('pendingInterval', '0'))
      
      measurement_backend_status = {
        "service": "prometheus",
        "url": prom_rule_engine.prom_api,
        "rule_file": rule_file
      }
      
      self._ps.add_policy_event(policy, PolicyEventsFactory.policy_activated())
      
      return {'prom-1': measurement_backend_status}
    
    raise Exception('Cannot measure a not telemetry spec')