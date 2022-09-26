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

"""Tests `utils.py`."""

import os
import unittest
from unittest import mock

from freezegun import api as fgapi

from pipelines import utils


class GetTimestampTest(unittest.TestCase):
    """Tests `get_timestamp`."""

    @fgapi.freeze_time("2022-01-01 04:02:00")
    def test_get_timestamp_ok(self):
        """It generates a timestamp correctly."""
        expected = "20220101-040200"
        output = utils.get_timestamp()
        self.assertEqual(expected, output)


class GetJobIdTest(unittest.TestCase):
    """Tests `get_job_id`."""

    def setUp(self):  # noqa: D102
        self.prefix = "some-prefix"
        self.mock_env = mock.patch.dict(os.environ, {"USER": ""}).start()
        self.timestamp = "20220101-040200"
        self.mock_get_timestamp = mock.patch.object(
            utils, "get_timestamp", return_value=self.timestamp
        ).start()
        self.job_id_base = f"{self.prefix}-{self.timestamp}"
        self.username = "some-user"

    def tearDown(self):  # noqa: D102
        mock.patch.stopall()

    def test_job_id_with_no_username(self):
        """It returns a job ID with no username."""
        expected = self.job_id_base
        output = utils.get_job_id(self.prefix)
        self.assertEqual(expected, output)

    def test_job_id_with_username_from_env_variable(self):
        """It returns a job ID with a username from USER env variable."""
        expected = f"{self.job_id_base}-{self.username}"
        with mock.patch.dict(os.environ, {"USER": self.username}):
            output = utils.get_job_id(self.prefix)
        self.assertEqual(expected, output)

    @mock.patch.dict(os.environ, {"USER": "ignored-user"})
    def test_job_id_with_username_from_arg(self):
        """It returns a job ID with username specified in argument."""
        expected = f"{self.job_id_base}-{self.username}"
        output = utils.get_job_id(self.prefix, username=self.username)
        self.assertEqual(expected, output)
