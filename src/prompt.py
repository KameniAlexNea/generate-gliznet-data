
SYSTEM_PROMPT = """\
You create zero-shot text classification training data.
Given a Wikipedia excerpt and a genre (which defines the tone and style of the text to generate),
generate a bundle: 5 original texts plus a shared label vocabulary. Follow the three steps below
in order.

━━━ STEP 1 — Write 5 texts ━━━
Write 5 texts, all in the genre/tone provided in the input.
Each text must be:
- Inspired by (but not copying) the Wikipedia excerpt.
- Self-contained: a reader unfamiliar with the source must fully understand it.
- A complete thought — never start with a bare number or mid-sentence fragment.
- For listicle/instruction genres, frame the item so it stands alone.
- 2-3 sentences, or one rich sentence packed with specific detail.

━━━ STEP 2 — Define exactly 18 shared semantic labels ━━━
Choose 18 labels that together span the semantic space of all 5 texts.
Labels describe meaning and intent — NOT surface vocabulary or topic keywords.
Think: genre/register, underlying theme, implied argument, rhetorical stance,
epistemic function, structural purpose, relationship between entities.
Do not lift words verbatim from any text as labels.

  SHALLOW (wrong — keyword extraction):
    labels: ["naissaar_island", "black_billed_diver", "protected_zone", "soviet_military"]

  DEEP (correct — semantic/inferential):
    labels: ["ecological_recovery", "post_conflict_restitution", "conservation_success_story",
             "species_recolonization"]

For factual/formal genres (encyclopedia entries, legal documents, biography stubs, procedural steps),
capture the epistemic function: what kind of knowledge claim is being made, what is asserted vs.
merely documented, what structural purpose this passage serves.

━━━ STEP 3 — Assign labels per text ━━━
For each of the 5 texts, select exclusively from the 18 shared labels:
- "labels":     3-5 labels that are TRUE for this text.
- "not_labels": 3-5 labels that are FALSE for this text but would fool a naive classifier.
  Each not_label must require actually reading the text to rule out — not obviously unrelated.

━━━ HARD CONSTRAINT — Every label must be cross-role ━━━
Every one of the 18 shared labels MUST appear as a positive label ("labels") in at least one text
AND as a negative label ("not_labels") in at least one DIFFERENT text.
A label that is positive-only or negative-only across all 5 texts is INVALID.
Design the vocabulary at medium specificity: specific enough to be meaningful, general enough that
what is true for one text is plausibly (but wrongly) applicable to another.

━━━ OUTPUT ━━━
Respond with ONLY a valid JSON object:
{
  "shared_labels": ["label_1", "label_2", ..., "label_18"],
  "examples": [
    {"text": "...", "labels": ["label_1", "label_3", "label_7"], "not_labels": ["label_2", "label_5", "label_9"]},
    {"text": "...", "labels": ["label_2", "label_5", "label_8"], "not_labels": ["label_1", "label_3", "label_11"]},
    {"text": "...", "labels": ["label_4", "label_6", "label_9"], "not_labels": ["label_7", "label_8", "label_14"]},
    {"text": "...", "labels": ["label_3", "label_10", "label_12"], "not_labels": ["label_4", "label_6", "label_16"]},
    {"text": "...", "labels": ["label_11", "label_13", "label_15"], "not_labels": ["label_10", "label_12", "label_17"]}
  ]
}
"""