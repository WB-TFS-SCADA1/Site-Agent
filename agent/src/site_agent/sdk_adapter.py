"""Optional OpenAI integration. Importing the offline runner does not load this."""

import asyncio
from agents import Agent, ModelSettings, OpenAIResponsesModel, Runner, RunConfig
from agents import function_tool, set_tracing_disabled
from openai import AsyncOpenAI
from pydantic import BaseModel, ConfigDict, Field

from .instructions import INSTRUCTIONS
from .schemas import canonical_json
from .tools import get_build_capabilities


class PlanningAdvice(BaseModel):
    model_config = ConfigDict(extra="forbid")
    summary: str = Field(max_length=4000)
    questions: list[str] = Field(max_length=20)
    suggested_checks: list[str] = Field(max_length=20)


@function_tool(name_override="get_build_capabilities")
async def capabilities_tool() -> list[dict[str, str]]:
    """Return the implementation status of the four artifact-build operations."""
    return get_build_capabilities()


def make_agent(model) -> Agent:
    return Agent(
        name="Site artifact planning starter",
        instructions=INSTRUCTIONS,
        model=model,
        model_settings=ModelSettings(max_tokens=1200, parallel_tool_calls=False, store=False),
        tools=[capabilities_tool],
        output_type=PlanningAdvice,
    )


async def run_with_model(request: dict, model, *, timeout: float = 60) -> dict:
    """Also accepts an SDK test model, allowing a real agent loop without HTTP."""
    set_tracing_disabled(True)
    result = await asyncio.wait_for(
        Runner.run(
            make_agent(model), canonical_json(request), max_turns=4,
            run_config=RunConfig(tracing_disabled=True, trace_include_sensitive_data=False),
        ), timeout=timeout,
    )
    return PlanningAdvice.model_validate(result.final_output).model_dump()


async def get_live_advice(request: dict, api_key: str, model_name: str) -> dict:
    # Explicit endpoint: this starter does not implement corporate proxy/provider routing.
    async with AsyncOpenAI(api_key=api_key, base_url="https://api.openai.com/v1",
                           timeout=30, max_retries=0) as client:
        model = OpenAIResponsesModel(model=model_name, openai_client=client)
        return await run_with_model(request, model)
