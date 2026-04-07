import asyncio
import os

from temporalio.client import Client
from temporalio.worker import Worker

from src.activities import (
    execute_research_step,
    fact_check,
    plan_research,
    synthesize_findings,
)
from src.workflows import ResearchPollingWorkflow, ResearchWorkflow

TASK_QUEUE = "research-agent"


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
    )

    print(f"Worker started on task queue '{TASK_QUEUE}'")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
