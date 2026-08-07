# Repository Evidence — Qt Component and Vision Workshop Suites

## Status

**Evidence level: repository-verified historical implementation with one focused dependency-free test executed.**

Reviewed supplied repositories:

- `cbComponent` history from 2021–2022.
- `cbWorkshop` history from 2022–2024.

A complete Qt/OpenCV build was not executed because the review environment did not contain Qt/qmake, OpenCV, Eigen, Qt Charts, Qt Multimedia, or Qt3D. The evidence below is therefore architectural/source evidence, not a claim of end-to-end build success.

## Architecture evidence

- Qt Designer custom widget collections and individual `QDesignerCustomWidgetInterface` adapters.
- Runtime QWidget implementations with custom painting, properties, signals/slots, forms, resources, and plug-in metadata.
- Core formatting, delegate, logging, profiling, container, request/response, and utility layers.
- OpenCV camera capture, image utilities, calibration, stereo matching, triangulation, and video processing.
- Qt camera/video controls, image lists, RGB/HSV/position inspection, charts, and workflow/navigation widgets.
- Qt3D skeleton, pose, grid, bone, joint, and visualization components.
- qmake deployment rules for multiple host/container environments.
- Component test forms and historical examples.

## Modernization evidence

The two repositories demonstrate a real brownfield component-product-line problem:

- Identical and diverged copies of core/logger/delegate/widget code coexist.
- Active, backup, example, and experimental sources are mixed in one tree.
- Runtime widget implementation and Designer plug-in wrappers are compiled together.
- Build files depend on developer/container-specific absolute paths and external `.pri` files.
- Serialized/source compatibility may depend on legacy misspellings in class and method names.
- Optional Qt modules, OpenCV, Eigen, Charts, Multimedia, and Qt3D are not isolated as explicit feature targets.
- A confirmed compile defect existed in a template utility (`passengerCount` returned a value from a `void` function), illustrating the need for lightweight non-Qt tests around reusable core code.

## Reusable interpretation

The transferable capability is not the legacy syntax. It is the ability to:

1. Reconstruct a component suite from source, build files, plug-in metadata, and history.
2. Identify public Qt/Designer contracts such as class/property/signal names, `domXml`, include paths, IID, resources, binary placement, ABI, and `.ui` serialization.
3. Select one authoritative source before deduplication.
4. Split runtime libraries from thin design-time adapters.
5. Introduce characterization/component-gallery tests before visual or lifecycle changes.
6. Run qmake and CMake in parallel during migration rather than combining build, Qt-version, API, and behavior changes.
7. Preserve legacy names through compatibility façades until downstream forms and consumers are migrated.

## Interpretation rule

Do not automatically reproduce historical choices such as global `using namespace`, macro-heavy configuration, raw allocation without explicit lifecycle policy, fixed-size painting, caller-thread sleeps, absolute deployment paths, or duplicated backup trees. Preserve compatibility only where consumers require it; modernize ownership, build reproducibility, testing, and feature boundaries deliberately.
