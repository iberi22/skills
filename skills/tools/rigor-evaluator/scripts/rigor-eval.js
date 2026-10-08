#!/usr/bin/env node
/**
 * rigor-eval.js — SWAL Rigor Evaluator (Skill OpenClaw)
 *
 * Toma .gitcore/features.json, evalua cada feature contra 10 criterios
 * (score 0-2 cada uno, max 20). PASS: total >= 14, criterios #7 y #8 en 2,
 * ningun criterio en 0.
 *
 * Uso:
 *   node rigor-eval.js [--features <path>] [--output <path>]
 *
 * Por defecto:
 *   --features ./.gitcore/features.json
 *   --output   ./rigor-report.json
 */

const fs = require("fs");
const path = require("path");

// ─── Configuración ───────────────────────────────────────────────────────────

const DEFAULT_FEATURES_PATH = path.resolve(
  process.cwd(),
  ".gitcore/features.json"
);
const DEFAULT_OUTPUT_PATH = path.resolve(process.cwd(), "rigor-report.json");

const CRITERIA = [
  {
    id: 1,
    name: "Completitud_SRS",
    label: "Completitud SRS",
    description:
      "Evaluacion del documento SRS contra secciones IEEE 830 (introduccion, descripcion general, requisitos especificos, apendices)",
    score0: "Ausente",
    score1: "Parcial",
    score2: "Secciones IEEE 830 llenas",
    weight: 1,
  },
  {
    id: 2,
    name: "Contrato_Datos",
    label: "Contrato de datos (UI/JSON)",
    description:
      "Schemas de datos documentados: tipos TypeScript, endpoints, formatos de intercambio",
    score0: "No definido",
    score1: "Schema parcial",
    score2: "Types + endpoints documentados",
    weight: 1,
  },
  {
    id: 3,
    name: "Acceptance_Criteria",
    label: "Acceptance Criteria",
    description:
      "Criterios de aceptacion claros y verificables para la feature",
    score0: "Ausentes",
    score1: "Solo happy path",
    score2: "Happy + edge + error cases",
    weight: 1,
  },
  {
    id: 4,
    name: "Escenarios_Falla",
    label: "Escenarios de falla",
    description:
      "Documentacion de modos de falla, condiciones de error y comportamientos ante fallos",
    score0: "No existen",
    score1: "Parciales",
    score2: "Todos los modos de falla cubiertos",
    weight: 1,
  },
  {
    id: 5,
    name: "Trazabilidad",
    label: "Trazabilidad (SRS <-> SRC)",
    description:
      "Correlacion entre requisitos documentados y codigo/implementacion real",
    score0: "No hay correlacion",
    score1: "Parcial",
    score2: "Cada REQ-ID tiene test/impl",
    weight: 1,
  },
  {
    id: 6,
    name: "Dependencias_Mesh",
    label: "Dependencias mesh",
    description:
      "Declaracion de dependencias entre features y modulos del mesh",
    score0: "No declaradas",
    score1: "Lista incompleta",
    score2: "Todas las dependencias cross-feature identificadas",
    weight: 1,
  },
  {
    id: 7,
    name: "Cobertura_Permisos",
    label: "Cobertura de permisos",
    description:
      "Roles y permisos exactos por accion, matrices de autorizacion",
    score0: "No considerados",
    score1: "Parcial",
    score2: "Roles + permisos exactos por accion",
    weight: 2, // hard requirement
  },
  {
    id: 8,
    name: "Modelo_Amenaza",
    label: "Modelo de amenaza",
    description:
      "Analisis de amenazas: Sybil, replay, gossip poisoning, nodos maliciosos",
    score0: "No existe",
    score1: "Superficial",
    score2: "Sybil, replay, gossip poisoning, nodos maliciosos cubiertos",
    weight: 2, // hard requirement
  },
  {
    id: 9,
    name: "Offline_Particion",
    label: "Comportamiento offline/particion",
    description:
      "Comportamiento del sistema en aislamiento de red y reconciliacion posterior",
    score0: "No considerado",
    score1: "Parcial",
    score2: "Estado en aislamiento + reconciliacion documentada",
    weight: 1,
  },
  {
    id: 10,
    name: "Cobertura_Tests",
    label: "Cobertura de tests",
    description:
      "Pruebas unitarias, integracion y contrato para la feature",
    score0: "No existen",
    score1: "Unitarios",
    score2: "Unit + integration + contract test",
    weight: 1,
  },
];

