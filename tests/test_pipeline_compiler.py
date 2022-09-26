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

"""Tests `base.py`."""

import json
import logging
import tempfile
import unittest

import cloudpathlib as cpl

from pipelines import pipeline_compiler


# Disables logging from objects-under-test
logging.disable(logging.CRITICAL)


def _is_json_file(filepath: str) -> bool:
    """Checks whether given `filepath` is a JSON file."""
    filepath_ = cpl.AnyPath(filepath)
    try:
        with filepath_.open() as fp:  # type: ignore[attr-defined]
            json.load(fp)
    except Exception:
        result = False
    else:
        result = True
    return result


class CompileTest(unittest.TestCase):
    """Tests `compile` function."""

    def test_local_output_path(self):
        """It generates a pipeline specification JSON file."""
        module_name = "sample_pipeline"
        function_name = "pipeline"
        with tempfile.NamedTemporaryFile(suffix=".json") as output_path:
            pipeline_compiler.compile(module_name, function_name, output_path.name)
            self.assertTrue(_is_json_file(output_path.name))
