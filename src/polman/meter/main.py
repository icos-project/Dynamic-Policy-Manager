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
from prometheus_client import start_http_server

from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

from polman.common.model import Policy, PolicyPhase
from polman.common.service import PolmanService
from polman.watcher.prometheus_rule_engine import subject_to_labels_dict
from opentelemetry.metrics import CallbackOptions, Observation

logger = logging.getLogger(__name__)


class PolmanMeter(PolmanService):

  def __init__(self) -> None:
       
    # Service name is required for most backends
    resource = Resource(attributes={
        SERVICE_NAME: "your-service-name"
    })

    # TODO: make this enabled/disabled and configurable
    
    logger.info("Initializing Meter")
    
    # Initialize PrometheusMetricReader which pulls metrics from the SDK
    # on-demand to respond to scrape requests
    reader = PrometheusMetricReader()
    provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(provider)
    meter = metrics.get_meter("my.meter.name")
    

    self._policy_enforced_status_cache = {}

    
    meter.create_observable_gauge("plm.policy.enforced", callbacks=[self._observe_enforced])
  
  async def start(self):
    start_http_server(port=9464, addr="0.0.0.0")
  
  def _observe_enforced(self, options: CallbackOptions):
    for k, v in self._policy_enforced_status_cache.items():
      yield Observation(v[0], v[1])
  
  def set_policy_enforced(self, policy: Policy):
    
    if policy.id in self._policy_enforced_status_cache and policy.status.phase == PolicyPhase.Inactive:
      del self._policy_enforced_status_cache[policy.id]
      return
    
    attributes = {"id": policy.id, "name": policy.name} | subject_to_labels_dict(policy.subject)
    
    self._policy_enforced_status_cache[policy.id] = (1 if policy.status.phase == PolicyPhase.Enforced else 0, attributes)
    
