# The Unofficial Guide: Purdue CS Professor Reviews

A RAG (Retrieval-Augmented Generation) system that makes student-generated knowledge about
Purdue CS professors searchable and answerable via a command-line interface.

---

## Domain and Document Sources

**Domain:** Student-generated reviews and opinions about Purdue CS professors — specifically
Borkowski, Sellke, and Bergstrom — covering courses CS 180, CS 18200, and CS 251.

This knowledge is valuable because it reflects real student experiences with grading style,
exam difficulty, lecture quality, and feedback that never appear in official course catalogs
or university websites. It is hard to find otherwise because it is scattered across Rate My
Professors pages, Reddit threads, and informal forums with no unified, searchable interface.

| # | Source | Description | URL |
|---|--------|-------------|-----|
| 1 | Rate My Professors | Student reviews for Michael Borkowski | https://www.ratemyprofessors.com/professor/3058603 |
| 2 | Rate My Professors | Student reviews for Sarah Sellke | https://www.ratemyprofessors.com/professor/1734941 |
| 3 | Rate My Professors | Student reviews for Tony Bergstrom | https://www.ratemyprofessors.com/professor/2523519 |
| 4 | Reddit r/Purdue | Thread: CS251 Borkowski curve question | https://www.reddit.com/r/Purdue/comments/1snpeix/ |
| 5 | Reddit r/Purdue | Threads: Bergstrom CS180 vs Dunsmore | https://www.reddit.com/r/Purdue/comments/1h5pxze/ |
| 6 | Reddit r/Purdue | Thread: CS251 curve and difficulty discussion | https://www.reddit.com/r/Purdue/ |
| 7 | Reddit r/Purdue | Thread: Sellke CS182/CS251 advice | https://www.reddit.com/r/Purdue/ |
| 8 | Purdue CS Faculty | Tony Bergstrom official faculty page | https://www.cs.purdue.edu/people/faculty/bgstm.html |
| 9 | Purdue CS Faculty | Michael Borkowski official faculty page | https://www.cs.purdue.edu/people/faculty/mhborkow.html |
| 10 | Coursicle | Michael Borkowski course history | https://www.coursicle.com/purdue/professors/Michael+Borkowski/ |

---

## Chunking Strategy

**Chunk size:** 300 characters
**Overlap:** 50 characters

**Reasoning:** RMP reviews are short opinion snippets — usually 2–5 sentences per review.
300 characters captures roughly 2–4 sentences of review text, which is enough for a single,
self-contained student opinion. A larger chunk would merge opinions about different topics
(grading, attendance, exams) into one embedding, making it hard to retrieve precisely. A
smaller chunk would cut sentences mid-thought and produce fragments with no standalone meaning.
50-character overlap ensures that a claim split across a chunk boundary is still represented
in at least one complete chunk.

### Sample Chunks

**Chunk 1** (source: rmp_borkowski.txt)
> "Prof. Borkowski is really nice and he knows the subject he's teaching. The class had generous policies and he was available to answer any questions I had. Overall a really good professor and experience."

**Chunk 2** (source: rmp_sellke.txt)
> "lectures are extremely hard to follow and don't explain concepts well at all. You'll be lost quickly even if you are paying attention. She is nice and tries to make things clear, but be ready to spend more time learning everything online yourself."

**Chunk 3** (source: reddit_bergstrom.txt)
> "Bergstrom is good, Dunsmore is considered universally good. Can't go wrong with either. I had Bergstrom last semester, and I found him to be decent. Although he doesn't provide his own slides ahead of time, he follows the same exact"

**Chunk 4** (source: reddit_cs251_curve.txt)
> "the curve is pretty nice, and make sure you do well on the projects since they're a decent chunk of your grade. This is just my opinion too, but I thought the exam 1 material was much harder than exam 2."

**Chunk 5** (source: reddit_sellke.txt)
> "I had Sellke for 182 and 251 and her best quality is that she's really nice. The unfortunate thing is she doesn't make sense a good 40-50% of the time."

---

## Embedding Model

**Model:** `all-MiniLM-L6-v2` via `sentence-transformers` (runs locally, no API key required)

