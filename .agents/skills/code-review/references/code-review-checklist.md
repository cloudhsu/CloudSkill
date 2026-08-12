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
- When persisted, cached, signed, or evidence-bearing state is compared, does
  identity preserve serialized types instead of relying on host-language
  equality that aliases values such as JSON booleans and numbers?

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

## Error and Recovery

- Is the original error preserved?
- Are logs sufficient to reconstruct the sequence?
- Does retry have a limit, delay, and eligibility rule?
- Can retry repeat a non-idempotent action?
- Is recovery based on actual external state or only local assumptions?
- Can the process restart without leaving the system ambiguous?
- Do authority, source, risk, or contract changes automatically invalidate the
  affected evidence, or can a caller forget to request invalidation?

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
