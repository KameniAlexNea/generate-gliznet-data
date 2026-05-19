import json
import random
from collections import Counter
from pathlib import Path

from src.config import Config


def _fmt_range(lo: int, hi: int) -> str:
    return str(lo) if lo == hi else f"{lo}–{hi}"


# ── Label mode flag (set externally) ──────────────────────────────────────────
FREE_LABELS: bool = False

# ── Label mode flag (set externally) ──────────────────────────────────────────
FREE_LABELS: bool = False

# ── Taxonomy loading ──────────────────────────────────────────────────────────

_TAXONOMY_PATH = Path(__file__).parent.parent / "data" / "label_taxonomy.json"

with open(_TAXONOMY_PATH) as _f:
    _TAXONOMY = json.load(_f)

_CLUSTERS: dict[str, dict] = _TAXONOMY["clusters"]

_CROSS_DOMAIN_CATEGORIES = {"rhetorical", "epistemic", "emotional", "language", "philosophy"}

# Keyword → list of domain category names (for excerpt-based matching)
_KEYWORD_TO_CATEGORIES: dict[str, list[str]] = {
    "species": ["nature", "environment"], "ecosystem": ["nature", "environment"],
    "forest": ["nature", "environment"], "climate": ["nature", "environment"],
    "ocean": ["nature", "environment"], "wildlife": ["nature"],
    "pollution": ["nature", "environment"], "conservation": ["nature", "environment"],
    "water": ["environment"], "energy": ["environment", "science"],
    "agriculture": ["environment"], "food": ["environment"],
    "economy": ["economics"], "market": ["economics"], "trade": ["economics"],
    "bank": ["economics"], "inflation": ["economics"], "company": ["economics"],
    "industry": ["economics"], "labor": ["economics"], "finance": ["economics"],
    "business": ["economics"], "stock": ["economics"], "investment": ["economics"],
    "government": ["politics"], "election": ["politics"], "democracy": ["politics"],
    "parliament": ["politics"], "law": ["politics", "legal"], "policy": ["politics"],
    "president": ["politics"], "congress": ["politics"], "political": ["politics"],
    "vote": ["politics"], "constitution": ["politics", "legal"],
    "research": ["science"], "technology": ["science", "technology"],
    "computer": ["science", "technology"], "algorithm": ["science", "technology"],
    "physics": ["science"], "chemistry": ["science"], "biology": ["science", "nature"],
    "data": ["science", "technology"], "software": ["technology"],
    "internet": ["technology"], "artificial": ["technology"],
    "disease": ["health"], "hospital": ["health"], "treatment": ["health"],
    "patient": ["health"], "medical": ["health"], "drug": ["health"],
    "virus": ["health"], "cancer": ["health"], "mental": ["health"],
    "vaccine": ["health"], "surgery": ["health"],
    "culture": ["culture"], "religion": ["culture"], "art": ["culture", "arts"],
    "music": ["culture", "arts"], "film": ["culture", "arts"],
    "language": ["culture"], "education": ["education"],
    "school": ["education"], "university": ["education"],
    "war": ["conflict"], "military": ["conflict"], "army": ["conflict"],
    "peace": ["conflict"], "weapon": ["conflict"], "terrorism": ["conflict"],
    "security": ["conflict"], "conflict": ["conflict"],
    "court": ["legal"], "judge": ["legal"], "trial": ["legal"],
    "rights": ["legal"], "crime": ["legal"], "prison": ["legal"],
    "city": ["spatial"], "urban": ["spatial"], "building": ["spatial"],
    "transport": ["spatial"], "infrastructure": ["spatial"],
    "housing": ["spatial"], "architecture": ["spatial", "arts"],
    "ancient": ["history"], "medieval": ["history"], "colonial": ["history"],
    "empire": ["history"], "century": ["history"], "revolution": ["history"],
    "civilization": ["history"], "dynasty": ["history"],
}


def _select_clusters(text: str, n_cross: int = 2, n_domain: int = 2, n_wildcard: int = 1) -> list[str]:
    """Pick relevant cluster names for a Wikipedia excerpt."""
    text_lower = text.lower()

    cross_clusters = [cn for cn, cd in _CLUSTERS.items() if cd["category"] in _CROSS_DOMAIN_CATEGORIES]
    domain_clusters = [cn for cn, cd in _CLUSTERS.items() if cd["category"] not in _CROSS_DOMAIN_CATEGORIES]

    matched_cats: Counter = Counter()
    for keyword, cats in _KEYWORD_TO_CATEGORIES.items():
        if keyword in text_lower:
            for cat in cats:
                matched_cats[cat] += 1

    if matched_cats:
        top_cats = {cat for cat, _ in matched_cats.most_common(3)}
        preferred = [cn for cn in domain_clusters if _CLUSTERS[cn]["category"] in top_cats]
        fallback = [cn for cn in domain_clusters if cn not in preferred]
        ordered_domain = preferred + fallback
    else:
        ordered_domain = domain_clusters

    selected: list[str] = []
    selected += random.sample(cross_clusters, min(n_cross, len(cross_clusters)))
    available = [c for c in ordered_domain if c not in selected]
    selected += random.sample(available, min(n_domain, len(available)))
    remaining = [cn for cn in _CLUSTERS if cn not in selected]
    if remaining and n_wildcard > 0:
        selected += random.sample(remaining, min(n_wildcard, len(remaining)))

    return selected


