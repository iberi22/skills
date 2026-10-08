# Dart/Flutter Commands for isar_agent_memory

> Added: 2026-07-22 (Wave 1, isar_agent_memory)
> Used for all Dart/Flutter issue creation and PR verification.

## Dependency Management

```bash
flutter pub get       # Resolve + download dependencies
dart pub get          # Pure Dart version (no Flutter SDK needed)
```

## Analysis

```bash
dart analyze lib/     # Lint — 0 errors expected (81-84 issues are fine: Isar codegen + tflite optional)
```

## Testing

```bash
# All tests (will fail on objectbox/isar codegen-dependent tests)
flutter test

# Pure-Dart tests (pass without codegen)
flutter test test/smoke_test.dart
flutter test test/encryption_service_test.dart
flutter test test/word_piece_tokenizer_test.dart
flutter test test/sync_manager_test.dart
flutter test test/pipeline_hooks_test.dart

# Single test file
flutter test test/pipeline_hooks_test.dart
```

## Running Tools

```bash
# Benchmark (mock mode — no model files needed)
dart run tool/benchmark.dart --mock

# Benchmark (real mode — requires ONNX model files)
dart run tool/benchmark.dart
```

## Known Issues

- Tests importing `MemoryGraph` will fail at load time because they trigger `objectbox` codegen (pre-existing)
- To run those, first run `dart run build_runner build` to generate Isar schemas
- Objectbox dependency was removed from pubspec.yaml by PR #69 — must be manually re-added if missing:
  ```
  objectbox: ^5.0.0
  ```
