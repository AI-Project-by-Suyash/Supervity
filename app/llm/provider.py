import json
import logging
import httpx
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class DualLLMProvider:
    """
    Orchestrates Groq as ultra-fast primary inference with automatic failover
    to NVIDIA NIM upon timeout, rate limits (429), or 5xx errors, plus deterministic offline fallback.
    """
    def __init__(self):
        self.groq_api_key = settings.GROQ_API_KEY
        self.groq_model = settings.GROQ_MODEL
        self.nvidia_api_key = settings.NVIDIA_API_KEY
        self.nvidia_model = settings.NVIDIA_MODEL
        self.nvidia_base_url = settings.NVIDIA_BASE_URL.rstrip('/')

    async def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        # Try Primary: Groq
        if self.groq_api_key:
            try:
                result = await self._call_groq(system_prompt, user_prompt)
                if result:
                    result['provider_used'] = 'Groq (llama-3.3-70b-versatile)'
                    return result
            except Exception as e:
                logger.warning(f"Groq primary LLM failed: {e}. Attempting failover to NVIDIA NIM.")

        # Try Secondary: NVIDIA NIM
        if self.nvidia_api_key:
            try:
                result = await self._call_nvidia(system_prompt, user_prompt)
                if result:
                    result['provider_used'] = 'NVIDIA NIM (nemotron-3.5-lightning)'
                    return result
            except Exception as e:
                logger.warning(f"NVIDIA NIM failover failed: {e}. Falling back to deterministic reasoning.")

        # Deterministic Offline Fallback
        return self._deterministic_fallback(user_prompt)

    async def _call_groq(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.groq_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
            "max_tokens": 800
        }
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                content = data['choices'][0]['message']['content']
                return json.loads(content)
            elif resp.status_code == 429:
                logger.warning("Groq rate limit 429 encountered.")
                raise Exception("Groq rate limited")
            else:
                raise Exception(f"Groq API error HTTP {resp.status_code}: {resp.text}")

    async def _call_nvidia(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        url = f"{self.nvidia_base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.nvidia_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.nvidia_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 1000
        }
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                content = data['choices'][0]['message']['content']
                # Clean codeblock markdown if present
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0].strip()
                elif '```' in content:
                    content = content.split('```')[1].split('```')[0].strip()
                return json.loads(content)
            else:
                raise Exception(f"NVIDIA API error HTTP {resp.status_code}: {resp.text}")

    def _deterministic_fallback(self, user_prompt: str) -> Dict[str, Any]:
        """Grounded rule-based synthesis for offline/unreachable LLM scenarios."""
        is_suggestion = "Recommend a resolution" in user_prompt
        if is_suggestion:
            if "AMOUNT_MISMATCH" in user_prompt:
                action = "REQUEST_VENDOR_CORRECTION"
                reason = "Grounded Rule Engine: Invoice billed amount deviates from approved Purchase Order beyond allowed tolerance threshold."
                score = 0.94
            elif "QUANTITY_MISMATCH" in user_prompt:
                if "null (missing)" in user_prompt:
                    action = "ESCALATE_TO_HUMAN"
                    reason = "Grounded Rule Engine: Delivered quantity is unrecorded in goods receipt manifest; manual investigation required."
                    score = 0.60
                else:
                    action = "REQUEST_QUANTITY_REVIEW"
                    reason = "Grounded Rule Engine: Received quantity differs from ordered quantity on purchase order."
                    score = 0.88
            else:
                action = "REQUEST_PAYMENT_REVIEW"
                reason = "Grounded Rule Engine: Invoice past due date; verified AP payment terms review recommended."
                score = 0.82
            return {
                "suggested_action": action,
                "reason": reason,
                "ai_score": score,
                "evidence_fields": ["variance", "invoice.amount", "purchase_order.amount"],
                "provider_used": "Deterministic Rule Engine (Offline Fallback)"
            }
        else:
            return {
                "explanation": "Grounded Root-Cause Summary: Transaction discrepancy identified via deterministic evaluation of invoice, purchase order, and delivery manifests.",
                "evidence_fields": ["variance", "invoice.amount", "purchase_order.amount"],
                "provider_used": "Deterministic Rule Engine (Offline Fallback)"
            }

llm_provider = DualLLMProvider()
