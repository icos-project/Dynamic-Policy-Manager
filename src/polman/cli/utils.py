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

import os
import re
from functools import update_wrapper

import click
from click import get_current_context
from pydantic import SecretStr

time_interval_regex = r"[\d\.,]+[smhwd]"


def click_params_to_pydantic_model(params, model_class):
    obj = click_params_to_pydantic_schema(
        params, model_class.model_json_schema()["properties"], model_class.model_json_schema()["$defs"]
    )
    return model_class.model_validate(obj)


def click_params_to_pydantic_schema(params, properties, definitions, prefix=""):
    """Build an object (dict) that conform with the pydantic schema taking values from click parameters.

    The function recursively iterates the provided pydantic schema creating an object that conforms
    to it. For any object key, if a corrsponding click parameter is found it assigns its value to the key.

    The iteration and recursion logic is the same of the function "pydantic_schema_to_click_options"

    Args:
    ----
        params: click parameters
        properties (_type_): schema properties of this level
        definitions (_type_): ALL schema definitions
        prefix (str): prefix for the upper level. Defaults to "".

    Returns:
    -------
        dict: a dict representing a pydantic model

    """
    obj = {}
    for k, v in properties.items():
        if "allOf" in v:
            nested_model_ref = v["allOf"][0]["$ref"]
            nested_model_name = nested_model_ref.split("/")[-1]
            nested_prefix = f"{prefix}-{k}" if prefix else k

            if "properties" in definitions[nested_model_name]:
                obj[k] = click_params_to_pydantic_schema(
                    params,
                    definitions[nested_model_name]["properties"],
                    definitions,
                    prefix=nested_prefix,
                )
                continue

            if "enum" in definitions[nested_model_name]:
                v |= definitions[nested_model_name]  # noqa: PLW2901

        scoped_name = f"{prefix}_{k}" if prefix else k
        if scoped_name in params:
            if v["type"] == "array":
                obj[k] = comma_separated_list(params[scoped_name])
                continue
            if v.get("format", None) == "password":
                obj[k] = SecretStr(params[scoped_name] or "")
                continue
            obj[k] = params[scoped_name]

    return obj


def pydantic_model_to_click_options(model_class, prefix=""):
    return pydantic_schema_to_click_options(
        model_class.model_json_schema()["properties"],
        model_class.model_json_schema()["$defs"],
    )


def pydantic_schema_to_click_options(properties, definitions, prefix="") -> list[dict]:
    """Build a list of click options from a pydantic object schema.

    The pydantic schema is made of a list of object's "definitions". Each definition
    contains the list of properties for that object. Each property has a dictionary
    with all the info about the property (e.g, type, default value, custom annotations, ...).
    If a property has a key "allOf", it means that the property is a nested object.

    For instance:
        {
            '$defs': {
                'DBConfig': {
                    'properties': {
                        'type': {'allOf': [{'$ref': '#/$defs/DBType'}], 'default': 'inmemory'},
                        'host': {'default': '', 'title': 'Host', 'type': 'string'},
                        'port': {'default': 0, 'title': 'Port', 'type': 'integer'},
                ...
                    },
                    'title': 'DBConfig',
                    'type': 'object'
                },
                'DBType': {'enum': ['inmemory', 'file', 'mongodb'], 'title': 'DBType', 'type': 'string'},
            },
            'properties': {
                'quiet': {'default': False, 'title': 'Quiet', 'type': 'boolean'},
                'verbosity': {'default': 2, 'title': 'Verbosity', 'type': 'integer'},
                'db': {'allOf': [{'$ref': '#/$defs/DBConfig'}], 'default': None},
            ...
            },
            'title': 'PolmanConfig',
            'type': 'object'
        }

    This function recursively process all the properties creating click options for each of them.

    Args:
    ----
        properties: list of properties at this level
        definitions: definitions
        prefix (str): The prefix of the upper level. Defaults to "".

    Returns:
    -------
        list: a list of dictionaries, each of them representing a different click option

    """
    opts = []
    for k, v in properties.items():
        # if there is "allOf" in a property, it means that that property is a nested object.
        # We call the function recursively to create the list of click options for the nested
        # object using the name of this property as prefix
        # e.g. {'allOf': [{'$ref': '#/$defs/APIConfig'}], 'default': None}
        if "allOf" in v:
            nested_model_ref = v["allOf"][0]["$ref"]
            nested_model_name = nested_model_ref.split("/")[-1]
            nested_prefix = f"{prefix}-{k}" if prefix else k

            # if the nested definitions if has "properties" it means that it is a nested
            # object...
            if "properties" in definitions[nested_model_name]:
                nested_options = pydantic_schema_to_click_options(
                    definitions[nested_model_name]["properties"],
                    definitions,
                    prefix=nested_prefix,
                )
                opts.extend(nested_options)
                continue

            # ... if it has "enum" it is an enum. In this case we do not need to recursively
            # iterate, but simply we treat it as property of this level
            if "enum" in definitions[nested_model_name]:
                v |= definitions[nested_model_name]  # noqa: PLW2901

        # create click option for the property
        scoped_name = f"{prefix}-{k}" if prefix else k
        opt_name = f"--{scoped_name}".replace("_", "-")
        params: dict = {"names": [opt_name]}
        if "default" in v:
            params["default"] = v["default"]


        if "click" in v:
            params.update(v["click"])
            if "short_name" in v["click"]:
                params["names"].append(f'-{v["click"]["short_name"]}')
                del params["short_name"]

        if v["type"] == "boolean":
            # see https://click.palletsprojects.com/en/8.1.x/options/#boolean-flags
            params["is_flag"] = True
            modified_name = f'{params["names"][0]}/--no-{params["names"][0][2:]}'
            params["names"] = [modified_name]
        
        # show default when showing the help (--help)
        params["show_default"] = True

        opts.append(params)
    return opts


def model_to_click_options(model_class):
    def decorator(function):
        opts = pydantic_model_to_click_options(model_class)
        for opt in opts:
            pos_args = opt["names"]
            named_args = dict(opt)
            del named_args["names"]
            function = click.option(*pos_args, **named_args)(function)
        return function

    return decorator


def click_params_to_config(model_class):
    def decorator_2(function):
        def new_func(*args, **kwargs):  # type: ignore
            model = click_params_to_pydantic_model(get_current_context().params, model_class)
            return function(model, *args, **kwargs)

        return update_wrapper(new_func, function)

    return decorator_2


def comma_separated_list(val):
    if val is None:
        return []
    if isinstance(val, str):
        return [i.strip() for i in val.split(",")] if val else []
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
    """
    Load config from env using the environ-config library.
    It is also possible to pass a config file with a list of
    "VAR=VALUE" one for each line. If enabled, os env variables
    will overwrite the config file values

    :param config_file:
    :param use_env:
    :return:
    """

    params = {}
    if config_as_string:
        lines = [line.strip() for line in config_as_string.split("\n") if line.strip()]
        for line in lines:
            tokens = line.split("=", 1)
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
