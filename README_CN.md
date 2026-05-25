# fact-atomizer

**AI 驱动的事实原子化器。** 输入任意文本，输出可独立验证的原子事实列表——每条事实附带实体提取和类型分类。

---

## 它能做什么

将文本拆解为最小的、可独立验证的陈述。灵感来自 Google DeepMind SAFE 论文的“声明拆分”步骤。

| 输入 | 输出 |
| --- | --- |
| 任意文本（新闻、公告、产品介绍、评论...） | `[{ claim_id, claim_text, entities_mentioned, claim_type, confidence }]` |

**示例：** “2024年Q3特斯拉交付46.3万辆，同比增长6.4%，低于预期47.2万辆。” → 4条原子事实。

---

## 安装

```bash
pip install fact-atomizer
```

**唯一依赖：** `openai` (>=1.0.0)。

---

## 快速开始

```python
from fact_atomizer import FactAtomizer

atomizer = FactAtomizer(api_key="sk-xxx")

claims = atomizer.atomize(
    "2024年Q3特斯拉交付46.3万辆，同比增长6.4%，低于预期47.2万辆。"
)

for c in claims:
    print(f"[{c['claim_type']}] {c['claim_text']}")
```

**3 行代码。** 这就是全部公开 API。

---

## API 参数

### `FactAtomizer(api_key, base_url, model)`

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `api_key` | str | 必填 | LLM API 密钥 |
| `base_url` | str | `None` | API 端点地址（可指向 DeepSeek/Ollama 等兼容服务） |
| `model` | str | `"gpt-4o-mini"` | 模型名称 |

### `atomize(text)`

**返回值：** `list[dict]`，每个字典包含：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `claim_id` | int | 声明编号 |
| `claim_text` | str | 原子事实陈述 |
| `entities_mentioned` | list[str] | 涉及实体 |
| `claim_type` | str | 声明类型：regulatory / inspection / numeric / event / causal / attribution / legal_obligation / existence |
| `confidence` | str | 信源可信度：certain / likely / uncertain |

---

## 支持的模型

任何兼容 OpenAI 协议的模型均可使用，已验证：

| 模型 | 说明 |
| --- | --- |
| **DeepSeek V4 Pro** | ✅ 已验证，推荐 |
| **GPT-4o-Mini** | ✅ 已验证 |
| **Ollama 本地模型** | ✅ 兼容（base_url 指向本地地址） |

---

## 与 Estimate 生态组合使用

```python
# L0: 原子化
from fact_atomizer import FactAtomizer
atomizer = FactAtomizer(api_key="sk-xxx", base_url="https://api.deepseek.com/v1", model="deepseek-v4-pro")
claims = atomizer.atomize("惠州监管部门立案调查涉事酒店...")

# L2: 内容质量评分（需安装 content-quality-judge）
# L3: 决策融合（需安装 decision-fusion）
```

---

## 验证结果

5类文本测试（新闻/公告/产品介绍/评论/学术摘要）：

| 指标 | 数值 |
| --- | --- |
| **Precision（精确率）** | 0.76 |
| **Recall（召回率）** | 0.68 |

---

## 许可

MIT