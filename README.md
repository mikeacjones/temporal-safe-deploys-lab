# Temporal Safe Deploys Lab

Sample project for the [Safe Deployments with Temporal Worker Versioning on Kubernetes](https://syntaxsugar.io/lab/temporal-safe-deploys/) lab.

## Branches

- **`starter`** - Starting point for the lab. Has the research agent workflow and all infrastructure, but no worker versioning configured. Clone this branch to follow along with the lab.
- **`main`** - Completed reference with all versioning pieces in place: `WorkerDeploymentConfig`, `PINNED` workflows, continue-as-new with `AUTO_UPGRADE`, wake-up signal pattern, and draining logic.

## Quick Start

```bash
git clone -b starter https://github.com/mikeacjones/temporal-safe-deploys-lab.git
cd temporal-safe-deploys-lab
uv sync
```

Then follow the lab at [syntaxsugar.io/lab/temporal-safe-deploys/](https://syntaxsugar.io/lab/temporal-safe-deploys/).

## What This Builds

A mocked "research agent" workflow that simulates expensive LLM calls. The lab walks through:

1. Deploying V1 of the agent to Kubernetes
2. Making a breaking change (adding a fact-check step) and seeing it fail
3. Using Worker Versioning to safely deploy changes without losing in-flight work
4. Handling long-running workflows with continue-as-new version migration
5. The sleeping workflow caveat and the wake-up signal pattern
