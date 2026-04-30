# Metodología Inmon — Introducción: Filosofía y Visión General

> **Manual de referencia para la construcción de Data Warehouses**  
> **Enfoque:** Top-Down — Enterprise Data Warehouse Normalizado  
> **Autor de referencia:** Bill Inmon (1945-)

---

## ¿Quién es Bill Inmon?

**William H. Inmon** es un informático y autor estadounidense reconocido como el **"Padre del Data Warehousing"** (*Father of Data Warehousing*). Es quien acuñó el término *Data Warehouse* en 1990 y estableció los principios fundacionales que definieron la disciplina.

Inmon ha publicado más de 60 libros y cientos de artículos sobre gestión de datos, arquitectura de información y Data Warehousing. Su obra más influyente es *Building the Data Warehouse* (1992), que ha sido actualizada en cuatro ediciones y sigue siendo referencia obligatoria en la industria.

### Obras principales

| Libro | Año | Enfoque |
|---|---|---|
| *Building the Data Warehouse* (1ª ed.) | 1992 | Fundamentos del DWH |
| *Building the Data Warehouse* (4ª ed.) | 2005 | Edición definitiva con actualizaciones |
| *Corporate Information Factory* | 1997 | Arquitectura empresarial completa |
| *Data Architecture: A Primer for the Data Scientist* | 2014 | Modelado empresarial moderno |
| *Data Lake Architecture* | 2016 | Integración con data lakes |

A diferencia de Kimball (quien se retiró en 2015), Inmon sigue activo en la industria, escribiendo sobre la evolución del Data Warehousing en la era del cloud y la inteligencia artificial.

---

## La Filosofía Inmon: Top-Down

La filosofía de Inmon se resume en una definición que es a la vez precisa y revolucionaria:

> **"Un Data Warehouse es una colección de datos orientada a temas, integrada, no volátil y variante en el tiempo, que se usa para el apoyo del proceso de toma de decisiones gerenciales."**

Cada palabra de esta definición es deliberada:

### Los 4 pilares del Data Warehouse según Inmon

```
┌───────────────────────────────────────────────────────────────────┐
│                    DATA WAREHOUSE (Inmon)                         │
├───────────────┬───────────────┬───────────────┬──────────────────┤
│  ORIENTADO    │  INTEGRADO    │  NO VOLÁTIL   │  VARIANTE EN     │
│  A TEMAS      │               │               │  EL TIEMPO       │
│               │               │               │                  │
│ Los datos se  │ Los datos de  │ Una vez que un│ Cada dato tiene  │
│ organizan por │ múltiples     │ dato entra al │ una marca        │
│ entidades de  │ sistemas se   │ DWH, no se    │ temporal que     │
│ negocio       │ unifican con  │ modifica ni   │ indica cuándo    │
│ (cliente,     │ las mismas    │ se borra.     │ era válido.      │
│ producto,     │ definiciones  │ Se agregan    │ El historial     │
│ venta), NO    │ y formatos.   │ nuevas        │ completo se      │
│ por sistema   │ Un cliente =  │ versiones.    │ preserva.        │
│ fuente ni     │ un cliente,   │               │                  │
│ departamento. │ sin importar  │               │                  │
│               │ de qué        │               │                  │
│               │ sistema venga.│               │                  │
└───────────────┴───────────────┴───────────────┴──────────────────┘
```

### 1. Orientado a Temas (*Subject-Oriented*)

El DWH no refleja la estructura de los sistemas operativos (tablas del ERP, tablas del CRM). Se organiza alrededor de los **temas centrales del negocio**: Cliente, Producto, Venta, Empleado, Contrato.

```
SISTEMA OPERATIVO (ERP):                 DATA WAREHOUSE (Inmon):
  Módulo de Ventas                         Tema: CLIENTE
  Módulo de Compras                        Tema: PRODUCTO
  Módulo de Inventario                     Tema: VENTA
  Módulo de RRHH                           Tema: EMPLEADO
  Módulo de Contabilidad                   Tema: FINANZAS
  
→ Cada módulo tiene SU versión del cliente   → UN SOLO concepto de cliente
→ Duplicados, inconsistencias               → Integrado, consistente
```

### 2. Integrado (*Integrated*)

La integración es quizás el principio más valioso y más difícil de implementar. Significa que **datos provenientes de múltiples sistemas se unifican bajo una sola definición y un solo formato**.

