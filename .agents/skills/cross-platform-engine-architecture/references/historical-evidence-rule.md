# Historical Evidence Rule

CloudBox is evidence of solved architecture problems under 2011–2012 era constraints.

Use evidence from:

- Portable C++ core.
- Android/iOS/Win32 adapters.
- Director/scene lifecycle.
- OpenGL rendering abstraction.
- texture pool and resume reload.
- touch cross-thread handling.
- audio/dialog/motion/store platform capabilities.

Do not automatically reproduce:

- Raw-pointer ownership.
- singleton access.
- fixed-function graphics.
- pre-modern C++ patterns.
- legacy build-project structure.

When recommending current architecture, preserve the problem-solving intent while selecting current language, graphics, ownership, build, and test mechanisms.

## Verifying dead-code and reachability claims

A comment claiming a class or file is old, unused, or superseded ("old
delegate, not use") is not evidence by itself. Comments drift from the code
they describe, especially in ported or copy-pasted platform adapters where
the same header comment can be duplicated across a live file and a genuinely
dead one.

Before excluding a file from a rebuild, a migration slice, or a written
architecture conclusion on the grounds that it is unused:

- Trace the actual reachable call graph from the real application entry
  point (not from the file that looks most like an entry point).
- Prefer building and running the code over reading it when feasible —
  execution is stronger evidence than any comment or static read.
- If a file is excluded based on this trace, name the entry point and the
  reference chain that proves it unreachable, so the claim is checkable.

Treat an unverified dead-code claim as a hypothesis to confirm, not a fact
to propagate into a plan.
