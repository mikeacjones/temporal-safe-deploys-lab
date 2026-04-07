"""
Mocked LLM responses. Each function simulates an expensive API call
with a sleep delay and returns canned output.

The delays are intentionally long enough that you can observe workflows
in-flight in the Temporal UI and deploy mid-execution.
"""

import asyncio


PLAN_DELAY = 1.0
RESEARCH_DELAY = 5.0  # the expensive one (~15s total for 3 steps)
SYNTHESIS_DELAY = 1.5
FACT_CHECK_DELAY = 1.5


async def plan_research(topic: str) -> dict:
    await asyncio.sleep(PLAN_DELAY)
    return {
        "topic": topic,
        "steps": [
            {
                "title": f"Background on {topic}",
                "description": f"Research the foundational concepts and history of {topic}.",
            },
            {
                "title": f"Current state of {topic}",
                "description": f"Investigate recent developments and the current landscape of {topic}.",
            },
            {
                "title": f"Future outlook for {topic}",
                "description": f"Analyze trends and predictions for the future of {topic}.",
            },
        ],
    }


async def execute_step(step_title: str, step_description: str) -> str:
    await asyncio.sleep(RESEARCH_DELAY)
    return (
        f"Findings for '{step_title}': Based on extensive analysis, "
        f"the research indicates several key insights related to "
        f"'{step_description}'. The evidence suggests significant "
        f"developments in this area with multiple contributing factors. "
        f"[Simulated LLM output - {RESEARCH_DELAY}s of compute time]"
    )


async def synthesize(topic: str, all_findings: list[str]) -> str:
    await asyncio.sleep(SYNTHESIS_DELAY)
    return (
        f"Research Summary for '{topic}': After analyzing {len(all_findings)} "
        f"research areas, the key takeaways are: (1) The field has seen "
        f"substantial growth, (2) Current trends point toward continued "
        f"evolution, and (3) Future developments will likely be shaped by "
        f"emerging technologies. [Synthesized from {len(all_findings)} steps]"
    )


async def fact_check(summary: str) -> dict:
    await asyncio.sleep(FACT_CHECK_DELAY)
    return {
        "original_summary": summary,
        "corrections": [
            "Minor clarification: growth figures should be qualified as estimates.",
        ],
        "verified_summary": summary + " [Fact-checked and verified]",
    }
