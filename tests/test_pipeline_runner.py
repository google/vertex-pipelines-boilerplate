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

"""Tests `pipeline_runner.py`."""

import logging
import tempfile
from typing import Any, Dict
import unittest
from unittest import mock

from google.cloud import aiplatform as vertex
import yaml

from pipelines import pipeline_runner


# Disables logging from objects-under-test
logging.disable(logging.CRITICAL)


class PipelineRunConfigTest(unittest.TestCase):
    """Tests `PipelineRunConfig`."""

    def setUp(self) -> None:
        self.required_params: Dict[str, Any] = {
            "pipeline-name": "some-pipeline",
            "pipeline-path": "gs://path/to/some-pipeline.json",
            "gcs-root-path": "gs://some-staging-bucket",
            "location": "us-central1",
        }
        self.optional_params: Dict[str, Any] = {
            "enable-caching": False,
            "service-account": "name@project.iam.gserviceaccount.com",
            "sync": False,
        }
        self.run_config_params = self.required_params

    def _write_config(self, tempf: tempfile._TemporaryFileWrapper) -> None:
        """Writes configuration data as a YAML file."""
        yaml.dump(self.run_config_params, tempf, default_flow_style=True)
        tempf.seek(0)

    def _get_expected_pipeline_run_config(self) -> pipeline_runner.PipelineRunConfig:
        """Returns PipelineRunConfig object from dict."""
        data = {k.replace("-", "_"): v for k, v in self.run_config_params.items()}
        return pipeline_runner.PipelineRunConfig(**data)  # type: ignore[arg-type]

    def test_from_file_default(self) -> None:
        """It checks `from_file` behavior without changing default values."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml") as tempf:
            self._write_config(tempf)
            expected = self._get_expected_pipeline_run_config()
            output = pipeline_runner.PipelineRunConfig.from_file(tempf.name)
            self.assertEqual(expected, output)

    def test_from_file_with_optional_params(self) -> None:
        """It parses optional parameters from config file."""
        self.run_config_params.update(self.optional_params)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml") as tempf:
            self._write_config(tempf)
            expected = self._get_expected_pipeline_run_config()
            output = pipeline_runner.PipelineRunConfig.from_file(tempf.name)
            self.assertEqual(expected, output)


class RunTest(unittest.TestCase):
    """Tests `run` function."""

    @mock.patch.object(vertex, "PipelineJob", autospec=True)
    def test_default_run_config(self, mock_pipeline_job):
        """It tests running the pipeline using default run config values."""
        pipeline_params = {"name": "World"}
        run_config = pipeline_runner.PipelineRunConfig(
            pipeline_name="Sample pipeline",
            pipeline_path="/path/to/pipeline.json",
            gcs_root_path="gs://some-staging-bucket",
            location="us-central1",
        )
        output = pipeline_runner.run(run_config, pipeline_params)
        self.assertIsInstance(output, str)
        mock_pipeline_job.assert_called_once_with(
            display_name=run_config.pipeline_name,
            job_id=mock.ANY,
            template_path=run_config.pipeline_path,
            pipeline_root=run_config.gcs_root_path,
            parameter_values=pipeline_params,
            enable_caching=run_config.enable_caching,
            location=run_config.location,
        )
        mock_pipeline_job.return_value.run.assert_called_once_with(
            service_account=run_config.service_account, sync=run_config.sync
        )
