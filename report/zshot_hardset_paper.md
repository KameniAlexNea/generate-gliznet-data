# ZSHOT-HARDSET: A Synthetic Dataset with Hard-Negative Semantic Labels for Zero-Shot Text Classification

**Authors**: Alex Kameni (Ivalua / Massy, France, eak@ivalua.com)
**Date**: May 2026

---

## Abstract

Zero-shot text classification (ZSC) benchmarks typically rely on surface-level topic labels (e.g., "sports", "politics") that can be matched through lexical overlap rather than genuine semantic understanding. We present **ZSHOT-HARDSET-v2**, a synthetic dataset of ~900k examples (and growing) designed around *hard-negative semantic labels* that require inferential reading to distinguish. Each example pairs a text with positive labels describing its meaning, rhetorical stance, and epistemic function, alongside carefully crafted negative labels that are plausible enough to fool a naive classifier but demonstrably false upon careful reading. Texts are generated from Wikipedia articles rewritten into 70 text registers; each bundle of 5 texts shares 15 semantic labels satisfying a cross-role constraint — every label must appear as both positive and negative across different texts within the same bundle. We describe the iterative development from an initial v1 (context-free generation with unconstrained labels) to v2 (Wikipedia-grounded generation with the cross-role constraint), showing how each design decision was motivated by observed failure modes. We demonstrate the dataset's utility through downstream evaluation on GliZNet, a zero-shot classification model that achieves 0.6701 average macro F1 on the GLiClass benchmark — competitive with models using 2× more data and multi-stage training with reinforcement learning. The dataset and generation code are publicly released.

---

## 1. Introduction

Zero-shot text classification — the ability to categorize text into labels not seen during training — is increasingly important for applications where label sets are dynamic, domain-specific, or too costly to annotate manually. The quality of training data is central to the performance of ZSC models, yet relatively little attention has been paid to *what makes a good ZSC training example*.

Most existing ZSC datasets and training corpora use labels that describe surface-level topics: "sports", "business", "technology". A model can often match these by detecting keywords ("goal", "stock", "algorithm") without understanding the text's meaning, argument structure, or rhetorical intent. This creates a brittle form of zero-shot generalization — the model appears to transfer to new labels but fails when labels require deeper semantic reasoning.

We argue that the key to robust zero-shot generalization lies in training with *hard-negative semantic labels*: labels that describe meaning, intent, rhetorical stance, and epistemic function rather than surface vocabulary, paired with negative labels that require careful reading to rule out. This paper introduces **ZSHOT-HARDSET-v2**, a dataset embodying this principle through two key mechanisms:

1. **Wikipedia-grounded genre-injected generation**: Each example is generated from a real Wikipedia article rewritten into one of 70 diverse text registers, preventing the repetitive and context-free outputs observed in our initial v1 approach.
2. **The cross-role constraint**: Within each bundle of 5 texts sharing 15 semantic labels, every label must appear as a positive in at least one text and as a negative in at least one different text — preventing the label-isolation failures observed in v1 and forcing models to learn deep text–label alignment rather than linearly separable label representations.

At ~900k examples and growing, ZSHOT-HARDSET-v2 aims to become the largest open-source training dataset for zero-shot text classification.

Our contributions are:

1. **A principled framework for hard-negative semantic label generation**, including the cross-role constraint and genre injection mechanisms that force labels to capture meaning rather than topic.
2. **An iterative design narrative** documenting the failure modes of v1 (repetition, label isolation) and how v2's design decisions address them.
3. **Empirical validation** showing that a model (GliZNet) trained on ZSHOT-HARDSET-v2 achieves competitive zero-shot performance (0.6701 avg F1) against models trained on 2× more data with multi-stage pipelines including reinforcement learning.
4. **A publicly released dataset and open-source generation pipeline** enabling the community to extend, adapt, or regenerate the data.

---

## 2. Related Work

### 2.1 Zero-Shot Classification Datasets

The standard evaluation suite for ZSC includes datasets like AG News (4 topic classes), SST-2/SST-5 (sentiment), 20-Newsgroups (20 topics), and Emotion (6 tweet emotions). These datasets were not designed for zero-shot evaluation — they are supervised classification benchmarks repurposed by withholding label descriptions during training. Their labels are coarse-grained topics or sentiments that can often be resolved through keyword matching.

