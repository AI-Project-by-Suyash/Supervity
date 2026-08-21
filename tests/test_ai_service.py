import pytest
from app.llm.provider import DualLLMProvider
from app.llm.prompts import SYSTEM_PROMPT, build_explain_prompt, build_suggest_prompt

@pytest.mark.asyncio
async def test_llm_provider_fallback_orchestration():
    provider = DualLLMProvider()
    # Test deterministic fallback specifically
    prompt = "Recommend a resolution for AMOUNT_MISMATCH"
    result = provider._deterministic_fallback(prompt)
    assert "suggested_action" in result
    assert result["suggested_action"] == "REQUEST_VENDOR_CORRECTION"
    assert "provider_used" in result

@pytest.mark.asyncio
async def test_llm_explain_fallback():
    provider = DualLLMProvider()
    prompt = "Analyze this transaction discrepancy and explain the root cause."
    result = provider._deterministic_fallback(prompt)
    assert "explanation" in result
    assert len(result["evidence_fields"]) > 0