```
Antes de la integración:

  ERP:     genero = 'M' / 'F'
  CRM:     genero = 'Masculino' / 'Femenino'
  RRHH:    genero = 1 / 2
  Encuesta:genero = 'Hombre' / 'Mujer' / 'No binario' / 'Prefiero no decir'

Después de la integración (en el EDW):

  edw.persona: genero = 'M' / 'F' / 'X' / 'N'
  (definición única del glosario corporativo, aplicada a TODOS los registros)
```

### 3. No Volátil (*Non-Volatile*)

En un sistema operativo, los datos se actualizan constantemente: el stock cambia, el saldo del cliente se modifica, el pedido cambia de estado. En el DWH de Inmon, **los datos no se modifican ni se borran**: se agregan nuevas versiones.

```
Sistema operativo (mutable):
  Día 1: cliente.ciudad = 'Córdoba'
  Día 50: UPDATE cliente SET ciudad = 'Rosario'  → Córdoba ya no existe

Data Warehouse (no volátil):
  Día 1:  id=1001, ciudad='Córdoba',  fecha_desde='2025-01-01', fecha_hasta='2025-02-19', vigente=FALSE
  Día 50: id=1002, ciudad='Rosario',  fecha_desde='2025-02-20', fecha_hasta='9999-12-31', vigente=TRUE
  → Ambas versiones existen. Se puede ver qué ciudad tenía el cliente en cualquier fecha.
```

### 4. Variante en el Tiempo (*Time-Variant*)

Todo dato en el DWH tiene una dimensión temporal explícita. Esto permite responder preguntas como:

- *¿Cuál era la composición de clientes Premium hace 2 años?*
- *¿Cuándo cambió este producto de categoría?*
- *¿Cómo evolucionó la estructura de costos en los últimos 5 años?*

Sin variabilidad temporal, el DWH solo puede responder preguntas sobre el presente. Con ella, puede analizar tendencias, detectar cambios y predecir el futuro.

---

## La Corporate Information Factory (CIF)

Inmon no ve al Data Warehouse como un sistema aislado, sino como el núcleo de un ecosistema más amplio llamado la **Corporate Information Factory** (Fábrica de Información Corporativa):

```
┌─────────────────────────────────────────────────────────────────────┐
│                 CORPORATE INFORMATION FACTORY                       │
│                                                                     │
│  ┌────────────────┐                                                 │
│  │ SISTEMAS       │  Datos operativos del día a día                 │
│  │ OPERATIVOS     │  (ERP, CRM, SCM, etc.)                         │
│  └───────┬────────┘                                                 │
│          │                                                          │
│          │ ETL                                                       │
│          ▼                                                          │
│  ┌────────────────────────────────────────────┐                     │
│  │        ENTERPRISE DATA WAREHOUSE            │                     │
│  │        (3FN — núcleo integrado)             │  ← CORAZÓN del     │
│  │                                             │     sistema         │
│  │  Modelo Empresarial + Glosario Corporativo  │                     │
│  └───────────────────┬─────────────────────────┘                     │
│                      │                                               │
│          ┌───────────┼───────────┐                                   │
│          ▼           ▼           ▼                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                             │
│  │ Data Mart│ │ Data Mart│ │ Data Mart│  ← Subconjuntos             │
│  │ Ventas   │ │ Finanzas │ │ RRHH     │     desnormalizados         │
│  └──────────┘ └──────────┘ └──────────┘                             │
│          │           │           │                                   │
│          └───────────┼───────────┘                                   │
│                      ▼                                               │
│  ┌────────────────────────────────────────────┐                     │
│  │        CAPA DE ACCESO ANALÍTICO             │                     │
│  │        (BI, Dashboards, ML, Ad-hoc)         │                     │
│  └────────────────────────────────────────────┘                     │
│                                                                     │
│  ┌────────────────────────────────────────────┐                     │
│  │        OPERATIONAL DATA STORE (ODS)         │  ← Opcional:       │
│  │        (datos operativos integrados,        │     vista           │
│  │         sin historial profundo)             │     operativa       │
│  └────────────────────────────────────────────┘     integrada        │
│                                                                     │
│  ┌────────────────────────────────────────────┐                     │
│  │        EXPLORATION WAREHOUSE               │  ← Opcional:       │
│  │        (sandbox para data scientists)       │     zona libre      │
│  └────────────────────────────────────────────┘     para exploración │
└─────────────────────────────────────────────────────────────────────┘
```

