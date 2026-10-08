---
name: codificacion-ciclos
description: Flujo SWAL por ciclos — leer features.json, implementar, verificar con 3 fuentes y actualizar el ledger. Usar al ejecutar o cerrar un ciclo de desarrollo.
---

# Codificación por Ciclos — SWAL Standard v2.0

**Basado en:** Anthropic "Effective Harnesses for Long-Running Agents" + metodología SWAL.

---

## Principio Fundamental

> **features.json es el SINGLE SOURCE OF TRUTH del proyecto.**
> Todo agente debe leerlo al iniciar y actualizarlo al finalizar CADA ciclo.
> El % en features.json refleja MADUREZ REAL (código + tests + wiring), no solo "código existe".

---

## Métricas de Madurez de Feature

Cada feature tiene 3 dimensiones de madurez:

| Dimensión | Peso | Qué mide |
|-----------|------|----------|
| **Code** | 40% | ¿El código existe y compila? |
| **Tests** | 30% | ¿Tiene tests unitarios + integración? |
| **Wiring** | 30% | ¿Está conectado al router/API/frontend activo? |

**Score real = (code × 0.4) + (tests × 0.3) + (wired × 0.3)**

---

## Pipeline de Ciclos

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│  INICIO DE SESIÓN                                        │
│  ├─ Leer features.json                                    │
│  ├─ Buscar en xavier /memory/search                       │
│  └─ Determinar % real de implementación                   │
│                                                          │
│  DEFINICIÓN DEL CICLO                                     │
│  ├─ Escanear codebase con tools                           │
│  ├─ Identificar features con score < 70%                  │
│  ├─ Identificar módulos NO cableados al router            │
│  ├─ Crear issues en GitHub (label jules si aplica)        │
│  └─ Priorizar: wiring > tests > features nuevas           │
│                                                          │
│  IMPLEMENTACIÓN                                           │
│  ├─ Feature por feature, incremental                      │
│  ├─ 1 feature = 1 commit atómico en main                  │
│  ├─ NO branches separados (excepto PRs de Jules)          │
│  └─ SIEMPRE: cargo check después de cada cambio           │
│                                                          │
│  CIERRE DEL CICLO                                         │
│  ├─ cargo check → 0 errors, 0 warnings                    │
│  ├─ Actualizar features.json con % reales                 │
│  ├─ SAME COMMIT: features.json + código                   │
│  ├─ git push origin main                                  │
│  ├─ Cerrar issues completados                             │
│  └─ Cerrar PRs de Jules ya mergeados                      │
│                                                          │
│  VERIFICACIÓN 3 FUENTES (OBLIGATORIA)                     │
│  ├─ F1: features.json → % y métricas                     │
│  ├─ F2: gh issue list / gh pr list → 0 abiertos          │
│  └─ F3: cargo check → build status real                  │
│                                                          │
│  REPORTE FINAL                                            │
│  ├─ 📊 Tabla de estado con % reales                       │
│  ├─ 📋 Features que necesitan atención (score < 70%)      │
│  └─ 🎯 Propuesta de siguiente ciclo                       │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Reglas NO NEGOCIABLES

### 1. features.json SIEMPRE actualizado en el MISMO commit

```bash
git add src/... features.json
git commit -m "feat/fix/docs: descripción"
git push origin main
```

**NUNCA commits separados de "docs: update features.json".** El estado y el código van juntos.

### 2. SIEMPRE escanear el codebase al finalizar

Antes de reportar "terminado", ejecutar:
- `cargo check` → build status
- `gh issue list` → issues abiertos
- `gh pr list` → PRs abiertos
- Escaneo de archivos vs features.json → cobertura real

### 3. SIEMPRE proponer siguiente ciclo

Al terminar, mencionar:
- Features con score < 70% que necesitan wiring/tests
- Módulos no cableados al router
- Vulnerabilidades pendientes
- Deuda técnica documentada

### 4. SIEMPRE verificar 3 fuentes independientes

NUNCA reportar basado en una sola fuente. Validar:
1. `features.json` → % declarado
2. `cargo check` → build status real
3. `gh issue list + gh pr list` → issues/PRs realmente cerrados

### 5. 1 feature = 1 commit (cuando sea práctico)

Commits atómicos y descriptivos:
```
feat: F40 MercadoPublico Chile — OCDS scraper (300+ LOC, 4 tests)
fix: clean 87 warnings → 0
fix: migrate jsonwebtoken 9→10
```

---

## Formato de features.json v8+

```json
{
  "version": "8.0",
  "updated": "ISO-8601",
  "status": "ciclo_N_completed|in_progress",
  "implementation_maturity": {
    "code_exists": "100%",
    "tests_coverage": "61%",
    "router_wiring": "65%",
    "overall_score": "82%"
  },
  "total_features": 40,
  "features": [
    {
      "id": "F01",
      "name": "SECOP ingestion",
      "code": 100,
      "tests": 90,
      "wired": 100,
      "score": 97
    }
  ],
  "not_wired_modules": ["payments", "analytics", "mercadopublico"],
  "tech_debt": [],
  "next_cycle_recommendations": []
}
```

---

## Integración con Jules

```
1. Crear issue → label "jules"
2. Jules procesa (3-30 min)
3. Revisar branch de Jules
4. Merge manual → main (NO merge directo si conflictos)
5. Verificar cargo check
6. Cerrar issue + PR de Jules
7. Actualizar features.json
8. Commit atómico + push
```

---

## Ejemplo de Reporte Final de Ciclo

```
📊 VERIFICACIÓN FINAL — 3 fuentes
├── F1 features.json:    40/40 code, 82% maturity
├── F2 gh issues:        0 abiertos
├── F3 cargo check:      0 errors, 0 warnings
└── ✅ Las 3 fuentes coinciden

📋 PRÓXIMO CICLO RECOMENDADO
├── P1: Wire payments al router (score 63% → 93%)
├── P2: Wire analytics al router (score 60% → 90%)
├── P3: Wire mercadopublico al router (score 70% → 100%)
└── P4: Resolver 5 vulns dependabot
```

---

*Versión 2.0 — Actualizado 2026-07-13 con investigación Anthropic harness pattern + escaneo de codebase real.*
*Este archivo debe actualizarse al menos semanalmente con mejoras del patrón.*
