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

# ruff: noqa: PLC0415

"""Main module."""

import asyncio
import logging
from pathlib import Path

from polman.common.config import PolmanConfig
from polman.common.service import PolmanService

logger = logging.getLogger(__name__)


def get_polman_version() -> str:
    """Return the version of the codebase.

    The function reads the Polman version from the a file named "version" in the
    working directory of in the root of the filesystem ("/version").

    Returns
    -------
        the current Polman version

    """
    if Path("version").exists():
        return Path("version").read_text(encoding="utf-8")
    if Path("/version").exists():
        return Path("/version").read_text(encoding="utf-8")
    return "unknown"


class PolmanApp(PolmanService):
    """Main Access point for a polman instnace."""

    def __init__(self, config: PolmanConfig) -> None:
        """Initialize a new PolmanApp from a config object."""
        super().__init__(config)
        logger.info("Initializing Polman...")

        self.config = config

        from polman.meter.main import PolmanMeter

        self.meter = PolmanMeter()

        from polman.storage.main import PolmanStorage

        self.storage = PolmanStorage(config, self.meter)

        from polman.enforcer.main import PolmanEnforcer

        self.enforcer = PolmanEnforcer(config)

        from polman.watcher.main import PolmanWatcher

        self.watcher = PolmanWatcher(config, self.storage, self.enforcer)

        from polman.registry.main import PolmanRegistry

        self.registry = PolmanRegistry(config, self.storage, self.watcher)

        from polman.api.main import PolmanApi

        self.api = PolmanApi(config, self.registry, self.watcher)

    def startup_reconciliation(self):
        # TODO(gabriele): reconciliation with the measurment backend
        policies = self.storage.list()
        logger.info("Running Startup Reconciliation for %s found in the db", len(policies))

        # TODO: this should be done after the policy reconciliation
        # with the backend has been performed
        for p in policies:
            self.meter.set_policy_enforced(p)
        logger.info("Starting Metric Server at 0.0.0.0:9464")

    async def start(self, dry_run=False):
        tasks = asyncio.gather(self.api.start(dry_run=dry_run), self.meter.start(dry_run=dry_run))

        if not dry_run:
            self.startup_reconciliation()

        await tasks

    def run(self, dry_run=False) -> None:
        asyncio.run(self.start(dry_run=dry_run))
