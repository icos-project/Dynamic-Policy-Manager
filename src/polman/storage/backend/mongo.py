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
from typing import Annotated
from urllib.parse import quote_plus

from pydantic_mongo.abstract_repository import AbstractRepository
from pydantic_mongo.fields import ObjectIdField
import pymongo
from bson import ObjectId
from pydantic import BeforeValidator, ConfigDict
from pymongo.results import UpdateResult

from polman.common.errors import PolicyNotFoundError
from polman.common.model import Policy, PolicyEvent, PolicyPhase, PolicySpec, PolicyVariableType
from .main import PolmanStorageBackend

logger = logging.getLogger(__name__)

# TODO: look at https://art049.github.io/odmantic/

PyObjectId = Annotated[str, BeforeValidator(str)]


class PolicyDB(Policy):
    id: ObjectIdField|None = None # type: ignore

    model_config = ConfigDict(
        populate_by_name=True,
        # json_encoders={ObjectId: str},
        # arbitrary_types_allowed=True
    )


class PoliciesRepository(AbstractRepository[PolicyDB]):
    class Meta: # type: ignore
        collection_name = "policies"


class MongodbPolicyStore(PolmanStorageBackend):
    def __init__(self, config, mongo_db_client=None, mongo_db_database_name=None) -> None:
        if mongo_db_client:
            client = mongo_db_client
        else:
            if config.db.url:
                url = config.db.url
            else:
                if config.db.user or config.db.password:
                    url = "mongodb://%s:%s@%s:%s" % (
                        quote_plus(config.db.user),
                        quote_plus(config.db.password.get_secret_value()),
                        config.db.host,
                        config.db.port,
                    )
                else:
                    url = "mongodb://%s:%s" % (config.db.host, config.db.port)

            client = pymongo.MongoClient(url)

        self.__policies_repo = PoliciesRepository(database=client[mongo_db_database_name or config.db.name])
        logger.info("Initialized mongodb store")

    def insert(self, policy: Policy) -> Policy:
        res = self.__policies_repo.save(PolicyDB(**policy.model_dump(exclude={"id"})))

        if isinstance(res, UpdateResult):
            pid = res.upserted_id
        else:
            pid = res.inserted_id
        return self.get(str(pid))

    def _update_existing_policy(self, policy: Policy) -> None:
        self.__policies_repo.save(PolicyDB(**policy.model_dump()))

    def get(self, policy_id: str):
        res = self.__policies_repo.find_one_by_id(ObjectId(policy_id))
        if res:
            return Policy(**res.model_dump())
        raise PolicyNotFoundError(policy_id)

    def add_policy_event(self, policy_id: str, event: PolicyEvent) -> None:
        p = self.get(policy_id)
        p.status.events.append(event)
        self._update_existing_policy(p)

    def set_policy_phase(self, policy_id: str, phase: PolicyPhase) -> None:
        p = self.get(policy_id)
        p.status.phase = phase
        self._update_existing_policy(p)

    def update_measurement_backend(self, policy_id: str, name: str, status: dict) -> None:
        p = self.get(policy_id)
        p.status.measurementBackends[name] = status
        self._update_existing_policy(p)

    def delete_measurement_backend(self, policy_id: str, name: str) -> None:
        """Delete a measurement backend status."""
        p = self.get(policy_id)
        del p.status.measurementBackends[name]
        self._update_existing_policy(p)

    def list(self, filters={}) -> list[Policy]:
        return [Policy(**p.model_dump()) for p in self.__policies_repo.find_by(filters)]

    def delete(self, policy_id: str) -> Policy:
        o = self.__policies_repo.find_one_by_id(ObjectId(policy_id))
        if not o:
            raise PolicyNotFoundError(policy_id)
        self.__policies_repo.delete(o)
        return Policy(**o.model_dump())

    def set_rendered_spec(self, policy_id: str, spec: PolicySpec) -> None:
        p = self.get(policy_id)
        p.status.renderedSpec = spec
        self._update_existing_policy(p)        

    def set_variable(self, policy_id: str, name: str, value: PolicyVariableType|None) -> None:
        p = self.get(policy_id)
        if not value:
            del p.variables[name]
        else:
            p.variables[name] = value
        self._update_existing_policy(p)  