More targeted ZSC resources include the MultiNLI dataset (Williams et al., 2018), which trains models to perform natural language inference as a proxy for classification, and the Yahoo Answers topic dataset. However, these still frame labels as broad categories rather than fine-grained semantic descriptors.

GLiClass (Stepanov et al., 2025) assembled a 1.2M-example training corpus from multiple sources, but the dataset construction methodology — label vocabulary design, hard-negative mining strategy, and quality constraints — was not the focus of their contribution and was not released as a standalone resource.

### 2.2 Synthetic Data Generation for NLP

The use of large language models to generate synthetic training data has become widespread: Alpaca (Taori et al., 2023) for instruction-following, Self-Instruct (Wang et al., 2023) for task generation, and various domain-specific efforts. For classification specifically, prior work has generated synthetic examples by prompting LLMs with category descriptions, but these approaches typically produce texts that cluster around topic keywords rather than exhibiting diverse registers and semantic properties.

Our approach differs in three ways: (1) we generate *labels* as well as texts, requiring the LLM to reason about semantics rather than reproducing topic vocabulary; (2) we inject genre diversity through 70 text registers, forcing variation in rhetorical stance and style; (3) we impose structural constraints (cross-role) that guarantee hard negatives by construction.

### 2.3 Hard-Negative Mining

Hard-negative mining is well-studied in metric learning and retrieval (Schroff et al., 2015; Robinson et al., 2021). In-batch negatives, semi-hard negatives, and curriculum-based strategies have been applied to contrastive learning of text representations. Our cross-role constraint is a form of *constructive* hard-negative generation: rather than mining hard negatives from a pool post hoc, the generation process guarantees that every label appears in both positive and negative contexts, ensuring that the model cannot rely on label identity alone.

---

## 3. From v1 to v2: Iterative Design Through Failure Analysis

ZSHOT-HARDSET-v2 is the result of iterative refinement. Each design decision was motivated by a concrete failure mode observed in the previous version. We describe this evolution before detailing the final pipeline.

### 3.1 v1: Context-Free Generation and Its Failures

The initial version (ZSHOT-HARDSET-v1) prompted the generating LLM to produce classification examples *from scratch*, without any source context. The prompt specified a genre and asked the model to write texts and generate labels freely.

**Failure mode 1 — Text repetition.** Without grounding in a factual source, the generating LLM fell into repetitive patterns. Across thousands of generations, the same sentence structures, topics, and phrasings recurred. The model drew from a narrow effective distribution of "typical" texts for each genre, producing near-duplicates that offered little training diversity. A dataset dominated by repeated examples provides redundant training signal and fails to cover the distribution of real-world inputs.

**Fix → Wikipedia grounding.** By providing a real Wikipedia excerpt as context, each generation is anchored to a distinct factual source. The LLM is instructed to write texts *inspired by but not copying* the excerpt, in the specified genre. This grounds generation in diverse factual content (Wikipedia covers millions of distinct topics) while preserving register diversity through genre injection.

**Failure mode 2 — Label isolation.** In v1, labels were generated independently per text without structural constraints. This produced two pathologies:
- **Single-role labels**: A label would appear only as a positive across the entire bundle, or only as a negative. A downstream model could learn to associate the label identity itself with a fixed polarity, rather than reasoning about the text–label relationship.
- **Non-reused labels**: Many labels appeared in only one text, providing no contrastive signal. Without seeing the same label applied positively to one text and negatively to another, the model has no reason to learn *why* a label applies — it can simply memorise a separating hyperplane for each label in embedding space.

**Fix → The cross-role constraint.** v2 requires that every one of the 15 shared labels appears as a positive in at least one text and as a negative in at least one different text within the same bundle. This structural constraint eliminates both pathologies and has a profound consequence for how downstream models learn (Section 3.3).

### 3.2 Semantic Depth over Surface Matching

Labels must describe *what the text means and how it means it* — not what topic it mentions. We distinguish:

- **Shallow labels** (rejected): `naissaar_island`, `black_billed_diver`, `protected_zone`, `soviet_military` — these are keyword extractions that a bag-of-words model could match.
- **Deep labels** (required): `ecological_recovery`, `post_conflict_restitution`, `conservation_success_story`, `species_recolonization` — these require understanding the passage's argument, framing, and implications.

The prompt explicitly instructs the generating LLM to focus on genre/register, underlying theme, implied argument, rhetorical stance, epistemic function, structural purpose, and entity relationships.

