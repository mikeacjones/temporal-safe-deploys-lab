from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from src.activities import (
        execute_research_step,
        fact_check,
        plan_research,
        synthesize_findings,
    )
    from src.models import PollingState, ResearchRequest, StepFindings


@workflow.defn
class ResearchWorkflow:
    """Runs a multi-step research pipeline with mocked LLM calls.

    Steps: plan -> (execute step + fact-check) x3 -> (optionally wait for proceed) -> synthesize.
    """

    def __init__(self) -> None:
        self._proceed = False

    @workflow.signal
    async def proceed(self) -> None:
        """Signal the workflow to continue to synthesis."""
        self._proceed = True

    @workflow.run
    async def run(self, topic: str, wait_for_proceed: bool = True) -> str:
        plan = await workflow.execute_activity(
            plan_research,
            topic,
            start_to_close_timeout=timedelta(seconds=30),
        )

        findings: list[StepFindings] = []
        for step in plan.steps:
            result = await workflow.execute_activity(
                execute_research_step,
                step,
                start_to_close_timeout=timedelta(seconds=30),
            )
            await workflow.execute_activity(
                fact_check,
                result,
                start_to_close_timeout=timedelta(seconds=30),
            )
            findings.append(result)

        if wait_for_proceed:
            await workflow.wait_condition(lambda: self._proceed)

        summary = await workflow.execute_activity(
            synthesize_findings,
            args=[topic, findings],
            start_to_close_timeout=timedelta(seconds=30),
        )

        return summary.summary


@workflow.defn
class ResearchPollingWorkflow:
    """Long-running workflow that processes research requests as they arrive.

    Detects version changes and gracefully migrates via continue-as-new.
    """

    def __init__(self) -> None:
        self._pending: list[ResearchRequest] = []
        self._draining: bool = False
        self._wake_up: bool = False

    @workflow.signal
    async def submit_request(self, request: ResearchRequest) -> None:
        self._pending.append(request)

    @workflow.signal
    async def wake_up(self) -> None:
        """Nudge an idle workflow to check for version changes."""
        self._wake_up = True

    @workflow.query
    def pending_count(self) -> int:
        return len(self._pending)

    @workflow.run
    async def run(self, state: PollingState) -> None:
        self._pending = list(state.pending_requests)

        while True:
            await workflow.wait_condition(
                lambda: (
                    len(self._pending) > 0
                    or workflow.info().is_continue_as_new_suggested()
                    or workflow.info().is_target_worker_deployment_version_changed()
                    or self._wake_up
                )
            )
            self._wake_up = False

            if (
                workflow.info().is_continue_as_new_suggested()
                or workflow.info().is_target_worker_deployment_version_changed()
            ):
                self._draining = True
                await workflow.wait_condition(workflow.all_handlers_finished)
                workflow.continue_as_new(
                    PollingState(
                        pending_requests=list(self._pending),
                        completed_count=state.completed_count,
                    ),
                    initial_versioning_behavior=(
                        workflow.ContinueAsNewVersioningBehavior.AUTO_UPGRADE
                    ),
                )

            if self._pending:
                request = self._pending.pop(0)
                await workflow.execute_child_workflow(
                    ResearchWorkflow.run,
                    args=[request.topic, False],
                    id=f"research-{request.request_id}",
                )
                state.completed_count += 1
