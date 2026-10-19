"""Optional real-SDK loop with a fake model. No credentials or network required."""
import asyncio
import importlib.util
import json
import unittest
from unittest import mock

SDK_INSTALLED = importlib.util.find_spec("agents") is not None


@unittest.skipUnless(SDK_INSTALLED, "Install agent/requirements-live.txt for SDK contract tests")
class SDKContractTests(unittest.TestCase):
    def test_tool_round_trip_and_structured_output_without_network(self):
        from agents import Model, ModelResponse, Usage
        from openai.types.responses import ResponseFunctionToolCall, ResponseOutputMessage, ResponseOutputText
        from site_agent.sdk_adapter import run_with_model

        class FakeModel(Model):
            def __init__(self):
                self.calls = 0

            async def get_response(self, *args, **kwargs):
                self.calls += 1
                if self.calls == 1:
                    output = [ResponseFunctionToolCall(
                        id="test-call", call_id="test-call", type="function_call",
                        name="get_build_capabilities", arguments="{}")]
                else:
                    history = kwargs.get("input", args[1] if len(args) > 1 else [])
                    tool_results = [item for item in history
                                    if isinstance(item, dict) and item.get("type") == "function_call_output"]
                    if not tool_results or "NOT_IMPLEMENTED" not in str(tool_results):
                        raise AssertionError("SDK did not return the capability tool result")
                    advice = {"summary": "Build adapter remains unimplemented.",
                              "questions": [], "suggested_checks": ["Verify selected source hash"]}
                    output = [ResponseOutputMessage(
                        id="test-output", type="message", role="assistant", status="completed",
                        content=[ResponseOutputText(type="output_text", text=json.dumps(advice), annotations=[])])]
                return ModelResponse(output=output, usage=Usage(), response_id=None)

            async def stream_response(self, *args, **kwargs):
                raise NotImplementedError
                yield  # SDK requires an async iterator implementation.

        model = FakeModel()
        with mock.patch("socket.socket.connect", side_effect=AssertionError("network")):
            result = asyncio.run(run_with_model({"donor_site": "Synthetic"}, model))
        self.assertEqual(model.calls, 2)
        self.assertEqual(result["summary"], "Build adapter remains unimplemented.")
        self.assertNotIn("status", result)

    def test_model_advice_cannot_set_release_status(self):
        from pydantic import ValidationError
        from site_agent.sdk_adapter import PlanningAdvice
        with self.assertRaises(ValidationError):
            PlanningAdvice(summary="Done", questions=[], suggested_checks=[], status="ARTIFACTS_READY")


if __name__ == "__main__":
    unittest.main()
