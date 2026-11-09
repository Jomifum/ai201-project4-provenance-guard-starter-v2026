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
of real-world accuracy. I co-wrote all five texts in the `human` group with
the AI assistant; none is solely my unaided writing. Only `human_05_formal`
is currently marked formal.

- **Criterion 1 — false positives:** not yet a valid human-writing test. Its
  data requirement (at least three formal human texts) is not met, and the
  current human group was co-written by me and the AI assistant. The current run
  labels 0/5 of those co-written examples `ai`, but that does not establish
  the false-positive rate on writing produced by me alone.
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
  reported AI-human gap moved from `0.0448` to `0.3126` across earlier
  calibration versions. It tuned those versions on texts it wrote itself.
- **What I changed or decided:** I questioned whether that showed a real
  difference, because the test texts came from the assistant. I did not accept
  the suggestions unchanged; I edited them for technical sense and my own
  voice. I co-wrote all five current human-group texts with the AI assistant.
  The latest measured gap is `0.2104`; it is not a result on texts written by
  me alone.

**Moment 2 — Borderline target**

- **What I asked:** I asked whether the borderline examples met my `0.40`–`0.60` score target.
- **What came back:** In an earlier calibration version, most borderline scores were between `0.65` and `0.74`, above the target.
- **What I changed or decided:** I left the target alone instead of tuning the scores to make them fit; I thought that could hurt accuracy and technical depth. I updated the human texts in `test_set/texts.json` and co-wrote all five with the assistant, which recalibrated the numbers. In the latest `python test_signals.py` run, the AI-human gap is `0.2104`, and the five borderline scores are `0.5808`, `0.5727`, `0.4570`, `0.5899`, and `0.5631`; all five are now in the target range and labeled `unsure`.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

### Unit 8

**Unit 8, Moment 1 — Diagnosing the four broken attacks.** I asked for a check of my diagnoses for EV02, EV05, EV09 and FP02. It pointed out that my EV02 answer described criterion 2, not the attack, and that my EV09 explanation left out the repetition weight and the disagreement adjustment (about 0.2947 raw, 0.3429 after the adjustment). I rewrote those diagnoses to cite the real scores and weights.

**Unit 8, Moment 2 — The first attack run.** 33 of 56 requests returned HTTP 500 with a "meta tensors" error. I asked for a diagnosis; it found lazy model loading with no lock and debug mode on, but could not prove which caused it. I restarted with `AI201_DEBUG=0`, warmed the model with one submission, re-ran the set cleanly, and kept the first report as invalid.

---

## Rate Limiting

**My limits:** 5 per minute, 50 per day

### Rate-Limit Reasoning & Caller Counts

My limits are 5 per minute and 50 per day on `/submit`, using Flask-Limiter's default fixed window with in-memory storage. A writer submitting their own work sends a few pieces an hour, so 5 per minute never gets in their way, and 50 per day leaves room to revise and resubmit several pieces. A script probing my thresholds needs many variations, and one caller at 5 per minute can send at most 300 an hour. The limiter identifies a caller by `creator_id` when the JSON has one and by remote address otherwise, so a script that changes `creator_id` on every request would not be slowed by this limit; I did not test that. Bodies that aren't JSON objects fall back to the address, which is probably why RQ10 and RQ11 returned 429 in the first clean run. In my flood test, six requests returned 200 before the 429s began; I think that was a window boundary effect but did not confirm it. `/appeal` has no rate limit.

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```
200 200 200 200 200 200 429 429 429 429 429 429 429 429 429
```

The limit is 5 per minute, but six 200s appeared; I believe this was a window
boundary effect, and I have not confirmed that.

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->

**Baseline:** `results/attack_run_2026-11-08_2249.md`. The
`results/attack_run_2026-11-08_2232.md` run was invalidated by a model-loading
failure (`Tensor.item() cannot be called on meta tensors`). For the later
runs, I used `AI201_DEBUG=0` and warmed the model with one submission before
running the set.

The `label` column shows the report's `guess` category (`human`, `unsure`, or
`ai`); `—` means the request was rejected before scoring.

