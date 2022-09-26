# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Test cases for `console` module."""
import json
import tempfile
import unittest
from unittest import mock

from click import testing

from pipelines import console
from pipelines import pipeline_compiler
from pipelines import pipeline_runner


class CliTestCase(unittest.TestCase):
    """Base class for CLI tests."""

    def setUp(self):
        self.runner = testing.CliRunner()


class CompileTest(CliTestCase):
    """Tests `compile` command."""

    @staticmethod
    def _is_valid_json(filepath: str):
        """Verifies that file is a valid JSON file."""
        try:
            with open(filepath) as fp:
                json.load(fp)
        except Exception:
            return False
        else:
            return True

    @mock.patch.object(pipeline_compiler, "compile", autospec=True)
    def test_compile_ok(self, mock_compile):
        """It calls `pipeline_compiler.compile` with expected params."""
        module_name = "some-module"
        function_name = "pipeline-function"
        with tempfile.NamedTemporaryFile() as output_path:
            result = self.runner.invoke(
                console.compile, [module_name, function_name, output_path.name]
            )
        self.assertEqual(0, result.exit_code)
        mock_compile.assert_called_once_with(
            module_name, function_name, output_path.name
        )


class RunTest(CliTestCase):
    """Tests `run` command."""

    def setUp(self):
        self.runner = testing.CliRunner()

    @mock.patch.object(pipeline_runner.PipelineRunConfig, "from_file")
    @mock.patch.object(pipeline_runner, "run", autospec=True)
    def test_run_ok(self, mock_run, mock_from_file):
        """It calls `pipeline_runner.run` with the expected params."""
        pipeline_config_file = "pipeline-config.yaml"
        args = [pipeline_config_file, "-p", "param1=some-param"]
        result = self.runner.invoke(console.run, args)
        self.assertEqual(0, result.exit_code)

        # Check called `run` function.
        pipeline_params = dict(param1="some-param")
        mock_run.assert_called_once_with(mock.ANY, pipeline_params)