### 3.3 The Cross-Role Constraint and Its Effect on Learned Representations

In a bundle of 5 texts sharing 15 labels, every label must appear as a positive (`labels`) in at least one text and as a negative (`not_labels`) in at least one different text. This constraint has three consequences:

1. **No trivially distinguishable labels**: A label that is always positive or always negative carries no discriminative information within the bundle. The cross-role constraint forces each label to be contextually determined — its truth value depends on the specific text, not on the label itself.

2. **Built-in hard negatives**: When label $l$ is positive for text $t_1$ and negative for text $t_2$, the model must learn to distinguish what makes $l$ true in $t_1$ and false in $t_2$ — which, by construction, requires reading the text rather than pattern-matching the label.

3. **Forcing embedding-based alignment over separable hyperplanes**: This is the critical insight from the v1→v2 transition. Without the cross-role constraint, a model can learn a simple decision boundary for each label: "if the label embedding falls on side A of a hyperplane, predict positive." The label's polarity is determined by its identity, not by its relationship to the text. With the cross-role constraint, the same label must be positive for some texts and negative for others. This makes label-identity-based hyperplanes *impossible* — the model is forced to compute a genuine text–label alignment score. In embedding terms, the model must learn representations where the *relative position* of a text embedding with respect to a label embedding determines the prediction, rather than the label embedding alone occupying a fixed "positive" or "negative" region of space.

Formally, let $\mathbf{h}_t$ be the text representation and $\mathbf{h}_l$ be the label representation. Without the cross-role constraint, a model can learn a classifier $f(\mathbf{h}_l) \to \{0, 1\}$ that ignores the text entirely. With the constraint, the model must learn $f(\mathbf{h}_t, \mathbf{h}_l) \to \{0, 1\}$ — a function of *both* representations — because the same $\mathbf{h}_l$ must yield different predictions for different texts.

### 3.4 Register Diversity

Real-world ZSC applications encounter texts across a vast range of registers: legal documents, social media posts, academic papers, product reviews, news articles. A training set confined to one register produces a model that generalizes poorly across registers. ZSHOT-HARDSET-v2 addresses this by injecting one of 70 text registers per generation, spanning:

| Category | Example Registers |
|----------|-------------------|
| Reference / Encyclopedic | encyclopedia entry, academic abstract, museum label, textbook explanation |
| Journalism | news lede, investigative journalism, tabloid lede, op-ed, sports commentary |
| Academic / Scientific | empirical finding, humanities argument, peer review, grant proposal, ethnographic field note |
| Personal / Conversational | Reddit post, blog post, diary entry, oral history, chat/SMS, podcast transcript |
| Narrative / Creative | documentary narration, biography, myth retelling, sci-fi world-building, song lyrics |
| Formal / Institutional | legal document, press release, diplomatic statement, parliamentary debate, patent claim |
| Promotional / Commercial | advertisement, real estate listing, job posting, crowdfunding pitch, startup pitch |
| Service / Practical | how-it-works explainer, instruction manual, recipe, FAQ, medical leaflet, technical README |
| Cultural / Miscellaneous | social media thread, product review, customer complaint, satirical piece, obituary, stand-up comedy |
| Specialized Professional | medical case report, philosophical thought experiment, therapy note, code comment |

Each register is paired with a randomly sampled **text length** (1 sentence to 5–8 sentences) and **language level** (A2 through C2 on the CEFR scale), creating a combinatorial space of approximately $70 \times 5 \times 5 = 1{,}750$ distinct generation conditions.

### 3.5 Asymmetric Label Counts

Real-world classification is imbalanced: for most label sets, a given text matches very few labels and does not match many. ZSHOT-HARDSET-v2 reflects this with 1–5 positive labels and 8–15 negative labels per text, forcing models to learn calibrated predictions under class imbalance.

---

## 4. Generation Pipeline

### 4.1 Source Data

Articles are streamed from `wikimedia/wikipedia 20231101.en` via HuggingFace Datasets in streaming mode with a 50,000-example shuffle buffer. Streaming avoids downloading the full ~21 GB dataset. Each article provides a title and body text; we extract up to 5 consecutive paragraphs from a random position in the article to serve as the Wikipedia excerpt.

### 4.2 Prompt Construction

For each article, we sample:
- One genre from the 70 available registers
- One text length from {very short, short, medium, long, very long}
- One language level from {A2, B1, B2, C1, C2}

These are assembled into a structured user prompt:

