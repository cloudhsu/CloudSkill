---
name: teach-while-building
description: Use when the user wants to build mastery of relevant knowledge as a side effect of real engineering work, not as a separate course — proactively check understanding of new concepts as they come up, then keep only the durable ones.
---

# Teach While Building

## Purpose

Real work surfaces real knowledge: a toolchain quirk, a platform-behavior change, a
non-obvious constraint. Explaining it once and moving on gives the user an illusory
sense of understanding — **fluency strength** — but not durable retention —
**storage strength**. Only effortful retrieval builds storage strength. This skill
folds a lightweight check into the existing work rhythm instead of opening a separate
teaching workspace or course.

## When to trigger

Self-judged, not user-triggered. Fire when, mid-task, you notice a concept that is
**both**:

- non-obvious *to this user, at their current level* (not a fixed, expert-calibrated
  bar — see Calibration below), and
- likely to matter again later in this project or the user's broader work.

Do not fire on every explanation. A teaching moment that happens on every third
sentence stops being effortful retrieval and starts being noise.

### Calibration: the bar adapts to the person, not a fixed standard

"Non-obvious" cannot be judged against your own knowledge, or against an expert
user's — that bar excludes real gaps for a junior or unfamiliar-with-this-stack
user, and produces constant noise for a genuine expert. Target each check at this
specific user's **zone of proximal development**: not what they already know alone,
not what would need a full lecture, but the next thing they could grasp with a short
nudge.

Calibrate from evidence, not assumption:

- **No history yet for this domain**: default toward checking *more*, not less — you
  have no signal the user already has this covered. Err generous until evidence says
  otherwise.
- **`LEARNING_LOG.md` already has entries in this domain**: treat prior confirmed
  entries as a real skill-level signal. If the user has independently built on a
  logged concept correctly since, the bar for that domain can rise — routine
  explanations in it stop needing a check.
- **The user expresses surprise about something you *didn't* flag** ("wait, I didn't
  know that"): this is a live miss — you judged it routine and were wrong. Lower the
  bar for that domain going forward, and treat it like any other confirmed concept
  once explained.
- **The user states their own level directly** ("I'm junior at X", "I already know
  Y"): that overrides inferred calibration immediately — don't wait for organic
  evidence when they've just told you.

This mirrors how real adaptive tutoring stays effective: target the zone between
"they could already do this alone" and "this needs scaffolding they don't have yet,"
using the learner's actual responses as the live signal, not a static assumption
about who they are.

### Optional explicit calibration file

A user can skip organic calibration entirely for a domain by stating it once in
writing instead of waiting for it to be inferred. If `LEARNING_LEVEL.md` exists next
to `LEARNING_LOG.md`, read it before applying any other calibration signal: an
explicit line for a domain (e.g. "iOS build toolchain: experienced", "Android
Gradle: junior") overrides both the no-history default and any signal drawn from
`LEARNING_LOG.md` for that domain. Only write a new line into this file when the
user states their level directly — the same trigger as the override rule above —
never infer an entry into it from how a conversation went.

### Timing: batch at natural pauses, don't interrupt mid-flow

Noticing a teaching moment does not mean checking it immediately. Hold flagged
concepts and run the check at the next natural pause — a slice/checkpoint
finishing, a build or test succeeding, a logical stopping point in the
conversation — covering everything flagged since the last check in one short
round, not one interruption per concept. Firing mid-implementation turns a
lightweight check into friction, and friction is what gets a feature turned off.

Exception: check immediately, without batching, when the concept is a hard
prerequisite for correctly following the very next step — the user cannot
usefully continue without it landing first.

## The check

At the next natural pause (see Timing above), ask short questions back for every
concept flagged since the last check — do not just restate the explanation and ask
"does that make sense?". One ❓/➡️ pair per concept; format each as:

```
❓ <question that requires recalling or applying the concept, not just recognizing it>
➡️ <your own expected/recommended answer, stated>
```

Stating your own expected answer alongside the question keeps this fast and
low-stakes: the user confirms, corrects, or extends it, rather than performing a
blind quiz. Wait for the answer before moving on. This is not a full multi-round
interview — one short round is enough; the goal is a confirmation checkpoint, not an
exam.

## What gets kept

Only log a concept once the check confirms it landed **and** it's worth retaining
later — not every explanation, not every check. Append it to a project-local
`LEARNING_LOG.md` (create one at the project root or docs directory if none exists),
in the user's own words/framing where possible, not a copy of your explanation. Each
entry should be short enough to be a real reference, not a transcript.

## Non-goals

- Not a replacement for real documentation, ADRs, or the project's own decision log —
  those capture *why a decision was made*; this captures *what the user now
  understands* that they might forget.
- Not a course. Do not build a curriculum, a resource list, or a lesson sequence
  around this — if the user wants that, it's a different, heavier request.
- Not mandatory per-explanation. If nothing genuinely new came up, there is nothing
  to check and nothing to log.
