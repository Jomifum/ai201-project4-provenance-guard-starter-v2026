# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---
## 1.

<!-- Your criterion. It must name a number. -->
1. False positives (human writing labeled high-confidence AI)

Test: Use `human_01`, `human_02`, `human_03`, `human_04`, and `human_05_formal` from `test_set/texts.json`; run `python test_signals.py` twice and count the five human rows in each run, for 10 results total. The target requires at least 3 formal texts, but the current set contains only one (`human_05_formal`); before running this check, replace the text in `human_01` and `human_02` with formal human writing, keeping those IDs. Check the `label` column: of the 10 results, at most 1 is labeled `ai`.

Why: On a writing site, a false accusation is more costly than a missed detection. The `0.75` AI threshold is intended to keep that risk low; these human examples check whether it does.
---

## 2.
2. Score spread

Test: Run `python test_signals.py` once on `ai_01` through `ai_05` as the clearly-AI group and `human_01` through `human_05_formal` as the clearly-human group in `test_set/texts.json`. Use the printed combined scores and group means. Check that the clearly-AI mean is at least 0.30 higher than the clearly-human mean, and that no clearly-AI text scores below 0.50.

Why: If these groups barely separate, the score carries little information. With model/style/repetition weights of `0.20`/`0.60`/`0.20` as configured in `config.py`, this check measures whether the combined score still distinguishes the groups.
---

## 3.
3. Label coverage

Test: Run `python test_signals.py` on all 15 IDs in `test_set/texts.json` (`ai_01`–`ai_05`, `human_01`–`human_05_formal`, and `borderline_01`–`borderline_05`). Check the table's label column for at least 1 `ai`, 1 `human`, and 1 `unsure`. Then run `python -c "import scoring; print(scoring.label_ranges())"`; check that the printed ranges cover 0.0 through 1.0 with no gaps or overlaps.

Why: A label that cannot be reached is a design bug. The `0.35` human and `0.75` AI thresholds define the bands; the middle range should remain available for uncertain cases rather than forcing accusations.
---

## 4.
4. Borderline text lands in "unsure"

Test: Run `python test_signals.py` and use exactly `borderline_01` through `borderline_05` in `test_set/texts.json` as the borderline group. Check their combined scores and labels: at least 4 of the 5 must score between 0.40 and 0.60 and be labeled `unsure`.

Why: These fixed borderline examples make the check repeatable without relying on a tester's judgment. The `0.75` AI threshold helps avoid turning uncertain writing into a high-confidence accusation.
---

## 5.
5. Appeal path and bad input

Test: Use the text for each of `ai_01`–`ai_05` and `human_01`–`human_05_formal` in `test_set/texts.json`. In Windows PowerShell, run this code to submit each text with `curl.exe`, then appeal its returned `content_id`:

```powershell
$items = Get-Content .\test_set\texts.json -Raw | ConvertFrom-Json
foreach ($id in @('ai_01','ai_02','ai_03','ai_04','ai_05','human_01','human_02','human_03','human_04','human_05_formal')) {
  $item = $items | Where-Object id -eq $id
  $submitBody = @{text=$item.text; creator_id='criteria-check'} | ConvertTo-Json -Compress
  $submission = (curl.exe -sS -X POST http://127.0.0.1:5000/submit -H 'Content-Type: application/json' -d $submitBody) | ConvertFrom-Json
  $appealBody = @{content_id=$submission.content_id; reasoning='I wrote this text myself.'} | ConvertTo-Json -Compress
  curl.exe -i -X POST http://127.0.0.1:5000/appeal -H 'Content-Type: application/json' -d $appealBody
}
```

A **valid appeal** means the ID belongs to an existing submission and the reasoning is a non-empty string. Check all 10 appeals return success, set the item's status to `under_review`, and append an appeal entry to `logs/audit.jsonl`. “Next to the original decision” means that appeal entry has the same `content_id` as its original decision entry; the two entries need not be adjacent lines. Then run `curl.exe -i -X POST http://127.0.0.1:5000/appeal -H "Content-Type: application/json" -d '{"content_id":"unknown-criteria-id","reasoning":"I wrote this text myself."}'`; check for a 4xx response and no audit-log change. Finally, run `curl.exe -i -X POST http://127.0.0.1:5000/submit -H "Content-Type: application/json" -d '{"creator_id":"criteria-check"}'` and the same request with `-d '{"text":"","creator_id":"criteria-check"}'`; check each returns a 4xx JSON error. For the over-length case, run `$body = '{"text":"' + ('x' * 10001) + '","creator_id":"criteria-check"}'; curl.exe -i -X POST http://127.0.0.1:5000/submit -H "Content-Type: application/json" -d $body`; check it returns a 4xx JSON error. None of these requests may return HTTP 500 or crash the service.

Why: An appeal is the only recourse for a falsely accused writer, so valid appeals must be recorded and bad requests must not disrupt the service. Keeping the `0.75` AI threshold high also reflects the cost of a false accusation.
---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
