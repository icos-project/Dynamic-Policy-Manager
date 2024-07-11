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

#
# Utility functions for the "environ-config" library
#
#
import os
import re
import typing
from functools import update_wrapper

import click
from click import get_current_context
from click.decorators import FC

time_interval_regex = r"[\d\.,]+[smhwd]"

def click_params_to_pydantic_model(params, model_class):
    print(params)
    obj = click_params_to_pydantic_schema(params, model_class.model_json_schema()['properties'], model_class.model_json_schema()['$defs'])
    return model_class.model_validate(obj)


def click_params_to_pydantic_schema(params, properties, definitions, prefix=''):
    obj = {}
    for k, v in properties.items():
        if 'type' in v:
            # property of this model
            scoped_name = f'{prefix}_{k}' if prefix else k
            if scoped_name in params:
                if v['type'] == 'array':
                    obj[k] = comma_separated_list(params[scoped_name])
                else:
                    obj[k] = params[scoped_name]
            continue
        # reference to a nested object
        if v.get('allOf', None):
            allOf = v.get('allOf')[0]
            if allOf.get('$ref', None):
                model_ref = allOf['$ref'].split('/')[-1]
                new_prefix = f'{prefix}_{k}' if prefix else k
                obj[k] = click_params_to_pydantic_schema(params, definitions[model_ref]['properties'], definitions, prefix=new_prefix)

    return obj


def pydantic_model_to_click_options(model_class, prefix=''):
    opts = pydantic_schema_to_click_options(model_class.model_json_schema()['properties'], model_class.model_json_schema()['$defs'])
    return opts


def pydantic_schema_to_click_options(properties, definitions, prefix=''):
    opts = []
    for k, v in properties.items():
        
        # reference to a nested object
        # e.g. {'allOf': [{'$ref': '#/$defs/APIConfig'}], 'default': None}
        if v.get('allOf', None):
            allOf = v.get('allOf')[0]
            if allOf.get('$ref', None):
                model_ref = allOf['$ref'].split('/')[-1]
                new_prefix = f'{prefix}-{k}' if prefix else k
                opts.extend(pydantic_schema_to_click_options(definitions[model_ref]['properties'], definitions, prefix=new_prefix))
        else:
            # assuming this is property of this model
            scoped_name = f'{prefix}-{k}' if prefix else k
            opt_name = f'--{scoped_name}'.replace('_', '-')
            params = {'names': [opt_name]}
            if 'default' in v:
                params['default'] = v['default']

            if 'click' in v:
                params.update(v['click'])
                if 'short_name' in v['click']:
                    params['names'].append(f'-{v["click"]["short_name"]}')
                    del params['short_name']
            opts.append(params)
    return opts


def model_to_click_options(model_class):

    def decorator(function):
        opts = pydantic_model_to_click_options(model_class)
        for opt in opts:
            pos_args = opt['names']
            named_args = dict(opt)
            del named_args['names']
            function = click.option(*pos_args, **named_args)(function)
        return function

    return decorator


def click_params_to_config(model_class):

    def decorator_2(function):

        def new_func(*args, **kwargs):  # type: ignore
            model = click_params_to_pydantic_model(get_current_context().params, model_class)
            return function(model, *args, **kwargs)

        return update_wrapper(typing.cast(FC, new_func), function)

    return decorator_2


def comma_separated_list(val):
    if val is None:
        return []
    if isinstance(val, str):
        return [i.strip() for i in val.split(',')] if val else []
    else:
        return val


seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}


def human_time_to_seconds(val):
    res = 0
    matches = re.finditer(time_interval_regex, val)
    for matchNum, match in enumerate(matches, start=1):
        t = match.group()
        res += float(t[:-1]) * seconds_per_unit[t[-1]]

    # no time token found, try to interpret the whole value as number of seconds
    if not res:
        res = val

    return int(res)


def whitespace_separated_list(val):
    return [i for i in val.split()] if val else []


def load_config_from_string(config_as_string, config_params_prefix, config_class, use_os_env=True):
    '''
    Load config from env using the environ-config library.
    It is also possible to pass a config file with a list of
    "VAR=VALUE" one for each line. If enabled, os env variables
    will overwrite the config file values

    :param config_file:
    :param use_env:
    :return:
    '''

    params = {}
    if config_as_string:
        lines = [line.strip() for line in config_as_string.split('\n') if line.strip()]
        for line in lines:
            tokens = line.split('=', 1)
            params[tokens[0].strip()] = tokens[1].strip()

    if use_os_env:
        for k in os.environ:
            if k.startswith(config_params_prefix):
                params[k] = os.environ[k]

    return config_class.from_environ(environ=params)


def load_config_from_file(config_file, config_params_prefix, config_class, use_os_env=True):
    if config_file:
        with open(config_file) as f:
            content = f.read()
        return load_config_from_string(content, config_params_prefix, config_class, use_os_env=use_os_env)
    else:
        return load_config_from_string(None, config_params_prefix, config_class, use_os_env=use_os_env)
