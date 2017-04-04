#!/usr/bin/python
import unittest
import json
from mock import *

import converge


class TestDeploy(unittest.TestCase):

    def test_diff_noDiff_shouldReturnEmptyList(self):
        desired = {"a": {"att": "b"}, "b": {"otheratt": 1}}
        current = {"a": {"att": "b"}, "b": {"otheratt": 1}}
        expected = []

        actual = converge.diff(desired, current)

        self.assertEqual(actual, expected)

    def test_diff_sameDict_shouldReturnEmptyList(self):
        desired = {"a": {"att": "b"}, "b": {"otheratt": 1}}
        current = desired
        expected = []

        actual = converge.diff(desired, current)

        self.assertEqual(actual, expected)

    def test_diff_oneDiff_shouldReturnList(self):
        desired = {"a": {"att": "b"}, "b": {"otheratt": 1}}
        current = {"a": {"att": "b"}, "b": {"otheratt": 2}}
        expected = [{"b": {"name": "otheratt", "value": 1}}]

        actual = converge.diff(desired, current)

        self.assertEqual(actual, expected)

    # TODO: This should change in the future. Instead of listing all "b"'s
    # attributes, it should list only the different ones
    def test_diff_newAttribute_shouldReturnList(self):
        desired = {"a": {"att": "b"}, "b": {"otheratt": 1, "newatt": "vvvv"}}
        current = {"a": {"att": "b"}, "b": {"otheratt": 1}}

        expected = [
            {"b": {"name": "newatt", "value": "vvvv"}}
        ]

        actual = converge.diff(desired, current)

        self.assertEqual(actual, expected)

    # TODO: This should change in the future. The output of this scenario
    # should be an empty list as the common attributes did not change.
    def test_diff_actualHasMoreAttributes_shouldReturnList(self):
        desired = {
            "app-auth": {
                "heap-size": "129m",
                "max-heap-size": "257m",
                "permgen-size": "65m",
                "max-permgen-size": "257m"
            }
        }

        current = json.loads(
            '{"app-auth" : {"agent-lib" : null, "agent-path" : null,\
"env-classpath-ignored" : null, "environment-variables" : null, "heap-size" :\
"129m", "java-agent" : null, "java-home" : null, "jvm-options" :\
["-Dorg.jboss.resolver.warning=true","-Dsun.rmi.dgc.server.gcInterval=3600000"\
,"-Dsun.lang.ClassLoader.allowArraySyntax=true","-Dfile.encoding=utf-8",\
"-Duser.language=pt","-Duser.region=BR","-Duser.country=BR",\
"-Djava.awt.headless=true","-Xss256k",\
"-Djava.security.egd=file:/dev/./urandom"], "max-heap-size" : "257m",\
"max-permgen-size" : "257m", "permgen-size" : "65m",\
"stack-size" : null, "type" : null}}'
        )

        expected = []

        actual = converge.diff(desired, current)

        self.assertItemsEqual(actual, expected)

    def test_get_output_file_stdout(self):
        args = MagicMock(output="stdout")

        self.assertIsNone(converge.get_output_file(args))

    def test_get_output_file_filename(self):
        args = MagicMock(output="somefile")

        m_open = mock_open()
        with patch(converge.__name__ + ".open", m_open):
            self.assertIsNotNone(converge.get_output_file(args))
            m_open.assert_called_once_with("somefile", 'w')

    def test_read_input_empty_controller(self):
        mock_config = {
            "desired.json": '{"what": "desired!"}',
            "current.json": '{"this": "current!"}'
        }

        side_effect = lambda x: mock_config[x]

        mock_read_from_file = MagicMock(side_effect=side_effect)

        args = MagicMock(
            desired="desired.json",
            controller=None
        )

        with patch(converge.__name__ + ".read_from_file", mock_read_from_file):
            desired, current = converge.read_input(args)

            self.assertEqual(desired, {'what': 'desired!'})
            self.assertEqual(current, {'this': 'current!'})

    def test_read_input_with_controller(self):
            mock_config = {
                "desired.json": '{"what": "desired!"}',
                "current.json": '{"this": "current!"}'
            }

            side_effect = lambda x: mock_config[x]

            mock_read_from_file = MagicMock(side_effect=side_effect)

            args = MagicMock(
                desired="desired.json",
                controller="host:port",
                type="system-property",
                address=""
            )

            jboss_mock = MagicMock()

            with patch(converge.__name__ + ".read_from_file", mock_read_from_file):
                with patch(converge.__name__ + ".get_controller", MagicMock(return_value=jboss_mock)):
                    desired, current = converge.read_input(args)

                    jboss_mock.invoke_cli.assert_called_once_with({
                        "operation": "read-children-resources",
                        "child-type": "system-property",
                        "address": []
                    })

    def test_missing(self):
        desired = {
            "existing": "Yay!",
            "missing": "This is missing!"
        }

        current = {
            "existing": "Yay!"
        }

        expected = [{
            "missing": "This is missing!"
        }]

        missing_items = converge.missing(desired, current)

        self.assertEqual(missing_items, expected)

    def test_map_parameters(self):
        data = {
            "name": "value",
            "name2": "value2",
            "name3": "value3"
        }

        expected = "name2=value2,name=value,name3=value3"

        actual = converge.map_params(data)

        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
