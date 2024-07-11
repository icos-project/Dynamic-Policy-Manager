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
import pprint
import click
import yaml

from polman.cli.utils import click_params_to_config, model_to_click_options
from polman.common.config import PolmanConfig
from polman.common.logging import init_logging
from polman.main import PolmanApp
from polman.registry.main import PolmanRegistry

logger = logging.getLogger(__name__)


@click.group()
@model_to_click_options(PolmanConfig)
@click_params_to_config(PolmanConfig)
@click.pass_context
def cli(ctx, config, **kwargs):
  init_logging(-1 if config.quiet else config.verbosity)
  logger.info('Polman initialization (set verbosity >= 3 to see startyp config)')
  logger.debug('Config: %s', pprint.pformat(config, indent=2, sort_dicts=False))
  ctx.ensure_object(dict)
  ctx.obj['parsed_config'] = config


@click.command()
@click.pass_context
def registry(ctx, **kwargs):
  PolmanRegistry(ctx.obj['parsed_config'])

@click.command()
@click.option('--output', '-o', default="yaml")
@click.pass_context
def print_config(ctx, output, **kwargs):
  if output == 'yaml':
    print(yaml.dump(ctx.obj['parsed_config'].model_dump()))
  else:
    print(ctx.obj['parsed_config'])
  
@click.command()
@click.option('--dry-run', default=False, is_flag=True)
@click.pass_context
def app(ctx, dry_run, **kwargs):
  app = PolmanApp(ctx.obj['parsed_config'])
  app.run(dry_run=dry_run)

  
cli.add_command(registry)
cli.add_command(app)
cli.add_command(print_config)