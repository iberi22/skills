---
name: flutter-gemma
description: On-device AI integration for OrionHealth using Flutter and Gemma 4 via AICore + ML Kit. Integrates Gemma 4 100% local on Android.
version: "1.0.0"
updated: "2026-04-23"
author: swal
license: MIT
---

# Flutter Gemma - On-Device AI for OrionHealth

> **Gemma 4 E2B/E4B on Android via AICore + ML Kit Prompt API**

## 🎯 Objetivo

Integrar Gemma 4 100% local en OrionHealth usando:
- **Android**: AICore Developer Preview + ML Kit GenAI Prompt API (Kotlin native)
- **Flutter**: Platform Channels para invocar código nativo Kotlin

## 📋 Requisitos del Sistema

| Modelo | RAM | Storage | Velocidad |
|--------|-----|---------|-----------|
| **E2B** (Fast) | 8GB | 2GB | 3x vs E4B |
| **E4B** (Full) | 12GB | 4GB | Mejor calidad |

<1.5GB memory con量化 para E2B.

## 🔧 Stack Tecnológico

```
Flutter App (Dart)
    ↓ Platform Channels (MethodChannel)
Android Native (Kotlin)
    ↓ ML Kit Prompt API
AICore System App
    ↓
Gemma 4 E2B/E4B (On-Device)
```

## 📦 Dependencias Android

```kotlin
// build.gradle.kts (android/app)
dependencies {
    implementation("com.google.mlkit:genai-prompt:1.0.0-beta2")
    implementation("com.google.android.gms:play-services-tasks:18.0.2")
}

// AndroidManifest.xml
<uses-library android:name="com.google.android.aicore" android:required="false" />
```

## 🏗️ Arquitectura de Implementación

### 1. Plugin Flutter: `flutter_aicore`

```
orionhealth/
├── android/
│   └── app/src/main/kotlin/.../
│       ├── AicorePlugin.kt          # Platform channel handler
│       ├── GemmaNativeEngine.kt      # Wrapper ML Kit Prompt API
│       └── AicoreEngine.kt           # AICore connection manager
└── lib/
    └── src/
        └── services/
            ├── aicore_service.dart   # Dart side of channel
            └── gemma_adapter.dart    # GemmaLlmAdapter refactorizado
```

### 2. Flujo de Inference

```
Flutter (Dart)
    ↓ generateResponse(prompt)
AicoreService (MethodChannel)
    ↓ invokeMethod
AicorePlugin (Kotlin)
    ↓ Generation.getClient(config)
GemmaNativeEngine
    ↓ generateContent()
ML Kit Prompt API
    ↓
AICore → Gemma 4 E2B/E4B
```

## 📝 Código Kotlin: GemmaNativeEngine

```kotlin
package com.orionhealth.orionhealth_health

import com.google.mlkit.genai.prompt.*
import kotlinx.coroutines.flow.Flow

class GemmaNativeEngine {
    
    private var generativeModel: GenerativeModel? = null
    
    // Configurar para E2B (fast) o E4B (full)
    fun initialize(useFullModel: Boolean = false) {
        val config = generationConfig {
            modelConfig = ModelConfig {
                releaseTrack = ModelReleaseTrack.PREVIEW
                preference = if (useFullModel) {
                    ModelPreference.FULL  // E4B
                } else {
                    ModelPreference.FAST  // E2B
                }
            }
        }
        
        generativeModel = GenerativeModel.getClient(config)
    }
    
    // Verificar disponibilidad
    suspend fun checkAvailability(): FeatureStatus {
        val model = generativeModel ?: throw IllegalStateException("Model not initialized")
        return model.checkStatus()
    }
    
    // Descargar modelo si es necesario
    suspend fun downloadModel(onProgress: (Int) -> Unit): Boolean {
        val model = generativeModel ?: return false
        
        model.download().collect { status ->
            when (status) {
                is DownloadStatus.DownloadStarted -> {
                    Log.d(TAG, "Starting Gemma download")
                }
                is DownloadStatus.DownloadProgress -> {
                    val progress = ((status.totalBytesDownloaded.toDouble() / status.totalBytesToDownload) * 100).toInt()
                    onProgress(progress)
                }
                DownloadStatus.DownloadCompleted -> {
                    Log.d(TAG, "Gemma download complete")
                    return true
                }
                is DownloadStatus.DownloadFailed -> {
                    Log.e(TAG, "Download failed: ${status.error}")
                    return false
                }
            }
        }
        return false
    }
    
    // Generar respuesta (streaming)
    fun generateContentStream(prompt: String): Flow<String> {
        val model = generativeModel ?: throw IllegalStateException("Model not initialized")
        
        return model.generateContentStream(prompt)
    }
    
    // Generar respuesta completa
    suspend fun generateContent(prompt: String): String {
        val model = generativeModel ?: throw IllegalStateModel("Model not initialized")
        
        val response = model.generateContent(prompt)
        return response.candidates.firstOrNull()?.text ?: ""
    }
    
    // Warmup para primera inferencia rápida
    suspend fun warmup() {
        generativeModel?.warmup()
    }
    
    fun close() {
        generativeModel?.close()
    }
    
    companion object {
        private const val TAG = "GemmaNativeEngine"
    }
}
```