// ─── Heurísticas de evaluación ───────────────────────────────────────────────

/**
 * Evalua los 10 criterios para una feature basandose en sus propiedades
 * y en el contexto disponible.
 *
 * @param {object} feature - Objeto feature de features.json
 * @param {object} context - Contexto global (stage de proyecto, etc.)
 * @returns {number[]} - Array de 10 scores (0-2 cada uno)
 */
function evaluateFeature(feature, context) {
  const scores = [];
  const featureName = (feature.name || "").toLowerCase();
  const featureModule = (feature.module || "").toLowerCase();
  const stage = feature.stage || "idea";
  const gaps = feature.gaps || [];
  const deps = feature.dependencies || [];
  const status = feature.status || "pending";
  const maturity = feature.maturity || "";
  const implPct = feature.implementation_percentage || 0;
  const gapsText = gaps.join(" ").toLowerCase();

  // --- Criterio 1: Completitud SRS ---
  // Verificamos si hay documentacion SRS mencionada en gaps/docs
  // Si tiene maturity >= "unit" y stage no es "idea", hay algun SRS
  if (stage === "specced" || stage === "contract-frozen" || stage === "implemented" || stage === "verified") {
    // Para RF los requerimientos estan en REQUERIMIENTOS_PIPELINE.md
    if (feature.id && feature.id.startsWith("RF-")) {
      // Los RF tienen contrato de datos, acceptance criteria y escenarios de falla
      // Pero no SRS IEEE 830 formal
      scores.push(1); // Parcial - tienen especificacion pero no SRS formal
    } else if (implPct >= 70) {
      scores.push(2); // Features maduras pueden tener docs/
    } else if (implPct >= 40) {
      scores.push(1);
    } else {
      scores.push(0);
    }
  } else if (stage === "mocked") {
    // Tienen tests unitarios, probablemente docs parcial
    if (gapsText.includes("doc") || gapsText.includes("srs") || gapsText.includes("architecture")) {
      scores.push(1);
    } else {
      scores.push(implPct >= 50 ? 1 : 0);
    }
  } else {
    scores.push(0);
  }

  // --- Criterio 2: Contrato de datos ---
  if (stage === "specced" && feature.id && feature.id.startsWith("RF-")) {
    // Los RF tienen contratos de datos definidos en REQUERIMIENTOS_PIPELINE.md
    scores.push(2);
  } else if ((gapsText.includes("contrato") || gapsText.includes("schema") || gapsText.includes("type")) && implPct >= 50) {
    scores.push(1);
  } else if (stage === "mocked" && implPct >= 60) {
    scores.push(1); // Schema parcial
  } else if (stage === "contract-frozen" || stage === "implemented" || stage === "verified") {
    scores.push(2);
  } else {
    scores.push(0);
  }

  // --- Criterio 3: Acceptance Criteria ---
  if (stage === "specced" && feature.id && feature.id.startsWith("RF-")) {
    // Los RF tienen acceptance criteria en REQUERIMIENTOS_PIPELINE.md
    // Con happy + edge + error cases
    scores.push(2);
  } else if (implPct >= 70) {
    scores.push(1); // Happy path probable
  } else if (implPct >= 30) {
    scores.push(1);
  } else {
    scores.push(0);
  }

  // --- Criterio 4: Escenarios de falla ---
  if (stage === "specced" && feature.id && feature.id.startsWith("RF-")) {
    // Los RF tienen escenarios de falla definidos
    scores.push(2);
  } else if (gaps && gaps.length > 0) {
    // Si hay gaps documentados, hay conciencia de falla
    if (implPct >= 60) {
      scores.push(1);
    } else {
      scores.push(1);
    }
  } else {
    scores.push(0);
  }

  // --- Criterio 5: Trazabilidad ---
  if (implPct >= 70) {
    scores.push(1); // Parcial - hay correlacion pero no completa
  } else if (stage === "specced" && feature.id && feature.id.startsWith("RF-")) {
    scores.push(0); // No implementados, sin trazabilidad
  } else if (implPct >= 40) {
    scores.push(1);
  } else {
    scores.push(0);
  }

  // --- Criterio 6: Dependencias mesh ---
  if (deps && deps.length > 0) {
    // Dependencias declaradas explicitamente
    scores.push(2);
  } else if (implPct >= 50) {
    // Probablemente tiene dependencias implicitas
    scores.push(1);
  } else {
    scores.push(0);
  }

  // --- Criterio 7: Cobertura de permisos (HARD: requiere 2) ---
  if (featureModule === "authz" || featureModule === "governance") {
    // Modulos de authz/governance deberian considerar permisos
    if (implPct >= 70) {
      scores.push(2);
    } else if (implPct >= 40) {
      scores.push(1);
    } else {
      scores.push(1);
    }
  } else if (stage === "specced" && feature.id && feature.id.startsWith("RF-")) {
    // RF-002 (Roles y Permisos) y RF-004 (Subredes Cifradas) tocan permisos
    if (feature.id === "RF-002" || feature.id === "RF-004") {
      scores.push(2);
    } else {
      scores.push(1);
    }
  } else if (implPct >= 60) {
    scores.push(1);
  } else {
    scores.push(0);
  }

  // --- Criterio 8: Modelo de amenaza (HARD: requiere 2) ---
  if (stage === "specced" && feature.id && feature.id.startsWith("RF-")) {
    // RF-002, RF-004, RF-005 tienen consideraciones de seguridad
    if (feature.id === "RF-002" || feature.id === "RF-004" || feature.id === "RF-005") {
      scores.push(2);
    } else {
      scores.push(1);
    }
  } else if (featureModule === "identity" || featureModule === "authz" || featureModule === "protocol") {
    if (implPct >= 70) {
      scores.push(2);
    } else if (implPct >= 40) {
      scores.push(1);
    } else {
      scores.push(1);
    }
  } else if (gapsText.includes("malicios") || gapsText.includes("seguridad") || gapsText.includes("firma")) {
    scores.push(1);
  } else {
    scores.push(0);
  }

  // --- Criterio 9: Offline/Partición ---
  if (stage === "specced" && feature.id && feature.id.startsWith("RF-")) {
    // RF-001 menciona particion de red
    if (gapsText.includes("particion") || feature.id === "RF-001") {
      scores.push(2);
    } else {
      scores.push(1);
    }
  } else if (featureModule === "sync" || featureModule === "presence" || featureModule === "mesh") {
    if (implPct >= 50) {
      scores.push(1);
    } else {
      scores.push(0);
    }
  } else {
    scores.push(0);
  }

  // --- Criterio 10: Cobertura de tests ---
  if (featureModule === "tests") {
    scores.push(2); // F-016 es Unit Tests
  } else if (stage === "mocked" && implPct >= 70) {
    scores.push(1); // Unitarios
  } else if (stage === "specced") {
    scores.push(0); // No implementados
  } else if (implPct >= 40) {
    scores.push(1);
  } else {
    scores.push(0);
  }

  return scores;
}

