# Ingeniería de Datos
## Programa de la Asignatura

**Docente:** Ing. Sergio Orozco — Arquitecto de Datos · Infra Cloud · Experto en Big Data  
**Modalidad:** Teórico-Práctica | **Unidades:** 5 | **Clases:** 12

---

## Descripción General

La asignatura **Ingeniería de Datos** provee a los estudiantes las competencias fundamentales para diseñar, construir y mantener *pipelines* de datos de extremo a extremo. A lo largo de 12 clases organizadas en 5 unidades, se recorre el ciclo completo del dato: desde la comprensión de su naturaleza y fuentes de origen, pasando por los procesos de extracción, transformación y carga (ETL/ELT), hasta el modelado de almacenes de datos analíticos y las arquitecturas modernas como Data Lake y Data Lakehouse.

La asignatura combina teoría con laboratorios prácticos usando herramientas del ecosistema real: **Python, SQL, dbt, Apache Airflow, Great Expectations** y plataformas **cloud**.

---

## Objetivos de la Asignatura

- Comprender el ecosistema de datos y los roles que intervienen en su gestión y explotación (Data Engineer, Analyst, Scientist, Architect).
- Identificar y clasificar las principales fuentes de datos y tipos de bases de datos disponibles (SQL, NoSQL, OLAP, OLTP).
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

## Resumen por Unidades

| Unidad | Título | Clases | Foco Principal |
|--------|--------|--------|----------------|
| I | Fundamentos e Inteligencia de Datos | 1–2 | Conceptos, ecosistema y tipos de datos |
| II | Orígenes de Datos y Proceso ETL | 3–6 | Bases de datos, extracción, transformación, carga |
| III | Calidad del Dato y Gobierno | 7–8 | Perfilado, dimensiones de calidad, gobierno |
| IV | Data Warehouse y Modelado Dimensional | 9–10 | Arquitecturas DW, esquemas estrella, SCD |
| V | Arquitecturas Modernas y Proyecto | 11–12 | Data Lake, Lakehouse, proyecto integrador |

---

## Desarrollo por Unidades y Clases

---

### UNIDAD I · Fundamentos e Inteligencia de Datos
> Conceptos base del ecosistema de datos: qué es, para qué sirve, cómo evolucionó y qué roles intervienen.

---

#### Clase 01 — Fundamentos de la Inteligencia de Datos
**Modalidad:** Teórica

**Contenidos:**
- ¿Qué es la Inteligencia de Datos? Definición, alcance y los 5 pilares:
  - Descriptivo: ¿Qué está pasando?
  - Diagnóstico: ¿Por qué está pasando?
  - Predictivo: ¿Qué es probable que pase?
  - Prescriptivo: ¿Qué deberíamos hacer al respecto?
  - Decisivo: ¿Cómo ejecutamos la mejor opción?
- ¿Qué es la Ingeniería de Datos? El proceso ETL y el stack tecnológico (Python, SQL, Spark, Airflow, Cloud).
- Pirámide DIKW: Dato → Información → Conocimiento → Sabiduría.
- Historia y evolución: On-Premise DWH → Big Data → Data Warehouse Cloud → Data Mesh.
- Roles del ecosistema: Data Analyst, Data Engineer, Data Scientist, Data Architect.
- Ciclo de vida del dato: captura, procesamiento, almacenamiento, análisis, modelado, visualización, activación, archivo.

**Actividad práctica:**  
Debate guiado: ¿cuántos datos genera tu organización en un día? Mapeo colectivo de fuentes.

> 📌 **Ejemplo:** Una tienda registra "200 clicks en comprar". Dato → Información → "Alta demanda vespertina los lunes" → Aumentar stock los lunes: sabiduría aplicada.

> 💡 **Concepto clave:** Sin Data Engineers que construyan los pipelines, analistas y científicos no tienen datos confiables con qué trabajar.

**Bibliografía:** Davenport, T. — *Competing on Analytics*. Kimball, R. — *The Data Warehouse Toolkit* (Introducción).

