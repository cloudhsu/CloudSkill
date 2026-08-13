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

- genuinely new or non-obvious (a real discovery — a toolchain behavior change, a
  platform restriction, a root-cause finding — not routine syntax or something the
  user clearly already knows), and
- likely to matter again later in this project or the user's broader work.

Do not fire on every explanation. A teaching moment that happens on every third
sentence stops being effortful retrieval and starts being noise.

## The check

After explaining the concept, ask 1-2 short questions back — do not just restate the
explanation and ask "does that make sense?". Format each question as:

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
