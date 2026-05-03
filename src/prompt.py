
from src.config import Config


def _fmt_range(lo: int, hi: int) -> str:
    return str(lo) if lo == hi else f"{lo}–{hi}"


SYSTEM_PROMPT = f"""\
Create zero-shot text classification training data.

Given a Wikipedia excerpt and a genre that defines the tone and style, generate one bundle containing 5 original texts plus a shared label vocabulary. Follow these 3 steps in order.

STEP 1 — Write 5 texts

Write 5 texts in the provided genre/tone, at the specified length and language level. Each text must be:
- Inspired by, but not copying, the Wikipedia excerpt.
- Self-contained so a reader unfamiliar with the source fully understands it.
- A complete thought; never start with a bare number or a mid-sentence fragment.
- For listicle or instruction genres, framed so the item stands alone.
- The length and language level specified in the input must be respected across all 5 texts.

STEP 2 — Define exactly {Config.NUM_LABELS} shared semantic labels

Choose exactly {Config.NUM_LABELS} labels that span the semantic space of all 5 texts.
- Labels must describe meaning and intent, not surface vocabulary or topic keywords.
- Focus on genre/register, underlying theme, implied argument, rhetorical stance, epistemic function, structural purpose, and relationships between entities.
- Do not copy words verbatim from any text into the labels.

SHALLOW (wrong — keyword extraction):
- labels: ["naissaar_island", "black_billed_diver", "protected_zone", "soviet_military"]

DEEP (correct — semantic/inferential):
- labels: ["ecological_recovery", "post_conflict_restitution", "conservation_success_story", "species_recolonization"]

For factual or formal genres, including encyclopedia entries, legal documents, biography stubs, and procedural steps:
- Capture the epistemic function.
- Indicate what kind of knowledge claim is being made.
- Distinguish what is asserted from what is merely documented.
- Reflect the structural purpose of the passage.

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
Design the vocabulary at medium specificity: specific enough to be meaningful, but general enough that what is true for one text is plausibly, though incorrectly, applicable to another.

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