#!/usr/bin/env python3
"""
Wikipedia synthetic data generator using vLLM.

Streams the wikimedia/wikipedia 20231101.en subset, picks a random paragraph
from each article, and uses a local LLM via vLLM to produce:
  - An original text INSPIRED by that paragraph.
  - A list of non-trivial `labels`     (what the text IS about).
  - A list of non-trivial `not_labels` (plausible-sounding but wrong labels).

Output: a JSONL file where each line is one generated example:
    {"source": "wikipedia", "text": "...", "labels": [...], "not_labels": [...]}

Usage:
    python generate_wikipedia.py \
        --output_path data/wikipedia_synthetic.jsonl \
        --model Jackrong/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled \
        --num_examples 5000 \
        --batch_size 16 \
        --tensor_parallel_size 2

Requirements:
    pip install vllm datasets tqdm
"""

import argparse
import json
import logging
import math
import random
import sys
from pathlib import Path

from datasets import load_dataset
from llm_output_parser import parse_json
from tqdm import tqdm
from vllm import LLM, SamplingParams

from src.genres import TEXT_GENRES
from src.prompt import SYSTEM_PROMPT
from src.config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)



USER_TEMPLATE = (
    "<genres>\n{genres_block}</genres>\n\n"
    "<wikipedia_excerpt>\n{title}\n\n{text}\n</wikipedia_excerpt>"
)
MAX_INPUT_TOKENS = Config.MAX_INPUT_TOKENS  # Adjust based on your model's context window and expected output length

EXAMPLES_PER_BUNDLE = Config.EXAMPLES_PER_BUNDLE      # Number of texts generated per LLM call


def _build_prompt(tokenizer, title: str, text: str) -> str:
    genres = random.sample(TEXT_GENRES, EXAMPLES_PER_BUNDLE)
    genres_block = "\n".join(
        f"{i + 1}. {name}: {desc}" for i, (name, desc) in enumerate(genres)
    )
    user_content = USER_TEMPLATE.format(
        genres_block=genres_block + "\n",
        title=title,
        text=text,
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content[:MAX_INPUT_TOKENS]},
    ]
    return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validate_bundle(obj: dict) -> bool:
    """Accept a bundle if it has valid structure and ≥50% of shared labels are cross-role."""
    if not isinstance(obj, dict):
        return False
    shared = obj.get("shared_labels", [])
    examples = obj.get("examples", [])
    if not isinstance(shared, list) or len(shared) < 6:
        return False
    if not isinstance(examples, list) or len(examples) < 2:
        return False
    shared_set = set(shared)
    pos_seen: set[str] = set()
    neg_seen: set[str] = set()
    for ex in examples:
        if not isinstance(ex, dict):
            return False
        text = ex.get("text", "")
        labels = ex.get("labels", [])
        not_labels = ex.get("not_labels", [])
        if not isinstance(text, str) or len(text) < Config.MIN_TEXT_LENGTH:
            return False
        if not isinstance(labels, list) or len(labels) < Config.MIN_NUM_LABELS:
            return False
        if not isinstance(not_labels, list) or len(not_labels) < Config.MIN_NUM_LABELS:
            return False
        if not all(isinstance(lab, str) for lab in labels + not_labels):
            return False
        pos_seen.update(labels)
        neg_seen.update(not_labels)
    cross_role = pos_seen & neg_seen
    return len(cross_role) >= max(1, len(shared_set) * 0.5)


def _expand_bundle(bundle: dict) -> list[dict]:
    """Expand a validated bundle into individual JSONL-ready example dicts."""
    return [
        {
            "source": "wikipedia",
            "text": ex["text"],
            "labels": ex["labels"],
            "not_labels": ex["not_labels"],
        }
        for ex in bundle["examples"]
    ]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate synthetic classification data from Wikipedia.")
    p.add_argument("--output_path", default="data/wikipedia_synthetic.jsonl")
    p.add_argument("--model", default="Qwen/Qwen2.5-72B-Instruct")
    p.add_argument("--num_examples", type=int, default=5000)
    p.add_argument("--batch_size", type=int, default=16,
                   help="Number of prompts per vLLM generation call.")
    p.add_argument("--tensor_parallel_size", type=int, default=2)
    p.add_argument("--temperature", type=float, default=0.9)
    p.add_argument("--max_tokens", type=int, default=4096)
    p.add_argument("--skip", type=int, default=0,
                   help="Articles to skip after shuffle (resume support).")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--shuffle_buffer", type=int, default=50_000,
                   help="Buffer size for streaming shuffle.")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    output_path = Path(args.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Count already-written lines for resume support
    written = 0
    if output_path.exists():
        with open(output_path) as f:
            written = sum(1 for _ in f)
        logger.info(f"Resuming: {written} examples already written.")

    remaining = args.num_examples - written
    if remaining <= 0:
        logger.info("Target already reached. Exiting.")
        return

    articles_needed = math.ceil(remaining / EXAMPLES_PER_BUNDLE)
    logger.info("Loading wikimedia/wikipedia 20231101.en (streaming, shuffled)...")
    ds = load_dataset(
        "wikimedia/wikipedia",
        "20231101.en",
        split="train",
        streaming=True,
    ).shuffle(seed=args.seed, buffer_size=args.shuffle_buffer)

    # Resume: approximate articles already consumed (each bundle uses one article).
    skip = args.skip + math.ceil(written / EXAMPLES_PER_BUNDLE)
    logger.info(f"Sampling {articles_needed} articles (skip={skip})...")
    articles: list[tuple[str, str]] = []
    for row in ds:
        if skip > 0:
            skip -= 1
            continue
        articles.append((row["title"], row["text"]))
        if len(articles) >= articles_needed:
            break
    logger.info(f"Collected {len(articles)} articles → up to {len(articles) * EXAMPLES_PER_BUNDLE} examples.")

    logger.info(f"Loading model {args.model} (tensor_parallel_size={args.tensor_parallel_size})...")
    llm = LLM(model=args.model, tensor_parallel_size=args.tensor_parallel_size)
    tokenizer = llm.get_tokenizer()

    sampling_params = SamplingParams(
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )

    success = 0
    failure = 0

    with open(output_path, "a") as out_file:
        for batch_start in tqdm(range(0, len(articles), args.batch_size), desc="Batches"):
            batch = articles[batch_start : batch_start + args.batch_size]
            prompts = [_build_prompt(tokenizer, title, text) for title, text in batch]

            outputs = llm.generate(prompts, sampling_params)

            for output in outputs:
                content = output.outputs[0].text
                try:
                    bundle = parse_json(content)
                except (ValueError, Exception):
                    bundle = None
                if bundle and _validate_bundle(bundle):
                    for example in _expand_bundle(bundle):
                        out_file.write(json.dumps(example, ensure_ascii=False) + "\n")
                        success += 1
                else:
                    failure += 1

        out_file.flush()

    logger.info(f"Done. success={success}, failure={failure}, total_written={written + success}")
    logger.info(f"Output: {output_path}")


if __name__ == "__main__":
    main()