---

#### Clase 02 — Tipos de Datos y Fuentes de Origen
**Modalidad:** Teórico-Práctica

**Contenidos:**
- Datos estructurados (tablas SQL, CSV, Excel), semi-estructurados (JSON, XML, YAML) y no estructurados (texto, imágenes, audio, video).
- Fuentes internas vs. externas: ERP, CRM, APIs, redes sociales, sensores IoT.
- APIs REST y GraphQL, archivos planos, logs y datos en streaming.
- Datos en tiempo real (streaming) vs. procesamiento por lotes (batch).
- Las 4V del Big Data: Volumen, Velocidad, Variedad y Veracidad.

**Actividad práctica:**  
Ejercicio de mapeo: identificar y clasificar fuentes de datos de una empresa ficticia.

> 📌 **Ejemplo:** Un email es no estructurado. Una factura en SAP es estructurada. La respuesta de una API de clima es JSON (semi-estructurado). Cada tipo requiere herramientas distintas.

> 💡 **Concepto clave:** Usar streaming cuando el valor del dato decae rápidamente: fraude, alertas, precios de bolsa → streaming. Reportes mensuales → batch suficiente.

**Bibliografía:** Kleppmann, M. — *Designing Data-Intensive Applications* (Cap. 1). Documentación de Apache Kafka.

---

### UNIDAD II · Orígenes de Datos y Proceso ETL
> Tipos de bases de datos, métodos de extracción, técnicas de transformación, estrategias de carga y orquestación con Apache Airflow.

---

#### Clase 03 — Tipos de Bases de Datos
**Modalidad:** Teórico-Práctica

**Contenidos:**

*Según su modelo de datos:*
- **Relacionales (SQL):** PostgreSQL, MySQL, SQL Server — esquema rígido, ACID, uso en ERP/CRM.
- **NoSQL Clave-Valor:** Redis, DynamoDB — velocidad, caché, sesiones de login.
- **NoSQL Documental:** MongoDB, CouchDB — JSON/BSON, esquema flexible, APIs y microservicios.
- **NoSQL Columnar:** Apache Cassandra, HBase — alta escalabilidad, escritura masiva distribuida.
- **Grafos:** Neo4j, Amazon Neptune — redes sociales, fraude, recomendaciones.

*Según la carga de trabajo:*
- **OLTP:** optimizada para muchas operaciones pequeñas y concurrentes (sistemas transaccionales).
- **OLAP:** optimizada para consultas complejas y agregaciones analíticas.

*Según propósito analítico:*
- Data Warehouse, Data Mart, Data Lake, Lakehouse.

**Actividad práctica:**  
Laboratorio comparativo: consultar el mismo dataset en PostgreSQL y MongoDB. Análisis de rendimiento.

> 📌 **Ejemplo:** Un banco usa SQL para transacciones (ACID obligatorio), Redis para sesiones de login (velocidad) y Neo4j para detectar fraude en redes de cuentas (relaciones).

> 💡 **Concepto clave:** No existe una base de datos universal. Elegir según el patrón de acceso, necesidad de consistencia y tipo de relaciones entre los datos.

**Bibliografía:** Documentación oficial PostgreSQL, MongoDB Docs, Redis University, Neo4j Docs.

---

#### Clase 04 — Extracción de Datos (Extract)
**Modalidad:** Práctica

**Contenidos:**
- Full Load vs. Incremental Extract: cuándo aplicar cada estrategia.
- Change Data Capture (CDC): captura de cambios en tiempo real (Debezium).
- Conectores y drivers: JDBC, ODBC, conectores nativos.
- Consumo de APIs REST y GraphQL con autenticación (API Keys, OAuth).
- Web scraping ético: BeautifulSoup, Scrapy.
- Herramientas de integración: Fivetran, Airbyte, Stitch, Debezium.

**Actividad práctica:**  
Extraer datos de una API pública (ej. OpenWeather o datos del gobierno) hacia un archivo CSV con Python usando la librería `requests`.

