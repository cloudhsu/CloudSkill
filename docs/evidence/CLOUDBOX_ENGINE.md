# Repository Evidence — CloudBox Cross-platform Engine

## Status

**Evidence level: repository-verified historical implementation.**

Repository: https://github.com/cloudhsu/CloudBox

CloudBox identifies itself as a cross-platform game engine/framework for iOS, Android, and Win32 and contains a portable native core plus platform-specific integration.

## Architecture evidence

- Director and scene lifecycle.
- Update/render orchestration.
- Action, event, view, component, and layout systems.
- Rendering abstraction and OpenGL/OpenGL ES backend.
- Texture pooling and resource reconstruction.
- Touch/input, orientation, and Retina/display adaptation.
- Background/foreground and Android resume behavior.
- Audio, dialog, motion, store/IAP, social, and native platform services.
- JNI/Java integration on Android.
- Objective-C++ integration on iOS.
- Win32 integration and multi-platform build variants.

Repository history includes Android texture reload after resume, context/lifecycle handling, texture-pool refactoring, touch cross-thread behavior, orientation/Retina support, and platform service integration.

## Interpretation rule

The reusable evidence is portable-core design, lifecycle ownership, rendering/resource boundaries, and cross-language platform adapters.

Do not automatically reproduce implementation-era choices such as raw-pointer ownership, singleton-heavy access, macros, fixed-function graphics, or legacy Visual Studio/Eclipse/Xcode project structures. Select current mechanisms while preserving the original problem-solving intent.