```xml
<genre>
{genre_name}: {genre_description}
</genre>

<length>{length_label}: {length_instruction}</length>

<language_level>{level_label}: {level_instruction}</language_level>

<wikipedia_excerpt>
{article_title}

{extracted_paragraphs}
</wikipedia_excerpt>
```

The system prompt instructs the LLM to:

1. **Write 5 texts** in the specified genre, inspired by (but not copying) the Wikipedia excerpt, at the specified length and language level.
2. **Define exactly 15 shared semantic labels** spanning the semantic space of all 5 texts, focusing on meaning and intent rather than surface vocabulary.
3. **Assign labels per text**: 1–5 positive labels and 8–15 negative labels from the shared vocabulary, where negatives must be plausible enough to require careful reading to rule out.
4. **Satisfy the cross-role constraint**: every label appears as positive in at least one text and negative in at least one different text.

### 4.3 LLM Generation

Generation uses a locally served LLM via vLLM. The project went through two generating models:

1. **Initial generation**: `Jackrong/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled` (27B parameters, reasoning-distilled). This model produced high-quality bundles but was prohibitively slow due to its reasoning chain-of-thought overhead — each generation included an internal reasoning trace before the JSON output, significantly increasing latency and reducing throughput.

2. **Current generation**: `google/gemma-4-E4B-it` (Gemma 4, released 2026, mixture-of-experts with only 4B active parameters). Despite being dramatically smaller in active parameter count, Gemma 4 E4B produces comparable label quality at much higher throughput, enabling the scale-up to ~900k examples. The smaller active footprint also reduces GPU memory pressure, allowing higher concurrency.

| Parameter | Value |
|-----------|-------|
| Current model | `google/gemma-4-E4B-it` (4B active params, MoE) |
| Previous model | `Jackrong/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled` (27B, reasoning) |
| Serving | vLLM with tensor parallelism (2 GPUs), `bfloat16`, prefix caching enabled |
| Temperature | 0.7 |
| Top-p | 0.95 |
| Top-k | 64 |
| Max output tokens | 4,096 |
| Max input tokens | 6,144 |
| Concurrency | 48 concurrent async workers |

The pipeline uses an async producer–consumer architecture: a feed task streams articles from the dataset into an `asyncio.Queue`, and a pool of worker tasks dequeue articles, build prompts, call the API, validate responses, and write results to a JSONL file under a shared lock.

### 4.4 Post-Processing and Validation

Each LLM response is parsed as JSON using `llm-output-parser` (which handles common LLM JSON formatting issues like trailing commas, missing quotes, and markdown code fences). Bundles are validated and expanded into individual examples:

1. **Bundle validation**: The response must be a dict with a non-empty `examples` list.
2. **Per-example validation**: Each example must have a non-empty `text` (string), at least one label in `labels`, and at least one label in `not_labels`.
3. **Intersection removal**: Any label appearing in both `labels` and `not_labels` for the same text is removed from both lists.
4. **Metadata attachment**: Each example is annotated with its source (`wikipedia`), genre name, and language level.

Failed API calls (after 5 retries with exponential backoff) and malformed responses are counted and logged but do not halt generation.

### 4.5 Resume Support

The pipeline supports resumption: on startup, it counts existing lines in the output file, computes how many articles have already been consumed (assuming 5 examples per bundle), and skips that many articles plus any user-specified skip offset in the streaming dataset. This enables running generation across multiple sessions without duplication.

### 4.6 Train/Test Split

The final dataset uses a **label-based split** to evaluate true zero-shot generalization:

1. A fraction of positive labels is randomly selected as held-out test labels.
2. Rows containing at least one held-out label in their `labels` field are assigned to the **test** split.
3. Rows where any held-out label appears in either `labels` or `not_labels` are excluded from the **train** split, preventing information leakage.

This yields approximately 30% novel labels in the test set — labels never encountered during training — forcing models to generalize to unseen semantic categories rather than memorizing label-specific patterns.

---

## 5. Dataset Statistics

| Property | Value |
|----------|-------|
| Total examples | ~900,000 (actively expanding) |
| Source | Wikipedia (`20231101.en`) |
| Distinct genres | 70 |
| Language levels | 5 (A2, B1, B2, C1, C2) |
| Text lengths | 5 (very short to very long) |
| Labels per bundle | 15 shared |
| Positive labels per text | 1–5 |
| Negative labels per text | 8–15 |
| Generation model | Gemma 4 E4B (4B active, MoE); initial runs used Qwen3.5-27B |
| Format | JSONL |
| License | See repository |

