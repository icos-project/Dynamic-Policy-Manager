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

import click
from pathlib import Path
import yaml
import json
import rich
from fastapi.openapi.utils import get_openapi

from polman.cli.utils import click_params_to_config, model_to_click_options
from polman.common.config import PolmanConfig
from polman.common.logging import init_logging, log_object
from polman.main import PolmanApp, get_polman_version

logger = logging.getLogger(__name__)


@click.group()
@model_to_click_options(PolmanConfig)
@click_params_to_config(PolmanConfig)
@click.pass_context
def cli(ctx, config, **kwargs):
    init_logging(-1 if config.quiet else config.verbosity, use_rich_output=config.rich_output)
    logger.info("Polman initialization (set verbosity >= 3 to see startyp config)")
    logger.debug("Configuration:\n%s", log_object(config))
    ctx.ensure_object(dict)
    ctx.obj["parsed_config"] = config


@click.command()
@click.option("--output", "-o", default="yaml")
@click.pass_context
def print_config(ctx, output, **kwargs):
    if output == "yaml":
        print(yaml.dump(ctx.obj["parsed_config"].model_dump()))
    else:
        print(ctx.obj["parsed_config"])


@click.command()
@click.option("--dry-run", default=False, is_flag=True)
@click.pass_context
def app(ctx, dry_run, **kwargs):
    app = PolmanApp(ctx.obj["parsed_config"])
    app.run(dry_run=dry_run)


@click.command()
@click.pass_context
def version(ctx) -> None:
    """Print version."""
    print(get_polman_version())

@click.command()
@click.option("--output", default="")
@click.pass_context
def dump_openapi(ctx, output, **kwargs):
    app = PolmanApp(ctx.obj["parsed_config"])
    schema = app.api.get_openapi_schema()
    if output:
        Path(output).write_text(json.dumps(schema))
    else:
        rich.print(schema)


cli.add_command(app)
cli.add_command(print_config)
cli.add_command(version)
cli.add_command(dump_openapi)