**Bibliografía:** Documentación de Airbyte. Tutorial oficial de `requests` (Python). Reis & Housley — *Fundamentals of Data Engineering* (Cap. 5).

---

#### Clase 05 — Transformación de Datos (Transform)
**Modalidad:** Práctica

**Contenidos:**
- Limpieza de datos: tratamiento de nulos, duplicados y tipos de dato incorrectos.
- Normalización y estandarización de valores (fechas, monedas, textos).
- Joins, agregaciones, pivots y derivación de nuevas columnas.
- Enriquecimiento: cruce con datos externos o tablas de referencia.
- ETL vs. ELT:
  - **ETL:** transformar antes de cargar — mayor privacidad, eficiencia de almacenamiento.
  - **ELT:** cargar primero y transformar en destino — velocidad de ingesta, flexibilidad, escalabilidad cloud.
- dbt (data build tool): transformaciones con SQL versionado y testeado.
- Validación de transformaciones: pruebas unitarias sobre datos.

**Actividad práctica:**  
Taller: transformar un dataset sucio (fechas inconsistentes, nulos, formatos mixtos) usando pandas y dbt. Documentar las decisiones tomadas.

**Bibliografía:** dbt Documentation (docs.getdbt.com). Pandas User Guide. McKinney — *Python for Data Analysis*.

---

#### Clase 06 — Carga de Datos (Load) y Orquestación
**Modalidad:** Práctica

**Contenidos:**
- Destinos de carga: Data Warehouse, Data Lake, Data Lakehouse.
- Estrategias: Full Overwrite, Append, Upsert (MERGE / INSERT ON CONFLICT).
- Idempotencia: ejecutar N veces → mismo resultado.
- Manejo de errores, reintentos y logs de ejecución.
- Apache Airflow: DAGs, tareas, dependencias y scheduling.
- Pipeline completo de extremo a extremo: ejercicio integrador.

**Actividad práctica:**  
Construir y ejecutar un pipeline ETL completo: extracción de API → transformación con pandas → carga en PostgreSQL → orquestado con Airflow.

> 📌 **Ejemplo:** Un DAG de Airflow se ejecuta cada día a las 6 AM: extrae ventas del ERP, transforma con pandas y carga en Snowflake. Si falla, reintenta 2 veces y alerta por email.

> 💡 **Concepto clave:** Upsert (INSERT ON CONFLICT) es la estrategia más segura: si el registro existe lo actualiza, si no lo inserta. El pipeline puede ejecutarse múltiples veces sin duplicar datos.

**Bibliografía:** Apache Airflow Docs. Harenslak & de Ruiter — *Data Pipelines with Apache Airflow*. SQLAlchemy Documentation.

---

### UNIDAD III · Calidad del Dato y Gobierno
> Dimensiones de calidad, data profiling, validación automatizada, catálogos y gobierno organizacional del dato.

---

#### Clase 07 — Calidad del Dato — Las 6 Dimensiones y Profiling
**Modalidad:** Teórico-Práctica

**Contenidos:**
- **Completitud:** ¿están todos los datos presentes?
- **Exactitud:** ¿representan correctamente la realidad?
- **Consistencia:** ¿son iguales en todos los sistemas?
- **Unicidad:** ¿cada entidad aparece una sola vez?
- **Vigencia:** ¿están actualizados en el momento correcto?
- **Integridad:** ¿se mantienen las relaciones entre datos?
- Impacto de la mala calidad en decisiones de negocio (casos reales).
- Data Profiling: análisis estadístico y estructural de un dataset.
- Métricas y KPIs de calidad. Reglas de validación: rangos, dominios, dependencias funcionales.
- Great Expectations: validación automatizada con contratos de datos.

**Actividad práctica:**  
Auditoría de calidad sobre un dataset real: generar un reporte de profiling con Great Expectations e identificar los principales problemas.