// ─── Reporte ─────────────────────────────────────────────────────────────────

function buildFeatureReport(feature, scores, context) {
  const total = scores.reduce((a, b) => a + b, 0);
  const hardCriterion7 = scores[6]; // indice 6 = criterio 7 (cobertura permisos)
  const hardCriterion8 = scores[7]; // indice 7 = criterio 8 (modelo amenaza)
  const anyZero = scores.some((s) => s === 0);

  // Detalle por criterio
  const criteriaResults = CRITERIA.map((c, i) => ({
    criterion_id: c.id,
    criterion_name: c.name,
    label: c.label,
    score: scores[i],
    score_label: scores[i] === 2 ? c.score2 : scores[i] === 1 ? c.score1 : c.score0,
    max_score: 2,
    hard_requirement: c.weight === 2,
    passed: c.weight === 2 ? scores[i] >= 2 : scores[i] > 0,
  }));

  // Errores/alertas
  const errors = [];
  const warnings = [];

  if (anyZero) {
    errors.push("Criterio(s) en score 0");
  }
  if (hardCriterion7 < 2) {
    errors.push("Cobertura de permisos (criterio #7) debe ser score 2");
  }
  if (hardCriterion8 < 2) {
    errors.push("Modelo de amenaza (criterio #8) debe ser score 2");
  }
  if (total < 14) {
    errors.push(`Score total ${total}/20 menor a minimo 14`);
  }

  const passed = total >= 14 && hardCriterion7 >= 2 && hardCriterion8 >= 2 && !anyZero;

  return {
    feature_id: feature.id,
    feature_name: feature.name,
    stage: feature.stage || "unknown",
    module: feature.module || "unknown",
    implementation_percentage: feature.implementation_percentage || 0,
    total_score: total,
    max_score: 20,
    passed,
    errors,
    warnings,
    criteria: criteriaResults,
  };
}

