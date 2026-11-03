# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

`POST /submit` takes a JSON object containing a non-empty `text` string and
non-empty `creator_id`. A request with missing/blank fields, text over 10,000
characters, or fewer than three GPT-2 tokens receives a JSON 4xx error (or
503 if the local model is unavailable). A successful response contains a
UUID `content_id`, three 0–1 signal scores, the combined score as both
`combined_score` and `confidence`, a machine-readable `guess`, the reader
label, and `verified_human`.

The path from request arrival to the reader-facing label is:

1. **Parse and validate:** Flask reads the JSON body and checks `text` and
   `creator_id` before scoring.
2. **Measure predictability:** `detector.model_signal(text)` uses local GPT-2
   to compute next-token loss/perplexity and maps it to an AI-likelihood score.
   The model input is capped at 400 tokens.
3. **Measure writing form:** `stylometry.style_signal(text)` combines
   sentence-length spread, type-token ratio, and punctuation density.
4. **Measure phrase repetition:** `repetition.repetition_signal(text)` counts
   repeated adjacent two-word phrases and normalizes their rate.
5. **Combine the three readings:** `scoring.combine_signals` applies weights
   `0.20 / 0.60 / 0.20` and pulls the weighted score toward `0.5` when signals
   disagree.
6. **Choose exactly one reader label:** `scoring.score_to_label` maps scores
   at or below `0.35` to human, at or above `0.75` to AI, and scores between
   those boundaries to unsure.
7. **Record and return:** the decision and all signal values are appended to
   `logs/audit.jsonl`; the JSON response returns the label text and score
   fields. A later `POST /appeal` appends an appeal event for the same
   `content_id` and sets its current status to `under_review`.


---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:** GPT-2's mean next-token negative log-likelihood, reported
as perplexity (`exp(loss)`). `detector.model_signal` maps perplexity through
`1 / (1 + (perplexity / 45) ** 1.6)`, rounded to four decimal places. Lower
perplexity therefore means a higher 0–1 AI-likelihood score. Model input is
truncated to 400 tokens.

**Why that might differ between human and AI writing:** a language model tends
to select probable next words, so generated text may be predictable to a
language model. Less predictable wording and turns of phrase increase loss
and perplexity.

**What it can't see:** predictability does not establish authorship. Plain,
common-word writing—including writing by second-language or younger writers,
or writing deliberately kept simple—can be easy for GPT-2 to predict and
therefore look AI-like. Conversely, ornate or rare vocabulary may look
human-like to this signal. This is a proxy, not proof that a writer used AI.

### Signal two — the style signal

**What it measures:** (1) sentence-length spread as coefficient of variation
(standard deviation divided by mean sentence length); (2) type-token ratio,
unique normalized words divided by total words; and (3) punctuation marks per
word. The 0–1 style score uses `0.90 * spread_ai + 0.05 * vocabulary_ai +
0.05 * punctuation_ai`. Low sentence-length spread, higher vocabulary
variety, and sparse punctuation map toward AI-like. This is a surface-form
heuristic, not a measure of meaning or authorship.

**Why that might differ between human and AI writing:** generated prose may
cluster around evenly sized, mid-length sentences and repeated, conventional
word choices. Human prose can have more uneven sentence lengths, more varied
word choice, and a more individual distribution of punctuation. Those are
tendencies, not rules for identifying a person.

**What it can't see:** stylometry cannot read meaning or know who wrote the
text. Changes to surface form—adding typos, splitting or joining sentences,
or inserting a quotation—can move these measurements without changing the
underlying authorship. Type-token ratio also tends to decrease as text gets
longer, so length differences can masquerade as vocabulary differences.

### Signal three — the repeated-phrase signal

**What it measures:** `repetition.repetition_signal(text)` tokenizes words and
counts occurrences of repeated adjacent two-word phrases after their first
occurrence. It divides that count by all adjacent pairs, then divides by the
configured `0.05` rate and caps the result at `1.0`.

**Why that might differ between human and AI writing:** templated or
formulaically generated writing may reuse nearby phrase patterns, while
independently composed passages may repeat them less often. Neither tendency
identifies an author.

**What it can't see:** ordinary repeated phrases (such as names or a shared
topic term) can raise the score, while AI-written text with varied wording can
score zero. It checks exact neighboring word pairs, not meaning or authorship.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when signals
     disagree? -->

**The rule:** first calculate the weighted average
`W = 0.20 * model + 0.60 * style + 0.20 * repetition`. Calculate
`D = (|model-style| + |model-repetition| + |style-repetition|) / 3`.
The final score is `0.5 + (W - 0.5) * (1 - 0.5 * D)`. Thus disagreement
shrinks the score's distance from `0.5`; it does not change any component
score.