def get_candidate_labels(text: str) -> list[str]:
    """Return a shuffled list of ~100-150 candidate labels for a Wikipedia excerpt."""
    selected = _select_clusters(text)
    candidates: list[str] = []
    for cname in selected:
        candidates.extend(_CLUSTERS[cname]["labels"])
    random.shuffle(candidates)
    return candidates


# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = f"""\
Create zero-shot text classification training data.

Given a Wikipedia excerpt and a genre that defines the tone and style, generate one bundle containing 5 original texts plus a shared label vocabulary. Follow these 3 steps in order.

CRITICAL — Genre vs Content

The genre defines ONLY the tone, register, and writing style (e.g. how a spam email sounds, how a news article is structured). It does NOT determine the subject matter.
The CONTENT of every text must be derived from the Wikipedia excerpt provided as context. The Wikipedia excerpt is the sole source of facts, topics, and subject matter.
Example: if the genre is "spam or phishing email" and the Wikipedia excerpt is about the Roman Empire, the text should be a spam-style email whose subject matter relates to the Roman Empire — not a generic spam email about pills or lottery wins.

STEP 1 — Write 5 texts

Write 5 texts in the provided genre/tone, at the specified length and language level. Each text must be:
- About the Wikipedia excerpt's subject matter, rewritten in the voice and register of the genre.
- Inspired by, but not copying, the Wikipedia excerpt.
- Self-contained so a reader unfamiliar with the source fully understands it.
- A complete thought; never start with a bare number or a mid-sentence fragment.
- For listicle or instruction genres, framed so the item stands alone.
- The length and language level specified in the input must be respected across all 5 texts.

STEP 2 — Select exactly {Config.NUM_LABELS} shared semantic labels FROM THE CANDIDATE LABELS

⚠️ You MUST select labels ONLY from the <candidate_labels> list provided in the user message.
Do NOT invent new labels. Every label in "shared_labels" must appear verbatim in the candidate list.

Select exactly {Config.NUM_LABELS} labels that best span the semantic space of all 5 texts:
- Choose labels that are applicable across multiple texts (some as positive, some as negative).
- Aim for a mix of certainty-level, rhetorical stance, and domain-relevant labels.
- Prefer labels that are meaningfully different from each other so they carry distinct signal.

STEP 3 — Assign labels per text

For each of the 5 texts, select labels exclusively from the {Config.NUM_LABELS} shared labels:
- labels: {_fmt_range(Config.POSITIVE_LABELS_MIN, Config.POSITIVE_LABELS_MAX)} label(s) that are true for the text.
- not_labels: {_fmt_range(Config.NEGATIVE_LABELS_MIN, Config.NEGATIVE_LABELS_MAX)} labels that are false for the text but plausible enough to fool a naive classifier.
- Each not_label must require actually reading the text to rule out; it must not be obviously unrelated.
- Use more negative labels than positive to reflect real-world class imbalance.

HARD CONSTRAINT — Every label must be cross-role

Every one of the {Config.NUM_LABELS} shared labels must appear:
- As a positive label ("labels") in at least one text, and
- As a negative label ("not_labels") in at least one different text.

A label that is only positive or only negative across all 5 texts is invalid.

OUTPUT

Respond with only a valid JSON object in this exact structure:
{{
  "shared_labels": ["label_1", "label_2", ..., "label_{Config.NUM_LABELS}"],
  "examples": [
    {{"text": "...", "labels": ["label_1"], "not_labels": ["label_2", "label_4", "label_6", "label_8"]}},
    {{"text": "...", "labels": ["label_2", "label_3"], "not_labels": ["label_1", "label_5", "label_7", "label_9"]}},
    {{"text": "...", "labels": ["label_4"], "not_labels": ["label_3", "label_6", "label_8", "label_{Config.NUM_LABELS}"]}},
    {{"text": "...", "labels": ["label_5", "label_6"], "not_labels": ["label_2", "label_4", "label_7", "label_9"]}},
    {{"text": "...", "labels": ["label_7"], "not_labels": ["label_1", "label_3", "label_5", "label_{Config.NUM_LABELS}"]}}
  ]
}}
"""

# ── Free-label system prompt (no candidate list, model generates its own labels) ──

FREE_LABEL_SYSTEM_PROMPT = f"""\
Create zero-shot text classification training data.

