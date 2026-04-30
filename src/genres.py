
# Each entry: (genre_name, brief_description_for_the_model)
# All genres are applied to a Wikipedia excerpt provided as context.
# The model must write texts INSPIRED BY (not copying) that excerpt, in the register below.
TEXT_GENRES = [
    # ── Reference / Encyclopedic ─────────────────────────────────────────────
    ("encyclopedia entry",         "A reworked neutral third-person encyclopedic paragraph about the Wikipedia topic, as it might appear in a different reference work — factual, structured, no original analysis. Do NOT copy the source verbatim; rephrase, reorganise, and compress."),
    ("academic abstract",          "The abstract of a research paper whose subject is drawn from the Wikipedia topic: structured summary of aim, method, results, and conclusion — past-tense, formal, impersonal."),
    ("museum or exhibit label",    "A short interpretive label displayed beside an artifact or exhibit about the Wikipedia topic: neutral, present-tense, contextualises the subject historically or culturally for a general audience."),
    ("textbook explanation",       "A pedagogical passage explaining the Wikipedia topic to students: clear definitions, structured reasoning, illustrative examples drawn from the topic's key concepts."),

    # ── Journalism ───────────────────────────────────────────────────────────
    ("news article lede",          "The opening sentence(s) of a news article reporting on the Wikipedia topic: who, what, when, where, why — direct and punchy."),
    ("investigative journalism",   "A passage from a long-form investigative piece on the Wikipedia topic: evidence-driven, narrative tension, named sources, building toward a revelation."),
    ("tabloid headline or lede",   "Sensational tabloid prose about the Wikipedia topic: punchy verbs, hyperbole, celebrity or scandal framing even for dry subjects — breathless register."),
    ("op-ed / opinion column",     "A strong personal argument about the Wikipedia topic in a newspaper opinion piece: direct, polemical, first-person authority."),
    ("sports commentary",          "Energetic commentary covering the Wikipedia topic as if it were a live or recent sporting event: competitive stakes, dramatic moments, statistics — any topic can be framed as a contest or championship."),

    # ── Academic / Scientific ────────────────────────────────────────────────
    ("empirical paper finding",    "A single key result or finding as it would appear in a scientific paper about the Wikipedia topic: specific, data-grounded, past-tense, with implied methodology."),
    ("humanities paper argument",  "A claim or interpretive assertion about the Wikipedia topic from a humanities essay: argumentative, citational, present-tense."),
    ("peer review comment",        "A referee-style critique treating the Wikipedia topic as the subject of an academic manuscript: constructive but critical, hedged with 'appears' or 'seems', numbered concerns, formal register."),
    ("grant proposal excerpt",     "An academic or NGO funding application whose project addresses the Wikipedia topic: formal, objective-driven, evidence-cited, future-tense."),
    ("ethnographic field note",    "An observer's field note about the Wikipedia topic treated as a social or cultural phenomenon under study: present-tense, etic perspective, thick description, analytical detachment."),

    # ── Personal / Conversational ────────────────────────────────────────────
    ("Reddit post",                "A casual first-person post on a subreddit relevant to the Wikipedia topic: conversational, opinionated, informal, may include personal anecdote or hot take."),
    ("personal blog post",         "A reflective first-person blog entry about the Wikipedia topic: engaging, anecdotal, written for a curious general audience."),
    ("diary or journal entry",     "An intimate personal note in which the writer reflects on the Wikipedia topic: introspective, emotional, present or past-tense, written for oneself."),
    ("oral history excerpt",       "A first-person spoken account about the Wikipedia topic as recalled in an interview or memoir: conversational, personal memory, vivid sensory detail."),
    ("forum Q&A answer",           "A direct answer to a question about the Wikipedia topic in an online forum: practical, slightly informal, to the point."),
    ("chat or SMS exchange",       "An informal text-message conversation about the Wikipedia topic between two people: fragmented sentences, abbreviations, real-time register."),
    ("podcast transcript excerpt", "A lightly edited spoken-word passage in which hosts discuss the Wikipedia topic: conversational rhythm, occasional filler words, exploratory tone."),

    # ── Narrative / Creative ─────────────────────────────────────────────────
    ("documentary narration",      "Voice-over narration from a documentary about the Wikipedia topic: evocative, present-tense, cinematic pacing, builds emotional engagement."),
    ("biography excerpt",          "A biographical or profile-style passage about the Wikipedia subject: if a person, narrative with specific life milestones; if a concept, place, or institution, treated as if it had a 'life story' — third-person, narrative."),
    ("myth or folklore retelling", "A passage from a traditional myth, fairy tale, or folk legend inspired by the Wikipedia topic: archetypal characters, timeless present or simple past, oral-story rhythm."),
    ("fantasy or sci-fi world-building", "Descriptive prose establishing a fictional world whose rules, history, or setting are drawn from the Wikipedia topic: immersive, invented terminology, world-atlas register."),
    ("song lyrics",                "An excerpt from song lyrics inspired by the Wikipedia topic: rhythmic, metaphorical, first- or second-person, emotionally direct, line-broken structure, repetition for emphasis."),
    ("children's book passage",    "Simple, rhythmic prose for young readers about the Wikipedia topic: short sentences, concrete imagery, gentle or playful tone."),
    ("film or TV synopsis",        "A neutral present-tense plot-summary treating the Wikipedia topic as if it were a film or TV episode: characters (real or conceptual), conflict, resolution — detached, informative, spoiler-ready."),

    # ── Formal / Institutional ───────────────────────────────────────────────
    ("legal or policy document",   "Dry, precise prose from a regulation, contract, or policy brief about the Wikipedia topic: formal, hedged, impersonal, structured clauses."),
    ("press release",              "A corporate or institutional announcement about the Wikipedia topic: formal, promotional, third-person, structured facts, standard boilerplate close."),
    ("diplomatic statement",       "An official international statement about the Wikipedia topic: formal hedging ('calls upon', 'reaffirms'), passive constructions, multilateral framing, impersonal register."),
    ("parliamentary debate",       "A floor speech about the Wikipedia topic: formal address to the chamber, adversarial framing, appeal to precedent or procedure, elevated register."),
    ("court or legal testimony",   "A first-person account related to the Wikipedia topic as given under oath: precise, chronological, hedged, formal diction."),
    ("patent claim",               "A formal patent claim whose invention is inspired by the Wikipedia topic: 'A method comprising…' syntax, exhaustive enumeration of steps or components, legal-technical register."),
    ("intelligence briefing memo", "An internal intelligence or policy briefing memo on the Wikipedia topic: factual bullet-point summary, action items, need-to-know framing, bureaucratic precision, impersonal."),
    ("financial report excerpt",   "A passage from an annual report or earnings release about an entity related to the Wikipedia topic: numerical, forward-looking statements, formal investor register."),
    ("political manifesto excerpt","A programmatic statement of values and goals related to the Wikipedia topic: declarative, urgent, ideologically charged."),

    # ── Promotional / Commercial ─────────────────────────────────────────────
    ("advertisement copy",         "Promotional text selling the Wikipedia topic as a product, service, or experience: benefit-driven, imperative or second-person, punchy hook, call to action."),
    ("real estate listing",        "A property-advertisement-style description treating the Wikipedia topic as a place or space to inhabit: feature-by-feature enumeration, aspirational adjectives, practical details — works literally for places or creatively for any subject."),
    ("job posting",                "A job advertisement where the Wikipedia topic defines the role, field, or hiring organisation: role-focused requirements, bullet-pointed skills drawn from the topic, formal-yet-inviting register."),
    ("crowdfunding pitch",         "A campaign pitch seeking public backing for a project related to the Wikipedia topic: emotive, first-person, problem–solution–ask structure."),
    ("startup pitch",              "A paragraph from a venture-capital pitch whose product or market is drawn from the Wikipedia topic: market-size framing, problem–solution–traction structure, confident future-tense, business jargon."),

    # ── Service / Practical ──────────────────────────────────────────────────
    ("how-it-works explainer",     "A plain-language explainer breaking down the Wikipedia topic as a process or mechanism for a curious lay reader."),
    ("instruction manual step",    "A single procedural step from a technical manual about using, performing, or applying the Wikipedia topic: imperative mood, precise, numbered-list style."),
    ("recipe",                     "A recipe-format text treating the Wikipedia topic as if it were a dish: its components as ingredients, its development as cooking steps, its outcome as the finished result — imperative mood, precise quantities or proportions, sensory cues."),
    ("FAQ entry",                  "A question-and-answer pair about the Wikipedia topic as it might appear on a help or support page: direct, practical, second-person, anticipates a common point of confusion."),
    ("medical patient leaflet",    "Plain-language information about the Wikipedia topic written for a non-expert, styled as a patient leaflet: reassuring tone, imperative cautions, structured sections (what it is, what to expect, what to do)."),
    ("technical README",           "Developer-facing documentation about the Wikipedia topic treated as a software library or tool: terse, imperative, code-adjacent, assumes technical literacy."),
    ("error message or system alert","A terse software-generated notification treating the Wikipedia topic as a system event, process, or failure: passive or imperative mood, code-like references, minimal prose, diagnostic register."),
    ("weather forecast",           "A meteorological-bulletin-style report treating the Wikipedia topic's dynamics, state, or trajectory as weather conditions: technical register (fronts, pressure, probability) applied metaphorically or literally to the topic."),
    ("travel guide entry",         "Descriptive travel-guide prose about the Wikipedia topic treated as a destination or experience: vivid sensory detail, practical information, second-person warmth — works for real places or reimagines any topic as somewhere to visit."),
    ("self-help passage",          "Motivational advice prose that uses the Wikipedia topic as a lesson, metaphor, or framework: second-person coaching, actionable steps, optimistic framing."),

    # ── Cultural / Miscellaneous ─────────────────────────────────────────────
    ("social media thread",        "The opening tweet or thread post about the Wikipedia topic: short, declarative, hook-driven, often provocative or surprising claim."),
    ("product or book review",     "A short consumer-style review treating the Wikipedia topic as the product, book, or experience being evaluated: personal encounter, evaluative tone, concrete details, implied star rating."),
    ("customer complaint",         "A frustrated but specific complaint about an experience with the Wikipedia topic treated as a service, product, or institution: first-person, grievance-driven, concrete incident."),
    ("listicle entry",             "One item from a numbered or bulleted web list about the Wikipedia topic: punchy, self-contained, slightly informal."),
    ("speech excerpt",             "A line from a formal speech or address about the Wikipedia topic: rhetorical, second-person appeal, elevated register, memorable phrasing."),
    ("letter or email",            "An excerpt from a formal or semi-formal letter about the Wikipedia topic: addressed tone, clear purpose, specific context."),
    ("satirical piece",            "Dry or absurdist humor commenting on the Wikipedia topic: deadpan, ironic, mimics a serious register (official report, academic paper) while undercutting it."),
    ("obituary",                   "A respectful retrospective about the Wikipedia subject: if a person, summarises life and legacy; if a concept, institution, or era, marks its significance, rise, and end — past-tense, commemorative, specific milestones."),
    ("eulogy",                     "A spoken tribute about the Wikipedia subject delivered to an implied audience: celebratory of achievements, emotionally layered, past-tense — works for people, institutions, or ended eras."),
    ("stand-up comedy bit",        "A segment of stand-up material about the Wikipedia topic: setup-punchline rhythm, observational or absurdist angle on the subject, conversational aside to the audience."),
    ("horoscope column",           "A weekly horoscope entry whose predictions are shaped by the Wikipedia topic: second-person address, vague yet intimate forecasts, celestial imagery applied metaphorically to the topic's themes."),
    ("auction catalog entry",      "A lot description from an art or antiques auction for an item related to the Wikipedia topic: provenance, condition, attribution, estimated value, formal art-world register."),
    ("nature writing",             "Reflective prose about the Wikipedia topic experienced through or compared to the natural world: sensory, slow-paced, ecological or philosophical awareness."),
    ("crisis communication statement","Corporate damage-control statement about an incident related to the Wikipedia topic: empathetic opening, factual recount, corrective action, forward-looking reassurance, carefully hedged language."),

    # ── Specialised Professional ─────────────────────────────────────────────
    ("medical case report",        "Clinical case write-up in which the Wikipedia topic is the central medical subject or condition: patient history, symptom timeline, diagnostic reasoning, treatment, outcome — third-person, formal, evidence-grounded."),
    ("philosophical thought experiment","A hypothetical scenario inspired by the Wikipedia topic used to test a philosophical claim: precise setup, controlled variables, logical implication, abstract register."),
    ("therapy progress note",      "A clinician's session note in which the Wikipedia topic is the presenting concern or context: objective behavioral observations, affective assessment, treatment goals, impersonal third-person clinical register."),
    ("code comment or docstring",  "Inline developer documentation treating the Wikipedia topic as a software component: terse, imperative or descriptive, parameter- and return-value-focused, assumes reader can read code."),

    # ── Multiple-Choice Questions (diverse domains) ──────────────────────────
    # FORMAT FOR ALL MCQ GENRES — completely different from other genres:
    #   "text"       : a SHORT CONTEXT (1–3 sentences of domain-relevant information inspired
    #                  by the Wikipedia topic) FOLLOWED BY a question. No answer options in text.
    #   "labels"     : list containing the correct answer(s), written as short answer strings.
    #   "not_labels" : list of 3–5 plausible-but-wrong distractor answers, also short strings.
    # The zero-shot model will receive `text` and must pick the right answer from
    # the union of labels + not_labels. Distractors must be drawn from the same
    # domain/category as the correct answer to be genuinely hard.
    ("math MCQ",                   "Write a short factual context (1–3 sentences about the Wikipedia topic's quantitative aspects), then a mathematics question. Text = context + question (no options). labels = [correct numerical or symbolic answer]. not_labels = [3 wrong answers based on common errors, e.g. sign mistake, wrong formula, off-by-one]."),
    ("history MCQ",                "Write a short historical context (1–3 sentences drawn from the Wikipedia topic), then a causal or interpretive question — NOT a fact-retrieval question. Ask WHY or WHAT CAUSED, not WHO or WHEN. Text = context + question (no options). labels = [correct answer: a cause, structural factor, or consequence that must be inferred from the context — never a name, date, or phrase appearing verbatim in the text]. not_labels = [3–4 historically plausible alternative explanations from the same era that the context does not support]."),
    ("science MCQ",                "Write a short scientific context (1–3 sentences explaining the relevant concept or phenomenon from the Wikipedia topic), then a question. Text = context + question (no options). labels = [correct answer: a concept, formula, or value]. not_labels = [3 distractors reflecting typical misconceptions or unit/sign errors]."),
    ("literature MCQ",             "Write a short literary context (1–3 sentences about the work, author, or movement connected to the Wikipedia topic), then an interpretive or thematic question — NOT an author-name or title-recall question. Ask about narrative function, thematic claim, or structural choice. Text = context + question (no options). labels = [correct answer: a thematic claim, literary device, or interpretive conclusion that must be inferred from the context — not a name or title stated verbatim]. not_labels = [3–4 plausible but wrong interpretations or misapplied critical concepts that fit the question's surface form]."),
    ("geography MCQ",              "Write a short geographic context (1–3 sentences describing the relevant place, region, or feature from the Wikipedia topic), then a relational or inferential question — NOT a 'what is the name of X' question. Ask about spatial consequences, geographic causes, or derived properties. Text = context + question (no options). labels = [correct answer: a spatial relationship, geographic consequence, or derived fact that must be reasoned from the context — not a place name stated verbatim]. not_labels = [3–4 plausible alternatives from the same region that the context does not support]."),
    ("medicine & biology MCQ",     "Write a short biomedical context (1–3 sentences about the relevant anatomy, condition, or mechanism from the Wikipedia topic), then a question. Text = context + question (no options). labels = [correct answer: anatomical structure, drug, mechanism, or condition]. not_labels = [3–4 distractors targeting frequent confusions between related structures or mechanisms]."),
    ("philosophy & ethics MCQ",    "Write a short philosophical context (1–3 sentences presenting the relevant argument, thinker, or ethical situation from the Wikipedia topic), then a question. Text = context + question (no options). labels = [correct answer: a philosopher, theory, term, or argument]. not_labels = [3–4 superficially similar positions, misattributions, or confused concepts]."),
    ("law & civics MCQ",           "Write a short legal or civic context (1–3 sentences describing the relevant doctrine, institution, or case inspired by the Wikipedia topic), then a question. Text = context + question (no options). labels = [correct answer: a doctrine, article, institution, or right]. not_labels = [3–4 related but wrong doctrines or provisions that exploit legal ambiguity]."),
    ("economics MCQ",              "Write a short economic context (1–3 sentences describing the relevant market situation, concept, or historical event from the Wikipedia topic), then a question. Text = context + question (no options). labels = [correct answer: a concept, effect, or definition]. not_labels = [3–4 distractors reflecting common confusions between related economic terms or effects]."),
    ("computer science MCQ",       "Write a short technical context (1–3 sentences describing the relevant algorithm, data structure, or system from the Wikipedia topic), then a question. Text = context + question (no options). labels = [correct answer: a complexity class, output, or definition]. not_labels = [3 plausible-sounding but wrong complexities, outputs, or definitions]."),
    ("general knowledge trivia MCQ","Write a short contextual setup (1–3 sentences of accessible background about the Wikipedia topic), then a question whose answer must be inferred or computed from the context — not retrieved verbatim from it. The context should make the answer deducible, not simply readable. Text = context + question (no options). labels = [correct answer: a fact, quantity, or relationship derivable from what the context implies]. not_labels = [3–4 plausible items from the same category that the context does not support]."),
    ("reading comprehension MCQ",  "Write a short passage (1–3 sentences) inspired by the Wikipedia topic, then an inferential comprehension question testing implied meaning, logical consequence, or authorial intent — NOT surface retrieval. Text = passage + question (no options). labels = [correct answer: an inference or implication supported by the passage but not stated verbatim — the reader must interpret, not scan]. not_labels = [3 plausible-sounding answers that require careful reading to rule out, including at least one that uses words from the passage but misrepresents its meaning]."),
]