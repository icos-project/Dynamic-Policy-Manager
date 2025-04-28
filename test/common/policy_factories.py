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

from polyfactory import Use
from polman.common.model import Policy, PolicySubjectApplication, PolicySubjectCustom, PolicySubjectHost
from polyfactory.factories.pydantic_factory import ModelFactory


class PolicySubjectApplicationFactory(ModelFactory[PolicySubjectApplication]):
  appName = Use(ModelFactory.__random__.choice, ['first-app','hello-world'])

class PolicySubjectHostFactory(ModelFactory[PolicySubjectHost]):
  pass

class PolicySubjectCustomFactory(ModelFactory[PolicySubjectCustom]):
  pass

class PolicyFactory(ModelFactory[Policy]):

  @classmethod
  def subject(cls):
    return cls.__random__.choice([PolicySubjectApplicationFactory, PolicySubjectHostFactory, PolicySubjectCustomFactory]).build()
