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

"""The Polman Enforcer."""

import logging

from polman.common.config import PolmanConfig
from polman.common.errors import PolmanError
from polman.common.keycloak import KeycloakClient
from polman.common.logging import log_object
from polman.common.model import Policy, PolicyActionWebhook, Violation
from polman.common.service import PolmanService
from polman.enforcer.http import http_request

logger = logging.getLogger(__name__)


class PolmanEnforcer(PolmanService):
    """PolmanEnforcer."""

    def __init__(self, config: PolmanConfig) -> None:
        """Initialize the PolmanEnforcer."""
        super().__init__(config)

        self._config = config
        self._kc_client = None

    async def start(self) -> None:
        """Start the PolmanEnforcer."""

    def __get_keycloak_client(self) -> KeycloakClient | None:
        """Return a singleton keycloak client.

        Returns
        -------
            the KeyclaokClient

        """
        if not self._kc_client and self._config.authn:
            self._kc_client = KeycloakClient(self._config)
        return self._kc_client

    def execute_violation_action(self, policy: Policy, violation: Violation) -> None:
        """Execute the violation action defined by the policy.

        Args:
        ----
            policy (Policy): the policy for which we are executing the action
            violation (Violation): the violation for which we are executing the action

        Raises:
        ------
            PolmanError: in case an unknown action is given

        """
        if isinstance(policy.action, PolicyActionWebhook):
            params = violation.model_dump() | policy.action.extraParams
            logger.debug("Executing violation action:\n\nSend HTTP %s %s with payload:\n%s\n", policy.action.httpMethod, policy.action.url, log_object(params))

            http_request(
                policy.action.httpMethod,
                policy.action.url,
                params,
                include_access_token=policy.action.includeAccessToken,
                keycloak_client=self.__get_keycloak_client(),
            )
            return

        msg = "Not executable action"
        raise PolmanError(msg)
