# Qt Cross-platform Tool Checklist

## UI and Application

- Signal/slot ownership, connection type, and disconnection.
- QObject parent/lifetime and plug-in unload behavior. When a QObject owns a
  background worker/thread/pipeline, perform the actual shutdown-and-wait
  logic inside that object's own destructor -- not only via a separately
  called method an external owner must remember to invoke -- so shutdown
  happens regardless of how the object is destroyed. Destroy such an object
  via `deleteLater()` (deferred, event-loop-driven deletion) rather than a
  synchronous `delete` when the worker's shutdown is not provably complete
  and synchronous at the point of destruction; a disabled/commented-out
  shutdown call left inside a destructor, relying on an external call site
  that may be skipped or reordered, is a known-recurring version of this gap.
- UI-thread affinity.
- Long-running work, cancellation, timeout, and late completion.
- Model/view separation.
- Native integration escape hatches.
- Localization, fonts, DPI, accessibility, and input differences.
- Custom painting bounds, scale, theme, and high-DPI behavior.
- Document the render-space and input-space units at the platform-adapter
  boundary explicitly (e.g. logical points vs. device/backing pixels vs. a
  device's own raw coordinate range) -- do not leave the conversion implicit.
  Test visible control bounds, edge taps, orientation change, density
  scaling, and the inverse conversion, not just the forward one. When visuals
  and hit-testing disagree, fix the shared coordinate contract at the adapter
  boundary first; patching individual controls with per-control offsets to
  compensate for a systemic scale/origin defect hides the real bug behind
  several uncoordinated workarounds instead of removing it. Repeat the actual
  interaction path (not just a screenshot) after the adapter fix.

## Designer Components

- Runtime widget library separated from Designer adapter library.
- Standard collection/interface IID.
- Stable widget class, namespace, property, signal, slot, and enum names.
- `domXml()` class/name/default-property compatibility.
- `includeFile()` and forwarding-header compatibility.
- Resource URL and icon availability inside the Designer process.
- Plug-in binary name, ABI, Qt version, debug/release mode, and install/discovery path.
- Designer host architecture, compiler/runtime ABI and toolkit ABI verified independently from the application runtime; successful application linking does not prove host loadability.
- Existing `.ui` samples load without promotion/substitution warnings.
- Disabled, experimental, and archived components are not silently registered.

## Hardware and Communication

- Transport abstraction.
- Device discovery.
- Reconnect and state reconciliation.
- Partial read/write.
- Protocol framing.
- Timeouts and late responses.
- Platform driver/permission differences.
- Diagnostic logs and trace identifiers.
- Camera/device start-stop ownership and blocking-call policy.
- When per-frame or per-cycle code consumes several correlated output
  streams from a shared asynchronous pipeline (a background graph/worker
  producing multiple conditionally-present results), check a target
  stream's own queue/availability state directly, immediately before a
  blocking dequeue on it, and skip consumption gracefully when it is
  currently empty -- do not gate consumption on a separate, only-correlated
  presence/flag stream that can desynchronize from the data stream over
  time, and do not call an unconditional blocking dequeue on a stream that
  is not guaranteed to produce data every cycle. Separately, identify
  whether any one output stream from the same pipeline is the de-facto
  per-cycle completion barrier (the stream whose blocking read is the only
  thing that actually waits for that cycle's processing to finish) and read
  it before consuming any other correlated stream for that cycle; document
  why the ordering is required so a later refactor does not silently
  reorder the calls and reintroduce a stale-read race.

## Build and Deployment

- Qt version and modules.
- C++ language standard and compiler/ABI matrix. Before raising the
  standard (or any other compiler flag not previously pinned) to satisfy
  one narrow slice's needs, check whether the project currently builds
  under an implicit/unspecified default -- raising it project-wide can
  surface new strictness violations in unrelated, unmodified files that
  happened to compile only under the old, looser implicit dialect. Scope
  the raised standard to only the files that actually require it (confirmed
  via grep for what includes the needed header/feature), using a per-file
  compiler-flag mechanism rather than the whole target, and treat each
  pre-existing violation the bump uncovers as a separate, disclosed
  decision rather than silently absorbing an unplanned wider fix into the
  slice's diff. When using a generator-expression-based mechanism to
  exclude a file type from a target-wide flag, verify it actually took
  effect by inspecting the real generated build project for the excluded
  file -- some generators do not honor such an exclusion for every file
  type, and a successful build does not confirm it was applied.
- Static/dynamic linkage policy.
- qmake/CMake coexistence and artifact comparison during migration.
- Imported dependency targets instead of developer-specific absolute paths.
- Optional OpenCV/Eigen/Charts/Multimedia/3D feature targets.
- Packaging shared libraries and Designer plug-ins.
- Release matrix covers platform, CPU/ABI, toolkit, debug/release mode, Designer host where applicable, packaging, clean install, upgrade, downgrade/rollback, and explicitly unsupported cells.
- Android permissions and lifecycle.
- Windows/Linux/macOS path, driver, signing, and runtime deployment differences.
- Upgrade, rollback, source compatibility, `.ui` compatibility, and ABI compatibility.
- When multiple backend-specific variants of the same logical component
  (CPU vs. GPU, one platform's implementation vs. another's) plug into a
  shared, string-keyed registry (a calculator/subgraph registry, a plug-in
  registry, any `register_as`/`type` style binding), assign each variant a
  distinct registration key -- never the same key reused across variants.
  Before adding a new variant, grep for every existing registration of that
  component's name (the build-target registration and any config/graph
  file referencing it) to confirm no collision; if a build/link failure or
  "the wrong variant ran" symptom appears, check registration-key
  uniqueness as a specific hypothesis, not only a generic wiring question.
- A toolchain or SDK version identifier passed downstream (into a container
  build, an install path, a versioned artifact name) is derived from the
  build system's own live version variable, never a hardcoded literal --
  even one that currently matches the common/default version, since the
  mismatch stays invisible exactly until someone builds with a different
  one. Check whether an equivalent live variable already exists before
  introducing a separate hardcoded copy.
- A post-build/post-link/deploy cleanup step that clears a shared output
  directory before writing into it scopes its deletion to a pattern
  matching only the current target's own artifact name, never an
  unqualified wildcard over the whole directory -- treat any `rm -f
  <dir>/*` (or equivalent glob/recursive delete) inside a per-target build
  step as a signal to verify the directory's ownership scope (exclusive to
  this target, or shared with others) before accepting the change.
- When a change moves a type/struct definition that a distributed
  header-plus-binary package's own public headers depend on, verify every
  other header in the SAME distributed package still resolves it -- either
  because the new location ships in the package's own include tree, or
  because the package's include-path configuration is updated to reach it.
  Attempt to resolve the changed header's include chain using only the
  files and include paths the package itself ships/declares, not the
  author's full private workspace, to confirm the public interface stays
  self-contained; a header reachable only through a path outside what the
  package's own setup instructions tell a consumer to check out is a
  packaging defect to fix, not an implicit expectation on the consumer.

## Process, Startup, and Local Secrets

- Process identity records more than a recycled numeric PID when stale-owner recovery matters; liveness is verified through the target OS rather than a shell-specific syntax or signal convention.
- Per-user startup, machine-wide startup, service installation, and privileged helpers have distinct owners, authorization, reconciliation, removal, and rollback behavior.
- Credentials and tokens are owned by an OS-appropriate protected store or explicit secret provider, not portable configuration, logs, bundles, source files, or UI state. Define account scope, least privilege, rotation, deletion, and unavailable-store behavior without hard-coding a vendor backend.
