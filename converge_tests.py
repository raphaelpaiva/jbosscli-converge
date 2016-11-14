#!/usr/bin/python
import unittest
import json

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
    # attributes, it shoyld list only the different ones
    def test_diff_newAttribute_shouldReturnList(self):
        desired = {"a": {"att": "b"}, "b": {"otheratt": 1, "newatt": "vvvv"}}
        current = {"a": {"att": "b"}, "b": {"otheratt": 1}}

        expected = [
            {"b": {"name": "newatt", "value": "vvvv"}},
            {"b": {"name": "otheratt", "value": 1}}
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

        expected = [
            {"app-auth": {"name": "heap-size", "value": "129m"}},
            {"app-auth": {"name": "max-heap-size", "value": "257m"}},
            {"app-auth": {"name": "permgen-size", "value": "65m"}},
            {"app-auth": {"name": "max-permgen-size", "value": "257m"}}
        ]

        actual = converge.diff(desired, current)

        self.assertItemsEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