**Production tradeoff reflection:** For a real deployment, several factors would influence
model choice. `all-MiniLM-L6-v2` is fast and free but has a 256-token context window, which
limits it for longer documents. A model like `text-embedding-3-small` from OpenAI offers
better accuracy on domain-specific phrasing and a larger context window, but costs per token
and introduces API latency and external uptime dependency. For a multilingual use case,
`paraphrase-multilingual-MiniLM-L12-v2` would be necessary. For this project, local + free
wins since latency and cost are not constraints — but in production with real user traffic,
a hosted model with better domain accuracy would be preferable, monitored with a held-out
eval set.

---

## Retrieval Test Results

**Query 1:** "Does Borkowski curve exams in CS 251?"

Top returned chunks:
- `reddit_cs251_curve.txt` (distance: 0.789) — "the curve is pretty nice" direct student quote
- `reddit_borkowski.txt` (distance: 0.906) — thread specifically asking about Borkowski's curve
- `rmp_borkowski.txt` (distance: 1.009) — Borkowski RMP review mentioning generous policies

**Why relevant:** The top two chunks directly address the curve question — one is a thread
explicitly asking about Borkowski's curve, the other contains a direct quote saying "the curve
is pretty nice." These are exactly the documents a student would want to find.

**Query 2:** "Are Sellke's lectures easy to follow in CS 18200?"

Top returned chunks:
- `rmp_sellke.txt` (distance: 0.683) — "lectures are extremely hard to follow"
- `rmp_sellke.txt` (distance: 0.794) — "rarely explained how she derived the next step"
- `rmp_sellke.txt` (distance: 0.824) — "Sellke was not the best at teaching"

**Why relevant:** All three top chunks come directly from Sellke's RMP page and address
lecture quality explicitly. Distance scores under 0.83 indicate strong semantic matches —
the best retrieval performance of any query in this system.

**Query 3:** "How hard is CS 180 with Bergstrom compared to other sections?"

Top returned chunks:
- `reddit_bergstrom.txt` (distance: 1.038) — comparison thread with Dunsmore
- `reddit_bergstrom.txt` (distance: 1.040) — "Can't go wrong with either"
- `rmp_bergstrom.txt` (distance: 1.221) — overall rating and difficulty score

---

## Grounded Generation

Grounding is enforced in the system prompt passed to the LLM on every query:

```
Answer the question using ONLY the information in the provided documents below.
If the documents don't contain enough information to answer the question, say exactly:
"I don't have enough information in my documents to answer that."
Do not use any outside knowledge. Cite which source(s) your answer draws from.
```

Retrieved chunks are injected into the prompt as labeled context blocks with their source
filename. The model is explicitly instructed not to use outside knowledge and to decline
out-of-scope questions rather than generating plausible-sounding answers from training data.

---

## Example Responses

**Example 1 — Grounded response with source attribution:**

Query: "Does Borkowski curve exams in CS 251?"

> According to the provided documents, specifically reddit_borkowski.txt and
> reddit_cs251_curve.txt, it seems that Borkowski does curve exams in CS 251. A comment from
> u/Old-Rutabaga630 mentions that "Last sem with Blocki + Borkowski a pass was 64.2",
> implying that there was a curve. Additionally, a comment mentions "the curve is pretty nice"
> directly stating that the curve is present.
>
> Sources: reddit_cs251_curve.txt, reddit_borkowski.txt, rmp_borkowski.txt

**Example 2 — Grounded response with source attribution:**

Query: "Would students recommend taking CS 18200 with Sellke?"

> Based on the provided documents, students would not highly recommend taking CS 18200 with
> Sellke. One student comments "Dont do Sellke I beg you" (Source: reddit_sellke.txt) and
> another states she "was not the best at teaching and often skipped important steps"
> (Source: rmp_sellke.txt). Students should know she is nice and tries to help, but lectures
> can be hard to follow and homework is heavy.
>
> Sources: reddit_sellke.txt, rmp_sellke.txt, rmp_borkowski.txt, reddit_bergstrom.txt

**Example 3 — Out-of-scope refusal:**

Query: "What is the best restaurant in West Lafayette?"

> I don't have enough information in my documents to answer that.
>
> Sources: reddit_bergstrom.txt, rmp_bergstrom.txt, rmp_borkowski.txt, rmp_sellke.txt

---

## Query Interface

The system uses a command-line interface. To ask a question, run:

```bash
python ask.py "your question here"
```

**Input:** A natural language question typed as a command-line argument.
**Output:** A grounded answer followed by a list of source documents it drew from.

**Sample interaction transcript:**