Each example contains:
```json
{
  "source": "wikipedia",
  "genre": "investigative journalism",
  "language_level": "B2",
  "text": "A three-year analysis of coastal erosion patterns...",
  "labels": ["evidence_based_causal_argument", "environmental_degradation_framing"],
  "not_labels": ["conservation_success_story", "policy_recommendation", "historical_documentation", ...]
}
```

---

## 6. Analysis

### 7.1 Label Quality: Semantic Depth

The defining feature of ZSHOT-HARDSET is that labels describe *meaning and intent* rather than surface topics. We illustrate this with representative examples from the Wikipedia variant.

**Example 1** — Genre: *investigative journalism*, Language level: C1

> Text: "Internal documents obtained by this newsroom reveal that the provincial water authority had been aware of elevated lead concentrations in the municipal supply for at least eighteen months before issuing any public advisory."

| | Labels |
|--|--------|
| Positive | `institutional_accountability_claim`, `evidence_based_revelation` |
| Negative (plausible but false) | `policy_recommendation`, `whistleblower_testimony`, `retrospective_causal_analysis`, `regulatory_compliance_documentation` |

Note that `whistleblower_testimony` is a strong hard negative: the text *looks like* it could involve a whistleblower, but it specifically frames the source as "internal documents obtained by this newsroom" — a journalistic investigation, not a whistleblower account.

**Example 2** — Genre: *Reddit post*, Language level: B1

> Text: "honestly I tried this recipe last weekend and it turned out way better than I expected, my kids actually asked for seconds which literally never happens"

| | Labels |
|--|--------|
| Positive | `surprised_positive_outcome`, `anecdotal_personal_evidence`, `casual_endorsement` |
| Negative (plausible but false) | `expert_culinary_assessment`, `comparative_product_evaluation`, `qualified_recommendation_with_caveats` |

Here, `expert_culinary_assessment` is a hard negative: the text discusses cooking, but the register is explicitly casual and personal, not expert.

### 7.2 The Cross-Role Constraint in Practice

The cross-role constraint ensures that within each bundle of 5 texts, every label switches roles. Consider a bundle about a Wikipedia article on volcanic geology:

| Label | Text 1 (encyclopedia) | Text 2 (Reddit post) | Text 3 (news lede) | Text 4 (patent claim) | Text 5 (poem) |
|-------|---------|---------|---------|---------|---------|
| `geological_process_explanation` | ✓ positive | ✗ negative | ✗ negative | — | — |
| `subjective_aesthetic_response` | ✗ negative | — | — | ✗ negative | ✓ positive |
| `technical_specification` | — | ✗ negative | — | ✓ positive | ✗ negative |

This structure means the model cannot learn "geological_process_explanation is always positive" — it must learn *when* it applies based on the text content.

### 7.3 Genre Distribution

The 70 genres span a wide register space. By sampling uniformly at random, the dataset achieves approximately equal representation across genres (~1.4% each), though some genres produce higher validation rates than others. Formal/institutional genres (legal document, patent claim) tend to have higher JSON-parse success rates due to more structured LLM outputs, while creative genres (song lyrics, stand-up comedy) occasionally produce responses that are harder to parse as valid JSON.

### 7.4 Language Level and Length Distribution

The 5 language levels (A2–C2) and 5 text lengths (very short to very long) are sampled uniformly. This creates a range from single-sentence A2 texts ("The volcano is very big and makes loud sounds.") to multi-paragraph C2 texts with complex subordination and domain-specific vocabulary. This variation is critical for training models that encounter diverse input complexity in practice.

---

## 7. Downstream Evaluation

### 7.1 GliZNet: Zero-Shot Text Classification

ZSHOT-HARDSET-v2 serves as the primary training corpus for GliZNet (Kameni, 2025), a zero-shot text classification model that processes text and all candidate labels jointly in a single transformer forward pass.

GliZNet's architecture uses label-conditioned cross-attention — each label attends to the text tokens most relevant to it, producing a unique text representation per label — followed by bilinear scoring. It is trained with a multi-objective loss combining one-vs-negatives softmax cross-entropy, focal loss, and label repulsion.

On the 10-dataset GLiClass benchmark (Stepanov et al., 2025):

