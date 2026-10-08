# Patron TUI de 4 areas — texto listo para pegar

## Bloque completo (turno que cerro trabajo: commit, verify, gate verde)

```
### 1. ESTADO
- **Contexto:** <1 linea: stack y objetivo de la sesion, con viabilidad>
- **Hecho:** <2-5 vinetas; cada una con evidencia: commit, test o ruta:linea>

### 2. AVANCE
- **Progreso:** <% medido + fuente, o "no medible: <motivo>">
- **Problema mayor:** <mecanismo en 1 linea, o "Ninguno en esta sesion">

### 3. ENTREGA
- **Listo para probar:** <ruta exacta con :linea, endpoint o comando de prueba>
- **Decision del usuario:** <opcion A/B con default recomendado, o "Ninguna: siguiente paso ya definido">

### 4. RUTA
- **Todo:** <bloque cerrado -> siguiente bloque | bloque abierto -> 3 micro-pasos>
- **Opciones:**
  1. <orden> - <que hace> - `<comando real, ejecutable tal cual>`
  2. ...
  3. ...
```

## Bloque compacto (turno informativo: lectura, duda, estado sin cambios)

```
### 1. ESTADO
- **Contexto:** <1 linea>
- **Hecho:** <1 linea: nada escrito en este turno | 1 cambio con su ruta>

### 2. AVANCE
- **Progreso:** <% con fuente | "no medible: sin PLAN">

### 3. ENTREGA
- **Listo para probar:** <ruta:línea | "nada nuevo">

### 4. RUTA
- **Todo:** <1 linea>
- **Opciones:**
  1. <orden> - <que hace> - `<comando>`
```

## Ejemplos de vinetas que NO valen (contraste)

| Mal | Bien |
|---|---|
| Progreso estimado: 80% | 62% (features.json 31/50) |
| El modulo de riesgo ya esta listo | `src/risk.rs:142` — gate de vol_atr, 12 tests verdes |
| Decision: elegir entre a y b | Ninguna: el siguiente paso ya esta definido |
| Ejecutar los tests | `cargo test --lib` (verde, 214 passed) |
| Se resolvio el problema de concurrencia | Ninguno en esta sesion |
| Opcion 1: correr tests con cargo | Opcion 1 - correr la suite - `scripts/ci-local.sh lite` |

## Como salir del modo

Frase que anula el modo: "informe normal", "ya no TUI", "veredicto normal".
En cuanto se oye, `informe-final` vuelve a mandar. El modo no persiste entre
sesiones: solo vive mientras el usuario lo pide.