**The numbers:** model weight `0.20`, style weight `0.60`, and
repetition weight `0.20` (sum `1.00`). All component and combined scores
point in the same direction: higher means more AI-like. The human threshold
is `0.35` (inclusive); the AI threshold is `0.75` (inclusive); scores strictly
between them are unsure. The wide unsure band is intended to reduce false
accusations.

**Where it lives:** `scoring.py::combine_signals`.

**A disagreement example:** model `0.9`, style `0.1`, repetition `0.5` gives
`W = 0.34` and `D = 0.5333`; the rule returns approximately `0.3827`, closer
to `0.5` than the weighted average.

**Calibration and current criteria results:** the weights were calibrated on
the project's 15-text corpus. In the latest `python test_signals.py` run,
the AI-group mean was `0.6776` and the human-group mean was `0.4672`, a gap
of `0.2104`. These are corpus calibration results, not independent evidence
of real-world accuracy. All five texts in the `human` group were written by
an AI assistant as synthetic examples until I replace them with my own
writing; only `human_05_formal` is currently marked formal.

- **Criterion 1 — false positives:** not yet a valid human-writing test. Its
  data requirement (at least three formal human texts) is not met, and the
  current human group is AI-authored. The current run labels 0/5 of those
  synthetic examples `ai`, but that does not establish the false-positive
  rate on real human writing.
- **Criterion 2 — score spread:** **FAIL**. The measured AI-human mean gap
  `0.2104` is below the required `0.30`; the minimum clearly-AI score is
  `0.6220`, so that part of its target passes.
- **Criterion 3 — label coverage:** **PASS** in the latest run: `ai=1`,
  `human=1`, `unsure=13`. The score mapping covers `[0, 1]`.
- **Criterion 4 — borderline band:** **PASS** in the latest run: all five
  borderline scores (`0.5808`, `0.5727`, `0.4570`, `0.5899`, `0.5631`)
  are in `[0.40, 0.60]` and labeled `unsure`.
- **Criterion 5 — appeal and bad input:** **PASS** in the live check: 10/10
  valid submission/appeal pairs returned success; an unknown appeal returned
  404 without changing the audit file; missing, empty, and 10,001-character
  text each returned a JSON 400.



---

## Label Variants

| Label | Score range | The exact text a reader sees |
|---|---|---|
| human | 0.00–0.35, inclusive | Your writing looks like it was written by a person. Thanks for sharing it. |
| unsure | >0.35 and <0.75 | We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI. |
| ai | 0.75–1.00, inclusive | This text has features often associated with AI-written text, but this is not proof of authorship. If this is your original work, you can appeal by sending its content ID and a brief explanation to POST /appeal. |

---

## Sample Run

The following are real HTTP responses from the local service. The `readme-demo`
creator first completed the prompted-sample step, so the submission also
demonstrates the credential flag.

**Submission request** — `POST /submit`

```powershell
curl.exe -sS -X POST http://127.0.0.1:5000/submit -H "Content-Type: application/json" --data-binary "@submit.json"
```

`submit.json` contains this request body:

```json
{
  "text": "On Tuesday the neighborhood garden opened its gate before sunrise. Mara carried a small notebook and checked which beds needed water. A light rain had passed overnight, so she skipped the tomatoes and filled the watering can for the herbs. One wooden marker had fallen beside the path. She cleaned it, pressed it back into the soil, and wrote the plant name again. By midmorning, two neighbors had arrived with seeds to share. They compared notes about the cool weather and made a plan to meet again on Saturday. The work was simple, but the garden looked brighter when they finished.",
  "creator_id": "readme-demo"
}
```

**Submission response** — HTTP 200

```json
{
  "combined_score": 0.4651,
  "confidence": 0.4651,
  "content_id": "46342ded-0d09-4bae-81d1-e36b270df2d1",
  "guess": "unsure",
  "label": "We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.",
  "model_score": 0.3555,
  "repetition_score": 0.0,
  "style_score": 0.6409,
  "verified_human": true
}
```

**Appeal request** — `POST /appeal`

```powershell
curl.exe -sS -X POST http://127.0.0.1:5000/appeal -H "Content-Type: application/json" --data-binary "@appeal.json"
```

`appeal.json` contains this request body:

```json
{
  "content_id": "46342ded-0d09-4bae-81d1-e36b270df2d1",
  "reasoning": "I wrote this text myself and want the decision reviewed."
}
```

**Appeal response** — HTTP 200

```json
{
  "content_id": "46342ded-0d09-4bae-81d1-e36b270df2d1",
  "message": "Your appeal has been recorded for review.",
  "status": "under_review"
}
```

**Resulting entries from `logs/audit.jsonl`** — the appeal keeps the same
`content_id` and does not replace the original decision:

```json
{"timestamp":"2026-11-03T15:52:01+00:00","content_id":"46342ded-0d09-4bae-81d1-e36b270df2d1","creator_id":"readme-demo","guess":"unsure","model_score":0.3555,"style_score":0.6409,"repetition_score":0.0,"combined_score":0.4651,"label":"We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.","status":"decided","verified_human":true}
{"timestamp":"2026-11-03T15:52:01+00:00","content_id":"46342ded-0d09-4bae-81d1-e36b270df2d1","creator_id":"readme-demo","event":"appeal","status":"under_review","reasoning":"I wrote this text myself and want the decision reviewed."}
```

---

## How I Used AI

**Moment 1 — Calibration**

- **What I asked:** I asked the assistant to help tune stylometry so the AI
  and human scores would spread apart.
- **What came back:** It changed the feature directions and weights, and the
  reported AI-human gap rose from `0.0448` to `0.3126`. It tuned those
  settings on texts it wrote itself.
- **What I changed or decided:** I questioned whether that showed a real
  difference, because the test texts came from the assistant. I did not accept
  the suggestions unchanged; I edited them for technical sense and my own
  voice. My current human test group is a mix of AI-written and my own writing,
  and the latest measured gap is `0.2104`, so I do not treat `0.3126` as a
  result on only human-written work.

**Moment 2 — Borderline target**

- **What I asked:** I asked whether the borderline examples met my `0.40`–`0.60` score target.
- **What came back:** In that run, most scores were between `0.65` and `0.74`, above the target.
- **What I changed or decided:** I left the target alone instead of tuning the scores to make them fit; I thought that could hurt accuracy and technical depth. I updated the human texts in `test_set/texts.json` to better align with the project's current scope, which recalibrated the numbers. In the latest `python test_signals.py` run, the five borderline scores are `0.5808`, `0.5727`, `0.4570`, `0.5899`, and `0.5631`; all five are now in the target range and labeled `unsure`.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->

---

## Stretch Notes

1. **Third signal — changed scoring and audit records.** The added
   `repetition.repetition_signal` scores repeated adjacent two-word phrases.
   The combined score now uses model/style/repetition weights `0.20/0.60/0.20`
   and the disagreement adjustment described above. Each decision log and
   `/submit` response now includes all three component scores.

2. **`GET /content/<id>` — added per-item status lookup.** This endpoint
   returns the decision and latest status, including `under_review` after an
   appeal; unknown IDs return a JSON 404.

   **Request**

   ```http
   GET /content/46342ded-0d09-4bae-81d1-e36b270df2d1
   ```

   ```powershell
   curl.exe -sS http://127.0.0.1:5000/content/46342ded-0d09-4bae-81d1-e36b270df2d1
   ```

   **Response** — HTTP 200, after the appeal

   ```json
   {
     "combined_score": 0.4651,
     "content_id": "46342ded-0d09-4bae-81d1-e36b270df2d1",
     "creator_id": "readme-demo",
     "guess": "unsure",
     "label": "We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.",
     "status": "under_review",
     "verified_human": true
   }
   ```

3. **Prompted-writing credential — added a persistent completion flag.**
   `POST /verify` asks the creator to submit at least 100 words in response to
   this prompt: “Describe a small task you completed recently. Include
   what you expected, one specific detail that changed, and how you
   responded.” A passing sample stores a credential for the `creator_id`.
   The route validates the 100-word minimum; it does not judge whether the
   sample actually follows the prompt.
   The flag appears as `verified_human: true` in subsequent submissions,
   audit entries, and content lookups. This proves only that the endpoint
   accepted a prompted sample; it does not verify identity or human authorship.

   **Verification request** — `POST /verify`

   ```json
   {
     "creator_id": "readme-demo",
     "writing_sample": "Last weekend I planned to fix the loose handle on a kitchen drawer. I expected the repair to be quick because I had tightened similar handles before. When I opened the drawer, I noticed the wooden front had shifted slightly and the old screw holes were wider than I remembered. I looked through a small box of spare parts and found two short screws and a washer. The washer made the handle sit evenly, so I used it on the inside of the drawer. I tightened each screw slowly and checked that the handle no longer moved when I pulled it. The drawer still opened smoothly, and the repair took longer than expected but worked well. I put the unused parts back in the box and made a note to check the other handles later. Small repairs are easier when I stop and inspect the whole problem before reaching for a tool."
   }
   ```

   **Verification response** — HTTP 200

   ```json
   {
     "creator_id": "readme-demo",
     "credential": "prompted_sample_completed",
     "message": "The prompted writing sample was received. This credential confirms completion only; it does not verify identity or authorship.",
     "verified_at": "2026-11-03T15:51:25+00:00",
     "verified_human": true,
     "word_count": 152
   }
   ```

   The content response above shows the resulting item carrying
   `"verified_human": true`.



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           all three signal scores and verified_human
       [ ] Three signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with the decision fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
