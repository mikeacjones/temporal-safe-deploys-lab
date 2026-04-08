import asyncio
import os

from temporalio.client import Client
from temporalio.common import VersioningBehavior, WorkerDeploymentVersion
from temporalio.worker import Worker, WorkerDeploymentConfig

from src.activities import (
    execute_research_step,
    fact_check,
    plan_research,
    synthesize_findings,
)
from src.workflows import ResearchPollingWorkflow, ResearchWorkflow

TASK_QUEUE = "research-agent"
DEPLOYMENT_NAME = os.environ.get("TEMPORAL_DEPLOYMENT_NAME", "research-agent")
BUILD_ID = os.environ.get("TEMPORAL_WORKER_BUILD_ID", "local-dev")


async def main() -> None:
    client = await Client.connect(
        os.environ.get("TEMPORAL_ADDRESS", "localhost:7233"),
        namespace=os.environ.get("TEMPORAL_NAMESPACE", "default"),
    )

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[ResearchWorkflow, ResearchPollingWorkflow],
        activities=[
            plan_research,
            execute_research_step,
            synthesize_findings,
            fact_check,
        ],
        deployment_config=WorkerDeploymentConfig(
            version=WorkerDeploymentVersion(
                deployment_name=DEPLOYMENT_NAME,
                build_id=BUILD_ID,
            ),
            use_worker_versioning=True,
            default_versioning_behavior=VersioningBehavior.PINNED,
        ),
    )

    print(f"Worker started on task queue '{TASK_QUEUE}' "
          f"(deployment={DEPLOYMENT_NAME}, build={BUILD_ID})")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
