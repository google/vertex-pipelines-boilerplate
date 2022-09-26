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

"""Utility functions."""

import datetime
import os
from typing import Optional


def get_timestamp() -> str:
    """Returns current date and time in YYYYMMDD-HHMMSS format."""
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


def get_job_id(prefix: str, username: Optional[str] = None) -> str:
    """Generates a unique ID for a pipeline job.

    Args:
        prefix: String prefix to prepend to the job ID.
        username: Optional username to append to the job ID.
            If this is not specified, the username will be sourced from
            the USER environmental variable, if it is set.

    Returns:
        ID string.
    """
    job_id = f"{prefix}-{get_timestamp()}"
    username = username or os.environ.get("USER")
    if username:
        job_id += f"-{username}"
    return job_id
