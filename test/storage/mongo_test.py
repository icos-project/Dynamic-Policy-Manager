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

import pytest
from polman.common.errors import PolicyNotFoundError
from polman.storage.backend.mongo import MongodbPolicyStore
from polman.storage.main import PolmanStorage


def test_insert_policy(test_storage_with_mongo_backend, test_policy_factory):
    for i in range(10):
        test_storage_with_mongo_backend.insert(test_policy_factory.build())

    assert len(test_storage_with_mongo_backend.list()) == 10


def test_fix_exception_on_not_existent_policy(test_storage_with_mongo_backend: PolmanStorage) -> None:
    """Test that the get operation return None if the policy does not exists."""
    not_existing_id = "66d9db7791f3ffbf23d95a42"

    with pytest.raises(PolicyNotFoundError):
        test_storage_with_mongo_backend.get(not_existing_id)
