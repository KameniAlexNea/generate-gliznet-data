import argparse
import asyncio
import json
import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()
from pathlib import Path

from datasets import load_dataset
from llm_output_parser import parse_json
from openai import AsyncOpenAI, APIConnectionError, APIError, APITimeoutError, RateLimitError
from tqdm import tqdm

from src.config import Config
from src.prompt_amazon import AMAZON_SYSTEM_PROMPT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

_SENTIMENT = {0: "negative", 1: "positive"}

USER_TEMPLATE = "<review>\n{text}\n</review>"


def _build_messages(text: str) -> list:
    user_content = USER_TEMPLATE.format(text=text)[: Config.MAX_INPUT_TOKENS]
    return [
        {"role": "system", "content": AMAZON_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]


async def _call_api(
    client: AsyncOpenAI,
    messages: list,
    model: str,
    temperature: float,
    max_tokens: int,
    use_top_k: bool = True,
    semaphore: asyncio.Semaphore | None = None,
) -> str | None:
    for attempt in range(8):
        try:
            kwargs = dict(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.95,
            )
            if use_top_k:
                kwargs["extra_body"] = {"top_k": 64, "chat_template_kwargs": {"enable_thinking": False}}
            if semaphore is not None:
                async with semaphore:
                    response = await client.chat.completions.create(**kwargs)
            else:
                response = await client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except RateLimitError as exc:
            retry_after = 60
            if hasattr(exc, "response") and exc.response is not None:
                retry_after = int(exc.response.headers.get("Retry-After", 60))
            logger.warning("Rate limited (429). Waiting %ds (attempt %d/8).", retry_after, attempt + 1)
            await asyncio.sleep(retry_after)
        except (APIError, APITimeoutError, APIConnectionError) as exc:
            if attempt == 7:
                logger.warning("API call failed after 8 attempts: %s", exc)
                return None
            await asyncio.sleep(2**attempt)
        except Exception as exc:
            logger.warning("Unexpected API error: %s", exc)
            return None


async def _feed_queue(
    ds_iter,
    queue: asyncio.Queue,
    num_examples: int,
    num_workers: int,
) -> None:
    loop = asyncio.get_running_loop()
    it = iter(ds_iter)
    count = 0
    while count < num_examples:
        item = await loop.run_in_executor(None, next, it, None)
        if item is None:
            break
        text = f"{item['title']}\n\n{item['content']}"
        sentiment = _SENTIMENT[item["label"]]
        await queue.put((text, sentiment))
        count += 1
    for _ in range(num_workers):
        await queue.put(None)


async def _worker(
    queue: asyncio.Queue,
    out_file,
    lock: asyncio.Lock,
    client: AsyncOpenAI,
    model: str,
    temperature: float,
    max_tokens: int,
    counters: dict,
    pbar,
    use_top_k: bool = True,
    semaphore: asyncio.Semaphore | None = None,
) -> None:
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            break
        text, sentiment = item
        content = await _call_api(
            client, _build_messages(text), model, temperature, max_tokens, use_top_k, semaphore
        )
        if content is None:
            counters["failure"] += 1
        else:
            try:
                annotation = parse_json(content)
            except Exception as exc:
                logger.warning("parse_json failed: %s\nRaw content:\n%s", exc, content[:500])
                annotation = None
            record = _expand_annotation(annotation, text, sentiment)
            if record is not None:
                async with lock:
                    out_file.write(json.dumps(record, ensure_ascii=False) + "\n")
                    out_file.flush()
                    counters["success"] += 1
            else:
                counters["failure"] += 1
        pbar.update(1)
        queue.task_done()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_MIN_LABELS = 5  # tolerate slight under-generation


def _expand_annotation(obj, text: str, sentiment: str) -> dict | None:
    if not isinstance(obj, dict):
        logger.warning("_expand_annotation: expected dict, got %s: %r", type(obj).__name__, obj)
        return None
    labels = [str(l).strip() for l in obj.get("labels", []) if str(l).strip()]
    not_labels = [str(l).strip() for l in obj.get("not_labels", []) if str(l).strip()]
    # Remove any overlap
    intersection = set(labels) & set(not_labels)
    labels = [l for l in labels if l not in intersection]
    not_labels = [l for l in not_labels if l not in intersection]
    if len(labels) < _MIN_LABELS or len(not_labels) < _MIN_LABELS:
        logger.warning(
            "_expand_annotation: too few labels after dedup — labels=%d, not_labels=%d (min=%d). Keys in obj: %s",
            len(labels), len(not_labels), _MIN_LABELS, list(obj.keys()),
        )
        return None
    return {
        "source": "amazon_polarity",
        "sentiment": sentiment,
        "text": text,
        "labels": labels,
        "not_labels": not_labels,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Annotate Amazon Polarity reviews with semantic labels via LLM."
    )
    p.add_argument("--output_path", default="data/amazon_annotated.jsonl")
    p.add_argument(
        "--model", default="Jackrong/Qwen3.5-9B-DeepSeek-V4-Flash"
    )
    p.add_argument(
        "--api_base",
        default="http://localhost:8000/v1",
        help="OpenAI-compatible API base URL (vLLM).",
    )
    p.add_argument("--num_examples", type=int, default=10000)
    p.add_argument(
        "--batch_size",
        type=int,
        default=16,
        help="Number of concurrent API requests.",
    )
    p.add_argument("--temperature", type=float, default=0.7)
    p.add_argument("--max_tokens", type=int, default=2048)
    p.add_argument(
        "--split",
        default="train",
        choices=["train", "test"],
        help="Dataset split to annotate.",
    )
    p.add_argument(
        "--skip",
        type=int,
        default=0,
        help="Examples to skip (resume support).",
    )
    p.add_argument("--seed", type=int, default=42)
    p.add_argument(
        "--concurrency",
        type=int,
        default=None,
        help="Max concurrent in-flight API requests (default: same as batch_size). Lower this to avoid 429s.",
    )
    p.add_argument(
        "--use_openrouter",
        action="store_true",
        help="Route requests through OpenRouter. Reads OPENROUTER_API_KEY from env/.env.",
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

    skip = args.skip + written
    logger.info(f"Loading fancyzhx/amazon_polarity ({args.split}, skip={skip})...")
    ds = load_dataset(
        "fancyzhx/amazon_polarity",
        split=args.split,
        streaming=True,
    )
    ds_iter = ds.skip(skip).take(remaining)

    if args.use_openrouter:
        openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
        if not openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY not set in environment or .env file")
        logger.info("Using OpenRouter backend.")
        client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_api_key,
            max_retries=0,
            default_headers={
                "HTTP-Referer": "https://github.com/generate-gliznet-data",
                "X-Title": "generate-gliznet-data",
            },
        )
        use_top_k = False
    else:
        client = AsyncOpenAI(base_url=args.api_base, api_key="EMPTY", max_retries=0)
        use_top_k = True

    concurrency = args.concurrency if args.concurrency is not None else args.batch_size
    semaphore = asyncio.Semaphore(concurrency)
    logger.info(f"Workers: {args.batch_size}, max concurrent API calls: {concurrency}")

    counters = {"success": 0, "failure": 0}
    queue: asyncio.Queue = asyncio.Queue(maxsize=args.batch_size * 2)
    lock = asyncio.Lock()

    with open(output_path, "a", encoding="utf-8") as out_file:
        with tqdm(total=remaining, desc="Reviews") as pbar:
            worker_tasks = [
                asyncio.create_task(
                    _worker(
                        queue, out_file, lock, client,
                        args.model, args.temperature, args.max_tokens,
                        counters, pbar, use_top_k, semaphore,
                    )
                )
                for _ in range(args.batch_size)
            ]
            await _feed_queue(ds_iter, queue, remaining, args.batch_size)
            await asyncio.gather(*worker_tasks)

    logger.info(
        f"Done. success={counters['success']}, failure={counters['failure']}, "
        f"total_written={written + counters['success']}"
    )
    logger.info(f"Output: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
