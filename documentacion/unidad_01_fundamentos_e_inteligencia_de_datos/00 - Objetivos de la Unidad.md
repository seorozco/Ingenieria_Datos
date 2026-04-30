# Unidad I — Fundamentos e Inteligencia de Datos
## Objetivos de la Unidad

> **Asignatura:** Ingeniería de Datos  
> **Docente:** Ing. Sergio Orozco  
> **Clases que componen esta unidad:** Clase 01 y Clase 02

---

## ¿De qué trata esta unidad?

Esta unidad es el **punto de partida** de la carrera en Ingeniería de Datos. Antes de escribir una sola línea de código o diseñar un pipeline, necesitamos entender el territorio en el que vamos a trabajar: qué son los datos, cómo se clasifican, de dónde vienen, quiénes los trabajan y qué valor generan para una organización.

Si la Ingeniería de Datos fuera la carrera de medicina, esta unidad sería anatomía: la base sobre la que todo lo demás se construye.

---

## Objetivos de Aprendizaje

Al finalizar esta unidad, el alumno será capaz de:

- ✅ Definir qué es la **Inteligencia de Datos** y comprender su alcance dentro de las organizaciones modernas.
- ✅ Explicar los **5 niveles de análisis** (descriptivo, diagnóstico, predictivo, prescriptivo y decisivo) y diferenciar cuándo aplicar cada uno.
- ✅ Comprender el rol de la **Ingeniería de Datos** y por qué es la base sobre la que se apoyan analistas y científicos de datos.
- ✅ Reconocer la **Pirámide DIKW** como modelo conceptual que transforma datos crudos en sabiduría aplicada.
- ✅ Describir la **evolución histórica** del ecosistema de datos: desde los primeros Data Warehouses hasta el Data Mesh.
- ✅ Identificar los **roles** del ecosistema de datos (Data Analyst, Data Engineer, Data Scientist, Data Architect) y las responsabilidades de cada uno.
- ✅ Explicar el **ciclo de vida del dato** desde su captura hasta su archivo.
- ✅ Clasificar los datos según su **estructura** (estructurados, semi-estructurados y no estructurados).
- ✅ Identificar las principales **fuentes de datos** internas y externas en una organización.
- ✅ Comprender las diferencias entre **procesamiento batch y streaming**, y las **4V del Big Data**.

---

## Estructura de la Unidad

```
Unidad I
├── Clase 01 — Fundamentos de la Inteligencia de Datos
│   ├── ¿Qué es la Inteligencia de Datos?
│   ├── Los 5 niveles de análisis
│   ├── ¿Qué es la Ingeniería de Datos?
│   ├── La Pirámide DIKW
│   ├── Evolución histórica del ecosistema de datos
│   ├── Los 4 roles principales del ecosistema
│   └── El ciclo de vida del dato
│
└── Clase 02 — Tipos de Datos y Fuentes de Origen
    ├── Datos estructurados, semi-estructurados y no estructurados
    ├── Fuentes internas vs. externas
    ├── APIs REST y GraphQL
    ├── Archivos planos y formatos (CSV, Parquet, JSON)
    ├── Batch vs. Streaming
    └── Las 4V del Big Data
```

---

## Aspectos Relevantes de la Unidad

### 🔑 Conceptos Clave

| Concepto | Por qué importa |
|---|---|
| **Pirámide DIKW** | Entender la diferencia entre dato, información, conocimiento y sabiduría es fundamental para el trabajo de cualquier profesional de datos. |
| **Los 5 niveles de análisis** | Define el "para qué" de todo lo que construimos: desde reportes simples hasta sistemas decisivos automatizados. |
| **Rol del Data Engineer** | Es el protagonista de esta carrera. Sin pipelines bien construidos, nada más funciona. |
| **Tipos de datos** | Saber si un dato es estructurado, semi-estructurado o no estructurado determina qué herramientas usar. |
| **Batch vs. Streaming** | Una de las primeras decisiones arquitectónicas que enfrentarás en cualquier proyecto. |

### ⚠️ Puntos que suelen generar confusión

1. **"Los datos por sí solos tienen valor"** — FALSO. El valor está en la capacidad de interpretarlos y actuar sobre ellos.
2. **"El Data Engineer hace lo mismo que el Data Scientist"** — Son roles completamente distintos con responsabilidades y herramientas diferentes.
3. **"Streaming siempre es mejor que batch"** — No. El streaming es más complejo y costoso. Se usa solo cuando la latencia importa.
4. **"Los datos no estructurados no sirven"** — Son el 80-90% de los datos del mundo y contienen información valiosísima.

### 📚 Relación con las unidades siguientes

Esta unidad provee el **vocabulario y el marco conceptual** que se usa en todo el resto de la materia:
- La **Unidad II** profundiza en cómo extraer datos de esas fuentes que clasificamos aquí.
- La **Unidad III** trabaja sobre la calidad de esos mismos tipos de datos.
- La **Unidad IV** construye el destino final (Data Warehouse) al que los datos estructurados llegarán.

---

## Diagrama General de la Unidad

```
┌─────────────────────────────────────────────────────────────┐
│              UNIDAD I — MAPA CONCEPTUAL                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ¿Por qué existen los datos?                                 │
│       │                                                      │
│       ▼                                                      │
│  INTELIGENCIA DE DATOS ──────────────────────────────────── │
│  (convertir datos en decisiones)                             │
│       │                                                      │
│       ├──► Niveles: Descriptivo → Diagnóstico →              │
│       │            Predictivo → Prescriptivo → Decisivo      │
│       │                                                      │
│       ▼                                                      │
│  ¿Quién construye la infraestructura?                        │
│  DATA ENGINEER ──────────────────────────────────────────── │
│  (el protagonista de esta carrera)                           │
│       │                                                      │
│       ▼                                                      │
│  ¿Con qué datos trabaja?                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  TIPOS         │  FUENTES           │  PARADIGMAS   │    │
│  │  Estructurado  │  Internas (ERP)    │  Batch        │    │
│  │  Semi-estruc.  │  Externas (APIs)   │  Streaming    │    │
│  │  No estruc.    │  Sensores / Web    │               │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

> 💡 **Consejo para los alumnos:** No intenten memorizar todo. Entiendan los conceptos y la lógica detrás de ellos. La Ingeniería de Datos es una disciplina de criterio: el 90% del valor está en saber *por qué* se hace algo, no solo *cómo*.
