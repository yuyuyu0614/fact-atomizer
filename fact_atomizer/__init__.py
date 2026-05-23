"""
fact_atomizer.py — Estimate L0: Fact Atomizer
Input: raw text  →  Output: list of atomic factual claims
Each claim is an independent, verifiable statement.

Design paradigm: 1 class, evaluate() method, zero internal deps, model-switchable.
"""

import json, os
from openai import OpenAI


ATOMIZER_SYSTEM_PROMPT = """You are a Fact Atomizer. Your job is to decompose any text into its atomic factual claims.

## What is an atomic claim?
A single, self-contained statement that:
1. Can be independently verified (true or false) without needing surrounding context
2. Contains a clear subject-verb-object structure with specific entities, dates, or numbers
3. Is a direct claim from the text — do NOT infer, summarize, or add information not present
4. Does NOT include: opinions, rhetorical questions, greetings, formatting, URLs, or meta-commentary

## Rules
- Extract EVERY factual claim. Do not skip any.
- If the text contains a numeric figure, date, named entity, or statistical claim, it MUST be extracted.
- If the text makes a causal claim ("X caused Y"), extract both the causal claim AND the underlying events.
- If a sentence contains multiple independent claims, split them into separate items.
- Do NOT combine claims from different sentences.
- If the text is entirely opinion or contains zero factual claims, return an empty array.

## Output format
Return ONLY a JSON object with this structure:
{
  "claims": [
    {
      "claim_id": 1,
      "claim_text": "The factual statement, in its original language, as a complete sentence.",
      "entities_mentioned": ["Entity1", "Entity2"],
      "claim_type": "numeric/event/causal/attribution/existence",
      "confidence": "certain/likely/uncertain"
    }
  ]
}

confidence guide:
- "certain": directly stated with specific numbers/dates
- "likely": stated but with hedging words
- "uncertain": implied but not explicitly stated
"""

ATOMIZER_USER_TEMPLATE = """Decompose the following text into atomic factual claims.

Text:
{text}

Output JSON:"""


# V1.1 optimization note (do not modify V1.0):
# - For texts with multi-path causal chains (e.g., "X reduces Y through A and B"),
#   add prompt rule: "If a sentence describes multiple independent causal paths,
#   split each path into a separate claim." This improves recall on academic/scientific texts.
class FactAtomizer:
    """Decompose text into atomic, independently-verifiable factual claims."""

    def __init__(self, api_key: str = None, base_url: str = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = base_url or os.environ.get("OPENAI_BASE_URL", None)
        self.model = model
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
        self.client = OpenAI(**client_kwargs)

    def atomize(self, text: str) -> list[dict]:
        """
        Decompose text into atomic claims.

        Args:
            text: Raw text to atomize (any length supported by model context)

        Returns:
            List of claim dicts, each with claim_id, claim_text, entities_mentioned, claim_type, confidence.
            Empty list if no factual claims found.
        """
        user_prompt = ATOMIZER_USER_TEMPLATE.format(text=text)
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": ATOMIZER_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.0,
                max_tokens=2000,
                response_format={"type": "json_object"},
            )
            raw = resp.choices[0].message.content
            result = json.loads(raw)
            claims = result.get("claims", [])
            return claims
        except Exception as e:
            return [{"error": str(e), "claim_id": -1, "claim_text": "", "entities_mentioned": [], "claim_type": "error", "confidence": "uncertain"}]

    def atomize_batch(self, texts: list[str]) -> list[list[dict]]:
        """Batch atomize multiple texts."""
        return [self.atomize(t) for t in texts]