| Model | Params | Training Data | Training Pipeline | Avg Macro F1 |
|-------|--------|---------------|-------------------|-------------|
| GLiClass-large-v3 | 439M | 1.2M examples | 3-stage (pretrain + RL + LoRA) | 0.7417 |
| GLiClass-base-v3 | 187M | 1.2M examples | 3-stage (pretrain + RL + LoRA) | 0.7056 |
| **GliZNet** | **184M** | **~900k examples** | **1-stage (supervised)** | **0.6701** |
| GLiClass-modern-base-v3 | 151M | 1.2M examples | 3-stage (pretrain + RL + LoRA) | 0.6170 |

GliZNet achieves 0.6701 avg F1 with less training data, no reinforcement learning, and a single-stage pipeline. The gap to GLiClass-base (−0.0355) is modest and suggests that the *quality* of ZSHOT-HARDSET-v2's hard-negative semantic labels partially compensates for the training complexity advantage.

Per-dataset breakdown:

| Dataset | GliZNet | GLiClass-large | GLiClass-base |
|---------|---------|----------------|---------------|
| CR (sentiment) | 0.8848 | 0.9281 | 0.9127 |
| SST-2 (binary sentiment) | 0.9110 | 0.9176 | 0.8959 |
| SST-5 (5-class sentiment) | 0.3777 | 0.3798 | 0.3236 |
| IMDb (sentiment) | 0.8952 | 0.9366 | 0.9248 |
| 20-Newsgroups (20 topics) | 0.4798 | 0.5806 | 0.5045 |
| Enron Spam | 0.5370 | 0.7574 | 0.6252 |
| Financial PhraseBank | 0.8078 | 0.9023 | 0.9094 |
| AG News (4 topics) | 0.6925 | 0.7229 | 0.7209 |
| Emotion (6 emotions) | 0.4375 | 0.4504 | 0.4450 |
| Rotten Tomatoes | 0.6772 | 0.8411 | 0.7943 |

