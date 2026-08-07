# Engine Platform Adapters

## Android

Consider:

- Java/Kotlin ↔ JNI boundary.
- Activity/application lifecycle.
- GL surface recreation.
- UI-thread versus render-thread calls.
- touch delivery.
- asset access.
- permissions.
- audio and store service callbacks.

## iOS

Consider:

- Objective-C++ bridge.
- UIApplication/view lifecycle.
- EAGL/Metal surface lifecycle depending on backend.
- orientation and display scale.
- main-thread-only services.
- background restrictions.
- store and platform service callbacks.

## Windows

Consider:

- Window/message loop.
- graphics context creation.
- input.
- file/layout differences.
- desktop packaging.
- x86/x64 and ABI.

## Contract Rule

Platform adapters should expose stable engine capabilities, but adapters may return capability/state information when platforms cannot provide identical semantics.