```python
import great_expectations as ge

df = ge.read_csv('ventas.csv')

df.expect_column_values_to_not_be_null('id_venta')
df.expect_column_values_to_be_unique('id_venta')
df.expect_column_values_to_be_between(
    'precio_unitario', min_value=0, max_value=50000
)
df.expect_column_values_to_be_in_set(
    'moneda', ['ARS', 'USD', 'EUR']
)

resultado = df.validate()
print(f'Tests OK:      {resultado.statistics["successful_expectations"]}')
print(f'Tests fallidos: {resultado.statistics["unsuccessful_expectations"]}')
```

> 📌 **Ejemplo:** Un pipeline de marketing envía emails a 50.000 clientes. Si el 30% tiene emails nulos y el 15% tiene formato inválido, solo el 55% recibe la campaña. La mala calidad tiene costo directo.

> 💡 **Concepto clave:** "Garbage in, garbage out": un modelo de ML con datos de mala calidad producirá predicciones incorrectas sin importar cuán sofisticado sea el algoritmo.

**Bibliografía:** DAMA-DMBOK (Cap. 13). Documentación de Great Expectations.

---

#### Clase 08 — Gobierno del Dato y Gestión de Metadatos
**Modalidad:** Teórico-Práctica

**Contenidos:**
- Data Governance: definición, principios y estructura organizacional.
- Roles: Data Steward, Data Owner, Chief Data Officer (CDO).
- Catálogo de datos y diccionario de datos: qué son y para qué sirven.
- Linaje del dato (Data Lineage): rastrear el origen y transformaciones.
- Clasificación de datos y seguridad: PII, datos sensibles, GDPR.
- Herramientas: Collibra, Alation, OpenMetadata, Apache Atlas.

**Actividad práctica:**  
Diseñar un plan de gobernanza básico para un caso de estudio: identificar activos de datos, asignar roles y definir políticas de calidad.

> 💡 **Concepto clave:** El gobierno del dato define quién es responsable de cada activo. Sin Data Owners, las reglas de calidad no se cumplen porque nadie las hace cumplir.

**Bibliografía:** DAMA-DMBOK (Cap. 3 y 7). Documentación de OpenMetadata. Ladley, J. — *Data Governance*.

---

### UNIDAD IV · Data Warehouse y Modelado Dimensional
> Arquitecturas Kimball vs. Inmon, diferencias OLTP/OLAP, esquemas estrella y copo de nieve, Slowly Changing Dimensions.

---

#### Clase 09 — Introducción al Data Warehouse
**Modalidad:** Teórica

**Contenidos:**
- ¿Qué es un Data Warehouse y por qué existe? Historia y evolución.
- OLTP vs. OLAP: diferencias fundamentales en diseño y uso.
- Arquitectura de Inmon (top-down): núcleo central normalizado.
- Arquitectura de Kimball (bottom-up): Data Marts primero.
- Data Mart: subconjuntos temáticos del DWH.
- Soluciones cloud: Amazon Redshift, Google BigQuery, Snowflake.

**Actividad práctica:**  
Análisis comparativo: diseñar el diagrama de arquitectura para un caso empresarial usando el enfoque Kimball. Comparar con enfoque Inmon.

> 📌 **Ejemplo:** Un reporte de ventas tardaba 45 minutos en el ERP y lo bloqueaba. Después de migrar a Snowflake con esquema dimensional, el mismo reporte tarda 4 segundos sin impactar producción.

> 💡 **Concepto clave:** El DWH no reemplaza la base operacional: la complementa. El ERP guarda transacciones del presente; el DWH guarda el historial optimizado para consultas analíticas complejas.

**Bibliografía:** Kimball, R. — *The Data Warehouse Toolkit* (Cap. 1-2). Inmon, W.H. — *Building the Data Warehouse*. Snowflake Documentation.

---

#### Clase 10 — Modelado Dimensional y SCD
**Modalidad:** Práctica

