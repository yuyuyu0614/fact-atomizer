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
2. Contains a clear subject-verb-object structure
3. Is a direct claim from the text — do NOT infer, summarize, or add information not present
4. Does NOT include: opinions, rhetorical questions, greetings, URLs, or meta-commentary

## Entity extraction rules
- entities_mentioned should only include FACTUAL SUBJECTS (people, organizations, brands, locations, laws, regulations, products).
- EXCLUDE: tools used for reporting (camera, UV light, fluorescent pen), measurement instruments, journalistic props.
- EXCLUDE: generic nouns that are not named entities (guest, reporter, hotel guest — unless part of a specific named entity).
- If unsure whether something is a factual subject, leave it out.

## Claim type classification
Use these precise types:
- "regulatory": government/official announcement, regulatory action, legal filing, law/policy citation
- "inspection": official inspection, sampling result, health/safety test data from authority
- "numeric": specific number, statistic, percentage, financial figure
- "event": a specific event that occurred at a specific time/place
- "causal": cause-effect relationship (X leads to Y)
- "attribution": someone said/claimed/announced something
- "legal_obligation": a legal duty, mandatory requirement, regulatory standard
- "existence": a state of being or descriptive fact (use sparingly — prefer more specific types)

## Confidence calibration
- "certain": official government announcement, regulatory action, published inspection data, law/regulation text, named source with specific numbers
- "likely": media report citing named sources, company announcement, widely reported event
- "uncertain": anonymous source, single unverified claim, speculative statement, journalist observation without official confirmation

IMPORTANT: Any claim citing a government regulator (market supervision bureau, health commission), official inspection results, or law/policy text should be marked "certain".

## Splitting rules
- Split different factual assertions into separate claims.
- BUT: if multiple clauses are cited together as a single legal/regulatory obligation (e.g., "Article X and Article Y both require..."), keep them as ONE claim describing the combined obligation.
- If the original text presents them as a list of parallel requirements from the same legal source, merge into one claim.
- If they come from different sources or different sentences, split.

## Output format
Return ONLY a JSON object with this structure:
{
  "claims": [
    {
      "claim_id": 1,
      "claim_text": "The factual statement, as a complete sentence in the original language.",
      "entities_mentioned": ["Entity1", "Entity2"],
      "claim_type": "regulatory/inspection/numeric/event/causal/attribution/legal_obligation/existence",
      "confidence": "certain/likely/uncertain"
    }
  ]
}

Note: confidence reflects the SOURCE reliability, not the truth of the claim itself.
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