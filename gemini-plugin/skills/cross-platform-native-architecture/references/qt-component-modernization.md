# Legacy Qt Component-suite Modernization

Use this reference when a repository contains custom widgets, Designer plug-ins, qmake projects, copied component trees, Qt 5-era code, OpenCV/Multimedia/Charts/3D integrations, or host-specific deployment scripts.

## 1. Reconstruct before redesign

Classify every source area as one of:

- Authoritative runtime implementation.
- Designer adapter/metadata.
- Compatibility façade or forwarding header.
- Example or component gallery.
- Generated output.
- Experimental branch.
- Archive/backup.
- Unknown authority.

Do not delete or merge copies merely because their filenames match. Compare history, consumers, build inclusion, binary exports, serialized names, and behavior.

## 2. Treat Qt and Designer metadata as contracts

Record at minimum:

- C++ class and namespace.
- Header/include path.
- `Q_OBJECT`, properties, enums, signals, slots, invokables.
- Designer collection and widget interface IID.
- `domXml()`, default object name, geometry, tooltips, container status.
- Resource URLs.
- Plug-in file name and install/discovery path.
- Existing `.ui` files, promoted widgets, source consumers, and binary consumers.

A spelling error may be a compatibility contract. Add a correctly spelled façade first; rename only with migration evidence.

## 3. Establish executable baselines

Use the cheapest evidence that can detect change:

- Pure C++ unit tests for dependency-free utilities.
- Characterization tests for algorithms and serialization.
- Component-gallery application for every active widget.
- Representative legacy `.ui` files loaded by Designer and at runtime.
- Screenshot/geometry/property snapshots where visual behavior matters.
- Device/camera tests isolated from headless tests.
- Build/package matrix on clean machines or containers.

Do not claim a Qt migration is safe based only on compilation.

## 4. Separate runtime from design time

Preferred dependency direction:

```text
core -> cv/qt adapters -> runtime widgets -> Designer adapters
```

Designer adapters should contain only factory and metadata behavior. Runtime applications should not depend on `QtUiPlugin` or Designer interfaces.

## 5. Make features explicit

Use separate optional targets for:

- Base widgets.
- Network/device integration.
- OpenCV algorithms.
- Camera/video/multimedia.
- Charts.
- Qt3D/OpenGL.
- Designer plug-ins.

This prevents one specialized component from forcing all consumers to install every dependency.

## 6. Migrate build systems in parallel

Before replacing qmake:

1. Capture the known-working qmake commands and artifacts.
2. Resolve hidden `.pri`, environment, absolute-path, copy, install, and packaging behavior.
3. Add CMake without deleting qmake.
4. Compare target names, defines, include paths, linked libraries, generated MOC/UIC/RCC output, plug-in placement, and runtime dependencies.
5. Remove qmake only after downstream build and rollback evidence exists.

## 7. Migrate Qt versions by feature family

Do not update all modules at once. Suggested order:

1. Core and base widgets.
2. Designer plug-ins.
3. Network/device utilities.
4. OpenCV conversion/capture.
5. Multimedia/camera.
6. Charts.
7. 3D/OpenGL/platform-specific integration.

For each family, record removed/deprecated APIs, changed module packaging, ownership/thread differences, and deployment changes.

## 8. Stop conditions

Stop and reconstruct when any of these are unknown:

- Which copy is authoritative.
- Which `.ui`/source/binary consumers exist.
- How Designer discovers the plug-in.
- Which thread owns start/stop/destruction.
- Which qmake rule produces/copies a required artifact.
- How to roll back a build, package, or serialized-name change.
