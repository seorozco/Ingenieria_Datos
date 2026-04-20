# Ingeniería de Datos

> **Docente:** Ing. Sergio Orozco — Arquitecto de Datos · Infra Cloud · Experto en Big Data  
> **Modalidad:** Teórico-Práctica | **Unidades:** 5 | **Clases:** 12

---

## Descripción

Esta asignatura provee las competencias fundamentales para diseñar, construir y mantener *pipelines* de datos de extremo a extremo. Se recorre el ciclo completo del dato: desde la comprensión de su naturaleza y fuentes de origen, pasando por los procesos de extracción, transformación y carga (ETL/ELT), hasta el modelado de almacenes de datos analíticos y las arquitecturas modernas como Data Lake y Data Lakehouse.

La cursada combina teoría con laboratorios prácticos usando herramientas del ecosistema real: **Python, SQL, dbt, Apache Airflow, Great Expectations** y plataformas cloud.

---

## Objetivos

- Comprender el ecosistema de datos y los roles que intervienen (Data Engineer, Analyst, Scientist, Architect).
- Identificar y clasificar las principales fuentes de datos y tipos de bases de datos (SQL, NoSQL, OLAP, OLTP).
- Diseñar e implementar pipelines ETL/ELT robustos aplicando buenas prácticas de ingeniería.
- Evaluar y garantizar la calidad del dato a través de métricas, reglas de validación y gobierno.
- Modelar almacenes de datos (Data Warehouses) usando la metodología dimensional de Kimball.
- Conocer y comparar arquitecturas modernas: Data Warehouse, Data Lake y Data Lakehouse.
- Integrar las competencias adquiridas en un proyecto grupal de ingeniería de datos real.

---

## Mapa del Programa

```
UNIDAD I          UNIDAD II           UNIDAD III          UNIDAD IV           UNIDAD V
Fundamentos   →   Orígenes y ETL  →   Calidad y Gob.  →   Data Warehouse  →   Arq. Modernas
Clases 1–2        Clases 3–6          Clases 7–8          Clases 9–10         Clases 11–12
```

> Ciclo completo: **Fuente → ETL → Calidad → DWH → Lakehouse → Análisis**

---

## Programa por Unidades

| # | Unidad | Clases | Foco |
|---|--------|--------|------|
| I | Fundamentos e Inteligencia de Datos | 1–2 | Conceptos, ecosistema, tipos de datos y roles |
| II | Orígenes de Datos y Proceso ETL | 3–6 | Bases de datos, extracción, transformación, carga, Airflow |
| III | Calidad del Dato y Gobierno | 7–8 | Perfilado, dimensiones de calidad, gobierno, catálogos |
| IV | Data Warehouse y Modelado Dimensional | 9–10 | Arquitecturas DWH, esquema estrella, SCD |
| V | Arquitecturas Modernas y Proyecto | 11–12 | Data Lake, Lakehouse, Medallion Architecture, proyecto integrador |

---

### Unidad I — Fundamentos e Inteligencia de Datos *(Clases 1–2)*

**Clase 01 · Fundamentos de la Inteligencia de Datos**  
Los 5 pilares del análisis (descriptivo, diagnóstico, predictivo, prescriptivo, decisivo), pirámide DIKW, evolución histórica del ecosistema de datos, roles y ciclo de vida del dato.

**Clase 02 · Tipos de Datos y Fuentes de Origen**  
Datos estructurados, semi-estructurados y no estructurados. Fuentes internas y externas: ERP, CRM, APIs, IoT. Batch vs. streaming. Las 4V del Big Data.

---

### Unidad II — Orígenes de Datos y Proceso ETL *(Clases 3–6)*

**Clase 03 · Tipos de Bases de Datos**  
Relacionales (SQL/ACID), NoSQL (clave-valor, documental, columnar, grafos), OLTP vs. OLAP, Data Warehouse vs. Data Lake.

**Clase 04 · Extracción de Datos (Extract)**  
Full Load vs. Incremental. Change Data Capture (CDC) con Debezium. Consumo de APIs REST. Web scraping ético con BeautifulSoup. Herramientas: Airbyte, Fivetran.

**Clase 05 · Transformación de Datos (Transform)**  
Limpieza, normalización y enriquecimiento con pandas. ETL vs. ELT. dbt como herramienta de transformación con SQL versionado.

**Clase 06 · Carga y Orquestación (Load)**  
Estrategias de carga: Full Overwrite, Append, Upsert. Idempotencia. Apache Airflow: DAGs, tareas y scheduling. Pipeline ETL completo.

---

### Unidad III — Calidad del Dato y Gobierno *(Clases 7–8)*

**Clase 07 · Las 6 Dimensiones de Calidad y Data Profiling**  
Completitud, exactitud, consistencia, unicidad, vigencia e integridad. Data Profiling con Python. Great Expectations para validación automatizada.

