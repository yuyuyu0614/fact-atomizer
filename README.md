# fact-atomizer

**AI-powered fact atomizer.** Input any text, get a list of atomic, independently-verifiable factual claims — each with entity extraction and claim type classification.

---

## What it does

Decomposes text into the smallest independently-verifiable statements. Think of it as "SAFE Step 1: claim decomposition" — the foundation block for any fact-checking pipeline.

| Input | Output |
| --- | --- |
| Raw text (news, policy, product, review...) | `[{ claim_id, claim_text, entities_mentioned, claim_type, confidence }]` |

**Example:** "Tesla delivered 463K vehicles in Q3 2024, up 6.4% YoY" → 4 atomic claims, each with specific numbers and entities.

---

## Installation

```bash
pip install fact-atomizer
# or from source:
pip install -e .
```

**Single dependency:** `openai` (>=1.0.0).

---

## Quick Start

```python
from fact_atomizer import FactAtomizer

atomizer = FactAtomizer(api_key="sk-xxx")

claims = atomizer.atomize(
    "2024年Q3特斯拉交付46.3万辆，同比增长6.4%，低于预期47.2万辆。"
)

for c in claims:
    print(f"[{c['claim_type']}] {c['claim_text']}")

# [numeric] 2024年第三季度，特斯拉全球交付46.3万辆汽车。
# [numeric] 同比增长6.4%。
# [numeric] 低于分析师预期的47.2万辆。
# [numeric] 分析师预期47.2万辆。
```

**3 lines of code.**

---

## API Reference

### `FactAtomizer(api_key, base_url=None, model="gpt-4o-mini")`

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `api_key` | `str` | (required) | LLM API key |
| `base_url` | `str` | `None` | Custom endpoint |
| `model` | `str` | `"gpt-4o-mini"` | Model name |

### `atomizer.atomize(text)`

| Parameter | Type | Description |
| --- | --- | --- |
| `text` | `str` | Raw text to decompose |

**Returns:** `list[dict]` — each dict contains:

| Field | Type | Description |
| --- | --- | --- |
| `claim_id` | `int` | Sequential ID |
| `claim_text` | `str` | The atomic claim, as a complete sentence |
| `entities_mentioned` | `list[str]` | Named entities in the claim |
| `claim_type` | `str` | numeric / event / causal / attribution / existence |
| `confidence` | `str` | certain / likely / uncertain |

Returns empty list if text contains zero factual claims (pure opinion).

### `atomizer.atomize_batch(texts)`

Batch version. Takes `list[str]`, returns `list[list[dict]]`.

---

## Supported Models

| Model | Provider | Notes |
| --- | --- | --- |
| **DeepSeek V4 Pro** | DeepSeek | Verified. Chinese-native, 1M context |
| GPT-4o-mini | OpenAI | Fast, cheap |
| GPT-4o | OpenAI | Higher quality |
| Any OpenAI-compatible | Custom | `model="..."`, `base_url="..."` |

---

## Verified Performance (5-text benchmark)

| Text Type | Precision | Recall |
| --- | --- | --- |
| Financial news | 0.80 | 0.80 |
| Policy announcement | 1.00 | 1.00 |
| Product specs | 1.00 | 1.00 |
| Pure opinion | — (correctly returns empty) |
| Academic abstract | 1.00 | 0.60 |
| **Average** | **0.76** | **0.68** |

---

## Use Cases

- **Fact-checking pipelines:** First step — decompose text before verification
- **RAG preprocessing:** Split documents into claim-level chunks
- **News analysis:** Extract all factual claims from articles
- **Contract review:** Identify every assertion in legal documents
- **Content moderation:** Detect unsupported claims in user-generated content

---

## Pair with content-quality-judge

L0 (atomize) → L2 (score):

```python
from fact_atomizer import FactAtomizer
from content_quality_judge import ContentQualityJudge

atomizer = FactAtomizer(api_key="sk-xxx")
judge = ContentQualityJudge(api_key="sk-xxx")

claims = atomizer.atomize("Some text with claims...")
for claim in claims:
    quality = judge.evaluate(claim["claim_text"], title, snippet, domain)
    print(f"{claim['claim_text']} → score: {quality['content_quality_score']}")
```

---

## License

MIT