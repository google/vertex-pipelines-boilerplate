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

"""Runs a Kubeflow pipeline in Vertex AI Pipelines."""

from __future__ import annotations

import dataclasses
from typing import Any, Dict, Optional

from google.cloud import aiplatform as vertex
import yaml

from pipelines import utils


@dataclasses.dataclass
class PipelineRunConfig:
    """Vertex Pipelines pipeline run configuration.

    Attributes:
        pipeline_name: Display name of the pipeline job in Vertex AI Pipelines.
        pipeline_path: Location of the pipeline specification file.
        gcs_root_path: GCS path to store data generated during pipeline execution.
        location: GCP location to use for running the pipeline, e.g. us-central1.
        enable_caching: If True, enable caching of pipeline runs.
        service_account: Service account to use.
        sync: Whether to execute this method synchronously.
            If False, this method will unblock and it will be executed in a concurrent
            Future.
    """

    pipeline_name: str
    pipeline_path: str
    gcs_root_path: str
    location: str
    enable_caching: bool = True
    service_account: Optional[str] = None
    sync: bool = True

    @classmethod
    def from_file(cls, filepath: str) -> PipelineRunConfig:  # noqa: ANN102
        """Creates a `PipelineRunConfig` instance from a YAML config file."""
        with open(filepath) as fp:
            data = yaml.safe_load(fp)
        run_config = cls(
            pipeline_name=data["pipeline-name"],
            pipeline_path=data["pipeline-path"],
            gcs_root_path=data["gcs-root-path"],
            location=data["location"],
        )
        for attr_name in ("enable-caching", "service-account", "sync"):
            if attr_name in data:
                attr_name_underscore = attr_name.replace("-", "_")
                setattr(run_config, attr_name_underscore, data[attr_name])
        return run_config


def run(
    run_config: PipelineRunConfig,
    pipeline_params: Dict[str, Any],
) -> str:
    """Runs a Kubeflow pipeline given by specification file.

    Args:
        run_config: Vertex Pipelines pipeline run configuration.
        pipeline_params: Kubeflow pipeline parameters

    Returns:
        Vertex Pipelines job ID.
    """
    job_id = utils.get_job_id(run_config.pipeline_name)
    vertex.PipelineJob(
        display_name=run_config.pipeline_name,
        job_id=job_id,
        template_path=run_config.pipeline_path,
        pipeline_root=run_config.gcs_root_path,
        parameter_values=pipeline_params,
        enable_caching=run_config.enable_caching,
        location=run_config.location,
    ).run(
        service_account=run_config.service_account,
        sync=run_config.sync,
    )
    return job_id
