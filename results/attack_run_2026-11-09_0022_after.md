# Attack run — after

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-09 00:22
- Auto-marked BROKE (5xx, crash, no response): **0**
- Left for you to judge: **56**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `0cfc64ce-cf60-48c2-9397-863249f8b236` | unsure | 0.512 |  |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `574a7d52-1a86-42d8-b870-d2d1cda12d1c` | human | 0.244 |  |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `92ed92fa-cfbc-4f1e-a918-9075abcd400a` | unsure | 0.360 |  |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `a3da194c-bb5b-4edd-b6d2-ee6534ec0947` | unsure | 0.579 |  |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `6ba86a51-9768-4f2d-bcc1-039b3e935350` | human | 0.150 |  |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `4f07a6fb-350d-4c5e-9b9a-3173c25553f2` | unsure | 0.449 |  |
| EV07 | evasion | signal two: padding with punctuation | 200 | `4468c20e-8ca9-45db-b44a-3392f8a6a014` | ai | 0.818 |  |
| EV08 | evasion | signal one: text below the token window | 200 | `7d34a9f5-2a92-4b15-b2f8-77b73c2d1106` | unsure | 0.418 |  |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `4c6d8008-4e40-46ce-976e-dd04341f6e6b` | unsure | 0.350 |  |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `e543ff54-f2f3-43d1-99ab-aa772556e804` | unsure | 0.653 |  |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `7edd934e-bc89-4151-9eb8-648a47d0766a` | unsure | 0.358 |  |
| FP02 | false_positive | human writing in a formal register | 200 | `07fc5a3e-6286-4251-94a8-7e1b4382e064` | ai | 0.755 |  |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `83f9c7b3-344b-401a-b3e9-6b916662a3f5` | unsure | 0.534 |  |
| FP04 | false_positive | a student essay written to a rubric | 200 | `6d3c11b0-ef42-434f-8791-5db79630910e` | unsure | 0.649 |  |
| FP05 | false_positive | technical documentation written by a person | 200 | `b9010160-fafa-4756-a4fa-9693b99ba8cb` | unsure | 0.739 |  |
| FP06 | false_positive | a person imitating a formal template | 200 | `832cd3b4-8be5-41e7-9bd6-eb99138c5ff2` | unsure | 0.516 |  |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `ef585dc8-bc2b-4c09-8dbc-983f9e2a2aaf` | unsure | 0.488 |  |
| FP08 | false_positive | very short genuine human submission | 200 | `66ed021d-383d-47dc-a5fa-edfc51d46779` | human | 0.265 |  |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `c1c2655a-fc77-40c4-a42d-f89791433462` | human | 0.299 |  |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `86a8acb0-d5f1-4d7f-8b7f-5b4d914f8dc1` | human | 0.111 |  |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `ef725c9c-2650-461d-af0c-937dc346c330` | unsure | 0.436 |  |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `b6fe59f6-f945-4587-8a02-2ed11c37b55e` | unsure | 0.352 |  |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `ce20296e-b2ad-46a9-82e1-84fee13158b4` | human | 0.322 |  |
| PI06 | prompt_injection | instruction plus real human text | 200 | `91780e05-88a7-4296-ba71-4c8ea68a73d1` | unsure | 0.351 |  |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — |  |
| MF02 | malformed | text is a single character | 400 | `—` | — | — |  |
| MF03 | malformed | text is control characters | 200 | `1c9bdad3-fbfd-4348-97d7-27c4634d0bab` | unsure | 0.483 |  |
| MF04 | malformed | text is only punctuation | 200 | `e4e7e714-8419-40b8-bb5d-4356a7158a23` | human | 0.294 |  |
| MF05 | malformed | text is a very long single word | 200 | `37f6cce0-2782-433a-a2dc-168113ac4c18` | unsure | 0.666 |  |
| MF06 | malformed | text is emoji only | 200 | `b3a9c2a6-f4ff-4872-af33-d36887e0efa7` | unsure | 0.499 |  |
| MF07 | malformed | text is right-to-left script | 200 | `4f908a12-2455-4a08-a1f9-85b6bf5305ac` | unsure | 0.484 |  |
| MF08 | malformed | text is 60,000 characters | 400 | `—` | — | — |  |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — |  |
| RQ02 | malformed | no creator_id | 400 | `—` | — | — |  |
| RQ03 | malformed | text is a number | 400 | `—` | — | — |  |
| RQ04 | malformed | text is a list | 400 | `—` | — | — |  |
| RQ05 | malformed | text is null | 400 | `—` | — | — |  |
| RQ06 | malformed | creator_id is an object | 400 | `—` | — | — |  |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — |  |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — |  |
| RQ09 | malformed | body is empty | 400 | `—` | — | — |  |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | `—` | — | — |  |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | `—` | — | — |  |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — |  |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `af816f62-ce7e-4eff-943d-7fb3b3e8508b` | unsure | 0.499 |  |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `4d6dfc9c-6a7f-4685-b9fe-de945e8b99d9` | unsure | 0.499 |  |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `f18b2568-f18f-417d-b037-43b22cf67d14` | unsure | 0.499 |  |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `8c884267-9891-4610-8a44-7d0cea38cd49` | unsure | 0.499 |  |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `885cc7ce-dabb-4087-8000-2d10b10b0211` | unsure | 0.499 |  |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 0 | 20 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "0cfc64ce-cf60-48c2-9397-863249f8b236",
  "creator_id": "attacker_EV01",
  "guess": "unsure",
  "confidence": 0.5123,
  "model_score": 0.1635,
  "style_score": 0.9543,
  "label": "We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.",
  "error": null,
  "verdict": ""
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "574a7d52-1a86-42d8-b870-d2d1cda12d1c",
  "creator_id": "attacker_EV02",
  "guess": "human",
  "confidence": 0.2437,
  "model_score": 0.5943,
  "style_score": 0.0637,
  "label": "Your writing looks like it was written by a person. Thanks for sharing it.",
  "error": null,
  "verdict": ""
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "92ed92fa-cfbc-4f1e-a918-9075abcd400a",
  "creator_id": "attacker_EV03",
  "guess": "unsure",
  "confidence": 0.3598,
  "model_score": 0.6662,
  "style_score": 0.3064,
  "label": "We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.",
  "error": null,
  "verdict": ""
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "a3da194c-bb5b-4edd-b6d2-ee6534ec0947",
  "creator_id": "attacker_EV04",
  "guess": "unsure",
  "confidence": 0.5791,
  "model_score": 0.6114,
  "style_score": 0.9227,
  "label": "We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.",
  "error": null,
  "verdict": ""
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "6ba86a51-9768-4f2d-bcc1-039b3e935350",
  "creator_id": "attacker_EV05",
  "guess": "human",
  "confidence": 0.1499,
  "model_score": 0.3212,
  "style_score": 0.0552,
  "label": "Your writing looks like it was written by a person. Thanks for sharing it.",
  "error": null,
  "verdict": ""
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "4f07a6fb-350d-4c5e-9b9a-3173c25553f2",
  "creator_id": "attacker_EV06",
  "guess": "unsure",
  "confidence": 0.449,
  "model_score": 0.5727,
  "style_score": 0.0655,
  "label": "We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.",
  "error": null,
  "verdict": ""
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "4468c20e-8ca9-45db-b44a-3392f8a6a014",
  "creator_id": "attacker_EV07",
  "guess": "ai",
  "confidence": 0.8182,
  "model_score": 0.5862,
  "style_score": 0.9451,
  "label": "This text has features often associated with AI-written text, but this is not proof of authorship. If this is your original work, you can appeal by sending its content ID and a brief explanation to POST /appeal.",
  "error": null,
  "verdict": ""
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "7d34a9f5-2a92-4b15-b2f8-77b73c2d1106",
  "creator_id": "attacker_EV08",
  "guess": "unsure",
  "confidence": 0.4185,
  "model_score": 0.2452,
  "style_score": 0.6678,
  "label": "We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.",
  "error": null,
  "verdict": ""
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "4c6d8008-4e40-46ce-976e-dd04341f6e6b",
  "creator_id": "attacker_EV09",
  "guess": "unsure",
  "confidence": 0.3502,
  "model_score": 0.7042,
  "style_score": 0.2564,
  "label": "We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.",
  "error": null,
  "verdict": ""
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "e543ff54-f2f3-43d1-99ab-aa772556e804",
  "creator_id": "attacker_EV10",
  "guess": "unsure",
  "confidence": 0.6534,
  "model_score": 0.9792,
  "style_score": 0.3948,
  "label": "We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.",
  "error": null,
  "verdict": ""
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "7edd934e-bc89-4151-9eb8-648a47d0766a",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.3584,
  "model_score": 0.6175,
  "style_score": 0.2637,
  "label": "We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.",
  "error": null,
  "verdict": ""
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "07fc5a3e-6286-4251-94a8-7e1b4382e064",
  "creator_id": "attacker_FP02",
  "guess": "ai",
  "confidence": 0.755,
  "model_score": 0.7387,
  "style_score": 0.7513,
  "label": "This text has features often associated with AI-written text, but this is not proof of authorship. If this is your original work, you can appeal by sending its content ID and a brief explanation to POST /appeal.",
  "error": null,
  "verdict": ""
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "83f9c7b3-344b-401a-b3e9-6b916662a3f5",
  "creator_id": "attacker_FP03",
  "guess": "unsure",
  "confidence": 0.5342,
  "model_score": 0.8051,
  "style_score": 0.5596,
  "label": "We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.",
  "error": null,
  "verdict": ""
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "6d3c11b0-ef42-434f-8791-5db79630910e",
  "creator_id": "attacker_FP04",
  "guess": "unsure",
  "confidence": 0.6493,
  "model_score": 0.8329,
  "style_score": 0.4822,
  "label": "We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.",
  "error": null,
  "verdict": ""
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "b9010160-fafa-4756-a4fa-9693b99ba8cb",
  "creator_id": "attacker_FP05",
  "guess": "unsure",
  "confidence": 0.7394,
  "model_score": 0.8005,
  "style_score": 0.6431,
  "label": "We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.",
  "error": null,
  "verdict": ""
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "832cd3b4-8be5-41e7-9bd6-eb99138c5ff2",
  "creator_id": "attacker_FP06",
  "guess": "unsure",
  "confidence": 0.5163,
  "model_score": 0.8814,
  "style_score": 0.128,
  "label": "We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.",
  "error": null,
  "verdict": ""
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "ef585dc8-bc2b-4c09-8dbc-983f9e2a2aaf",
  "creator_id": "attacker_FP07",
  "guess": "unsure",
  "confidence": 0.4883,
  "model_score": 0.8816,
  "style_score": 0.0246,
  "label": "We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.",
  "error": null,
  "verdict": ""
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 200,
  "content_id": "66ed021d-383d-47dc-a5fa-edfc51d46779",
  "creator_id": "attacker_FP08",
  "guess": "human",
  "confidence": 0.2654,
  "model_score": 0.3223,
  "style_score": 0.3132,
  "label": "Your writing looks like it was written by a person. Thanks for sharing it.",
  "error": null,
  "verdict": ""
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "c1c2655a-fc77-40c4-a42d-f89791433462",
  "creator_id": "attacker_PI01",
  "guess": "human",
  "confidence": 0.2992,
  "model_score": 0.4625,
  "style_score": 0.0815,
  "label": "Your writing looks like it was written by a person. Thanks for sharing it.",
  "error": null,
  "verdict": ""
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "86a8acb0-d5f1-4d7f-8b7f-5b4d914f8dc1",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.111,
  "model_score": 0.2044,
  "style_score": 0.063,
  "label": "Your writing looks like it was written by a person. Thanks for sharing it.",
  "error": null,
  "verdict": ""
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "ef725c9c-2650-461d-af0c-937dc346c330",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.4365,
  "model_score": 0.5943,
  "style_score": 0.5444,
  "label": "We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.",
  "error": null,
  "verdict": ""
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "b6fe59f6-f945-4587-8a02-2ed11c37b55e",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.352,
  "model_score": 0.4998,
  "style_score": 0.3949,
  "label": "We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.",
  "error": null,
  "verdict": ""
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "ce20296e-b2ad-46a9-82e1-84fee13158b4",
  "creator_id": "attacker_PI05",
  "guess": "human",
  "confidence": 0.3218,
  "model_score": 0.6401,
  "style_score": 0.2268,
  "label": "Your writing looks like it was written by a person. Thanks for sharing it.",
  "error": null,
  "verdict": ""
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "91780e05-88a7-4296-ba71-4c8ea68a73d1",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.3511,
  "model_score": 0.5583,
  "style_score": 0.2906,
  "label": "We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.",
  "error": null,
  "verdict": ""
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 200,
  "content_id": "1c9bdad3-fbfd-4348-97d7-27c4634d0bab",
  "creator_id": "attacker_MF03",
  "guess": "unsure",
  "confidence": 0.4829,
  "model_score": 0.0,
  "style_score": 0.95,
  "label": "We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.",
  "error": null,
  "verdict": ""
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 200,
  "content_id": "e4e7e714-8419-40b8-bb5d-4356a7158a23",
  "creator_id": "attacker_MF04",
  "guess": "human",
  "confidence": 0.294,
  "model_score": 0.0112,
  "style_score": 0.5,
  "label": "Your writing looks like it was written by a person. Thanks for sharing it.",
  "error": null,
  "verdict": ""
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 200,
  "content_id": "37f6cce0-2782-433a-a2dc-168113ac4c18",
  "creator_id": "attacker_MF05",
  "guess": "unsure",
  "confidence": 0.6663,
  "model_score": 0.9976,
  "style_score": 1.0,
  "label": "We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.",
  "error": null,
  "verdict": ""
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 200,
  "content_id": "b3a9c2a6-f4ff-4872-af33-d36887e0efa7",
  "creator_id": "attacker_MF06",
  "guess": "unsure",
  "confidence": 0.4995,
  "model_score": 0.9969,
  "style_score": 0.5,
  "label": "We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.",
  "error": null,
  "verdict": ""
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 200,
  "content_id": "4f908a12-2455-4a08-a1f9-85b6bf5305ac",
  "creator_id": "attacker_MF07",
  "guess": "unsure",
  "confidence": 0.4837,
  "model_score": 0.9064,
  "style_score": 0.5,
  "label": "We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.",
  "error": null,
  "verdict": ""
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF08",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 400,
  "content_id": null,
  "creator_id": {
    "id": "x"
  },
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "af816f62-ce7e-4eff-943d-7fb3b3e8508b",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.4986,
  "model_score": 0.0287,
  "style_score": 0.9815,
  "label": "We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.",
  "error": null,
  "verdict": ""
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 200,
  "content_id": "4d6dfc9c-6a7f-4685-b9fe-de945e8b99d9",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.4986,
  "model_score": 0.0287,
  "style_score": 0.9815,
  "label": "We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.",
  "error": null,
  "verdict": ""
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 200,
  "content_id": "f18b2568-f18f-417d-b037-43b22cf67d14",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.4986,
  "model_score": 0.0287,
  "style_score": 0.9815,
  "label": "We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.",
  "error": null,
  "verdict": ""
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 200,
  "content_id": "8c884267-9891-4610-8a44-7d0cea38cd49",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.4986,
  "model_score": 0.0287,
  "style_score": 0.9815,
  "label": "We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.",
  "error": null,
  "verdict": ""
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 200,
  "content_id": "885cc7ce-dabb-4087-8000-2d10b10b0211",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.4986,
  "model_score": 0.0287,
  "style_score": 0.9815,
  "label": "We can't tell who wrote this text. This result is uncertain, and we are not accusing you of using AI.",
  "error": null,
  "verdict": ""
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```
