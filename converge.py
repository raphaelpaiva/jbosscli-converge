#!/usr/bin/python
from __future__ import print_function
from jbosscli import *

import json
import argparse


class Operation:
    def __init__(self, template, keys):
        self.template = template
        self.keys = keys


ADD_OPERATION = Operation(
    "/system-property={0}:add(value=\"{1}\",boot-time={2})\n",
    ["value", "boot-time"]
)
UPDATE_OPERATION = Operation(
    "/system-property={0}:write-attribute(name={1},value=\"{2}\")\n",
    ["attribute", "value"]
)


def main():
    args = parse_args()
    desired, current = read_input(args)

    to_add_items = missing(desired, current)
    to_update_items = diff(desired, current)

    print_cli(to_add_items, ADD_OPERATION)
    print_cli(to_update_items, UPDATE_OPERATION)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generates [un]deploy commands which you can " +
        "pipe through jboss-cli script."
    )

    parser.add_argument(
        "-c", "--controller",
        help="The controller to interact with.",
        default="localhost:9990"
    )

    parser.add_argument(
        "-a", "--auth",
        help="The credentials to authenticate on the controller",
        default="jboss:jboss@123"
    )

    return parser.parse_args()


def read_from_file(path):  # pragma: no cover
    lines = []
    with open(path) as f:
        return f.read()


def read_input(args):
    desired_file = read_from_file("desired.json")
    desired = json.loads(desired_file)

    cli = Jbosscli(args.controller, args.auth)
    current = cli.get_system_properties()

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
                diff.append({name: {"attribute": key, "value": value}})

    return diff


def print_cli(data, operation=ADD_OPERATION):
    output = ""

    for item in data:
        for key, value in item.iteritems():
            output += operation.template.format(
                key, *map(
                    lambda x: value[x] if x in value else "false",
                    operation.keys
                )
            )

    print(output)

if __name__ == "__main__":
    main()
