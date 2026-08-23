# Touch and Native Device Utility Architecture

Use this reference for desktop/native tools that combine Qt UI, device discovery, HID/USB or vendor commands, firmware state, display/input mapping, privileged Windows/Linux integration, installers, and field support.

## 1. Identify the real system boundary

A device utility is not only a GUI. Its behavior spans:

- User/operator workflow.
- Application state and configuration.
- Authoritative device inventory.
- Protocol and command semantics.
- Transport and OS APIs.
- Driver/device lifecycle.
- Installer, startup, privilege, logging, and support evidence.

Treat those operational mechanisms as architecture, not deployment details.

## 2. Separate the primary layers

A practical decomposition is:

1. **Presentation and interaction** - views, touch-friendly controls, localization, accessibility, resolution/DPI behavior.
2. **Application/use-case layer** - enable/disable, mapping, mode selection, firmware information/update, import/export, and operator-safe workflows.
3. **Authoritative state services** - device inventory, selected device, configuration, capability state, update session, and reconciliation.
4. **Protocol layer** - command builder, packet framing, payload validation, response/status interpretation, retry classification.
5. **Device façade** - open/close/read/write/exchange contract without exposing platform handles to application code.
6. **Platform adapters** - HID/USB, hot plug, raw input, monitor topology, calibration, registry/startup, process/session, privilege, audio/buzzer, and driver calls.
7. **Operations** - installer, signing, upgrade, rollback, logs, crash evidence, support package, and release metadata.

A class named `Host`, `Manager`, or singleton is not automatically authoritative. Verify who owns mutation, persistence, reconciliation, and lifecycle.

## 3. Device inventory and hot-plug

Define:

- Stable identity: parent ID, path, VID/PID, serial, interface, or a composed key.
- Enumeration source and filtering rules.
- Deduplication when one physical device exposes several interfaces.
- Add/remove ordering and duplicate notifications.
- Selected-device behavior after removal.
- Reopen/reconciliation after firmware reset or re-enumeration.
- Per-device capability and configuration state.
- UI projection versus authoritative inventory.

Do not let each view maintain its own device list.

A connection/handle wrapper's open call must release any handle it already
holds before acquiring a new one -- reassigning the handle member without an
explicit close/release first leaves the prior connection open, which can
make the new open fail or silently talk over a stale one. Reopening the
same logical port/device across repeated open-close cycles is a required
verification case, not an edge case.

## 4. Protocol and transport

Keep command construction and transport separate. Specify:

- Frame/report length and byte order.
- Command/status/payload validation.
- Timeout, retry, and backoff policy.
- Partial and short responses.
- Polling versus request/response mode.
- Device removal during exchange.
- Threading and serialization of commands.
- Diagnostic correlation IDs and packet logging policy.
- Compatibility across firmware/protocol versions.

A retry must name the retryable condition. Do not retry validation, unsupported command, or permanent capability errors as though they were transport noise.

## 5. Configuration and firmware reconciliation

Classify each value as:

- User preference.
- Product policy/default.
- Device/firmware authoritative state.
- Cached observation.
- Mapping or calibration artifact.
- Sensitive/privileged setting.

Define startup order, read-back, conflict resolution, save timing, migration, and reset semantics. A file value should not silently overwrite firmware state unless that policy is explicit.

## 6. Privileged and OS-owned behavior

For global input, calibration, device enable/disable, drivers, registry, scheduled tasks, or secure desktop behavior, document:

- Required privilege and elevation flow.
- Supported OS/session contexts.
- Failure when elevation is refused.
- Security impact of global hooks or input injection.
- Driver signing and architecture.
- 32/64-bit executable and system-directory behavior.
- Interaction with login, lock, UAC, remote session, sleep, and shutdown.

Prefer a narrow privileged helper/service over elevating the full UI when the capability and deployment model justify it.

## 7. Display, touch, and mouse mapping

Model separately:

- Physical device identity.
- Logical display identity.
- Desktop coordinate space.
- Orientation and scaling.
- Device report coordinate range.
- Mapping/calibration result.
- Touch, single-touch, multi-touch, and mouse modes.

Recompute or invalidate mapping on display add/remove, rotation, resolution/DPI change, device reset, or topology reorder. Define operator guidance when automatic reconciliation is unsafe.

## 8. Firmware update as a controlled transaction

Specify:

- Device eligibility and image compatibility.
- Pre-update mode/state transition.
- Exclusive access and interruption handling.
- Progress source and timeout.
- Reset/re-enumeration behavior.
- Post-update version verification.
- Recovery path for partial failure.
- Logs and support evidence.
- Whether configuration/mapping must be restored.

Do not present a successful file transfer as a successful firmware update without read-back/re-enumeration evidence.

When more than one firmware/image format or chip family can be loaded through
the same picker, identify which format a file is by parsing an
identifying signature the format itself defines (a magic-byte header, an
explicit format field) -- never by the file's byte size. A size threshold
guessed from currently-known sample files misclassifies any legitimate
file whose size lands on or past that boundary, and boundary values (an
image that is exactly the guessed cutoff) are exactly the case a heuristic
gets wrong.

Check an OS file-selection or save dialog's result for cancellation (an
empty path/no selection) before acting on it. Do not assume a dialog
callback always carries a usable path.

## 9. Product variants

Separate:

- Shared device/protocol/core capability.
- Product policy and defaults.
- Customer-specific workflow.
- UI composition and branding.
- Optional hardware/OS capability.

Use configuration, capability policy, or product composition when variants share lifecycle and contracts. Use a separate product/module when release cadence, ownership, safety, or deployment differs materially. Track variant divergence explicitly.

## 10. Verification matrix

Include at least:

- No device, one device, multiple devices, multiple interfaces.
- Add/remove during idle and during command/update.
- Unsupported firmware/protocol version.
- Short/late/error response.
- Restart and stale configuration.
- Display add/remove/rotate/scale/reorder.
- Standard user, admin, denied elevation, login/lock/remote session.
- Clean install, upgrade, downgrade/rollback, silent install, uninstall/reinstall.
- Localization and target resolutions/DPI.
- Crash/log/support evidence collection.