**Clase 08 · Gobierno del Dato y Gestión de Metadatos**  
Data Governance: principios y estructura organizacional. Roles: Data Steward, Data Owner, CDO. Catálogo y diccionario de datos. Linaje. Clasificación de datos PII/GDPR.

---

### Unidad IV — Data Warehouse y Modelado Dimensional *(Clases 9–10)*

**Clase 09 · Introducción al Data Warehouse**  
El problema que motivó el DWH. OLTP vs. OLAP. Arquitectura top-down de Inmon vs. bottom-up de Kimball. Data Marts. Plataformas cloud: Redshift, BigQuery, Snowflake.

**Clase 10 · Modelado Dimensional y SCD**  
Tablas de hechos (métricas, granularidad, tipos). Tablas de dimensiones. Esquema estrella y copo de nieve. Slowly Changing Dimensions: Tipo 1, Tipo 2 y Tipo 3.

---

### Unidad V — Arquitecturas Modernas y Proyecto Integrador *(Clases 11–12)*

**Clase 11 · Data Lake, Lakehouse y Medallion Architecture**  
Data Lake: zonas Raw/Staged/Curated. Delta Lake (ACID sobre object storage, Time Travel). Medallion Architecture: Bronze → Silver → Gold. Apache Iceberg y Hudi. Data Lakehouse con Databricks.

**Clase 12 · Proyecto Integrador y Tendencias**  
Presentación y defensa de proyectos grupales: pipeline ETL completo end-to-end. DataOps, MLOps, datos para IA. Ingeniería de datos en tiempo real con Kafka + Flink.

---

## Evaluación

| Instancia | Descripción | Peso |
|-----------|-------------|------|
| Participación | Debates, ejercicios en clase y laboratorios | 10% |
| Trabajos prácticos (×4) | Entregas de las Unidades II, III y IV | 30% |
| Evaluación parcial | Prueba escrita + resolución de caso (Unidades I–III) | 25% |
| Proyecto integrador | Pipeline completo: extracción → transformación → calidad → DWH. Presentación grupal | 35% |

El proyecto integrador debe demostrar: fuente real → extracción → transformación → calidad → esquema estrella en DWH cloud → DAG de orquestación.

---

## Stack Tecnológico

| Categoría | Herramientas |
|-----------|-------------|
| Lenguajes | Python 3.x · SQL |
| ETL / Transformación | pandas · dbt · Apache Airflow |
| Integración / Extracción | Airbyte · requests · Debezium |
| Bases de datos | PostgreSQL · MongoDB · Redis · Neo4j |
| Calidad del dato | Great Expectations · OpenMetadata |
| Data Warehouse cloud | Snowflake · BigQuery · DuckDB |
| Arquitectura Lakehouse | Delta Lake · Databricks CE · Apache Iceberg |
| Control de versiones | Git · GitHub · dbt Cloud |

---

## Estructura del Repositorio

```
Ingenieria_Datos/
├── documentacion/          # Apuntes completos por unidad
│   ├── unidad_01_fundamentos_e_inteligencia_de_datos.md
│   ├── unidad_02_origenes_de_datos_y_proceso_etl.md
│   ├── unidad_03_calidad_del_dato_y_gobierno.md
│   ├── unidad_04_clase_09_introduccion_al_data_warehouse.md
│   └── unidad_04_clase_10_modelado_dimensional_y_scd.md
├── manueles/               # Guías metodológicas
│   ├── Inmon/              # Arquitectura Inmon paso a paso
│   └── kimball/            # Metodología Kimball paso a paso
├── notebook/               # Laboratorios prácticos en Jupyter
│   └── unidad_II/
│       ├── extraccion_sqlserver.ipynb
│       ├── extraccion_api_publica.ipynb
│       ├── web_scraping.ipynb
│       └── bcra_scraping_vs_api.ipynb
├── plan_de_estudio.md      # Programa completo de la asignatura
├── BIBLIOGRAFIA.md         # Bibliografía sugerida por unidad
└── README.md               # Este archivo
```

---

## Notebooks de Laboratorio

| Notebook | Unidad | Descripción |
|----------|--------|-------------|
| [extraccion_sqlserver.ipynb](notebook/unidad_II/extraccion_sqlserver.ipynb) | II | Extracción desde SQL Server con pyodbc/SQLAlchemy |
| [extraccion_api_publica.ipynb](notebook/unidad_II/extraccion_api_publica.ipynb) | II | Consumo de APIs REST: feriados y clima Buenos Aires |
| [web_scraping.ipynb](notebook/unidad_II/web_scraping.ipynb) | II | Web scraping con BeautifulSoup: libros y frases |
| [bcra_scraping_vs_api.ipynb](notebook/unidad_II/bcra_scraping_vs_api.ipynb) | II | Comparativa: scraping bloqueado vs. API REST del BCRA |

---

*Ingeniería de Datos · 5 Unidades · 12 Clases · Ing. Sergio Orozco*