## 📝 Platform Channel: AicorePlugin

```kotlin
package com.orionhealth.orionhealth_health

import io.flutter.embedding.engine.plugins.FlutterPlugin
import io.flutter.plugin.common.MethodCall
import io.flutter.plugin.common.MethodChannel
import io.flutter.plugin.common.MethodChannel.MethodCallHandler
import io.flutter.plugin.common.MethodChannel.Result
import kotlinx.coroutines.*

class AicorePlugin : FlutterPlugin, MethodCallHandler {
    
    private lateinit var channel: MethodChannel
    private val engine = GemmaNativeEngine()
    private val scope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    
    override fun onAttachedToEngine(binding: FlutterPlugin.FlutterPluginBinding) {
        channel = MethodChannel(binding.binaryMessenger, "com.orionhealth/aicore")
        channel.setMethodCallHandler(this)
    }
    
    override fun onDetachedFromEngine(binding: FlutterPlugin.FlutterPluginBinding) {
        channel.setMethodCallHandler(null)
        scope.cancel()
        engine.close()
    }
    
    override fun onMethodCall(call: MethodCall, result: Result) {
        when (call.method) {
            "initialize" -> {
                val useFullModel = call.argument<Boolean>("useFullModel") ?: false
                engine.initialize(useFullModel)
                result.success(true)
            }
            
            "checkAvailability" -> {
                scope.launch {
                    val status = engine.checkAvailability()
                    result.success(status.name)
                }
            }
            
            "downloadModel" -> {
                scope.launch {
                    val success = engine.downloadModel { progress ->
                        channel.invokeMethod("onDownloadProgress", mapOf("progress" to progress))
                    }
                    result.success(success)
                }
            }
            
            "generateContent" -> {
                val prompt = call.argument<String>("prompt") ?: ""
                scope.launch {
                    try {
                        val response = engine.generateContent(prompt)
                        result.success(response)
                    } catch (e: Exception) {
                        result.error("GENERATION_ERROR", e.message, null)
                    }
                }
            }
            
            "generateContentStream" -> {
                val prompt = call.argument<String>("prompt") ?: ""
                scope.launch {
                    try {
                        engine.generateContentStream(prompt).collect { token ->
                            channel.invokeMethod("onToken", mapOf("token" to token))
                        }
                        channel.invokeMethod("onComplete", null)
                    } catch (e: Exception) {
                        channel.invokeMethod("onError", mapOf("error" to e.message))
                    }
                }
            }
            
            "warmup" -> {
                scope.launch {
                    engine.warmup()
                    result.success(true)
                }
            }
            
            else -> result.notImplemented()
        }
    }
}
```

## 📝 Dart Service: aicore_service.dart

```dart
import 'package:flutter/services.dart';

enum AicoreStatus { available, downloadable, unavailable, downloading }

class AicoreService {
  static const _channel = MethodChannel('com.orionhealth/aicore');
  
  bool _initialized = false;
  bool _useFullModel = false;
  
  // Escuchar eventos nativos
  static void setupEventListeners({
    void Function(int progress)? onDownloadProgress,
    void Function(String token)? onToken,
    void Function()? onComplete,
    void Function(String error)? onError,
  }) {
    _channel.setMethodCallHandler((call) {
      switch (call.method) {
        case 'onDownloadProgress':
          onDownloadProgress?.call(call.arguments['progress'] as int);
          break;
        case 'onToken':
          onToken?.call(call.arguments['token'] as String);
          break;
        case 'onComplete':
          onComplete?.call();
          break;
        case 'onError':
          onError?.call(call.arguments['error'] as String);
          break;
      }
    });
  }
  
  Future<bool> initialize({bool useFullModel = false}) async {
    try {
      _useFullModel = useFullModel;
      final result = await _channel.invokeMethod('initialize', {
        'useFullModel': useFullModel,
      });
      _initialized = result == true;
      return _initialized;
    } catch (e) {
      return false;
    }
  }
  
  Future<AicoreStatus> checkAvailability() async {
    try {
      final status = await _channel.invokeMethod<String>('checkAvailability');
      return AicoreStatus.values.firstWhere(
        (s) => s.name == status,
        orElse: () => AicoreStatus.unavailable,
      );
    } catch (e) {
      return AicoreStatus.unavailable;
    }
  }
  
  Future<bool> downloadModel() async {
    try {
      final result = await _channel.invokeMethod<bool>('downloadModel');
      return result ?? false;
    } catch (e) {
      return false;
    }
  }
  
  Future<String> generateContent(String prompt) async {
    try {
      final result = await _channel.invokeMethod<String>('generateContent', {
        'prompt': prompt,
      });
      return result ?? '';
    } catch (e) {
      throw Exception('Generation failed: $e');
    }
  }
  
  Future<void> generateContentStream(String prompt) async {
    await _channel.invokeMethod('generateContentStream', {
      'prompt': prompt,
    });
  }
  
  Future<bool> warmup() async {
    try {
      final result = await _channel.invokeMethod<bool>('warmup');
      return result ?? false;
    } catch (e) {
      return false;
    }
  }
  
  bool get isInitialized => _initialized;
  bool get usesFullModel => _useFullModel;
}
```

