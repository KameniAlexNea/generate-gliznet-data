# generate-gliznet-data

**Generation pipeline for [ZSHOT-HARDSET-v2](https://huggingface.co/datasets/alexneakameni/ZSHOT-HARDSET-v2) — a hard-negative zero-shot text classification benchmark.**

---

## Overview

ZSHOT-HARDSET-v2 is a synthetic dataset designed to train and evaluate **zero-shot text classification** models. Unlike standard ZSC datasets that rely on surface-level topic matching, this dataset targets *semantic* understanding: labels describe meaning, intent, rhetorical stance, and epistemic function — not keywords.

Each example in the dataset contains:
- `text` — an original short passage (2–3 sentences) written in a specific genre/register
- `labels` — 3–5 labels that are **semantically true** for this text
- `not_labels` — 3–5 labels that are **plausible but wrong**: they would fool a naive classifier but are clearly false to a careful reader

---

## Generation Pipeline

### 1. Source: Wikipedia (streaming)
Articles are sampled from the `wikimedia/wikipedia 20231101.en` split via HuggingFace Datasets in streaming mode with a large shuffle buffer. Wikipedia provides broad topical diversity while keeping content grounded in factual reality.

### 2. Genre injection (70 registers)
Each Wikipedia article is paired with a randomly sampled **genre** from a vocabulary of 70 text registers, spanning:
- Factual: encyclopedia entry, academic abstract, empirical paper finding, patent claim …
- Journalistic: news article lede, investigative journalism, tabloid lede …
- Conversational: Reddit post, forum Q&A, podcast transcript, chat/SMS …
- Creative / narrative: myth retelling, documentary narration, song lyrics, children's book …
- Institutional: legal document, press release, diplomatic statement, parliamentary debate …
- Personal: diary entry, eulogy, oral history, customer complaint …
- And many more

This forces the model to rewrite factual content into diverse registers, producing texts that vary in rhetorical stance, epistemic function, and social context — not just topic.

### 3. LLM generation (vLLM)
Bundles of **5 texts + 18 shared semantic labels** are generated per article using a local LLM served via vLLM. The prompt enforces three hard constraints:
- Labels must capture *meaning and intent*, not surface vocabulary
- Every label must appear as a **positive** in at least one text and a **negative** in at least one different text (cross-role constraint)
- `not_labels` must require actually reading the text to rule out — not obviously unrelated

Model: `Jackrong/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled` (reasoning-distilled, 27B)

### 4. Post-processing
- Bundles are parsed and validated; malformed JSON is discarded
- Rows with the same text are merged: `labels` and `not_labels` are unioned, and any intersection is removed from `not_labels`

### 5. Train / Test split (label-disjoint)
The dataset uses a **label-disjoint split** to ensure genuine zero-shot evaluation:
1. All positive labels are counted and randomly shuffled
2. Labels are greedily added to a held-out test pool until ~30% of rows are covered
3. A row is assigned to **test** if any of its positive labels is a held-out label
4. **No test label ever appears as a positive label in train** — the model must generalise to truly unseen semantic categories

---

## Repository Structure

```
generate-gliznet-data/
├── main.py                  # Entry point: stream Wikipedia, generate, write JSONL
├── launch.sh                # Example launch command with vLLM parameters
├── src/
│   ├── prompt.py            # System prompt with generation constraints
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

- **Dataset on HuggingFace Hub**: [alexneakameni/ZSHOT-HARDSET-v2](https://huggingface.co/datasets/alexneakameni/ZSHOT-HARDSET-v2)
- **Generation code**: [KameniAlexNea/generate-gliznet-data](https://github.com/KameniAlexNea/generate-gliznet-data)

---

## License

See [LICENSE](LICENSE).
