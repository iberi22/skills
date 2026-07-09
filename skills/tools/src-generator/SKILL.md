---
id: src-generator
name: src-generator
category: tools
tags:
  - src-generator
goals:
  - "**src-generator** - Generador de Documentos de Requisitos de Software (SRC)"
authors:
  - Brahyan Belalcazar
---

# SKILL.md - SRC Generator

## Nombre
**src-generator** - Generador de Documentos de Requisitos de Software (SRC)

## Descripción
Este skill recolecta información del proyecto y genera un documento SRC (Software Requirements Specification) profesional en formato PDF, siguiendo estándares IEEE 830.

## Uso
```
/src-generate [nombre-del-proyecto]
```

## Flujo de Trabajo

### 1. Recolección de Datos (Preguntas)

El skill debe preguntar/recolectar:

**Sección 1: Información General**
- Nombre del proyecto
- Cliente/Organización
- Versión del documento
- Fecha de elaboración
- Autor(es)

**Sección 2: Introducción**
- Propósito del documento
- Alcance del producto
- Definiciones importantes
- Referencias externas

**Sección 3: Descripción General**
- Perspectiva del producto (nuevo, mejora, integración)
- Funciones principales del producto
- Clases de usuarios
- Ambiente de operación
- Restricciones de diseño

**Sección 4: Requisitos Funcionales**
- Módulos del sistema
- Casos de uso principales
- Flujos de datos
- Reglas de negocio

**Sección 5: Requisitos No Funcionales**
- Rendimiento
- Seguridad
- Disponibilidad
- Escalabilidad
- Compatibilidad
- Mantenibilidad

**Sección 6: Interfaces**
- Interfaces de usuario
- Interfaces de hardware
- Interfaces de software/API
- Interfaces de comunicación

**Sección 7: Requisitos de Base de Datos**
- Entidades principales
- Relaciones
- Volumen de datos esperado

### 2. Generación del Documento

El skill genera un PDF estructurado con:
- Portada profesional
- Tabla de contenidos
- Numeración de secciones
- Tablas y figuras donde corresponda
- Historial de versiones

### 3. Formato de Salida

- **PDF**: Documento profesional listo para entregar
- **Markdown**: Borrador editable

## Archivos del Skill

- `SKILL.md` - Definición principal
- `src-template.md` - Plantilla de preguntas
- `src-structure.md` - Estructura IEEE 830
- `generate-src.py` - Script de generación PDF

## Estándar IEEE 830

Este skill sigue la norma IEEE 830 para especificaciones de requisitos de software, asegurando:
- Completitud
- Consistencia
- Verificabilidad
- Modificabilidad
- Trazabilidad