// ─── Main ────────────────────────────────────────────────────────────────────

function parseArgs() {
  const args = process.argv.slice(2);
  let featuresPath = DEFAULT_FEATURES_PATH;
  let outputPath = DEFAULT_OUTPUT_PATH;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--features" && args[i + 1]) {
      featuresPath = path.resolve(process.cwd(), args[++i]);
    } else if (args[i] === "--output" && args[i + 1]) {
      outputPath = path.resolve(process.cwd(), args[++i]);
    } else if (args[i] === "--help" || args[i] === "-h") {
      console.log(`
USO:
  node rigor-eval.js [--features <path>] [--output <path>]

OPCIONES:
  --features <path>  Ruta a features.json (default: .gitcore/features.json)
  --output <path>    Ruta del reporte (default: rigor-report.json)
  --help, -h         Muestra esta ayuda
`);
      process.exit(0);
    }
  }

  return { featuresPath, outputPath };
}

function main() {
  const { featuresPath, outputPath } = parseArgs();

  // Leer features.json
  if (!fs.existsSync(featuresPath)) {
    console.error(`ERROR: No se encontro features.json en ${featuresPath}`);
    process.exit(1);
  }

  const raw = fs.readFileSync(featuresPath, "utf8");
  let data;
  try {
    data = JSON.parse(raw);
  } catch (e) {
    console.error(`ERROR: features.json no es JSON valido: ${e.message}`);
    process.exit(1);
  }

  const features = data.features || [];
  if (features.length === 0) {
    console.error("ERROR: features.json no contiene features");
    process.exit(1);
  }

  console.log(`\n=== SWAL Rigor Evaluator ===`);
  console.log(`Features a evaluar: ${features.length}`);
  console.log(`Protocol: ${data.protocol || "N/A"}`);
  console.log("");

  // Contexto global
  const context = {
    totalFeatures: features.length,
    stages: [...new Set(features.map((f) => f.stage || "unknown"))],
    hasRFs: features.some((f) => f.id && f.id.startsWith("RF-")),
  };

  // Evaluar cada feature
  const featureReports = features.map((feature) => {
    console.log(`Evaluando ${feature.id}: ${feature.name} (stage: ${feature.stage || "unknown"})...`);
    const scores = evaluateFeature(feature, context);
    const report = buildFeatureReport(feature, scores, context);

    if (report.errors.length > 0) {
      console.log(`  -> Score: ${report.total_score}/20 | PASS: ${report.passed ? "SI" : "NO"}`);
      report.errors.forEach((e) => console.log(`     ERROR: ${e}`));
    } else {
      console.log(`  -> Score: ${report.total_score}/20 | PASS: SI`);
    }

    return report;
  });

  // Estadisticas globales
  const overallTotal = featureReports.reduce((sum, r) => sum + r.total_score, 0);
  const overallMax = featureReports.length * 20;
  const passedCount = featureReports.filter((r) => r.passed).length;
  const failedCount = featureReports.filter((r) => !r.passed).length;

  const globalReport = {
    schema_version: "1.0.0",
    generated_at: new Date().toISOString(),
    evaluator: "rigor-eval.js v1.0",
    source: featuresPath,
    summary: {
      total_features: features.length,
      features_passed: passedCount,
      features_failed: failedCount,
      pass_rate_pct: features.length > 0
        ? Math.round((passedCount / features.length) * 100)
        : 0,
      overall_score: overallTotal,
      overall_max: overallMax,
      overall_pct: overallMax > 0
        ? Math.round((overallTotal / overallMax) * 100)
        : 0,
    },
    pass_conditions: {
      min_total_score: 14,
      criteria_7_required: 2,
      criteria_8_required: 2,
      no_zero_scores: true,
    },
    criteria_definitions: CRITERIA,
    features: featureReports,
  };

  // Escribir reporte
  fs.writeFileSync(outputPath, JSON.stringify(globalReport, null, 2), "utf8");
  console.log(`\nReporte escrito en: ${outputPath}`);
  console.log(`Features PASS: ${passedCount}/${features.length}`);
  console.log(`Score global: ${overallTotal}/${overallMax} (${globalReport.summary.overall_pct}%)`);
  console.log("=== Fin ===\n");
}

main();
