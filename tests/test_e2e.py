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

"""Tests end-to-end run of sample pipeline in Vertex Pipelines."""

import os
import unittest

from click import testing
import cloudpathlib as cpl
import pytest

from pipelines import console
from pipelines import pipeline_runner


@pytest.mark.e2e
class SamplePipelineTest(unittest.TestCase):  # noqa: D101
    def _assert_message_in_file(self, expected_message: str, gcs_file: str) -> None:
        """It checks whether expected message is in given GCS file."""
        with cpl.CloudPath(gcs_file).open() as fp:
            output_message = fp.read()
        self.assertEqual(expected_message, output_message)

    def setUp(self) -> None:
        self.runner = testing.CliRunner()
        self.config_file = "pipeline-run-config.yaml"
        self.config = pipeline_runner.PipelineRunConfig.from_file(self.config_file)
        self.pipeline_module_name = "sample_pipeline"
        self.pipeline_func_name = "pipeline"
        self.pipeline_path = self.config.pipeline_path

    def test_run_on_gcp_ok(self):
        """It runs the sample pipeline successfully in Vertex Pipelines."""
        result = self.runner.invoke(
            console.compile,
            [self.pipeline_module_name, self.pipeline_func_name, self.pipeline_path],
        )
        self.assertEqual(0, result.exit_code)
        message = "Hello World!"
        message_output_path = os.path.join(
            self.config.gcs_root_path, "output/message.txt"
        )
        run_params = [
            self.config_file,
            "-p",
            f"message={message}",
            "-p",
            f"gcs_filepath={message_output_path}",
        ]
        result = self.runner.invoke(console.run, run_params)
        self.assertEqual(0, result.exit_code)
        self._assert_message_in_file(message, message_output_path)
