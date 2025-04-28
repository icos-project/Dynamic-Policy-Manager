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

"""Watcher module."""

import logging

from polman.common.config import PolmanConfig
from polman.common.errors import PolmanError
from polman.common.events import PolicyEventsFactory
from polman.common.logging import log_object
from polman.common.model import Policy, PolicyPhase, PolicySpecTelemetry
from polman.common.service import PolmanService
from polman.enforcer.main import PolmanEnforcer
from polman.storage.main import PolmanStorage
from polman.watcher.model import AlertmanagerAlert, AlertmanagerWebhook
from polman.watcher.prometheus_rule_engine import PrometheusRuleEngine
from polman.watcher.violation import build_violation

logger = logging.getLogger(__name__)


class PolmanWatcher(PolmanService):
    """The PolmanWatcher service.

    This service is responsible for evaluating the policies
    """

    def __init__(
        self, config: PolmanConfig, ps: PolmanStorage, pe: PolmanEnforcer
    ) -> None:
        super().__init__(config)
        self._config = config
        self._ps = ps
        self._pe = pe

    async def start(self) -> None:
        pass



    def violate_policy(self, policy: Policy, backend_name: str, current_value: float, labels: dict):


        try:
          violation = build_violation(backend_name, current_value, labels, policy)
        except Exception as ex:
            self._ps.add_policy_event(policy, PolicyEventsFactory.policy_rendering_error(policy.spec, str(ex)))
            self._ps.set_policy_phase(policy, PolicyPhase.Violated)
            return
        
        
        self._ps.add_policy_event(
            policy,
            PolicyEventsFactory.policy_violated(violation),
        )
        self._ps.set_policy_phase(policy, PolicyPhase.Violated)

        self._pe.execute_violation_action(policy, violation)

    def resolve_policy(self, policy: Policy):
        # TODO(gabriele): trigger the action also for resolved?
        self._ps.add_policy_event(policy, PolicyEventsFactory.policy_resolved())
        self._ps.set_policy_phase(policy, PolicyPhase.Enforced)

    def process_alertmanager_alert(self, alert: AlertmanagerAlert) -> None:
        """Process an alert received by the Alertmanager."""
        logger.debug("Processing received Webhook from AlertManager:\n%s", log_object(alert))

        if "plm_id" not in alert.annotations:
            logger.error("plm_id not found: this is not an alert for a policy!")
            return

        policy_id = alert.annotations["plm_id"]

        policy = self._ps.get(policy_id)

        if not policy:
            logger.error("No policy with id %s found", policy_id)
            return

        if alert.status == "firing":
            backend_name = alert.annotations['plm_measurement_backend']
            current_value = float(alert.annotations['plm_expr_value'])
            labels = dict(alert.labels)
            del labels['alertname']
            self.violate_policy(policy, backend_name, current_value, labels)

        if alert.status == "resolved":
            self.resolve_policy(policy)

        logger.warning('Ignoring alert with status "%s"', alert.status)
        return

    def unset_measurement_backends(self, policy: Policy) -> None:
        """Stop watching a policy."""


        if "prom-1" not in policy.status.measurementBackends:
            logger.error("Measurement backend not active. Exiting")
            return

        status = policy.status.measurementBackends["prom-1"]

        if self._config.prometheus.rules_api_url != status["url"]:
            raise PolmanError("URL mismatch. The rule was created from a different instance?")

        rule_file = status["rule_file"]

        prom_rule_engine = PrometheusRuleEngine(
            api_url=self._config.prometheus.rules_api_url
        )

        prom_rule_engine.delete_rule(str(rule_file))  # str() is not needed but required for type checking

        self._ps.delete_measurement_backend(policy, "prom-1")
        self._ps.add_policy_event(policy, PolicyEventsFactory.policy_deactivated())
        return


    def set_measurement_backends(self, policy):

        if not self._config.prometheus.rules_api_url:
            raise PolmanError(
                "Prometheus backend not enabled in the config! Cannot activate policy"
            )

        spec = policy.status.renderedSpec

        # set measurement backend for telemetry
        if isinstance(spec, PolicySpecTelemetry):
            prom_rule_engine = PrometheusRuleEngine(
                api_url=self._config.prometheus.rules_api_url
            )

            rule_file = prom_rule_engine.add_rule(
                policy_name=policy.name,
                policy_id=policy.id,
                expression=spec.expr,
                extra_annotations={"plm_measurement_backend": "prom-1"},
                for_param=policy.properties.get("pendingInterval", "0"),
            )

            measurement_backend_status = {
                "service": "prometheus",
                "url": prom_rule_engine.prom_api,
                "rule_file": rule_file,
            }

            self._ps.update_measurement_backend(
                policy, "prom-1", measurement_backend_status
            )
            self._ps.add_policy_event(policy, PolicyEventsFactory.policy_activated())
            return

        raise PolmanError("Policy cannot be watched")