GliZNet trained on ZSHOT-HARDSET-v2 excels on tasks with semantically similar labels (SST-5: 0.3777 vs. GLiClass-base's 0.3236) — precisely the scenario where hard-negative training data provides the greatest advantage. The model must distinguish "very positive" from "positive" or "neutral", which mirrors the fine-grained semantic distinctions in the training labels.

### 7.2 Planned: Sentence-Level Classification

The semantic label framework of ZSHOT-HARDSET-v2 naturally extends to sentence-level classification. Because each text in the dataset is annotated with fine-grained semantic labels describing rhetorical stance, epistemic function, and argumentative structure, the dataset can support:

- **Multi-label sentence classification**: assigning multiple semantic descriptors to individual sentences
- **Sentence-level zero-shot transfer**: training on paragraph-level annotations and evaluating at the sentence level
- **Label-conditioned retrieval**: using label embeddings to retrieve sentences that match specific rhetorical or stylistic criteria

These experiments are planned as future work.

---

## 8. Ablation Considerations

While formal ablations are deferred to future work, the pipeline design enables several natural ablation studies:

### 9.1 Genre Diversity

**Question**: Does training on 70 genres help compared to a single genre (e.g., encyclopedia entries only)?

The genre injection mechanism allows generating datasets with any subset of genres. We hypothesize that genre diversity is critical for cross-register generalization — a model trained only on encyclopedia-style texts would struggle with informal inputs like Reddit posts or product reviews.

### 9.2 Number of Shared Labels

**Question**: Is 15 labels per bundle optimal, or would 5 or 30 be better?

The `NUM_LABELS` parameter in the configuration controls this. Fewer labels may produce higher-quality individual labels but less diversity; more labels may overwhelm the LLM's ability to maintain coherent semantic coverage.

### 9.3 Cross-Role Constraint

**Question**: How much does the cross-role constraint matter compared to unconstrained label generation?

Removing the cross-role constraint from the prompt would allow labels that are always positive or always negative within a bundle. We expect this would reduce the difficulty of the negative examples and produce weaker models, but this remains to be verified empirically.

### 9.4 Label Depth

**Question**: What is the effect of shallow (topic-keyword) vs. deep (semantic) labels?

The prompt explicitly contrasts shallow and deep labels with examples. Replacing the depth instruction with a generic "generate labels" directive would test whether the explicit depth guidance matters.

---

## 9. Limitations

1. **Single-language**: The dataset is English-only. Extending to multilingual generation would require multilingual source data and potentially multilingual generating LLMs.

2. **LLM-generated labels are not human-verified at scale**: While spot-checking confirms that the generating LLM generally follows the semantic depth and cross-role constraints, we have not conducted a systematic human evaluation of label quality across the full dataset. Some labels may be shallow despite the prompt constraints.

3. **Cross-role constraint is self-reported**: The generating LLM is instructed to satisfy the constraint, but compliance is not verified programmatically post hoc. Enforcement through validation (rejecting bundles that violate the constraint) would increase quality at the cost of throughput.

4. **Genre distribution is uniform by design**, which may not match the register distribution of downstream applications. Weighted sampling of genres could be used to tailor the dataset to specific domains.

5. **Reproducibility depends on LLM availability**: The generating models (`google/gemma-4-E4B-it`, `Jackrong/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled`) are open-weight but may be updated or removed. The generation code is fully released to enable regeneration with alternative models.

---

## 10. Ethics and Broader Impact

The dataset is generated from Wikipedia (CC BY-SA 3.0). The generating LLMs may reproduce biases present in their training data. The texts are synthetic — no personal data is collected or annotated.

The dataset is intended for research on zero-shot text classification. The generation pipeline could be adapted for adversarial purposes (e.g., generating plausible-sounding but false labels to mislead classifiers), though this risk is inherent to any synthetic data generation capability.

---

## 11. Conclusion

ZSHOT-HARDSET-v2 introduces a principled approach to training data for zero-shot text classification: hard-negative semantic labels generated under structural constraints (cross-role, genre diversity, depth requirements) that force models to learn genuine semantic reasoning rather than surface-level pattern matching.

The iterative development from v1 to v2 revealed two critical failure modes — text repetition without grounding context, and label isolation without the cross-role constraint — and demonstrated that each fix directly improved downstream model quality. The cross-role constraint is particularly important: by requiring the same label to be positive for some texts and negative for others, it makes label-identity-based separable hyperplanes impossible and forces models to learn genuine text–label alignment through embedding interaction.

Trained on ZSHOT-HARDSET-v2, GliZNet achieves competitive zero-shot performance (0.6701 avg F1) with no reinforcement learning and a single-stage pipeline compared to GLiClass models using multi-stage training. The dataset's advantage is most pronounced on tasks requiring fine-grained label discrimination (SST-5), validating the hard-negative design.

The dataset, generation code, and trained models are publicly available:

- **ZSHOT-HARDSET-v2**: [huggingface.co/datasets/alexneakameni/ZSHOT-HARDSET-v2](https://huggingface.co/datasets/alexneakameni/ZSHOT-HARDSET-v2)
- **Generation code**: [github.com/KameniAlexNea/generate-gliznet-data](https://github.com/KameniAlexNea/generate-gliznet-data)
- **GliZNet model and training**: [github.com/KameniAlexNea/zero-shot-classification](https://github.com/KameniAlexNea/zero-shot-classification)

---

## References

- Kameni, A. (2025). *GliZNet: A Novel Architecture for Zero-Shot Text Classification*. Technical report.
- Stepanov, I. et al. (2025). *GLiClass: Generalist Lightweight Model for Sequence Classification Tasks*. arXiv:2508.07662.
- Williams, A., Nangia, N., & Bowman, S. R. (2018). *A Broad-Coverage Challenge Corpus for Sentence Understanding through Inference*. NAACL-HLT.
- Taori, R. et al. (2023). *Stanford Alpaca: An Instruction-Following LLaMA Model*. GitHub repository.
- Wang, Y. et al. (2023). *Self-Instruct: Aligning Language Models with Self-Generated Instructions*. ACL.
- Schroff, F., Kalenichenko, D., & Philbin, J. (2015). *FaceNet: A Unified Embedding for Face Recognition and Clustering*. CVPR.
- Robinson, J. et al. (2021). *Contrastive Learning with Hard Negative Samples*. ICLR.
- Zaratiana, U. et al. (2023). *GLiNER: Generalist Model for Named Entity Recognition Using Bidirectional Transformer*. arXiv:2311.08526.
- He, P. et al. (2021). *DeBERTaV3: Improving DeBERTa using ELECTRA-Style Pre-Training*. arXiv:2111.09543.
- Yin, W. et al. (2019). *Benchmarking Zero-Shot Text Classification: Datasets, Evaluation and Entailment Approach*. arXiv:1909.00161.
