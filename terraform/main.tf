/**
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

terraform {
  required_version = ">= 0.13.7, <= 1.3.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "3.46"
    }
  }
}

provider "google" {
  project = var.project
  region  = var.region
  zone    = var.zone
}

# Enable Vertex AI
resource "google_project_service" "vertex_ai_api" {
  service                    = "aiplatform.googleapis.com"
  disable_dependent_services = true
}

# Enable Cloud Storage API
resource "google_project_service" "cloud_storage_api" {
  service                    = "storage-component.googleapis.com"
  disable_dependent_services = true
}

# Create a service account for Vertex AI Pipelines
resource "google_service_account" "service_account" {
  account_id   = var.service_account_id
  display_name = var.service_account_display_name
}

# Grant necessary roles to Vertex AI Pipelines service account
resource "google_project_iam_member" "service_account_roles" {
  for_each = toset([
    "roles/aiplatform.user",
    "roles/storage.objectCreator",
    "roles/storage.objectViewer",
  ])
  role   = each.key
  member = "serviceAccount:${google_service_account.service_account.email}"
}

# Create GCS bucket
resource "google_storage_bucket" "staging_bucket" {
  name                        = var.staging_bucket
  storage_class               = "REGIONAL"
  location                    = var.region
  uniform_bucket_level_access = true
  versioning {
    enabled = true
  }
  # checkov:skip=CKV_GCP_62:Skip logging access to another bucket
}