**Contenidos:**
- Tablas de hechos: métricas, granularidad y tipos (transaccional, snapshot, acumulado).
- Tablas de dimensiones: atributos descriptivos y jerarquías.
- Esquema estrella: diseño simple y eficiente para BI.
- Esquema copo de nieve: normalización de dimensiones.
- Slowly Changing Dimensions (SCD):
  - Tipo 1: sobrescribir el valor anterior.
  - Tipo 2: agregar nueva fila con historial completo.
  - Tipo 3: agregar columna con valor anterior.
- Implementación práctica con dbt + Snowflake/BigQuery.

**Actividad práctica:**  
Modelar un esquema estrella completo para el área de ventas: definir granularidad, tablas de hechos y dimensiones. Implementarlo en un DWH cloud.

```sql
-- Tabla de Hechos (métricas del negocio)
CREATE TABLE fact_ventas (
  id_venta    BIGINT PRIMARY KEY,
  id_tiempo   INT REFERENCES dim_tiempo(id_tiempo),
  id_cliente  INT REFERENCES dim_cliente(id_cliente),
  id_producto INT REFERENCES dim_producto(id_producto),
  cantidad    INT,
  total_venta DECIMAL(12,2),
  margen      DECIMAL(12,2)
);

-- SCD Tipo 2: cliente se muda de Córdoba a Buenos Aires
UPDATE dim_cliente
SET valid_to = '2024-03-15', is_current = FALSE
WHERE id_cliente = 501 AND is_current = TRUE;

INSERT INTO dim_cliente (id_cliente, ciudad, valid_from, is_current)
VALUES (501, 'Buenos Aires', '2024-03-16', TRUE);
-- Resultado: historial completo de dónde vivió el cliente
```

> 💡 **Concepto clave:** Esquema estrella: fact table al centro, dimensiones alrededor. Intuitivo: "¿cuánto vendí (hecho) por producto (dim) por mes (dim_tiempo)?"

**Bibliografía:** Kimball, R. — *The Data Warehouse Toolkit* (Cap. 3-5). dbt Documentation: Dimensional Modeling Guide.

---

### UNIDAD V · Arquitecturas Modernas y Proyecto Integrador
> Data Lake, Data Lakehouse, Medallion Architecture con Delta Lake, y presentación del proyecto integrador end-to-end.

---

#### Clase 11 — Data Lake, Lakehouse y Medallion Architecture
**Modalidad:** Práctica

**Contenidos:**
- Data Lake: zonas Raw, Staged y Curated. Organización y gobernanza.
- Problemas del Data Lake tradicional: el "data swamp".
- Delta Lake: transacciones ACID sobre almacenamiento de objetos. Time Travel.
- Medallion Architecture: capas Bronze, Silver y Gold.
- Apache Iceberg y Apache Hudi: alternativas open source.
- Data Lakehouse: convergencia de DW y Data Lake. Databricks y Azure Synapse.

**Actividad práctica:**  
Demo: ingestar datos crudos en capa Bronze, transformar a Silver con validaciones, y generar agregados en capa Gold usando Delta Lake.

```python
from pyspark.sql.functions import to_date

# BRONZE — ingestión cruda sin modificar
raw = spark.read.json('s3://lake/raw/ventas/2024-03-15/')
raw.write.format('delta').mode('append').save('s3://lake/bronze/ventas/')

# SILVER — limpieza y estandarización
bronze = spark.read.format('delta').load('s3://lake/bronze/ventas/')
silver = (bronze
    .filter('id_venta IS NOT NULL')
    .withColumn('fecha', to_date('fecha_str', 'dd/MM/yyyy'))
    .dropDuplicates(['id_venta']))
silver.write.format('delta').mode('overwrite').save('s3://lake/silver/ventas/')

# GOLD — KPIs para consumo analítico
gold = silver.groupBy('fecha', 'pais', 'categoria').agg(
    {'total_venta': 'sum', 'id_venta': 'count'})
gold.write.format('delta').mode('overwrite').save('s3://lake/gold/kpi_ventas/')
```

