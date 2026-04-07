from temporalio import activity

from src.models import (
    FactCheckResult,
    ResearchPlan,
    ResearchStep,
    ResearchSummary,
    StepFindings,
)
from src import mock_llm


@activity.defn
async def plan_research(topic: str) -> ResearchPlan:
    result = await mock_llm.plan_research(topic)
    return ResearchPlan(
        topic=result["topic"],
        steps=[ResearchStep(**s) for s in result["steps"]],
    )


@activity.defn
async def execute_research_step(step: ResearchStep) -> StepFindings:
    findings = await mock_llm.execute_step(step.title, step.description)
    return StepFindings(step_title=step.title, findings=findings)


@activity.defn
async def synthesize_findings(
    topic: str, findings: list[StepFindings]
) -> ResearchSummary:
    all_text = [f.findings for f in findings]
    summary = await mock_llm.synthesize(topic, all_text)
    return ResearchSummary(
        topic=topic, summary=summary, steps_completed=len(findings)
    )


@activity.defn
async def fact_check(findings: StepFindings) -> FactCheckResult:
    result = await mock_llm.fact_check(findings.findings)
    return FactCheckResult(
        original_summary=findings.findings,
        corrections=result["corrections"],
        verified_summary=result["verified_summary"],
    )
