# Unidad IV — Data Warehouse y Modelado Dimensional
## Objetivos de la Unidad

> **Asignatura:** Ingeniería de Datos  
> **Docente:** Ing. Sergio Orozco  
> **Clases que componen esta unidad:** Clase 09 y Clase 10

---

## ¿De qué trata esta unidad?

Llegamos al destino final de todos los pipelines ETL que construimos en las unidades anteriores: el **Data Warehouse**. Esta unidad responde las preguntas más importantes de la arquitectura analítica:

- ¿Por qué los datos analíticos no pueden vivir en el mismo sistema que los transaccionales?
- ¿Cómo se diseña una base de datos para que sea rápida en consultas complejas sobre millones de registros?
- ¿Cómo manejamos los datos que cambian con el tiempo sin perder la historia?

Esta unidad es, probablemente, la más relevante en términos de diseño arquitectónico. Un Data Warehouse bien diseñado es la diferencia entre un equipo de BI que puede responder preguntas en segundos y uno que tarda horas en sacar un reporte.

---

## Objetivos de Aprendizaje

Al finalizar esta unidad, el alumno será capaz de:

- ✅ Explicar qué es un **Data Warehouse**, para qué sirve y qué problema vino a resolver.
- ✅ Describir las **4 características de la definición de Inmon** (orientado a temas, integrado, no volátil, variante en el tiempo).
- ✅ Diferenciar con precisión los sistemas **OLTP** y **OLAP** en diseño, uso y optimización.
- ✅ Comparar las arquitecturas **Inmon (top-down)** y **Kimball (bottom-up)**.
- ✅ Entender qué es un **Data Mart** y su relación con el DWH.
- ✅ Conocer las principales **plataformas cloud** de DWH (Snowflake, BigQuery, Redshift).
- ✅ Comprender el **modelado dimensional** como metodología de diseño para DWH.
- ✅ Diseñar una **tabla de hechos** con su granularidad y tipos de métricas.
- ✅ Diseñar **tablas de dimensiones** con atributos, jerarquías y claves sustitutas.
- ✅ Construir un **esquema estrella** completo para un dominio de negocio.
- ✅ Aplicar las tres estrategias de **Slowly Changing Dimensions (SCD)** para manejar cambios históricos.

---

## Estructura de la Unidad

```
Unidad IV
├── Clase 09 — Introducción al Data Warehouse
│   ├── El problema que motivó el DWH
│   ├── Definición de Bill Inmon (4 características)
│   ├── Evolución histórica: on-premise → cloud → lakehouse
│   ├── OLTP vs. OLAP: el contraste fundamental
│   ├── Inmon (top-down) vs. Kimball (bottom-up)
│   ├── Data Mart: el subconjunto temático
│   └── Plataformas cloud: Redshift, BigQuery, Snowflake
│
└── Clase 10 — Modelado Dimensional y SCD
    ├── ¿Qué es el modelado dimensional?
    ├── Tablas de Hechos: métricas, granularidad y tipos
    ├── Tablas de Dimensiones: atributos, jerarquías, surrogate key
    ├── Esquema Estrella vs. Copo de Nieve
    ├── Slowly Changing Dimensions (SCD)
    │   ├── SCD Tipo 1 — Sobrescribir
    │   ├── SCD Tipo 2 — Historial completo
    │   └── SCD Tipo 3 — Valor anterior
    └── Implementación con SQL y Python

Módulo de profundización docente (base SQL Server WideWorldImporters)
├── 11 - Kimball Fase 01 - Planificación y Requerimientos
├── 12 - Kimball Fase 02 - Modelado Dimensional
├── 13 - Kimball Fase 03 - Diseño Físico
├── 14 - Kimball Fase 04 - Diseño ETL
├── 15 - Kimball Fase 05 - BI y Despliegue
├── 16 - Topologías de Data Warehouse
├── 17 - Guía de Tablas Dimensionales
└── 18 - Guía de Tablas de Hechos
```

---

## Aspectos Relevantes de la Unidad

### 🔑 Conceptos Clave

| Concepto | Por qué importa |
|---|---|
| **Las 4 características del DWH** | Son el "contrato" que diferencia un DWH de cualquier otra BD |
| **OLTP vs. OLAP** | La razón de existir del DWH: sistemas separados para operación y análisis |
| **Granularidad** | La decisión de diseño más crítica de toda la tabla de hechos |
| **Surrogate Key** | Permite que el DWH sea independiente de los sistemas fuente |
| **SCD Tipo 2** | La estrategia más poderosa: historial completo de cambios en dimensiones |
| **Esquema Estrella** | El estándar de facto para modelos dimensionales en producción |

### ⚠️ Puntos que suelen generar confusión

1. **"El DWH es solo una copia de la base de datos operativa"** — No. Es una reinterpretación orientada al análisis, con transformaciones, integraciones y un modelo completamente diferente.
2. **"Cuanto más normalizado, mejor"** — En OLAP, la desnormalización es correcta e intencional. La normalización es para OLTP.
3. **"La granularidad más agregada es más eficiente"** — Al revés: siempre preferir la granularidad más detallada. Se puede agregar hacia arriba; no se puede desagregar.
4. **"SCD Tipo 2 siempre es la mejor opción"** — Depende del caso de uso. Agrega complejidad y volumen. A veces el Tipo 1 es suficiente.

### 📚 Esta unidad es el destino de todo lo anterior

- Los pipelines ETL de la **Unidad II** alimentan el DWH.
- Las reglas de calidad de la **Unidad III** son la condición de entrada al DWH.
- El modelado dimensional definido aquí es el esquema que los Data Analysts usarán para sus consultas.

---

## Diagrama General de la Unidad

```
┌─────────────────────────────────────────────────────────────────────┐
│                UNIDAD IV — MAPA CONCEPTUAL                          │
│                                                                     │
│  ¿Por qué existe el DWH?                                           │
│  ─────────────────────────────────────────────────────────────     │
│  Los sistemas OLTP no pueden responder preguntas analíticas.       │
│  Se necesita un sistema separado, optimizado para lectura masiva.  │
│                                                                     │
│  ¿Cómo se construye?                                               │
│  ─────────────────────────────────────────────────────────────     │
│                                                                     │
│  ARQUITECTURA           MODELADO DIMENSIONAL                       │
│  ────────────           ─────────────────────                      │
│  Inmon (top-down)  ──►  Tabla de HECHOS                           │
│  Kimball (bottom-up)    (métricas, granularidad)                   │
│  Cloud: Snowflake   +   Tablas de DIMENSIONES                     │
│         BigQuery        (contexto descriptivo)                     │
│         Redshift     =  ESQUEMA ESTRELLA ★                        │
│                                                                     │
│  ¿Y cuando los datos cambian?                                      │
│  ─────────────────────────────────────────────────────────────     │
│  SLOWLY CHANGING DIMENSIONS (SCD)                                  │
│  Tipo 1: sobrescribir (sin historia)                               │
│  Tipo 2: fila nueva por cada cambio (historia completa) ← GOLD    │
│  Tipo 3: columna adicional (valor actual + valor anterior)        │
└─────────────────────────────────────────────────────────────────────┘
```

---

> 💡 **Consejo para los alumnos:** El modelado dimensional puede parecer abstracto al principio. La mejor forma de entenderlo es pensar siempre en preguntas de negocio concretas: "¿cuánto vendimos del producto X en la región Y en el Q3?" y luego diseñar el modelo para que esa pregunta sea fácil de responder con SQL simple. Si tu modelo necesita 8 JOINs para responder esa pregunta, el diseño está mal.
