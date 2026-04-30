
SYSTEM_PROMPT = """\
Create zero-shot text classification training data.

Given a Wikipedia excerpt and a genre that defines the tone and style, generate one bundle containing 5 original texts plus a shared label vocabulary. Follow these 3 steps in order.

STEP 1 — Write 5 texts

Write 5 texts in the provided genre/tone. Each text must be:
- Inspired by, but not copying, the Wikipedia excerpt.
- Self-contained so a reader unfamiliar with the source fully understands it.
- A complete thought; never start with a bare number or a mid-sentence fragment.
- For listicle or instruction genres, framed so the item stands alone.
- Either 2–3 sentences or 1 detail-rich sentence.

SPECIAL RULE — MCQ genres (any genre whose name contains "MCQ")

For MCQ genres, use a completely different format from the standard format above.

CORE RULE — inference over retrieval:
- The correct answer must never appear verbatim or near-verbatim in the context.
- Every answer must be inferred, computed, or derived from the context.
- A question is invalid if its answer can be found by scanning for a matching string.
- The context should make the answer deducible, not directly readable.
- This applies to all MCQ genres: history, geography, literature, trivia, and all others.

Each of the 5 texts must be a question-answering item with this exact structure:
- text:
  - A short context of 2–4 sentences with domain-relevant background drawn from the Wikipedia topic.
  - Followed immediately by a question on a new line.
  - Do not embed answer options (A/B/C/D) inside the text.
  - The text must contain only context plus question.
- labels:
  - A list containing only the correct answer.
  - The answer must be a short conceptual phrase that directly answers the question.
  - The answer must require understanding the context to identify.
  - The answer must not appear verbatim in the context; it must be inferred or paraphrased.
  - Keep it short: a phrase, not a full sentence.
  - Never use a keyword copied from the text.
  - Examples: ["legal immunity of privileged estates"], ["aerobic respiration"], ["monopoly over legitimate violence"], ["O(n log n) worst-case complexity"]
- not_labels:
  - A list of 3–5 wrong but highly plausible alternative answers.
  - Distractors must fit the question's surface form and be conceptually related, but not supported by the context.
  - A skimming reader could plausibly choose any distractor.
  - The correct answer should require careful reading and inference to distinguish from distractors.
  - Use varied phrasing and vocabulary, including synonyms and adjacent concepts.
  - Do not create distractors by swapping one word or slightly changing a date.
  - Bad distractors: ["purple", "democracy", "a vegetable"]
  - Good distractors for "legal immunity of privileged estates":
    ["excessive colonial military debt", "weak centralized administrative control", "peasant refusal to pay agricultural levies"]

The shared_labels field for an MCQ bundle must list all candidate answer strings used across all 5 questions, including correct answers and distractors. Treat each short answer string as a label.

The cross-role constraint still applies:
- Every answer string that is a correct answer for one question must also appear as a distractor for at least one other question in the same bundle.
- Every distractor must also appear as a correct answer for at least one other question in the same bundle.
- Design question sets with overlapping answer pools so this is achievable.

EXAMPLE of one MCQ item (history MCQ about the French Revolution):
- text: "Despite the French crown's awareness of its deepening fiscal crisis, attempts to tax the nobility were systematically blocked by the parlements, whose members were themselves drawn from the privileged estates. Meanwhile the peasantry and urban poor bore an increasingly heavy burden through indirect taxes on basic goods like bread and salt.
What structural feature of the Ancien Régime most directly explains why the monarchy was unable to resolve its debt crisis through fiscal reform alone?"
- labels: ["legal immunity of the tax-exempt privileged orders"]
- not_labels: ["excessive military expenditure in colonial wars", "absence of centralized royal authority over the provinces", "unwillingness of the peasantry to pay agricultural taxes"]

Notice:
- The question requires inferring a structural cause from the pattern of failures described in the context, not retrieving a date or name.
- The distractors are historically plausible explanations for fiscal failure.
- Only the correct answer is directly supported by the context.
- The answer strings are short conceptual phrases, not keywords or sentences.

STEP 2 — Define exactly 18 shared semantic labels

Choose exactly 15 labels that span the semantic space of all 5 texts.
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

For MCQ genres, labels are the answer strings themselves, including correct answers and distractors.

STEP 3 — Assign labels per text

For each of the 5 texts, select labels exclusively from the 18 shared labels:
- labels: 3–5 labels that are true for the text.
- not_labels: 3–5 labels that are false for the text but plausible enough to fool a naive classifier.
- Each not_label must require actually reading the text to rule out; it must not be obviously unrelated.

For MCQ genres:
- labels = correct answer(s)
- not_labels = distractors

HARD CONSTRAINT — Every label must be cross-role

Every one of the 15 shared labels must appear:
- As a positive label ("labels") in at least one text, and
- As a negative label ("not_labels") in at least one different text.

A label that is only positive or only negative across all 5 texts is invalid.
Design the vocabulary at medium specificity: specific enough to be meaningful, but general enough that what is true for one text is plausibly, though incorrectly, applicable to another.

OUTPUT

Respond with only a valid JSON object in this exact structure:
{
  "shared_labels": ["label_1", "label_2", ..., "label_15"],
  "examples": [
    {"text": "...", "labels": ["label_1", "label_3", "label_7"], "not_labels": ["label_2", "label_5", "label_9"]},
    {"text": "...", "labels": ["label_2", "label_5", "label_8"], "not_labels": ["label_1", "label_3", "label_11"]},
    {"text": "...", "labels": ["label_4", "label_6", "label_9"], "not_labels": ["label_7", "label_8", "label_14"]},
    {"text": "...", "labels": ["label_3", "label_10", "label_12"], "not_labels": ["label_4", "label_6", "label_16"]},
    {"text": "...", "labels": ["label_11", "label_13", "label_15"], "not_labels": ["label_10", "label_12", "label_14"]}
  ]
}
"""