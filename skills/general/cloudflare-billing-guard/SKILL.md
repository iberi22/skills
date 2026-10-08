---
name: cloudflare-billing-guard
title: Cloudflare Billing Guard & Anti-Runaway Protection
description: Reglas y salvaguardas para prevenir bucles infinitos, explosiones de facturación y saturación de recursos en Cloudflare Workers, Durable Objects y KV. Provee patrones de Circuit Breaker para alarmas, límites mínimos de reprogramación (>= 60s) y checks de auditoría.
tags:
  - cloudflare
  - durable-objects
  - billing
  - security
  - devops
category: security
---

# Cloudflare Billing Guard & Anti-Runaway Protection

> **MANDATORIO:** Un bucle infinito en alarmas de Durable Objects o escrituras en KV puede generar facturas de miles de dólares en pocas horas ($0.20 / 1M operaciones SQLite, invocaciones masivas).
> Todo agente que cree o modifique Durable Objects (`setAlarm`, `alarm()`), crons o Workers en bucle **DEBE cumplir estas reglas**.

---

## 1. Reglas Cardinales para Durable Object Alarms

1. **Delta Mínimo de Reprogramación ($\ge 60$s):**
   - **PROHIBIDO:** `setAlarm(Date.now() + 1)` o reprogramaciones inmediatas.
   - **OBLIGATORIO:** Todo reintento o siguiente tarea debe tener al menos 60 segundos de separación:
     ```typescript
     const MIN_ALARM_INTERVAL_MS = 60_000;
     const targetTime = Math.max(nextDueTime, Date.now() + MIN_ALARM_INTERVAL_MS);
     await this.ctx.storage.setAlarm(targetTime);
     ```

2. **Circuit Breaker Obligatorio (Presupuesto por Hora):**
   - Cada Durable Object debe registrar el número de ejecuciones de alarma en la última hora.
   - Si se superan 60 ejecuciones en una ventana de 60 minutos, la alarma se destruye (`deleteAlarm()`) y se emite un error crítico o webhook de alerta.

3. **Manejo Idempotente y Fail-Closed en `alarm()`:**
   - Cloudflare reintenta automáticamente las alarmas que lanzan excepciones no capturadas.
   - **Regla:** El bloque principal del handler `alarm()` debe capturar errores y aplicar **Backoff Exponencial** en lugar de reintentar en bucle cerrado:
     ```typescript
     async alarm(): Promise<void> {
       try {
         await this.enforceCircuitBreaker();
         await this.processScheduledWork();
       } catch (err) {
         console.error("Error crítico en alarma:", err);
         await this.applyExponentialBackoff();
       }
     }
     ```

---

## 2. Implementación Canónica del Guard

```typescript
import { DurableObject } from "cloudflare:workers";

export class SafeDurableObject extends DurableObject {
  private static readonly MAX_HOURLY_ALARMS = 60;
  private static readonly MIN_INTERVAL_MS = 60_000; // 60 segundos

  private async enforceCircuitBreaker(): Promise<void> {
    const now = Date.now();
    const hourAgo = now - 3600_000;

    // Tabla SQLite interna para tracking de ejecuciones
    this.ctx.storage.sql.exec(`
      CREATE TABLE IF NOT EXISTS _alarm_audit (
        executed_at INTEGER PRIMARY KEY
      )
    `);

    // Limpiar ejecuciones viejas
    this.ctx.storage.sql.exec("DELETE FROM _alarm_audit WHERE executed_at < ?", hourAgo);

    // Contar ejecuciones en la última hora
    const count = this.ctx.storage.sql.exec<{ count: number }>(
      "SELECT count(*) as count FROM _alarm_audit"
    ).one()?.count ?? 0;

    if (count >= SafeDurableObject.MAX_HOURLY_ALARMS) {
      await this.ctx.storage.deleteAlarm();
      throw new Error(`[BILLING GUARD] Circuit breaker disparado: >${SafeDurableObject.MAX_HOURLY_ALARMS} alarmas/hora. Alarma cancelada.`);
    }

    this.ctx.storage.sql.exec("INSERT INTO _alarm_audit (executed_at) VALUES (?)", now);
  }

  protected async safeSetAlarm(targetTimestamp: number): Promise<void> {
    const minSafeTime = Date.now() + SafeDurableObject.MIN_INTERVAL_MS;
    const finalTimestamp = Math.max(targetTimestamp, minSafeTime);
    await this.ctx.storage.setAlarm(finalTimestamp);
  }
}
```

---

## 3. Checklist Pre-Despliegue

- [ ] ¿Hay algún `setAlarm` con valores dinámicos que puedan ser $\le 0$ o menores a 60,000 ms?
- [ ] ¿El bloque `alarm()` tiene `try/catch` con backoff exponencial para evitar reintentos continuos de Cloudflare?
- [ ] ¿Se limpian las alarmas no necesarias con `deleteAlarm()` al terminar las tareas programadas?
- [ ] ¿Se cuenta con alertas configuradas en Cloudflare Dashboard para facturación y picos de invocaciones?