| ID | Family | Target | Score | Model | Style | Label | HTTP | HELD/BROKE |
|---|---|---|---:|---:|---:|---|---:|---|
| EV01 | evasion | signal two: typos raise word variety | 0.5718 | 0.1635 | 0.9543 | unsure | 200 | HELD |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 0.2250 | 0.5943 | 0.0637 | human | 200 | BROKE |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 0.3577 | 0.6662 | 0.3064 | unsure | 200 | HELD |
| EV04 | evasion | signal one: unusual words raise perplexity | 0.6218 | 0.6114 | 0.9227 | unsure | 200 | HELD |
| EV05 | evasion | both signals: heavy human editing pass | 0.1405 | 0.3212 | 0.0552 | human | 200 | BROKE |
| EV06 | evasion | signal two: one very long sentence and one very short | 0.3994 | 0.5727 | 0.0655 | unsure | 200 | HELD |
| EV07 | evasion | signal two: padding with punctuation | 0.8313 | 0.5862 | 0.9451 | ai | 200 | HELD |
| EV08 | evasion | signal one: text below the token window | 0.4609 | 0.2452 | 0.6678 | unsure | 200 | HELD |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 0.3429 | 0.7042 | 0.2564 | human | 200 | BROKE |
| EV10 | evasion | signal two: repeated stanza structure | 0.6059 | 0.9792 | 0.3948 | unsure | 200 | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 0.3461 | 0.6175 | 0.2637 | human | 200 | HELD |
| FP02 | false_positive | human writing in a formal register | 0.7532 | 0.7387 | 0.7513 | ai | 200 | BROKE |
| FP03 | false_positive | a non-native English speaker writing carefully | 0.5370 | 0.8051 | 0.5596 | unsure | 200 | HELD |
| FP04 | false_positive | a student essay written to a rubric | 0.6164 | 0.8329 | 0.4822 | unsure | 200 | HELD |
| FP05 | false_positive | technical documentation written by a person | 0.7167 | 0.8005 | 0.6431 | unsure | 200 | HELD |
| FP06 | false_positive | a person imitating a formal template | 0.4591 | 0.8814 | 0.1280 | unsure | 200 | HELD |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 0.4265 | 0.8816 | 0.0246 | unsure | 200 | HELD |
| FP08 | false_positive | very short genuine human submission | 0.2790 | 0.3223 | 0.3132 | human | 200 | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 0.2663 | 0.4625 | 0.0815 | human | 200 | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 0.1074 | 0.2044 | 0.0630 | human | 200 | HELD |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 0.4563 | 0.5943 | 0.5444 | unsure | 200 | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 0.3641 | 0.4998 | 0.3949 | unsure | 200 | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 0.3144 | 0.6401 | 0.2268 | human | 200 | HELD |
| PI06 | prompt_injection | instruction plus real human text | 0.3443 | 0.5583 | 0.2906 | human | 200 | HELD |
| MF01 | malformed | text is only whitespace | — | — | — | — | 400 | HELD |
| MF02 | malformed | text is a single character | — | — | — | — | 400 | HELD |
| MF03 | malformed | text is control characters | 0.5478 | 0.0000 | 0.9500 | unsure | 200 | HELD |
| MF04 | malformed | text is only punctuation | 0.3352 | 0.0112 | 0.5000 | human | 200 | HELD |
| MF05 | malformed | text is a very long single word | 0.6997 | 0.9976 | 1.0000 | unsure | 200 | HELD |
| MF06 | malformed | text is emoji only | 0.4996 | 0.9969 | 0.5000 | unsure | 200 | HELD |
| MF07 | malformed | text is right-to-left script | 0.4869 | 0.9064 | 0.5000 | unsure | 200 | HELD |
| MF08 | malformed | text is 60,000 characters | — | — | — | — | 400 | HELD |
| RQ01 | malformed | no text field at all | — | — | — | — | 400 | HELD |
| RQ02 | malformed | no creator_id | — | — | — | — | 400 | HELD |
| RQ03 | malformed | text is a number | — | — | — | — | 400 | HELD |
| RQ04 | malformed | text is a list | — | — | — | — | 400 | HELD |
| RQ05 | malformed | text is null | — | — | — | — | 400 | HELD |
| RQ06 | malformed | creator_id is an object | — | — | — | — | 400 | HELD |
| RQ07 | malformed | body is a JSON array, not an object | — | — | — | — | 400 | HELD |
| RQ08 | malformed | body is unparseable JSON | — | — | — | — | 400 | HELD |
| RQ09 | malformed | body is empty | — | — | — | — | 400 | HELD |
| RQ10 | malformed | body is form-encoded, not JSON | — | — | — | — | 429 | HELD |
| RQ11 | malformed | body is JSON claiming to be plain text | — | — | — | — | 429 | HELD |
| RQ12 | malformed | deeply nested JSON | — | — | — | — | 400 | HELD |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 0.5637 | 0.0287 | 0.9815 | unsure | 200 | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 0.5637 | 0.0287 | 0.9815 | unsure | 200 | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 0.5637 | 0.0287 | 0.9815 | unsure | 200 | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 0.5637 | 0.0287 | 0.9815 | unsure | 200 | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 0.5637 | 0.0287 | 0.9815 | unsure | 200 | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | — | — | — | — | 429 | HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | — | — | — | — | 429 | HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | — | — | — | — | 429 | HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | — | — | — | — | 429 | HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | — | — | — | — | 429 | HELD |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | — | — | — | — | 429 | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | — | — | — | — | 429 | HELD |

