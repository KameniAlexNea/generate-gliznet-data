import argparse
import asyncio
import json
import logging
import math
import random
import sys
from pathlib import Path

from datasets import load_dataset
from llm_output_parser import parse_json
import httpx
from openai import AsyncOpenAI, APIConnectionError, APIError, APITimeoutError
from tqdm import tqdm

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
    "<genres>\n{genres_block}\n</genres>\n\n"
    "<wikipedia_excerpt>\n{title}\n\n{text}\n</wikipedia_excerpt>"
)


def _build_messages(title: str, text: str) -> list:
    name, desc = random.choice(TEXT_GENRES)
    genres_block = f"{name}: {desc}"
    user_content = USER_TEMPLATE.format(
        genres_block=genres_block + "\n",
        title=title,
        text=text,
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content[: Config.MAX_INPUT_TOKENS]},
    ]


async def _call_api(
    client: AsyncOpenAI,
    messages: list,
    model: str,
    temperature: float,
    max_tokens: int,
) -> str | None:
    for attempt in range(5):
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.95,
                extra_body={"top_k": 64},
            )
            return response.choices[0].message.content
        except (APIError, APITimeoutError, APIConnectionError) as exc:
            if attempt == 4:
                logger.warning("API call failed after 5 attempts: %s", exc)
                return None
            await asyncio.sleep(2**attempt)
        except Exception as exc:
            logger.warning("Unexpected API error: %s", exc)
            return None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _validate_bundle(obj: dict) -> bool:
    """Accept a bundle if it is a dict with a non-empty examples list."""
    return (
        isinstance(obj, dict)
        and isinstance(obj.get("examples"), list)
        and bool(obj["examples"])
    )


def _expand_bundle(bundle: dict) -> list[dict]:
    """Expand a bundle into individual JSONL-ready example dicts, skipping invalid examples."""
    results = []
    for ex in bundle["examples"]:
        if not isinstance(ex, dict):
            continue
        text = ex.get("text", "")
        labels = [str(lab).strip() for lab in ex.get("labels", []) if str(lab).strip()]
        not_labels = [
            str(lab).strip() for lab in ex.get("not_labels", []) if str(lab).strip()
        ]
        intersection = set(labels) & set(not_labels)
        labels = [lab for lab in labels if lab not in intersection]
        not_labels = [lab for lab in not_labels if lab not in intersection]
        if not isinstance(text, str) or not labels or not not_labels:
            continue
        results.append(
            {
                "source": "wikipedia",
                "text": text,
                "labels": labels,
                "not_labels": not_labels,
            }
        )
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate synthetic classification data from Wikipedia."
    )
    p.add_argument("--output_path", default="data/wikipedia_synthetic.jsonl")
    p.add_argument(
        "--model", default="Jackrong/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled "
    )
    p.add_argument(
        "--api_base",
        default="http://localhost:8000/v1",
        help="Base URL of the vLLM OpenAI-compatible server.",
    )
    p.add_argument("--num_examples", type=int, default=10000)
    p.add_argument(
        "--batch_size",
        type=int,
        default=16,
        help="Number of concurrent API requests per batch.",
    )
    p.add_argument("--temperature", type=float, default=0.9)
    p.add_argument("--max_tokens", type=int, default=3072)
    p.add_argument(
        "--skip",
        type=int,
        default=0,
        help="Articles to skip after shuffle (resume support).",
    )
    p.add_argument("--seed", type=int, default=42)
    p.add_argument(
        "--shuffle_buffer",
        type=int,
        default=50_000,
        help="Buffer size for streaming shuffle.",
    )
    return p.parse_args()


async def main() -> None:
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

    articles_needed = math.ceil(remaining / Config.EXAMPLES_PER_BUNDLE)
    logger.info("Loading wikimedia/wikipedia 20231101.en (streaming, shuffled)...")
    ds = load_dataset(
        "wikimedia/wikipedia",
        "20231101.en",
        split="train",
        streaming=True,
    ).shuffle(seed=args.seed, buffer_size=args.shuffle_buffer)

    # Resume: approximate articles already consumed (each bundle uses one article).
    skip = args.skip + math.ceil(written / Config.EXAMPLES_PER_BUNDLE)
    logger.info(f"Sampling {articles_needed} articles (skip={skip})...")
    ds_batched = ds.skip(skip).take(articles_needed).batch(args.batch_size)

    health_url = args.api_base.rstrip("/").removesuffix("/v1") + "/health"
    logger.info(f"Waiting for vLLM server at {health_url} ...")
    async with httpx.AsyncClient() as hc:
        while True:
            try:
                r = await hc.get(health_url, timeout=5.0)
                if r.status_code == 200:
                    break
            except Exception:
                pass
            logger.info("Server not ready, retrying in 5 s...")
            await asyncio.sleep(5)
    logger.info("Server is up.")

    client = AsyncOpenAI(base_url=args.api_base, api_key="EMPTY", max_retries=0)

    success = 0
    failure = 0

    num_batches = math.ceil(articles_needed / args.batch_size)
    with open(output_path, "a", encoding="utf-8") as out_file:
        for batch in tqdm(ds_batched, total=num_batches, desc="Batches"):
            batch_messages = [
                _build_messages(title, text)
                for title, text in zip(batch["title"], batch["text"])
            ]

            contents = await asyncio.gather(
                *[
                    _call_api(client, msgs, args.model, args.temperature, args.max_tokens)
                    for msgs in batch_messages
                ]
            )

            for content in contents:
                if content is None:
                    failure += 1
                    continue
                try:
                    bundle = parse_json(content)
                except Exception:
                    bundle = None
                if bundle and _validate_bundle(bundle):
                    for example in _expand_bundle(bundle):
                        out_file.write(json.dumps(example, ensure_ascii=False) + "\n")
                        success += 1
                else:
                    failure += 1

            out_file.flush()

    logger.info(
        f"Done. success={success}, failure={failure}, total_written={written + success}"
    )
    logger.info(f"Output: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
