# Repository and Document Evidence - Historical Touch IC Utility

## Status

**Evidence level: repository-verified and document-verified historical implementation.**

Source: a user-supplied historical Qt/C++ touch-device utility repository and its controlled/uncontrolled engineering documents. The source was inspected locally; it was not rebuilt end to end and is not linked from this public skill repository.

No firmware binaries, raw command tables, customer-identifying content, credentials, private logs, or proprietary source are copied into CloudSkill.

## Repository evidence

The supplied Git history contains:

- 357 commits from 2023-10-24 through 2025-06-09.
- 17 named release tags from the 4.x through 5.x product line.
- A primary Qt 6/C++17 Windows utility plus related keypad, scanner, test, prototype, installer, driver-research, and product-variant projects.
- Iterative work across device hot plug, HID/USB communication, firmware information/update, sound/buzzer behavior, monitor/touch/mouse mapping, rotation, localization, installer/startup, import/export, product variants, and field defect correction.

Commit counts and tags are treated as historical evidence only; they do not by themselves prove test coverage or release readiness.

## Architecture evidence

The source demonstrates:

- A device interface/facade with platform-specific Windows/Linux/emulator implementations selected by a factory.
- Separation of command/protocol construction from device transport and higher-level touch-device operations.
- Device discovery, filtering, add/remove notification, multi-interface/device identity handling, and an application-level device inventory.
- Qt presentation combined with tray, single-instance, startup, session, raw input, monitor topology, calibration/mapping, privilege, device enable/disable, and Windows-specific integration.
- Configuration, localization, logging, firmware metadata/update, installer, and product/customer variation.
- Prototype/test utilities used to reduce uncertainty around HID, device change, input injection, buzzer/driver access, and OS behavior.

Historical source demonstrates problem-solving capability; it does not endorse all implementation-era mechanisms such as broad singletons, raw ownership, compile-time product flags, checked-in binaries, or Windows-specific coupling.

## Product and project evolution evidence

The documents preserve a visible evolution chain:

- Early specifications start from a narrow non-engineer workflow and the decision to replace a difficult-to-build legacy utility.
- Later revisions add hot-plug behavior, high-resolution/touch-friendly UX, multiple touch/mouse modes, device information, localization, installer/startup behavior, privilege constraints, mapping/rotation, firmware update, and product variants.
- A release plan records urgent scope insertion, target release windows, capacity/leave constraints, unresolved decisions, “function first” staging, and deferred backlog.
- Customer-feedback presentations compare current and desired workflows and feed new requirements into the specification.
- Release notes, tags, test utilities, logs, installer definitions, and field fixes provide partial implementation/operational evidence.
- Follow-on specifications extend the product into alternative UI styles, driver research, and a keypad utility.

One supplied specification filename had a higher version suffix while its title, revision table, and extracted content remained the prior version. This is retained only as a governance lesson: filename version is not sufficient evidence of an approved new baseline.

## Reusable interpretation

The reusable capabilities are:

- Native device utility architecture across UI, application state, protocol, transport, OS integration, firmware, and deployment.
- Evidence-based reconstruction of product evolution from repositories and documents.
- Requirement/specification lineage and release-baseline control.
- Lightweight project management for uncertain hardware/OS work, customer feedback, urgent changes, release trains, and product variants.
- Operational completion that includes installer, privilege, configuration, compatibility, logs, rollback, and field support.

Do not reproduce customer-specific names, private protocol data, firmware content, binaries, or logs in generic skills or public documentation.

## Skill mapping

- Primary architecture owner: `cross-platform-native-architecture`.
- Primary product/project evolution owner: `development-process-tailoring`.
- Specification and evidence owner: `document-governance`.
- Shared core/variant and extension boundaries: `framework-design`.
- Legacy replacement and compatibility-preserving migration: `safe-incremental-refactoring`.
- Quality scenarios and release gates: `software-quality-iso25010`.
- Decision reconstruction: `architecture-review`.
- Implementation correctness review: `code-review`.
