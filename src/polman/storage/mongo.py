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
from typing import Annotated
from urllib.parse import quote_plus
from bson import ObjectId
from pydantic import BeforeValidator, ConfigDict
from pydantic_mongo import AbstractRepository, ObjectIdField

import pymongo
from pymongo.results import UpdateResult

from polman.common.model import Policy, PolicyEvent, PolicyPhase, Violation
from polman.meter.main import PolmanMeter
from polman.storage.main import PolmanStorage


logger = logging.getLogger(__name__)

# TODO: look at https://art049.github.io/odmantic/

PyObjectId = Annotated[str, BeforeValidator(str)]

class PolicyDB(Policy):
  id: ObjectIdField = None

  model_config = ConfigDict(
      populate_by_name=True,
      #json_encoders={ObjectId: str},
      #arbitrary_types_allowed=True
      )
  
class PoliciesRepository(AbstractRepository[PolicyDB]):
   class Meta:
      collection_name = 'policies'
      
class MongodbPolicyStore(PolmanStorage):
  
  def __init__(self, config, pm: PolmanMeter, mongo_db_client=None, mongo_db_database_name=None) -> None:
    super().__init__(config)
    
    if mongo_db_client:
      client = mongo_db_client
    else:
      if config.db.url:
        url=config.db.url
      else:
        url = "mongodb://%s:%s@%s:%s" % (
                  quote_plus(config.db.user), quote_plus(config.db.password), config.db.host, config.db.port)
      client = pymongo.MongoClient(url)
    
    self.__policies_repo = PoliciesRepository(database=client[mongo_db_database_name or config.db.name])
    self._pm = pm
    logger.info('Initialized mongodb store')

  def start(self):
    pass
 
  def insert(self, db_policy: Policy):
    res = self.__policies_repo.save(PolicyDB(**db_policy.model_dump(exclude=['id'])))
    
    if isinstance(res, UpdateResult):
      id = res.upserted_id
    else:
      id = res.inserted_id or res.upserted_id
    return self.get(str(id))

  def get(self, id: str):
    return Policy(**self.__policies_repo.find_one_by_id(ObjectId(id)).model_dump())

  def add_policy_event(self, policy: Policy, event: PolicyEvent):
    policy.status.events.append(event)
    return self.__policies_repo.save(PolicyDB(**policy.model_dump()))

  def set_policy_phase(self, policy: Policy, phase: PolicyPhase):
    policy.status.phase = phase
    self.__policies_repo.save(PolicyDB(**policy.model_dump()))
    if self._pm:
      self._pm.set_policy_enforced(policy)
    
  def add_violation_to_history(self, policy: Policy, violation: Violation):
    policy.status.violationHistory.append(violation)
    return self.__policies_repo.save(PolicyDB(**policy.model_dump()))
    
  def update_measurement_backend(self, policy: Policy, name: str, status: dict):
    policy.status.measurementBackends[name] = status
    return self.__policies_repo.save(PolicyDB(**policy.model_dump()))
  
  def list(self):
    return [Policy(**p.model_dump()) for p in self.__policies_repo.find_by({})]


  def delete(self, id: str):
    o = self.__policies_repo.find_one_by_id(ObjectId(id))
    print(o)
    return self.__policies_repo.delete(o)
