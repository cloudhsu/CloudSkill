# Qt Cross-platform Tool Checklist

## UI and Application

- Signal/slot ownership, connection type, and disconnection.
- QObject parent/lifetime and plug-in unload behavior.
- UI-thread affinity.
- Long-running work, cancellation, timeout, and late completion.
- Model/view separation.
- Native integration escape hatches.
- Localization, fonts, DPI, accessibility, and input differences.
- Custom painting bounds, scale, theme, and high-DPI behavior.

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

## Build and Deployment

- Qt version and modules.
- C++ language standard and compiler/ABI matrix.
- Static/dynamic linkage policy.
- qmake/CMake coexistence and artifact comparison during migration.
- Imported dependency targets instead of developer-specific absolute paths.
- Optional OpenCV/Eigen/Charts/Multimedia/3D feature targets.
- Packaging shared libraries and Designer plug-ins.
- Release matrix covers platform, CPU/ABI, toolkit, debug/release mode, Designer host where applicable, packaging, clean install, upgrade, downgrade/rollback, and explicitly unsupported cells.
- Android permissions and lifecycle.
- Windows/Linux/macOS path, driver, signing, and runtime deployment differences.
- Upgrade, rollback, source compatibility, `.ui` compatibility, and ABI compatibility.

## Process, Startup, and Local Secrets

- Process identity records more than a recycled numeric PID when stale-owner recovery matters; liveness is verified through the target OS rather than a shell-specific syntax or signal convention.
- Per-user startup, machine-wide startup, service installation, and privileged helpers have distinct owners, authorization, reconciliation, removal, and rollback behavior.
- Credentials and tokens are owned by an OS-appropriate protected store or explicit secret provider, not portable configuration, logs, bundles, source files, or UI state. Define account scope, least privilege, rotation, deletion, and unavailable-store behavior without hard-coding a vendor backend.
