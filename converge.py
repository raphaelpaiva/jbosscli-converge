#!/usr/bin/python
from __future__ import print_function
from jbosscli import *

import json
import argparse


ADD_OPERATION = "add"

UPDATE_OPERATION = "write-attribute"


def main():
    args = parse_args()
    desired, current = read_input(args)

    to_add_items = missing(desired, current)
    to_update_items = diff(desired, current)

    output = get_output_file(args)

    print_cli(
        to_add_items,
        args.address,
        args.type,
        ADD_OPERATION,
        output
    )

    print_cli(
        to_update_items,
        args.address,
        args.type,
        UPDATE_OPERATION,
        output
    )

    if output:
        output.close()


def get_output_file(args):
    output_file = args.output
    if output_file == "stdout":
        return None
    else:
        return open(output_file, "w")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Creates cli recipes from json files describing the\
current and desired states to enforce compliance."
    )

    parser.add_argument(
        "-c", "--controller",
        help="The controller to interact with. Grabs the current state from \
the controller, instead of looking for a 'current.json' file.",
    )

    parser.add_argument(
        "-a", "--auth",
        help="The credentials to authenticate on the controller",
        default="jboss:jboss@123"
    )

    parser.add_argument(
        "-d", "--desired",
        help="The json file containing the desired state.\
 Defaults to 'desired.json'",
        default="desired.json"
    )

    parser.add_argument(
        "-o", "--output",
        help="Output file. Defaults to stdout.",
        default="stdout"
    )

    parser.add_argument(
        "--address",
        help="The cli address to the resource. Defaults to '' (root).",
        default=""
    )

    parser.add_argument(
        "-t", "--type",
        help="The cli resource type. Defaults to 'system-property'.",
        default="system-property"
    )

    return parser.parse_args()


def read_from_file(path):  # pragma: no cover
    lines = []
    with open(path) as f:
        return f.read()


def read_input(args):
    desired_file = read_from_file(args.desired)
    desired = json.loads(desired_file)

    current = None

    if args.controller:
        address = args.address or ""
        resource_type = args.type

        command = '{{"operation": "read-children-resources",\
"child-type": "{0}", "address": {1}}}'.format(
            resource_type,
            address.replace('/', ' ').replace('=', ' ').split()
        ).replace("\'", "\"")

        cli = Jbosscli(args.controller, args.auth)
        current = cli._invoke_cli(command)['result']
    else:
        current_file = read_from_file("current.json")
        current = json.loads(current_file)

    return desired, current


def missing(desired, current):
    desired_keys = frozenset(desired.keys())
    current_keys = frozenset(current.keys())

    to_add = desired_keys - current_keys

    items = [
        {key: value} for key, value in desired.iteritems() if key in to_add
    ]

    return items


def diff(desired, current):
    desired_keys = frozenset(desired.keys())
    current_keys = frozenset(current.keys())

    diff = desired_keys & current_keys

    items = [
        {key: value} for key, value in desired.iteritems()
        if key in diff and value != current[key]
    ]

    diff = []
    for item in items:
        for name, obj in item.iteritems():
            for key, value in obj.iteritems():
                diff.append({name: {"name": key, "value": value}})

    return diff


def print_cli(data, address, type, operation=ADD_OPERATION, output_file=None):
    """ data = "name": {"boot-time": false, "value": "somevalue"} """

    output = ""

    template = "{address}/{type}={name}:{operation}({params})\n"

    for item in data:
        for key, value in item.iteritems():
            output += template.format(
                address=address,
                type=type,
                name=key,
                operation=operation,
                params=map_params(value)
            )

    print(output, file=output_file)


def map_params(data):
    params = []
    for k, v in data.items():
        params.append("{0}={1}".format(k, v))

    return ",".join(params)

if __name__ == "__main__":
    main()
