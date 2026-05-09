# generate-gliznet-data

**Generation pipeline for [ZSHOT-HARDSET-v2](https://huggingface.co/datasets/alexneakameni/ZSHOT-HARDSET-v2) and [ZSHOT-HARDSET-Polarity](https://huggingface.co/datasets/alexneakameni/ZSHOT-HARDSET-Polarity) — hard-negative zero-shot text classification benchmarks.**

---

## Overview

This repository contains the generation pipelines for two complementary zero-shot text classification datasets. Unlike standard ZSC datasets that rely on surface-level topic matching, these datasets target *semantic* understanding: labels describe meaning, intent, rhetorical stance, and epistemic function — not keywords.

### ZSHOT-HARDSET-v2 (Wikipedia)

Each example contains:
- `text` — an original short passage (2–3 sentences) written in a specific genre/register
- `labels` — 3–5 labels that are **semantically true** for this text
- `not_labels` — 3–5 labels that are **plausible but wrong**: they would fool a naive classifier but are clearly false to a careful reader

### ZSHOT-HARDSET-Polarity (Amazon Reviews)

Each example contains:
- `text` — an Amazon product review (title + content)
- `sentiment` — the ground-truth sentiment (`positive` / `negative`)
- `labels` — **50** labels that are semantically true for this review
- `not_labels` — **50** labels that are plausible but wrong

The key difference from the Wikipedia variant is the **scale of labels**: 50 positive and 50 negative labels per example, requiring fine-grained semantic distinctions about rhetorical stance, emotional register, argumentative moves, writing style, and epistemic signals.

---

## Generation Pipelines

### Wikipedia Pipeline (ZSHOT-HARDSET-v2)

#### 1. Source: Wikipedia (streaming)
Articles are sampled from the `wikimedia/wikipedia 20231101.en` split via HuggingFace Datasets in streaming mode with a large shuffle buffer. Wikipedia provides broad topical diversity while keeping content grounded in factual reality.

#### 2. Genre injection (70 registers)
Each Wikipedia article is paired with a randomly sampled **genre** from a vocabulary of 70 text registers, spanning:
- Factual: encyclopedia entry, academic abstract, empirical paper finding, patent claim …
- Journalistic: news article lede, investigative journalism, tabloid lede …
- Conversational: Reddit post, forum Q&A, podcast transcript, chat/SMS …
- Creative / narrative: myth retelling, documentary narration, song lyrics, children's book …
- Institutional: legal document, press release, diplomatic statement, parliamentary debate …
- Personal: diary entry, eulogy, oral history, customer complaint …
- And many more

This forces the model to rewrite factual content into diverse registers, producing texts that vary in rhetorical stance, epistemic function, and social context — not just topic.

#### 3. LLM generation (vLLM)
Bundles of **5 texts + 18 shared semantic labels** are generated per article using a local LLM served via vLLM. The prompt enforces three hard constraints:
- Labels must capture *meaning and intent*, not surface vocabulary
- Every label must appear as a **positive** in at least one text and a **negative** in at least one different text (cross-role constraint)
- `not_labels` must require actually reading the text to rule out — not obviously unrelated

Model: `Jackrong/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled` (reasoning-distilled, 27B)

#### 4. Post-processing
- Bundles are parsed and validated; malformed JSON is discarded
- Rows with the same text are merged: `labels` and `not_labels` are unioned, and any intersection is removed from `not_labels`

#### 5. Train / Test split
The dataset uses a label-based split to encourage zero-shot evaluation:
1. A small fraction of positive labels is randomly selected as held-out test labels
2. Rows containing at least one held-out label in `labels` are assigned to **test**
3. Rows where any held-out label appears in either `labels` or `not_labels` are excluded from **train**

This yields ~30% novel labels in the test set (labels never seen during training), forcing the model to generalise to unseen semantic categories.

### Amazon Polarity Pipeline (ZSHOT-HARDSET-Polarity)

#### 1. Source: Amazon Polarity
Reviews are streamed from `fancyzhx/amazon_polarity` via HuggingFace Datasets. Each review includes a title, content, and binary sentiment label.

#### 2. LLM annotation
Each review is annotated by an LLM that generates **50 positive labels** and **50 negative labels** per review. Labels describe:
- Rhetorical stance (what claim the reviewer is making and how)
- Emotional register (feeling the text conveys or appeals to)
- Argumentative moves (evidence or reasoning structure)
- Implied relationship to the product (expert, casual buyer, gift buyer…)
- Writing style markers (colloquial, formal, hyperbolic, hedged…)
- Epistemic signals (certainty, doubt, recommendation, warning…)
- Discourse function (introduces, contrasts, exemplifies, concedes…)

Labels are short `snake_case` phrases (2–5 words) and must **not** include product names, brands, category keywords, or generic sentiment words.

#### 3. Post-processing
- Parsed and validated; malformed JSON or under-generated annotations (< 5 labels) are discarded
- Any label appearing in both `labels` and `not_labels` is removed from both lists

---

## Repository Structure

```
generate-gliznet-data/
├── main.py                  # Wikipedia pipeline: stream, generate, write JSONL
├── annotate_amazon.py       # Amazon Polarity pipeline: annotate reviews
├── launch.sh                # Launch command for Wikipedia generation
├── launch_amazon.sh         # Launch command for Amazon annotation (local vLLM)
├── launch_amazon_openrouter.sh  # Launch command for Amazon annotation (OpenRouter)
├── src/
│   ├── prompt.py            # System prompt for Wikipedia generation
│   ├── prompt_amazon.py     # System prompt for Amazon annotation
│   ├── genres.py            # 70 text genre definitions
│   └── config.py            # Token budget and generation constants
├── notebooks/
│   └── CreateDataset.ipynb  # Load JSONL → merge → split → push to HF Hub
└── data/                    # Generated JSONL files (gitignored)
```

---

## Quickstart

```bash
pip install vllm datasets tqdm llm-output-parser

python main.py \
    --output_path data/wikipedia_synthetic.jsonl \
    --model Jackrong/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled \
    --num_examples 64000 \
    --batch_size 16 \
    --tensor_parallel_size 2 \
    --max_tokens 4096 \
    --temperature 0.9 \
    --seed 42 \
    --shuffle_buffer 50000
```

---

## Links

- **ZSHOT-HARDSET-v2 (Wikipedia)**: [alexneakameni/ZSHOT-HARDSET-v2](https://huggingface.co/datasets/alexneakameni/ZSHOT-HARDSET-v2)
- **ZSHOT-HARDSET-Polarity (Amazon)**: [alexneakameni/ZSHOT-HARDSET-Polarity](https://huggingface.co/datasets/alexneakameni/ZSHOT-HARDSET-Polarity)
- **Generation code**: [KameniAlexNea/generate-gliznet-data](https://github.com/KameniAlexNea/generate-gliznet-data)

---

## License

See [LICENSE](LICENSE).