## 🔄 Integración con GemmaLlmAdapter Existente

```dart
// lib/features/local_agent/infrastructure/adapters/gemma_llm_adapter.dart

import 'package:orionhealth/core/services/aicore_service.dart';

class GemmaLlmAdapter {
  final AicoreService _aicoreService;
  
  GemmaLlmAdapter({AicoreService? aicoreService})
      : _aicoreService = aicoreService ?? AicoreService();
  
  Future<void> initialize() async {
    // Por defecto E2B para velocidad
    await _aicoreService.initialize(useFullModel: false);
    
    // Verificar y descargar si es necesario
    final status = await _aicoreService.checkAvailability();
    if (status == AicoreStatus.downloadable) {
      await _aicoreService.downloadModel();
    }
    
    // Warmup para primera respuesta rápida
    await _aicoreService.warmup();
  }
  
  Future<String> generateResponse(String prompt) async {
    return await _aicoreService.generateContent(prompt);
  }
  
  Stream<String> generateResponseStream(String prompt) {
    // Implementar stream con listeners
    final controller = StreamController<String>();
    
    AicoreService.setupEventListeners(
      onToken: (token) => controller.add(token),
      onComplete: () => controller.close(),
      onError: (error) => controller.addError(error),
    );
    
    _aicoreService.generateContentStream(prompt);
    return controller.stream;
  }
  
  Future<void> dispose() async {
    // Cleanup si es necesario
  }
}
```

## 📋 Pasos de Implementación

### Fase 1: Android Native (Kotlin)
1. [ ] Crear `GemmaNativeEngine.kt` con ML Kit Prompt API
2. [ ] Crear `AicorePlugin.kt` con MethodChannel
3. [ ] Agregar dependencias en `build.gradle.kts`
4. [ ] Declarar `<uses-library>` en `AndroidManifest.xml`
5. [ ] Testear con app Android standalone (sin Flutter)

### Fase 2: Flutter Integration
1. [ ] Crear `aicore_service.dart` (Dart side)
2. [ ] Registrar plugin en `MainActivity.kt`
3. [ ] Actualizar `GemmaLlmAdapter` para usar `AicoreService`
4. [ ] Implementar fallback: Gemini cloud si AICore no disponible

### Fase 3: Testing & Optimization
1. [ ] Test streaming en dispositivo real
2. [ ] Medir latency E2B vs E4B
3. [ ] Optimizar cold start con warmup()
4. [ ] Probar conHealth data context

## 🔍 Debugging

```bash
# Ver logs AICore
adb logcat | grep -i "aicore\|gemma\|mlkit"

# Verificar AICore instalado
adb shell dumpsys package com.google.android.aicore

# Forzar reinstall AICore
adb shell cmd package install-existing com.google.android.aicore
```

## 📚 Recursos

- [ML Kit Prompt API Docs](https://developers.google.com/ml-kit/genai/prompt/android/get-started)
- [AICore Developer Preview](https://developers.google.com/ml-kit/genai/aicore-dev-preview)
- [Gemma 4 Model Card](https://ai.google.dev/gemma/docs/core/model_card_4)
- [Android Blog: Gemma 4](https://android-developers.googleblog.com/2026/04/gemma-4-new-standard-for-local-agentic-intelligence.html)

## ⚠️ Notas Importantes

1. **AICore no viene preinstalado** - usuario debe descargarlo del Play Store
2. **Error -101** = AICore no instalado o versión muy antigua
3. **CUOTA por app** - AICore limita requests por minuto
4. **Solo inglés validado** - otros idiomas pueden dar calidad reducida
5. **Tokens** - Max 4000 input, 256 output

## 🔄 Fallback Strategy

```
generateResponse(prompt)
    ↓
[AicoreService disponible?] → NO → GeminiLlmAdapter (cloud)
    ↓ YES
[Gemma E2B/E4B local]
    ↓
[Streaming response]
```

---

*Skill creado: 2026-04-16*
*Para OrionHealth - Gemma 4 100% local on Android*