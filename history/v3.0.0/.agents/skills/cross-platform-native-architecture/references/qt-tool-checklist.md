# Qt Cross-platform Tool Checklist

## UI and Application

- Signal/slot ownership and disconnection.
- QObject parent/lifetime.
- UI-thread affinity.
- Long-running work and cancellation.
- Model/view separation.
- Native integration escape hatches.
- Localization, fonts, DPI, and input differences.

## Hardware and Communication

- Transport abstraction.
- Device discovery.
- Reconnect and state reconciliation.
- Partial read/write.
- Protocol framing.
- Timeouts and late responses.
- Platform driver/permission differences.
- Diagnostic logs and trace identifiers.

## Build and Deployment

- Qt version and modules.
- Static/dynamic linkage policy.
- Platform toolchains.
- Packaging shared libraries/plugins.
- Android permissions and lifecycle.
- Windows/Linux path and driver differences.
- Upgrade and compatibility.
