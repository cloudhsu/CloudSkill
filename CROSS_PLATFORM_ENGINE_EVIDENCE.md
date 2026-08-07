# Cross-platform Engine Evidence — CloudBox

## Evidence Status

**Repository-verified, historical implementation.**

The public repository identifies CloudBox as a cross-platform game engine/framework for iOS, Android, and Win32 and contains 98 commits.

## Verified Repository Structure

The repository includes:

- iOS project/platform integration.
- Android Java and JNI/NDK integration.
- Win32 projects and libraries.
- A portable native `jni/CloudBox` core.
- Platform-specific Android, iOS, Win32, component, and extension directories.
- OpenGL graphics classes.
- Scene/director, action, event, layout, image, label, button, audio, dialog, environment, factory, and component classes.

The history documents work on:

- Android texture reload after resume.
- Background/foreground events.
- Texture-pool refactoring.
- Android touch cross-thread behavior.
- iOS orientation and Retina support.
- Audio on iOS and Android.
- Motion/accelerometer.
- Dialog and store/IAP integration.
- Cross-platform component testing.

## Architecture Capability Demonstrated

The implementation supports the following conclusions:

- Portable native core design.
- Platform service adapters.
- Cross-language integration.
- Graphics/rendering abstraction.
- Scene and application lifecycle orchestration.
- Resource pooling and reconstruction.
- Input and display adaptation.
- Reusable components and action/event systems.
- Multi-platform build and deployment awareness.

## Historical-context Rule

Do not convert implementation-era details into current preferences.

Examples that require historical interpretation:

- Raw pointer ownership.
- Singleton-heavy access.
- Macros and conditional compilation.
- Fixed-function OpenGL/OpenGL ES.
- Legacy Visual Studio, Eclipse, NDK, and Xcode project structures.

The reusable lesson is the boundary/lifecycle reasoning, not automatic reuse of the original mechanisms.
