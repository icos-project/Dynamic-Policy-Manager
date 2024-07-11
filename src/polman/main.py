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

import asyncio
import logging
from polman.common.config import PolmanConfig
from polman.common.service import PolmanService
from polman.storage.file import FilePolmanStorage

logger = logging.getLogger(__name__)


class PolmanApp(PolmanService):

  def __init__(self, config: PolmanConfig):
    super().__init__(config) 
    logger.info('Initializing Polman...')
    
    self.config = config
    
    from polman.meter.main import PolmanMeter
    self.meter = PolmanMeter()
    
    self.__init_storage()
    
    from polman.enforcer.main import PolmanEnforcer
    self.enforcer = PolmanEnforcer(config)

    from polman.watcher.main import PolmanWatcher
    self.watcher = PolmanWatcher(config, self.storage, self.enforcer)

    from polman.registry.main import PolmanRegistry
    self.registry = PolmanRegistry(config, self.storage, self.watcher)
    
    from polman.api.main import PolmanApi
    self.api = PolmanApi(config, self.registry, self.watcher)
    
  def __init_storage(self):
    from polman.storage.main import InMemoryPolmanStorage
    from polman.storage.mongo import MongodbPolicyStore

    self.storage = None
    
    if self.config.db.type == 'inmemory':
        self.storage = InMemoryPolmanStorage(self.config)
    
    if self.config.db.type == 'mongodb':
      self.storage = MongodbPolicyStore(self.config, self.meter)
      
    if self.config.db.type == 'file':
      self.storage = FilePolmanStorage(self.config)

  def startup_reconciliation(self):
    
    # TODO: reconciliation with the measurment backend
    
    policies = self.storage.list()
    logger.info(f'Running Startup Reconciliation for {len(policies)} found in the db')
    
    # FIXME: this should be done after the policy reconciliation
    # with the backend has been performed
    for p in policies:
      self.meter.set_policy_enforced(p)
    logger.info("Starting Metric Server at 0.0.0.0:9464")

  async def start(self, dry_run=False):
    tasks = asyncio.gather(
      self.api.start(dry_run=dry_run),
      self.meter.start())
    
    if not dry_run:
      self. startup_reconciliation()
    
    await tasks
    
  def run(self, dry_run=False):
    asyncio.run(self.start(dry_run=dry_run))
