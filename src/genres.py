
# Each entry: (genre_name, brief_description_for_the_model)
# All genres are applied to a Wikipedia excerpt provided as context.
# The model must write texts INSPIRED BY (not copying) that excerpt, in the register below.

# (label, instruction passed to the model)
TEXT_LENGTHS = [
    ("very short",  "Each text must be exactly 1 sentence — dense and self-contained."),
    ("short",       "Each text must be 1–2 sentences."),
    ("medium",      "Each text must be 2–3 sentences."),
    ("long",        "Each text must be 3–5 sentences forming a coherent, developed paragraph."),
    ("very long",   "Each text must be 5–8 sentences: a fully developed paragraph with context, development, and a closing point."),
]

# (label, instruction passed to the model)
LANGUAGE_LEVELS = [
    ("A2",  "Use very simple English: short sentences, common everyday words only, no jargon or complex grammar. Suitable for beginners."),
    ("B1",  "Use plain, clear English: straightforward sentences, familiar vocabulary, minimal technical terms. Suitable for intermediate speakers."),
    ("B2",  "Use standard educated English: varied sentence structure, some domain vocabulary, clear but not simplified."),
    ("C1",  "Use sophisticated English: complex sentence structures, precise vocabulary, idiomatic expressions, domain-specific register."),
    ("C2",  "Use highly sophisticated English: nuanced, dense prose, advanced register, rhetorical complexity — as in published academic or literary writing."),
]
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
    ("letter to the editor",       "A reader's letter submitted to a newspaper or magazine about the Wikipedia topic: opinionated, concise, addressed to the publication, appeals to civic or community concern — distinct from an op-ed in its brevity and reader-voice register."),

    # ── Academic / Scientific ────────────────────────────────────────────────
    ("empirical paper finding",    "A single key result or finding as it would appear in a scientific paper about the Wikipedia topic: specific, data-grounded, past-tense, with implied methodology."),
    ("humanities paper argument",  "A claim or interpretive assertion about the Wikipedia topic from a humanities essay: argumentative, citational, present-tense."),
    ("peer review comment",        "A referee-style critique treating the Wikipedia topic as the subject of an academic manuscript: constructive but critical, hedged with 'appears' or 'seems', numbered concerns, formal register."),
    ("grant proposal excerpt",     "An academic or NGO funding application whose project addresses the Wikipedia topic: formal, objective-driven, evidence-cited, future-tense."),
    ("ethnographic field note",    "An observer's field note about the Wikipedia topic treated as a social or cultural phenomenon under study: present-tense, etic perspective, thick description, analytical detachment."),
    ("academic lecture transcript", "A lightly edited excerpt from a spoken university lecture on the Wikipedia topic: pedagogical but conversational, uses rhetorical questions and hedged claims, directly addresses students, builds understanding step by step."),

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
    ("sermon or religious address", "A passage from a sermon or religious speech using the Wikipedia topic as a moral or spiritual illustration: earnest, exhortatory, appeals to shared values, rhythmic repetition, second-person address to a congregation or assembly."),
    ("internal corporate memo",    "A workplace memo about the Wikipedia topic addressed to staff or management: action-oriented, audience-aware, less formal than a press release, bullet-pointed directives, impersonal but accessible register."),
    ("incident or police report",  "A formal record of an event related to the Wikipedia topic as it might appear in an official incident or police report: passive voice, third-person, precise dates and locations, bureaucratic documentation of facts without editorial interpretation."),
    ("terms of service excerpt",   "A passage from user-facing legal terms or an end-user license agreement related to the Wikipedia topic: dense subordinate clauses, limitation-of-liability framing, enumerated conditions, consumer-legal register."),

    # ── Promotional / Commercial ─────────────────────────────────────────────
    ("advertisement copy",         "Promotional text selling the Wikipedia topic as a product, service, or experience: benefit-driven, imperative or second-person, punchy hook, call to action."),
    ("real estate listing",        "A property-advertisement-style description treating the Wikipedia topic as a place or space to inhabit: feature-by-feature enumeration, aspirational adjectives, practical details — works literally for places or creatively for any subject."),
    ("job posting",                "A job advertisement where the Wikipedia topic defines the role, field, or hiring organisation: role-focused requirements, bullet-pointed skills drawn from the topic, formal-yet-inviting register."),
    ("crowdfunding pitch",         "A campaign pitch seeking public backing for a project related to the Wikipedia topic: emotive, first-person, problem–solution–ask structure."),
    ("startup pitch",              "A paragraph from a venture-capital pitch whose product or market is drawn from the Wikipedia topic: market-size framing, problem–solution–traction structure, confident future-tense, business jargon."),
    ("dating profile",             "A self-promotional first-person profile treating the Wikipedia topic as the subject seeking connection: aspirational, quirky self-description, highlights unique traits, appeals to shared interests — any topic reimagined as a personality looking for its match."),
    ("business proposal",          "A formal pitch document proposing a project or partnership related to the Wikipedia topic: structured sections, ROI framing, deliverables-focused, B2B register — more formal and specific than a startup pitch, addressed to a known decision-maker."),

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
    ("museum audio guide script",  "A timed spoken-word guide for a visitor standing before an exhibit related to the Wikipedia topic: second-person address, paced for a two-minute listening experience, sensory prompts directing attention, builds to a closing reflection — evocative but informative."),
    ("personal recommendation letter", "A formal letter endorsing a person, organisation, or initiative related to the Wikipedia topic: first-person endorser voice, specific evidence of merit, formal salutation and close, testimonial register — distinct from a press release in its personal accountability."),

    # ── Scalar / Ordinal Genres ──────────────────────────────────────────────
    # These genres produce texts where labels naturally form ordered scales or
    # task-linked groups (e.g. intensity, severity, progression, confidence).
    # The cross-role constraint forces the same scalar label to be positive for
    # one text (at that level) and negative for another (at a different level).
    ("performance evaluation",     "A workplace performance review passage about the Wikipedia topic treated as an employee, team, or system being assessed: uses graduated language implying a specific level on a scale from inadequate to exceptional — the reader should be able to infer the rating tier from tone and specifics alone."),
    ("severity triage note",       "A triage or incident-severity assessment about the Wikipedia topic treated as a condition, event, or system state: clinical or operational language that implies a specific severity tier (negligible, minor, moderate, serious, critical) — the 5 texts in this bundle must span different severity levels for the same underlying phenomenon."),
    ("maturity or readiness assessment", "An assessment of readiness, maturity, or development stage about the Wikipedia topic treated as a project, technology, organism, or institution: language that implies a specific stage on a maturity curve (nascent, developing, established, advanced, pioneering) — each text should inhabit a distinct stage."),
    ("confidence or certainty report", "A passage conveying a claim or prediction about the Wikipedia topic at a specific epistemic confidence level: language cues (hedging, qualifiers, assertiveness) must clearly signal the degree of certainty — from speculative conjecture through tentative hypothesis to established consensus. Each text in the bundle must occupy a different confidence tier."),
    ("emotional intensity narrative", "A first-person or close-third-person passage experiencing the Wikipedia topic at a specific emotional intensity: from detached observation through mild interest, moderate engagement, strong feeling, to overwhelming affect — the register, sentence rhythm, and word choice must encode the intensity level without naming it explicitly."),
    ("risk or threat assessment",  "A risk-assessment passage about the Wikipedia topic treated as a potential hazard, threat, or opportunity cost: formal evaluative language that places the subject at a specific risk level (negligible, low, moderate, high, extreme) — each text should correspond to a different risk tier while discussing the same underlying topic."),
    ("progress or phase update",   "A status update about the Wikipedia topic treated as a project, process, or journey at a specific phase: language must signal where on the timeline the subject stands (not started, early stage, midway, nearly complete, concluded) — each text occupies a distinct phase."),
    ("quality or grade description", "A quality-assessment passage about the Wikipedia topic treated as a product, specimen, or output being graded: descriptive language that implies a specific quality tier (defective, below average, acceptable, good, exemplary) without stating the grade explicitly — the reader infers the tier from details and tone."),
    ("urgency communication",      "A message about the Wikipedia topic whose register and framing encode a specific urgency level: from routine informational notice through advisory, to action-required warning, to immediate-response demand — sentence length, imperative density, and temporal framing must match the urgency tier."),
    ("commitment or conviction statement", "A statement of intent, belief, or allegiance related to the Wikipedia topic at a specific conviction level: from tentative openness through cautious support, firm commitment, passionate advocacy, to unconditional devotion — the strength of modal verbs, repetition, and rhetorical intensity must encode the level."),
]