```
$ python ask.py "Are Sellke's lectures easy to follow in CS 18200?"

Answer:
No, according to the student reviews, Sellke's lectures in CS 18200 are not easy to follow.
One review states that the "lectures are extremely hard to follow and don't explain concepts
well at all" (Source: rmp_sellke.txt). Another review mentions that Sellke "rarely explained
how she derived the next step in her work" (Source: rmp_sellke.txt), which suggests that her
lectures may not be clear or easy to understand.

Sources:
  • rmp_sellke.txt
  • reddit_sellke.txt
  • reddit_bergstrom.txt
```

---

## Evaluation Report

| # | Question | Expected Answer | System Response | Accuracy |
|---|----------|-----------------|-----------------|----------|
| 1 | Does Borkowski curve exams in CS 251? | Yes — multiple reviews mention a generous curve | System correctly identified the curve, citing "pass was 64.2" and "the curve is pretty nice" from retrieved documents | Accurate |
| 2 | Are Sellke's lectures easy to follow in CS 18200? | No — reviews say lectures are hard to follow | System correctly answered no, citing "lectures are extremely hard to follow" and "rarely explained how she derived the next step" | Accurate |
| 3 | How hard is CS 180 with Bergstrom compared to other sections? | Harder than average — tagged tough grader, 32% would take again | System gave a mixed/partial answer, noting difficulty of 4.0 and "mid based on ratemyprofessor" but did not clearly state he is harder than average | Partially Accurate |
| 4 | Does Borkowski give useful feedback on assignments? | Yes — RMP tags include "Gives good feedback" and "Clear grading criteria" | System returned "I don't have enough information in my documents to answer that" — the relevant chunk was present but did not surface in top-k retrieval | Inaccurate |
| 5 | Would students recommend taking CS 18200 with Sellke? | Mixed — nice but lectures hard to follow, expect to self-teach | System correctly captured the mixed sentiment, citing "Dont do Sellke I beg you" alongside notes that she is nice and tries to help | Accurate |

### Failure Case Analysis

**Question 4** ("Does Borkowski give useful feedback on assignments?") is the clearest failure.
The answer exists in the documents — `rmp_borkowski.txt` contains the tag "Gives good feedback"
and "Clear grading criteria" — but neither chunk surfaced in the top-5 retrieval results.
The cause is a chunking boundary issue: the tags ("Clear grading criteria, Gives good feedback,
Caring") were separated from the review text they belonged to when the document was split at
300-character boundaries. The embedding for a chunk containing only tag metadata carries weak
semantic signal, so it scored poorly against a query about "useful feedback." A fix would be
to chunk by review block rather than fixed character count, keeping each review's text and tags
together in one chunk.

---

## Spec Reflection

**One way the spec helped:** Writing the chunking strategy section of planning.md before
touching any code forced a concrete decision — 300 characters, 50 overlap — rather than
defaulting to whatever a library's default was. This made the ingestion code straightforward
to implement because the parameters were already decided.

**One way implementation diverged:** The planning.md specified a Gradio web UI for the query
interface. During implementation this was changed to a CLI using argparse. The reason was
practical — the system worked end-to-end in the terminal already, and adding Gradio would have
required additional disk space and dependencies on an already full machine. The CLI satisfies
the spec requirement ("a command-line tool") and is fully demonstrable in a video.

---

## AI Usage

**Instance 1 — Ingestion and chunking pipeline (Milestone 3):**
I gave Claude my planning.md chunking strategy section (chunk size 300, overlap 50) and asked
it to implement `load_documents()` and `chunk_text()`. Claude generated the full `ingest.py`
script. I reviewed the output, ran it, and verified the 68 chunks by printing 5 samples —
checking that each was readable, had a source field, and was under 300 characters. I did not
override any logic but noted that header metadata lines (SOURCE:, URL:) were being chunked
alongside review text, which is a known noise issue documented in the evaluation.

**Instance 2 — Embedding, retrieval, and generation (Milestones 4 and 5):**
I gave Claude my retrieval approach section (all-MiniLM-L6-v2, top-k=5, ChromaDB) and the
grounding requirement from planning.md, and asked it to implement `embed.py` and `ask.py`.
Claude generated both scripts. I verified `embed.py` by checking that distance scores on
test queries were reasonable and that retrieved chunks visibly related to each query. For
`ask.py`, I tested the out-of-scope refusal ("What is the best restaurant in West Lafayette?")
to confirm the grounding instruction was working — the system correctly declined rather than
hallucinating an answer.