Given a Wikipedia excerpt and a genre that defines the tone and style, generate one bundle containing 5 original texts plus a shared label vocabulary. Follow these 3 steps in order.

CRITICAL — Genre vs Content

The genre defines ONLY the tone, register, and writing style (e.g. how a spam email sounds, how a news article is structured). It does NOT determine the subject matter.
The CONTENT of every text must be derived from the Wikipedia excerpt provided as context. The Wikipedia excerpt is the sole source of facts, topics, and subject matter.
Example: if the genre is "spam or phishing email" and the Wikipedia excerpt is about the Roman Empire, the text should be a spam-style email whose subject matter relates to the Roman Empire — not a generic spam email about pills or lottery wins.

STEP 1 — Write 5 texts

Write 5 texts in the provided genre/tone, at the specified length and language level. Each text must be:
- About the Wikipedia excerpt's subject matter, rewritten in the voice and register of the genre.
- Inspired by, but not copying, the Wikipedia excerpt.
- Self-contained so a reader unfamiliar with the source fully understands it.
- A complete thought; never start with a bare number or a mid-sentence fragment.
- For listicle or instruction genres, framed so the item stands alone.
- The length and language level specified in the input must be respected across all 5 texts.

STEP 2 — Invent exactly {Config.NUM_LABELS} shared semantic labels

Create exactly {Config.NUM_LABELS} original labels that describe the semantic properties of your 5 texts. Labels must:

1. Describe MEANING, INTENT, and RHETORICAL FUNCTION — not surface topic.
   BAD (shallow):  "roman_empire", "military_history", "ancient_rome"
   GOOD (deep):    "causal_chain_argument", "nostalgic_glorification", "institutional_critique"

2. Include FINE-GRAINED INTENSITY DISTINCTIONS where relevant.
   Instead of one generic sentiment label, use a GRADIENT:
   - "strong_positive_endorsement" vs "mild_positive_leaning" vs "cautious_qualified_approval"
   - "absolute_certainty_claim" vs "hedged_probabilistic_assertion" vs "speculative_conjecture"
   - "severe_condemnation" vs "measured_disapproval" vs "gentle_reservation"
   Labels that differ only in INTENSITY must co-exist in the same bundle so the model
   learns to distinguish degrees, not just polarity.

3. Use COMPOSITIONAL, DESCRIPTIVE label names (snake_case, 2–5 words).
   Each label should be self-explanatory without external context.

4. Be DIVERSE across multiple semantic dimensions:
   - Certainty/hedging level
   - Emotional valence AND intensity
   - Rhetorical stance (persuading, informing, entertaining, warning, ...)
   - Epistemic status (established fact, personal opinion, speculation, hearsay)
   - Argumentative function (claim, evidence, rebuttal, concession)

STEP 3 — Assign labels per text

For each of the 5 texts, select labels exclusively from the {Config.NUM_LABELS} shared labels:
- labels: {_fmt_range(Config.POSITIVE_LABELS_MIN, Config.POSITIVE_LABELS_MAX)} label(s) that are true for the text.
- not_labels: {_fmt_range(Config.NEGATIVE_LABELS_MIN, Config.NEGATIVE_LABELS_MAX)} labels that are false for the text but plausible enough to fool a naive classifier.
- Each not_label must require actually reading the text to rule out; it must not be obviously unrelated.
- When two labels differ only in intensity (e.g. "strong_positive" vs "mild_positive"),
  assign the correct intensity as positive and the adjacent intensity as a hard negative.
- Use more negative labels than positive to reflect real-world class imbalance.

HARD CONSTRAINT — Every label must be cross-role

Every one of the {Config.NUM_LABELS} shared labels must appear:
- As a positive label ("labels") in at least one text, and
- As a negative label ("not_labels") in at least one different text.

A label that is only positive or only negative across all 5 texts is invalid.

OUTPUT

Respond with only a valid JSON object in this exact structure:
{{
  "shared_labels": ["label_1", "label_2", ..., "label_{Config.NUM_LABELS}"],
  "examples": [
    {{"text": "...", "labels": ["label_1"], "not_labels": ["label_2", "label_4", "label_6", "label_8"]}},
    {{"text": "...", "labels": ["label_2", "label_3"], "not_labels": ["label_1", "label_5", "label_7", "label_9"]}},
    {{"text": "...", "labels": ["label_4"], "not_labels": ["label_3", "label_6", "label_8", "label_{Config.NUM_LABELS}"]}},
    {{"text": "...", "labels": ["label_5", "label_6"], "not_labels": ["label_2", "label_4", "label_7", "label_9"]}},
    {{"text": "...", "labels": ["label_7"], "not_labels": ["label_1", "label_3", "label_5", "label_{Config.NUM_LABELS}"]}}
  ]
}}
"""
