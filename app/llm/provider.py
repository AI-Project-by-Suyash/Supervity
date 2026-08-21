import json
import logging
import re
import httpx
from typing import Dict, Any, Optional, List
from app.core.config import settings

logger = logging.getLogger(__name__)

class DualLLMProvider:
    """
    Orchestrates high-speed Groq inference with automatic failover to NVIDIA NIM
    and deterministic offline fallback.
    """
    def __init__(self):
        self.groq_api_key = settings.GROQ_API_KEY
        deprecated_map = {
            "llama-3.3-70b-versatile": "openai/gpt-oss-120b",
            "nvidia/nemotron-3.5-lightning-30b-a3b": "meta/llama-3.1-8b-instruct"
        }
        primary_groq = deprecated_map.get(settings.GROQ_MODEL, settings.GROQ_MODEL)
        self.groq_models = list(dict.fromkeys([primary_groq, "openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.6-27b"]))
        
        self.nvidia_api_key = settings.NVIDIA_API_KEY
        primary_nvidia = deprecated_map.get(settings.NVIDIA_MODEL, settings.NVIDIA_MODEL)
        self.nvidia_models = list(dict.fromkeys([primary_nvidia, "meta/llama-3.1-8b-instruct", "meta/llama-3.1-70b-instruct"]))
        self.nvidia_base_url = settings.NVIDIA_BASE_URL.rstrip('/')

    async def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        # 1. Try Groq Models
        if self.groq_api_key:
            for model_name in self.groq_models:
                try:
                    result = await self._call_groq(model_name, system_prompt, user_prompt)
                    if result:
                        result['provider_used'] = f"Groq ({model_name})"
                        return result
                except Exception as e:
                    logger.warning(f"Groq model {model_name} failed: {e}. Trying next model...")

        # 2. Try NVIDIA NIM Models
        if self.nvidia_api_key:
            for model_name in self.nvidia_models:
                try:
                    result = await self._call_nvidia(model_name, system_prompt, user_prompt)
                    if result:
                        result['provider_used'] = f"NVIDIA NIM ({model_name})"
                        return result
                except Exception as e:
                    logger.warning(f"NVIDIA NIM model {model_name} failed: {e}. Trying next model...")

        # 3. Deterministic Offline Fallback
        return self._deterministic_fallback(user_prompt)

    async def _call_groq(self, model: str, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
            "max_tokens": 800
        }
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                content = data['choices'][0]['message']['content']
                return self._parse_json(content)
            else:
                raise Exception(f"Groq API HTTP {resp.status_code}: {resp.text}")

    async def _call_nvidia(self, model: str, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        url = f"{self.nvidia_base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.nvidia_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 800
        }
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                content = data['choices'][0]['message']['content']
                return self._parse_json(content)
            else:
                raise Exception(f"NVIDIA API HTTP {resp.status_code}: {resp.text}")

    def _parse_json(self, raw_text: str) -> Dict[str, Any]:
        """Extract and parse clean JSON from model output."""
        text = raw_text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        # Regex fallback to find JSON block
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        return json.loads(text)

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

