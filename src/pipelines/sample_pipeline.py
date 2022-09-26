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

"""Sample Kubeflow pipeline."""


import kfp
from kfp.v2 import dsl


@dsl.component(base_image="python:3.10", packages_to_install=["cloudpathlib==0.10.0"])
def _save_message_to_file(message: str, gcs_filepath: str) -> None:
    """Saves a given message to a given file in GCS."""
    import cloudpathlib as cpl

    with cpl.CloudPath(gcs_filepath).open("w") as fp:
        fp.write(message)


@kfp.dsl.pipeline(name="sample-pipeline")
def pipeline(message: str, gcs_filepath: str) -> None:
    """Sample Kubeflow pipeline definition."""
    _save_message_to_file(message, gcs_filepath)
