# Cloud Vertex AI Pipelines boilerplate

Boilerplate code for running one or more Kubeflow pipelines using
Cloud Vertex AI Pipelines.
This implements a simple pipeline and command-line interface for
running the pipeline.

# Environment Setup

## Python Poetry
This project template makes use of Python Poetry for managing package
dependencies, the Python virtual environment for development, and setup of
the project's own Python package.

Visit [Poetry's official website](https://python-poetry.org/docs/)
for installation instructions.
You should install Poetry on your local development machine and outside
of any Python virtual environment.

See `.gitlab-ci.yml` for the version of Poetry that's used for CI.
Note that later versions of Poetry might have some ongoing issues.

## Google Cloud
If using a local shell, make sure you authenticate with your GCP project.
```
gcloud config set project <name of your GCP project>
gcloud auth login --update-adc
```

## Terraform
While you can set up Vertex AI Pipelines in your GCP project following
[this guide](https://cloud.google.com/vertex-ai/docs/pipelines/configure-project)
from the official Cloud website, it may be better to use Terraform to set up
your project in a managed way.

[Install Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli)
on your machine. You should install a version matching the `required_version`
constraint specified in the `terraform/main.tf` file.

Make sure to authenticate with the GCP project you want to use and have the
required permissions to run Terraform.

You can then prepare your GCP project using Terraform through the following
commands.

Initialize a working directory containing Terraform configuration files.
```
cd terraform/
terraform init
````

Create an execution plan, which lets you preview the changes that Terraform
plans to make to your infrastructure.
```
terraform plan
```

Execute the actions proposed by `terraform plan`.
```
terraform apply
```

You may want to define or overwrite certain variables in `variables.tf`.
In particular, to avoid having to specify the project ID every time you
run `terraform plan/apply`, you can create a file called `terraform.tfvars`
and define project-specific settings there.

Example:
```sh
# In terraform/terraform.tfvars
project        = "your-gcp-project-id"
staging_bucket = "bucket-with-unique-global-name"
```


## Pipeline configuration

A Vertex AI pipeline job can be configured through a YAML file.
The project includes `pipeline-run-config.yaml.example` that shows the
required parameters to be defined by the user. You can copy the file
and omit the `.example` suffix and update the parameter values for your
particular GCP project environment.

All the pipeline run config
parameters are defined in `pipelines.pipeline_runner.PipelineRunConfig`.

## Installing the CLI
You can install the pipelines command line interface (CLI) using Poetry
```
poetry install
```

This will make available the `pipelines-cli` command in your shell, which
compiles the pipeline into a JSON specification file and runs the pipeline
using Vertex AI Pipelines.

# Running a pipeline

Before you can run your pipeline, you would first need to compile it and
generate a specification file.
```
pipelines-cli compile <module-name> <function-name> <gcs-output-path>
```

Where `module-name` is the name of a module containing a Kubeflow pipeline
function definition in the `src/pipelines` folder.

Using the included `sample_pipeline.py` as an example:
```
pipelines-cli compile sample_pipeline pipeline gs://path/to/pipeline.json
```

Next, configure the pipeline run parameters. You can copy the sample
pipeline run config file:
```
cp pipeline-run-config.yaml.example pipeline-run-config.yaml
```
And update its parameters.
In particular, you would want to update the values for the following:
1. `pipeline-path`
2. `gcs-root-path`
3. `service-account`

The first should point to the output path you used for compiling the pipeline.

The second should point to the Cloud Storage path where Vertex will store
intermediate files generated as part of the pipeline job. This could be the
same value as `staging_bucket` in `terraform/variables.tf`.

The third should refer to a service account that has permissions for Vertex AI
and Cloud Storage. If you used Terraform to configure your GCP project, you can
use the service account email outputted by `terraform apply`.


Then you can the above pipeline using the CLI:
```
pipelines-cli run \
    pipeline-run-config.yaml \
    -p "message=Hello World!" \
    -p "gcs_filepath=gs://path/to/output/message.txt"
```

Where the `-p` flags indicate that the argument is for the pipeline
(i.e. as opposed to the pipeline runner).

The `gcs-output-path` you used when compiling the pipeline should also be
specified in your pipeline run config file, `pipeline-run-config.yaml`.

# Development and testing

## Terraform linting
When updating Terraform scripts, you can run `terraform validate` to check the
configuration files and `terraform fmt` to autoformat the contents in place.

Additionally, you should install the following Terraform linting tools:
- [TFLint](https://github.com/terraform-linters/tflint)
- [Checkov](https://github.com/bridgecrewio/checkov)

You can check the GitLab CI/CD config file (`.gitlab-ci.yml`) for suggested
versions of the above tools.

Run TFLint
```
tflint terraform
```

Run Checkov
```
checkov --directory terraform
```


## Nox
Python test automation is handled by [Nox](https://nox.thea.codes/en/stable/).
You can install Nox through `pip`:
```
pip install --user --upgrade nox
```

The various types of tests (unit tests, linting, etc.) are managed by Nox,
which you can configure by editing `noxfile.py`.

You can run all the tests locally by simply executing the `nox` command.
```
nox
```

A few useful flags you can enable are `-r`, which reuses the existing
Python virtual environment, and `-s`, which allows you to pick a session
to run

Example:
```
nox -rs lint
```

The above command will run the `lint` session, which invokes `flake8`

You can find all the sessions in `noxfile.py`, which are functions decorated
with `@nox.session`.

## End-to-end testing
An end-to-end test that runs the sample pipeline in Vertex AI Pipelines can be
found in `tests.test_e2e.py`.
This requires configuration parameter values to be defined in a file called
`pipeline-run-config.yaml`. A similar YAML file suffixed by `.example` is
included for reference.

The nox `tests` session will not run the end-to-end test, but you can run it
manually.
```
pytest tests/test_e2e.py
```

## Pre-commit
This template uses
[pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks)
to manage Git pre-commit commands.

Install the package using pip.
```
pip install --user --upgrade pre-commit
```

Configure pre-commit hooks in the `.pre-commit-config.yaml` file.

Install the hooks by running the following command.
```
pre-commit install
```

You can test run pre-commit using the following command
```
pre-commit run -a
```
where the `-a` flag tells it to run on all the files in the repo.

# Documentation
You can autogenerate documentation for your project through the following
Nox command:
```
nox -rs docs
```
Doc generation is handled by [`Sphinx`](https://www.sphinx-doc.org/en/master/).
