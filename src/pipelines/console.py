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

"""Command line interface."""

from typing import Any, Dict

import click

from pipelines import __version__
from pipelines import pipeline_compiler
from pipelines import pipeline_runner


def _parse_pipeline_args(pipeline_args: Dict[str, Any]) -> Dict[str, Any]:
    """Parses pipeline keyword arguments."""
    args = pipeline_args["param"]
    params = dict([p.split("=") for p in args])
    return params


@click.version_option(version=__version__)
@click.group()
def cli() -> None:  # noqa: D103
    pass


@cli.command()
@click.argument("module_name")
@click.argument("function_name")
@click.argument("output_path")
def compile(module_name: str, function_name: str, output_path: str) -> None:
    """Compiles a pipeline function into a pipeline specification.

    Args:
        module_name: Path to Python module containing pipeline function.
        function_name: Name of pipeline function.
        output_path: Output file path.
    """
    pipeline_compiler.compile(module_name, function_name, output_path)


@cli.command()
@click.argument("run_config_file")
@click.option(
    "-p",
    "--param",
    multiple=True,
    help=(
        "Pipeline-specific params in key=value format."
        " Example: `-p 'message=hello world'`"
    ),
)
def run(run_config_file: str, **pipeline_args: int) -> None:
    """Runs a Kubeflow pipeline in Vertex AI Pipelines.

    RUN_CONFIG_FILE is used to specify the Pipelines job params.
    """  # noqa: DAR101
    pipeline_params = _parse_pipeline_args(pipeline_args)
    run_config = pipeline_runner.PipelineRunConfig.from_file(run_config_file)
    pipeline_runner.run(run_config, pipeline_params)


if __name__ == "__main__":
    cli()