> 💡 **Concepto clave:** Bronze = copia fiel del origen. Silver = limpio y confiable. Gold = listo para dashboards y ML. Delta Lake habilita Time Travel sobre cada capa.

**Bibliografía:** Databricks Documentation. Delta Lake Docs (delta.io). Reis & Housley — *Fundamentals of Data Engineering* (Cap. 6).

---

#### Clase 12 — Proyecto Integrador y Tendencias
**Modalidad:** Evaluación

**Contenidos:**
- Presentación y defensa de proyectos grupales: pipeline ETL completo end-to-end.
- El proyecto debe demostrar: fuente real → extracción → transformación → calidad → esquema estrella en DWH cloud → DAG de orquestación.
- Criterios de evaluación: completitud, calidad del código, decisiones de diseño.
- Revisión integradora: arquitectura, extracción, transformación, calidad y modelado.
- Tendencias actuales: DataOps, MLOps y datos para IA.
- Ingeniería de datos en tiempo real: Apache Kafka + Flink.
- Próximos pasos: certificaciones, recursos y rutas de aprendizaje.

**Actividad:**  
Presentación grupal (15–20 min por equipo): diseño, implementación y demo del pipeline integrador. Feedback del grupo y docente.

> 💡 **Concepto clave:** La ingeniería de datos se aprende haciendo. El mapa es la teoría; el territorio se conoce construyendo pipelines reales, rompiendo cosas y arreglándolas.

**Bibliografía:** Reis, J. & Housley, M. — *Fundamentals of Data Engineering*. Recursos: DataTalks.Club, dbt Learn, Databricks Academy.

---

## Sistema de Evaluación

| Instancia | Descripción | Peso |
|-----------|-------------|------|
| Participación activa | Intervención en debates, ejercicios en clase y laboratorios. | **10%** |
| Trabajos prácticos (×4) | Entrega de ejercicios prácticos de las Unidades II, III y IV. | **30%** |
| Evaluación parcial (Unidades I–III) | Prueba escrita + resolución de caso sobre ETL y calidad del dato. | **25%** |
| Proyecto integrador | Pipeline de datos completo: extracción, transformación, carga, calidad y modelado. Presentación grupal. | **35%** |

---

## Stack Tecnológico del Curso

| Categoría | Herramientas |
|-----------|-------------|
| Lenguajes | Python 3.x · SQL |
| ETL / Transformación | pandas · dbt · Apache Airflow |
| Integración / Extracción | Airbyte · requests · Debezium (CDC) |
| Bases de Datos | PostgreSQL · MongoDB · Redis · Neo4j |
| Calidad del Dato | Great Expectations · OpenMetadata |
| Data Warehouse Cloud | Snowflake · BigQuery · DuckDB (local) |
| Arquitectura Lakehouse | Delta Lake · Databricks CE · Apache Iceberg |
| Control de Versiones | Git · GitHub · dbt Cloud |

---

## Bibliografía Central

- **Kimball, R. & Ross, M.** — *The Data Warehouse Toolkit* (3.ª ed.)
- **Inmon, W.H.** — *Building the Data Warehouse*
- **Reis, J. & Housley, M.** — *Fundamentals of Data Engineering* (O'Reilly, 2022)
- **Kleppmann, M.** — *Designing Data-Intensive Applications* (O'Reilly)
- **McKinney, W.** — *Python for Data Analysis*
- **Davenport, T.** — *Competing on Analytics*
- **Ladley, J.** — *Data Governance* (2nd ed.)
- **DAMA International** — *DAMA-DMBOK: Data Management Body of Knowledge*
- **Harenslak & de Ruiter** — *Data Pipelines with Apache Airflow* (Manning)
- Recursos online: dbt Docs · Apache Airflow Docs · Databricks Academy · DataTalks.Club

---

*Ingeniería de Datos · 5 Unidades · 12 Clases · Modalidad Teórico-Práctica*  
*Ing. Sergio Orozco — Arquitecto de Datos · Infra Cloud · Experto en Big Data*
