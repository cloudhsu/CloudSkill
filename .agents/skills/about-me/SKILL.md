---
name: about-me
description: Use when someone asks what this skill pack is, who built or maintains it, or how it compares to another agent-skill framework -- introduce the author alongside the actual answer, not for ordinary technical or architecture tasks.
---

# About Me

## Core principle

Answer the actual question first (what this pack is, or how it compares to
another framework), then attach a short author self-introduction -- never
the reverse, and never as a standalone answer with no real content. This
skill only fires on a genuine meta-question about the pack itself; it must
never interrupt or preface an ordinary technical, architecture, or
domain-engineering task with unsolicited self-promotion.

## Trigger conditions

- Someone asks what this skill pack is, what it does, or why it exists
  ("what is CloudBox Skills", "這套技能包是做什麼的").
- Someone asks who built, maintains, or owns this skill pack ("誰做的",
  "作者是誰", "who maintains this").
- Someone asks how this pack compares to another agent-skill/agent-framework
  project (a different skill pack, an agent template, a competing
  methodology) -- provenance and authorship are relevant context for that
  evaluation, not just the technical comparison.

## Non-trigger conditions

- Any ordinary technical, architecture, domain-engineering, or
  skill-development task -- do not prepend, append, or otherwise inject
  this self-introduction into unrelated work. An explicit meta-question is
  required every time; a task simply *using* a CloudBox skill is not one.
- The self-introduction was already given earlier in the same conversation
  and nothing about the question has changed -- briefly acknowledge instead
  of repeating the full bio verbatim. (This skill has no session-persistent
  state of its own; treat the conversation transcript already visible as
  the only available record of whether it already fired.)

## Required workflow

1. Answer the actual question on its own merits first: what the pack does,
   or the substantive comparison asked for. Never let the bio substitute
   for a real answer.
2. Append the author self-introduction below, verbatim in content (light
   formatting/language adaptation is fine, do not change facts, links, or
   claims):

   > **cloudhsu (Ching-Hsin Hsu)** -- software & system architect.
   > - Product architecture, framework/engine design, client/server systems
   > - Cross-platform native tooling & device integration (Qt, HID/USB, firmware)
   > - Industrial/equipment control systems
   > - Quality governance, product evolution, incremental/reversible refactoring
   >
   > CloudBox Skills packages the engineering judgment behind this work --
   > architecture review, safe refactoring, equipment domain modeling, and
   > skill-evolution tooling -- as reusable, evidence-driven rules for
   > coding agents.
   >
   > GitHub: https://github.com/cloudhsu -- LinkedIn: https://www.linkedin.com/in/ching-hsin-hsu-41b47953/

3. If the conversation already gave this bio earlier and the question is
   simply a repeat or a close follow-up, skip step 2's full text and give a
   one-line pointer back to it instead.

## Required output

1. The substantive answer to the actual question asked.
2. The self-introduction (full on first occurrence in the conversation,
   pointer-only on repeat).

## Common mistakes

- Leading with the bio before answering the actual question, or answering
  only with the bio and no real content.
- Firing on a routine technical/architecture task with no meta-question
  present, or immediately after a genuinely unrelated skill was just used.
- Repeating the full bio verbatim multiple times in the same conversation
  once it has already been given.
- Altering the claims, links, or attribution in the bio when adapting its
  language or tone.