El **Operational Data Store (ODS)** es un componente opcional que provee una vista integrada de los datos operativos con latencia baja (minutos a horas), útil para consultas operativas que necesitan datos de múltiples sistemas pero no requieren historial profundo.

El **Exploration Warehouse** es un sandbox donde los data scientists pueden experimentar libremente sin afectar el EDW ni los Data Marts.

---

## Comparación con Kimball: Las Diferencias Fundamentales

| Aspecto | Inmon (Top-Down) | Kimball (Bottom-Up) |
|---|---|---|
| **Filosofía** | El todo antes que las partes | Las partes construyen el todo |
| **Primer paso** | Modelo empresarial completo | Un proceso de negocio específico |
| **Estructura central** | EDW normalizado (3FN) | No hay estructura central; Data Marts conectados por dimensiones conformadas |
| **Data Marts** | Derivados del EDW (dependientes) | Construidos desde las fuentes (independientes, luego conformados) |
| **Normalización** | 3FN en el EDW | Desnormalizado (esquema estrella) desde el inicio |
| **ETL** | Dos saltos: fuente → EDW → Data Mart | Un salto: fuente → Data Mart |
| **Consistencia** | Garantizada por construcción (una sola fuente de verdad) | Garantizada por disciplina (dimensiones conformadas) |
| **Tiempo al primer resultado** | 6-18 meses | 2-3 meses |
| **Inversión inicial** | Alta | Menor |
| **Flexibilidad ante nuevas preguntas** | Alta (el EDW tiene todos los datos) | Limitada al alcance del Data Mart actual |
| **Riesgo principal** | Parálisis de análisis; proyecto que nunca entrega | Data Marts inconsistentes si no se conforman las dimensiones |
| **Ideal para** | Organizaciones grandes con gobernanza fuerte | Organizaciones que necesitan resultados rápidos |

### ¿Son mutuamente excluyentes?

**No.** En la práctica moderna, muchas organizaciones usan un enfoque híbrido:

- La **capa de integración** (zona "curada" del data lake o del lakehouse) sigue los principios de Inmon: datos integrados, normalizados, con historial.
- La **capa analítica** (Data Marts) sigue los principios de Kimball: esquemas estrella desnormalizados para consumo de BI.

```
Enfoque híbrido moderno:

  Fuentes → Data Lake (raw) → Zona Curada (Inmon/3FN) → Data Marts (Kimball/★) → BI
                                     ↑                          ↑
                              Principios Inmon           Principios Kimball
                              (integración,              (esquema estrella,
                               historial, 3FN)            dimensiones conformadas)
```

---

## ¿Por qué estudiar Inmon hoy?

Puede parecer que una metodología de los años 90 es obsoleta, pero los principios de Inmon son más relevantes que nunca:

1. **Data Mesh necesita integración:** la arquitectura descentralizada de Data Mesh solo funciona si hay estándares de interoperabilidad entre dominios. El modelo empresarial de Inmon es exactamente eso.

2. **Data Lakehouse adopta los mismos principios:** las capas "Bronze → Silver → Gold" de los lakehouses son una reimaginación de "Staging → EDW → Data Marts" de Inmon.

3. **La gobernanza es más importante que nunca:** con la explosión de datos y las regulaciones de privacidad (GDPR, Ley de Datos Personales), la integración y consistencia que Inmon propone son requisitos legales, no opcionales.

4. **La IA necesita datos integrados:** los modelos de ML y IA generativa son tan buenos como los datos que los alimentan. Un EDW integrado es la mejor fuente de datos de entrenamiento.

---

## Las 5 Etapas de este Manual

Este manual desarrolla la arquitectura Inmon en 5 etapas secuenciales:

| # | Etapa | Contenido principal |
|---|---|---|
| **01** | [Modelado Empresarial](01_modelado_empresarial.md) | Modelo de datos empresarial (3 niveles), áreas temáticas, glosario corporativo, técnicas de relevamiento |
| **02** | [EDW Normalizado](02_enterprise_data_warehouse_normalizado.md) | Diseño del EDW en 3FN, formas normales, staging area, capas internas, versionado temporal, diseño físico |
| **03** | [ETL al EDW](03_etl_al_edw.md) | Extracción (full, incremental, CDC), transformación (limpieza, integración, historial), carga, orquestación, ELT moderno |
| **04** | [Derivación de Data Marts](04_derivacion_data_marts.md) | Desnormalización, esquema estrella, queries de derivación, consistencia EDW↔DM, gobierno de Data Marts |
| **05** | [Capa de Acceso Analítico](05_capa_de_acceso_analitico.md) | Capa semántica, herramientas de BI, tipos de análisis, OLAP, seguridad, data storytelling, integración con ML |

---

## Glosario Rápido de la Terminología Inmon

| Término | Definición |
|---|---|
| **EDW** (*Enterprise Data Warehouse*) | Repositorio central normalizado (3FN) que contiene todos los datos analíticos integrados de la organización. |
| **3FN** (*Tercera Forma Normal*) | Nivel de normalización donde cada dato existe en un solo lugar y no hay dependencias transitivas. |
| **Modelo Empresarial** (*Enterprise Data Model*) | Representación completa de las entidades, relaciones y definiciones de datos de toda la organización. |
| **Área Temática** (*Subject Area*) | Agrupación lógica de entidades relacionadas (ej: "Clientes", "Productos", "Ventas"). |
| **Glosario Corporativo** (*Business Glossary*) | Documento que define oficialmente cada término de negocio con una sola definición acordada. |
| **Data Mart Dependiente** | Data Mart que se alimenta exclusivamente del EDW, nunca directamente de los sistemas fuente. |
| **Staging Area** | Zona temporal donde se copian los datos de los sistemas fuente antes de transformarlos y cargarlos al EDW. |
| **CIF** (*Corporate Information Factory*) | Ecosistema completo de Inmon: sistemas operativos + ODS + EDW + Data Marts + capa de acceso. |
| **ODS** (*Operational Data Store*) | Almacén de datos integrados con baja latencia para consultas operativas (no históricas). |
| **Data Steward** | Persona responsable de la calidad y las definiciones de datos de un área temática. |
| **Data Owner** | Ejecutivo de negocio responsable de aprobar las definiciones del glosario y las reglas de acceso a los datos de su área. |
| **No Volatilidad** | Principio del DWH: los datos no se modifican ni eliminan; se agregan nuevas versiones históricas. |
| **Variabilidad Temporal** | Principio del DWH: cada dato tiene una marca temporal que indica cuándo era válido. |
| **Integración** | Principio del DWH: datos de múltiples fuentes se unifican bajo definiciones comunes. |
| **Hash de Registro** | Valor calculado (SHA-256) sobre los campos de un registro, usado para detectar cambios sin comparar campo a campo. |

---

## Lecturas Recomendadas

### Textos fundacionales

- **Inmon, W.H.** — *Building the Data Warehouse*, 4ta edición (2005). Wiley. **La referencia definitiva** de la arquitectura top-down.
- **Inmon, W.H., Imhoff, C. & Sousa, R.** — *Corporate Information Factory*, 2da edición (2001). Wiley. La visión completa del ecosistema.
- **Inmon, W.H.** — *Data Architecture: A Primer for the Data Scientist* (2014). Morgan Kaufmann. Actualización para la era moderna.

### Contexto moderno

- **Reis, J. & Housley, M.** — *Fundamentals of Data Engineering* (2022). O'Reilly. Perspectiva moderna que integra Inmon con data lakes, streaming y cloud.
- **Dehghani, Z.** — *Data Mesh: Delivering Data-Driven Value at Scale* (2022). O'Reilly. Cómo el modelo empresarial evoluciona en arquitecturas descentralizadas.
- **DAMA International** — *DAMA-DMBOK: Data Management Body of Knowledge*, 2da edición (2017). Technics Publications. Marco completo de gestión de datos.
- **Kleppmann, M.** — *Designing Data-Intensive Applications* (2017). O'Reilly. Fundamentos técnicos de almacenamiento y procesamiento.

### Perspectiva crítica

- **Kimball, R. & Ross, M.** — *The Data Warehouse Toolkit*, 3ra edición (2013). Wiley. Para entender el enfoque alternativo y complementario.
- **Linstedt, D.** — *Building a Scalable Data Warehouse with Data Vault 2.0* (2015). Morgan Kaufmann. Evolución moderna del EDW normalizado.
