# Unidad III — Calidad del Dato y Gobierno
## Objetivos de la Unidad

> **Asignatura:** Ingeniería de Datos  
> **Docente:** Ing. Sergio Orozco  
> **Clases que componen esta unidad:** Clase 07 y Clase 08

---

## ¿De qué trata esta unidad?

En las unidades anteriores aprendimos a construir pipelines ETL que extraen, transforman y cargan datos. Pero hay una pregunta fundamental que todavía no respondimos: **¿cómo sabemos si esos datos son correctos?**

Esta unidad aborda dos pilares que hacen que los datos sean confiables en una organización:

1. **Calidad del Dato:** la disciplina técnica de medir, detectar y corregir problemas en los datos (nulos, duplicados, inconsistencias, outliers).
2. **Gobierno del Dato:** el marco organizacional que define quién es responsable de los datos, cómo se documentan y cómo se protegen.

> **Por qué importa:** Según estudios de la industria, los equipos de datos gastan entre el 60% y el 80% de su tiempo limpiando y verificando datos. Sin procesos formales de calidad y gobierno, ese tiempo se desperdicia en arreglar los mismos problemas una y otra vez.

---

## Objetivos de Aprendizaje

Al finalizar esta unidad, el alumno será capaz de:

- ✅ Identificar y explicar las **6 dimensiones de calidad del dato** y evaluar su impacto en decisiones de negocio.
- ✅ Realizar un proceso de **Data Profiling** completo sobre un dataset real usando Python.
- ✅ Definir y calcular **métricas y KPIs de calidad** para monitorear la salud de los datos.
- ✅ Implementar reglas de validación automatizadas usando **Great Expectations** y **pandas**.
- ✅ Construir un **reporte de auditoría de calidad** que identifique y cuantifique problemas.
- ✅ Explicar qué es el **Gobierno del Dato**, sus principios y su estructura organizacional.
- ✅ Diferenciar los roles de **Data Steward**, **Data Owner** y **Chief Data Officer (CDO)**.
- ✅ Comprender qué es un **catálogo de datos** y un **diccionario de datos**, y cómo construirlos.
- ✅ Explicar el concepto de **linaje del dato** y por qué es esencial para la trazabilidad.
- ✅ Clasificar datos sensibles (**PII**) y aplicar políticas básicas de protección con Python.

---

## Estructura de la Unidad

```
Unidad III
├── Clase 07 — Calidad del Dato
│   ├── ¿Por qué importa la calidad del dato?
│   ├── Las 6 dimensiones: Completitud, Exactitud, Consistencia,
│   │   Unicidad, Vigencia, Integridad
│   ├── Data Profiling con Python (pandas)
│   ├── Métricas y KPIs de calidad
│   ├── Detección de outliers con IQR
│   └── Validación automatizada con Great Expectations
│
└── Clase 08 — Gobierno del Dato
    ├── ¿Qué es el Data Governance?
    ├── Roles: CDO, Data Owner, Data Steward
    ├── Catálogo de datos y Diccionario de datos
    ├── Linaje del dato (Data Lineage)
    └── Datos PII y regulaciones (Ley 25.326, GDPR)
```

---

## Aspectos Relevantes de la Unidad

### 🔑 Conceptos Clave

| Concepto | Por qué importa |
|---|---|
| **"Garbage in, garbage out"** | El principio fundamental que motiva toda la unidad |
| **Las 6 dimensiones de calidad** | El framework estándar (DAMA) para evaluar datos |
| **Data Profiling** | El "diagnóstico" previo a cualquier transformación |
| **Great Expectations** | La librería estándar para contratos de calidad en pipelines |
| **Gobierno del Dato** | Sin responsabilidades claras, la calidad no se mantiene |
| **Datos PII** | Responsabilidad legal que todo Data Engineer debe conocer |

### ⚠️ Puntos que suelen generar confusión

1. **"La calidad del dato es responsabilidad solo del equipo de datos"** — FALSO. Cada área de negocio es responsable de la calidad de los datos que genera.
2. **"Un dato presente no es un dato correcto"** — La dimensión de Exactitud separa la completitud de la veracidad. Un dato puede estar presente y ser incorrecto.
3. **"El Data Steward y el Data Engineer hacen lo mismo"** — No. El Data Steward define las reglas de calidad y documenta; el Data Engineer las implementa técnicamente.
4. **"GDPR solo aplica a empresas europeas"** — Aplica a toda organización que procese datos de ciudadanos de la UE, sin importar dónde esté la empresa.

### 📚 Relación con las unidades siguientes

- La calidad del dato es la **condición de entrada** para el Data Warehouse. En la **Unidad IV**, los datos que llegan al DWH deben cumplir los estándares definidos aquí.
- El linaje del dato es fundamental para auditar las **Slowly Changing Dimensions** (SCD) que veremos en la Unidad IV.

---

## Diagrama General de la Unidad

```
┌─────────────────────────────────────────────────────────────────────┐
│                UNIDAD III — MAPA CONCEPTUAL                         │
│                                                                     │
│  Los datos llegaron del pipeline ETL. ¿Qué tan buenos son?        │
│                           │                                         │
│                           ▼                                         │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                  CALIDAD DEL DATO                             │  │
│  │                                                               │  │
│  │  DATA PROFILING ──► Diagnosticar el dataset                  │  │
│  │       │                                                       │  │
│  │       ▼                                                       │  │
│  │  6 DIMENSIONES ──► Completitud, Exactitud, Consistencia,     │  │
│  │                    Unicidad, Vigencia, Integridad             │  │
│  │       │                                                       │  │
│  │       ▼                                                       │  │
│  │  GREAT EXPECTATIONS ──► Contratos de calidad automatizados   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                           │                                         │
│                           ▼                                         │
│  ¿Quién es responsable de que esa calidad se mantenga?             │
│                           │                                         │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                GOBIERNO DEL DATO                              │  │
│  │                                                               │  │
│  │  CDO → Data Owner → Data Steward → Data Engineer            │  │
│  │                                                               │  │
│  │  Catálogo de Datos  +  Diccionario  +  Linaje               │  │
│  │                                                               │  │
│  │  Protección de PII  +  Cumplimiento Regulatorio             │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

> 💡 **Consejo para los alumnos:** La calidad y el gobierno del dato pueden parecer "burocracia" al principio. En la práctica, son la diferencia entre una organización que toma decisiones basadas en datos confiables y una que discute en cada reunión si los números son correctos. Un pipeline sin validación de calidad es un pipeline que va a fallar silenciosamente.
