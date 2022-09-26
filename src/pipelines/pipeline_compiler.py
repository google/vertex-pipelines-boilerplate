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

"""Compiles a Kubeflow pipeline."""

import importlib
import logging
import pathlib
import tempfile
from typing import Callable, Union

import cloudpathlib as cpl
from kfp.v2 import compiler


def _get_function_obj(module_name: str, function_name: str) -> Callable:
    """Returns function object given path to module file and function name."""
    module = importlib.import_module(f"pipelines.{module_name}")
    return getattr(module, function_name)


def _is_local_path(path: Union[cpl.AnyPath, cpl.CloudPath, pathlib.Path]) -> bool:
    """Returns True if given path is a local path."""
    return isinstance(path, pathlib.Path)


def _kfp_compile_wrapper(pipeline_func: Callable, package_path: str) -> None:
    """Wrapper around KFP's `Compiler.compile` function."""
    compiler.Compiler().compile(
        pipeline_func=pipeline_func, package_path=str(package_path)
    )


def _compile_pipeline_func(pipeline_func: Callable, package_path_: cpl.AnyPath) -> None:
    """Compiles pipeline function into JSON specification."""
    if _is_local_path(package_path_):
        _kfp_compile_wrapper(pipeline_func, str(package_path_))
    else:
        with tempfile.NamedTemporaryFile(suffix=".json") as tempf:
            _kfp_compile_wrapper(pipeline_func, tempf.name)
            package_path_.upload_from(tempf.name)  # type: ignore[abstract,attr-defined]


def compile(module_name: str, function_name: str, package_path: str) -> None:
    """Compiles pipeline function as string into JSON specification."""
    package_path_ = cpl.AnyPath(package_path)
    if package_path_.exists():  # type: ignore[attr-defined]
        logging.warning("Output path already exists. Overwriting...")
    pipeline_func = _get_function_obj(module_name, function_name)
    _compile_pipeline_func(pipeline_func, package_path_)
