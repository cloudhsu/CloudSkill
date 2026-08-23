# Production Code Review Checklist

## State and Concurrency

- Is shared state protected consistently?
- Can callbacks re-enter the same object?
- Can a timeout race with a successful response?
- Can a previous request's result satisfy a later request?
- Is mutable state reset at the correct lifecycle boundary?
- Are collections thread-safe in both access and compound operations?
- Is cancellation distinguished from failure?
- Are memory visibility and ordering assumptions valid?
- When a field is assigned twice in sequence (e.g. a production default
  immediately followed by a reassignment), does an adjacent comment
  correctly describe which literal actually ships? A later assignment
  silently wins regardless of what a "for user"/"for test" comment claims,
  unless the reassignment is itself gated by a build flag or environment
  check.
- Does a barrier/rendezvous/aggregator that advances shared state once a
  group of participants is "ready" gate that decision on an explicit
  completeness check (all registered participants have reported for the
  current round), rather than reaching a positive decision from inspecting
  only the one participant it happens to look at? Treat the existence of a
  separate ready-status/registration collection as a requirement to
  actually compare its size/membership against the participant set before
  advancing, not merely bookkeeping.

## Communication

- Are message boundaries explicit?
- Is partial read/write handled?
- Before decoding a binary field, are declared lengths and offsets bounded, and are byte order, signedness, width, and alignment explicit rather than inferred from representative messages?
- Is correlation identity validated?
- Are duplicate, delayed, malformed, or out-of-order messages handled?
- Are disconnect and reconnect transitions explicit?
- Can a command be sent twice during retry or reconnection?
- Is protocol encoding defined?
- Are buffers owned and cleared correctly?

## Resource Lifetime

- Who owns streams, sockets, handles, timers, threads, tasks, buffers, and native resources?
- Does every worker have an owner, cancellation and wake-up path, and bounded join before dependencies are destroyed? Treat detach/fire-and-forget as an explicit lifetime transfer, not as cleanup.
- Can dispose race with active operations?
- Are event handlers detached?
- Can background work retain dead objects?
- Are platform-specific handles released on every path?
- For a `weak_ptr` (or equivalent non-owning smart-reference) member, does a
  specific other owner actually hold the corresponding `shared_ptr` for a
  lifetime that starts before and outlives this reference's use? Flag any
  `.lock()`/equivalent result that is dereferenced without a null/expired
  check, and flag it more urgently when no `shared_ptr` to that object
  exists anywhere in the codebase -- a `weak_ptr` with no real owner is
  reliably expired, not occasionally. When no independent owner exists,
  recommend owning the data directly instead.

## Naming and Control Flow

- Does a method/function that wraps or forwards to a same-named library or
  global function risk resolving its own internal unqualified call to
  itself (self-recursion) rather than the intended library function? This
  applies to any language with lexical/member scoping rules, not only
  C++. Recommend renaming the wrapper or explicitly qualifying the inner
  call (e.g. `::rand()`), and check this specifically whenever a newly
  introduced method's name collides with a standard-library or
  globally-visible function it is meant to call. A defect like this can be
  platform- or branch-gated (only one `#ifdef` arm broken) -- success on
  one platform/branch is not evidence the other's equivalent path is
  correct.
- When an `if`/`else if` chain is driven by two or more independent
  boolean flags that are not mutually exclusive, are branches ordered from
  most specific (more flags required to match) to least specific? An
  `if`/`else if` chain always takes the first branch whose condition is
  true regardless of how many later branches would also match, so a more
  general condition checked first silently swallows the more specific
  case. Also verify a chain missing a final `else` still covers every
  reachable flag combination -- an omitted `else` does nothing for any
  combination that falls through, rather than failing loudly. When a new
  boolean flag is added to a system whose existing branches already depend
  on flags it can co-occur with, re-audit every existing chain gated on
  the older flags, since the new flag can silently change which branch a
  pre-existing chain reaches for combinations that used to be impossible.
- When a function's declared return type is a Result/StatusOr/Expected-
  style wrapper (or any converting type) around a move-only payload
  (`unique_ptr`, a non-copyable value type), and the return statement names
  a local of the unwrapped payload type rather than the wrapper type
  itself, is the wrapper constructed explicitly around an explicit
  `std::move` of the local (`return WrapperType(std::move(local));`)
  rather than a bare `return local;`? C++'s implicit-move-on-return rule
  applies only when the returned expression's type is the same as (or
  derives from) the declared return type; a converting wrapper is a
  different type, so the exemption does not automatically apply. A compile
  failure citing a deleted copy constructor on a move-only type at a
  `return` statement is a signal to check for this type mismatch, not a
  signal to make the payload copyable.

## Error and Recovery

- Is the original error preserved?
- Are logs sufficient to reconstruct the sequence?
- Does retry have a limit, delay, and eligibility rule?
- Can retry repeat a non-idempotent action?
- Is recovery based on actual external state or only local assumptions?
- Can the process restart without leaving the system ambiguous?

## Framework and Cross-Platform

- Is portable policy separated from platform mechanism?
- Does the abstraction hide a semantic difference that callers must know?
- Is conditional compilation localized?
- Are plug-in and module versions validated?
- Is the contract stable enough to justify the abstraction?

## UI and Device Control

- Is UI-thread affinity respected?
- Is long-running work kept off the UI thread?
- Are transport connected, protocol ready, command accepted, correlated completion, and authoritative readback represented as different states where the system exposes those boundaries?
- Does the UI reflect authoritative state rather than optimistic local state?
- Are operator commands validated against current equipment state?
- Is manual intervention represented in the state model?