After waiting 65 seconds, RQ10 and RQ11 were re-sent in isolation with fresh
creator IDs. Each returned HTTP 400, `"Request body must be a JSON object"`,
so both remain HELD and have now been tested for the behavior they target.

**Per-family counts**

| Family | HELD | BROKE |
|---|---:|---:|
| evasion | 7 | 3 |
| false_positive | 7 | 1 |
| flood_same_creator | 12 | 0 |
| malformed | 20 | 0 |
| prompt_injection | 6 | 0 |
| **Total** | **52** | **4** |

MF03–MF07 are HELD only because they did not crash; all five were scored.
MF04 received a `human` label with model score `0.0112`.

PI01–PI06 are HELD because the injection did not visibly change the label.
I did not compare them against the same text without the injection.

The 2254 run repeated the 2249 baseline exactly: all 56 rows matched for
combined score, model score, style score, label, and HTTP status.

**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json
{"timestamp":"2026-11-09T03:49:47+00:00","content_id":"77886ecd-5118-49a8-9dc9-cd4f6ee18cce","creator_id":"attacker_EV02","guess":"human","model_score":0.5943,"style_score":0.0637,"repetition_score":0.0,"combined_score":0.225,"label":"Your writing looks like it was written by a person. Thanks for sharing it.","status":"decided","verified_human":false}
{"timestamp":"2026-11-09T03:49:48+00:00","content_id":"dc2ac33b-6070-4269-9c80-964ece374637","creator_id":"attacker_EV05","guess":"human","model_score":0.3212,"style_score":0.0552,"repetition_score":0.0,"combined_score":0.1405,"label":"Your writing looks like it was written by a person. Thanks for sharing it.","status":"decided","verified_human":false}
{"timestamp":"2026-11-09T03:49:49+00:00","content_id":"4b990f3c-70e8-4c30-b60a-04a3c73c3a93","creator_id":"attacker_EV09","guess":"human","model_score":0.7042,"style_score":0.2564,"repetition_score":0.0,"combined_score":0.3429,"label":"Your writing looks like it was written by a person. Thanks for sharing it.","status":"decided","verified_human":false}
{"timestamp":"2026-11-09T03:49:49+00:00","content_id":"37305323-86d5-45ac-8467-ac41114441a7","creator_id":"attacker_FP02","guess":"ai","model_score":0.7387,"style_score":0.7513,"repetition_score":0.8,"combined_score":0.7532,"label":"This text has features often associated with AI-written text, but this is not proof of authorship. If this is your original work, you can appeal by sending its content ID and a brief explanation to POST /appeal.","status":"decided","verified_human":false}
{"timestamp":"2026-11-09T03:49:49+00:00","content_id":"f8b060b7-9405-417e-b1b2-7a4efb05f528","creator_id":"attacker_FP03","guess":"unsure","model_score":0.8051,"style_score":0.5596,"repetition_score":0.2439,"combined_score":0.537,"label":"We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.","status":"decided","verified_human":false}
{"timestamp":"2026-11-09T03:49:50+00:00","content_id":"a10407fd-df80-4d1d-ac46-65e9897a35f8","creator_id":"attacker_PI01","guess":"human","model_score":0.4625,"style_score":0.0815,"repetition_score":0.4545,"combined_score":0.2663,"label":"Your writing looks like it was written by a person. Thanks for sharing it.","status":"decided","verified_human":false}
{"timestamp":"2026-11-09T03:49:50+00:00","content_id":"a0880125-2540-470f-b7cf-ebb317a2146e","creator_id":"attacker_PI02","guess":"human","model_score":0.2044,"style_score":0.063,"repetition_score":0.0,"combined_score":0.1074,"label":"Your writing looks like it was written by a person. Thanks for sharing it.","status":"decided","verified_human":false}
{"timestamp":"2026-11-09T03:49:51+00:00","content_id":"25386db8-a90c-4234-9a7c-c66679297c74","creator_id":"attacker_MF04","guess":"human","model_score":0.0112,"style_score":0.5,"repetition_score":0.0,"combined_score":0.3352,"label":"Your writing looks like it was written by a person. Thanks for sharing it.","status":"decided","verified_human":false}
{"timestamp":"2026-11-09T03:49:53+00:00","creator_id":"attacker_RQ01","event":"rejected","status":"rejected","reason":"missing_or_empty_text"}
{"timestamp":"2026-11-09T03:49:53+00:00","creator_id":"attacker_flood","event":"rejected","status":"rejected","reason":"rate_limited","limit":"5 per 1 minute"}
```

After a 65-second wait, the RQ10 and RQ11 retest rejection entries were:

```json
{"timestamp":"2026-11-09T04:21:20+00:00","creator_id":"unknown","event":"rejected","status":"rejected","reason":"invalid_request_body"}
{"timestamp":"2026-11-09T04:21:57+00:00","creator_id":"unknown","event":"rejected","status":"rejected","reason":"invalid_request_body"}
```

A misquoted `curl.exe` call also added one extra `invalid_request_body`
entry:

```json
{"timestamp":"2026-11-09T04:21:31+00:00","creator_id":"unknown","event":"rejected","status":"rejected","reason":"invalid_request_body"}
```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:

### Worst-Outcome Note

The worst outcome is FP02, a formal human text (the attack set describes it as human; I haven't verified authorship). It scored 0.7550, only 0.005 over my 0.75 threshold, and still got the AI label after my change. The label says this is not proof and tells the writer how to appeal, but it still tells someone who wrote their own work that it looks AI-written, and I would not want to explain a score that close to the line.


---

## Run Log and Verdicts

### BEFORE (weights 0.20/0.60/0.20)

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Own writing | At most 1/10 labeled ai; at least 3 formal | Not run | Not run | Not run | NOT RUN |
| 2. Score spread | AI-human gap >=0.30; AI minimum >=0.50 | Gap 0.21040; AI min 0.622 | Gap 0.21040; AI min 0.622 | Gap 0.21040; AI min 0.622 | MISSED |
| 3. Label coverage | >=1 ai, human, unsure; ranges cover 0-1 | 1 ai, 1 human, 13 unsure | 1 ai, 1 human, 13 unsure | 1 ai, 1 human, 13 unsure | MET |
| 4. Borderline | At least 4/5 in 0.40-0.60 and unsure | 5/5 | 5/5 | 5/5 | MET |
| 5. Appeals and bad input | 10 valid appeals; unknown appeal leaves audit unchanged; bad inputs return 4xx | 10/10; 3x400; unknown 404; audit 310 to 311 | 10/10; 3x400; unknown 404; audit 334 to 335 | 10/10; 3x400; unknown 404; audit 358 to 359 | MISSED |

### AFTER (weights 0.20/0.40/0.20)

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Own writing | At most 1/10 labeled ai; at least 3 formal | Not run | Not run | Not run | NOT RUN |
| 2. Score spread | AI-human gap >=0.30; AI minimum >=0.50 | Gap 0.16846; AI min 0.5929 | Gap 0.16846; AI min 0.5929 | Gap 0.16846; AI min 0.5929 | MISSED |
| 3. Label coverage | >=1 ai, human, unsure; ranges cover 0-1 | 0 ai, 1 human, 14 unsure | 0 ai, 1 human, 14 unsure | 0 ai, 1 human, 14 unsure | MISSED (fixtures; ai remains reachable in attack set) |
| 4. Borderline | At least 4/5 in 0.40-0.60 and unsure | 5/5 | 5/5 | 5/5 | MET |
| 5. Appeals and bad input | 10 valid appeals; unknown appeal leaves audit unchanged; bad inputs return 4xx | 10/10; 3x400; unknown 404; audit 529 to 530 | 10/10; 3x400; unknown 404; audit 553 to 554 | 10/10; 3x400; unknown 404; audit 577 to 578 | MISSED |

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



**Overall:** The change helped EV09 (human to unsure) but did not change EV02, EV05 or FP02. It moved FP01 (plain human writing) from human to unsure, narrowed the AI-human gap from 0.2104 to 0.1685, and left no ai label in the criterion 3 fixtures.



---

### Production Trade-off

I would favor fewer wrong accusations, which matches my criterion 1 target of at most 1 false positive in 10, so I would keep the wide unsure band and raise the AI threshold. A writer wrongly flagged pays first, and every reader pays when AI text gets through, because nothing in my system catches it afterwards. The only review step is the appeal, and it only starts when a flagged writer objects.

## What's Still Broken

**EV02 and EV05 (still BROKE).** Style scores of 0.0637 and 0.0552 pulled the combined scores to 0.2437 and 0.1499 after my change. I would look at the style signal's components on these two texts and consider limiting how far the style score alone can pull a combined score. Changing the style weight from 0.60 to 0.40 barely moved them, and I stopped because the unit allows one change.

**FP02 (still BROKE).** At 0.7550 it sits 0.005 over the 0.75 threshold. I would raise the AI threshold to about 0.80, which from my results would move FP02 to unsure while EV07 (0.8182) stays labeled AI, then re-run everything. The cost is fewer AI texts caught. I stopped for the same reason.

**Criterion 2.** The AI-human gap is 0.1685 against a 0.30 target, down from 0.2104 before my change. Fixing it likely needs a better style or model signal, not a different weight.

**Criterion 3.** After my change no `ai` label appeared among the 15 fixtures, though `ai` is still reachable in the attack set (EV07 at 0.8182, FP02 at 0.7550).

**Criterion 5 (missed).** My target said an unknown appeal should change nothing. It added a `content_not_found` rejection to the audit log, which is the logging I added in Milestone 1, so the target and the logging conflicted. I count it as MISSED and have not changed the original target. `/appeal` has no rate limit, so repeated unknown IDs could grow the log without bound; I did not test this. I would either drop "changes nothing" from the target or stop logging unknown IDs, and I stopped because the unit allows one change.

**Prompt injection (PI01 to PI06).** I marked these HELD because no label visibly changed, but I never compared them to the same text without the injection, so the result is unverified. I would run each with the injection line removed.

**MF04.** Punctuation-only text got a "human" label at model score 0.0112. I would reject text with too few words before scoring.

**Unhandled errors.** In the first attack run, 33 requests returned an HTML debugger page and left no audit entry. I would catch detector errors, return a JSON 503, and log a rejection.

**Criterion 1.** Not run: my ten pieces were not added to `scenarios.py`.

**The trade I'd make if this ran for real:** see the production trade paragraph above.

---

## Stretch Features Declared

Before implementing these stretch features, I plan to:

1. **Add a third signal.** I will combine the model signal at weight `0.20`,
   the style signal at weight `0.60`, and the new signal at weight `0.20` using
   a weighted average whose weights sum to `1.00`.
2. **Add `GET /content/<id>`.** It will look up the item's audit history and
   return its current status, including `under_review` after an appeal.
3. **Add a verified-human path.** A writer will complete an extra verification
   step to earn a credential, which the service will show on that writer's work.

This declaration was first committed in `29f5f22`, before the stretch code in
`76301c4`.

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
