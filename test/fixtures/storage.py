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

import mongomock
import pymongo
import pytest

from polman.storage.main import InMemoryPolmanStorage
from polman.storage.mongo import MongodbPolicyStore
 
@pytest.fixture
def test_storage_in_memory(test_config):
    return InMemoryPolmanStorage(test_config, init_store={})

@pytest.fixture
# not using decorator here otherwise the same instance will be used for all the tests
# (see mongomock.patch docstring )
# @mongomock.patch(servers=(('server.example.com', 27017),))
def test_mongo_storage():
  with mongomock.patch(servers=(('server.example.com', 27017),)):
    return MongodbPolicyStore(None, None, mongo_db_client=pymongo.MongoClient('server.example.com'), mongo_db_database_name="test")