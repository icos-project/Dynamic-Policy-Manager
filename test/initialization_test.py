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

from click.testing import CliRunner
from polman.cli.pmctl import cli



def test_icos_app_descriptor_job_manager_url():
  runner = CliRunner()
  cmdline = 'print-config -o yaml'
  result = runner.invoke(cli,cmdline.split(' '), env={
    'PML_ICOS_JOB_MANAGER_BASE_URL': 'http://my-jm-url:8888'
  }, auto_envvar_prefix='PML')
  print(result.output)
  assert result.exit_code == 0
  assert '  job_manager_base_url: http://my-jm-url:8888' in result.output



def test_icos_app_descriptor():
  runner = CliRunner()
  cmdline = '--verbosity 3 app --dry-run'
  result = runner.invoke(cli,cmdline.split(' '))
  assert result.exit_code == 0
  assert 'Initializing Polman...' in result.output

