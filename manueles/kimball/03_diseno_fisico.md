# Arquitectura Kimball · Etapa 3 — Diseño Físico

> **Arquitectura:** Kimball — Bottom-Up  
> **Posición en el ciclo:** Tercera etapa. Traduce el modelo lógico (esquema estrella) en una estructura de base de datos que funciona bien en producción con datos reales y volúmenes reales.

---

## La diferencia entre diseño lógico y diseño físico

El **diseño lógico** (Etapa 2) definió *qué* existe: las tablas, las columnas, los tipos de datos lógicos y las relaciones. Responde a la pregunta: "¿Cómo organizamos la información?"

El **diseño físico** define *cómo* el motor de base de datos almacena y accede a esos datos en disco. Responde a la pregunta: "¿Cómo hacemos que las consultas sean rápidas con millones o miles de millones de filas?"

Un esquema estrella perfectamente diseñado en términos lógicos puede ser inutilizable en producción si el diseño físico no está bien pensado.

---

## 1. Selección de la plataforma técnica

Antes de implementar el diseño físico, el equipo debe haber seleccionado la plataforma de base de datos. Esta decisión depende de factores como el volumen de datos esperado, el presupuesto, la infraestructura existente y los requerimientos de escalabilidad.

### Bases de datos relacionales clásicas (OLAP)

**PostgreSQL + extensión columnar (Citus / pg_analytics)**
- Open source, bajo costo.
- Excelente para volúmenes medianos (< 500 GB de hechos).
- Familiaridad alta en equipos de desarrollo.
- Limitado para escala masiva sin extensiones.

**Amazon Redshift**
- Almacenamiento columnar distribuido.
- Optimizado para consultas analíticas de alta complejidad.
- Escala desde gigabytes hasta petabytes.
- Ideal para organizaciones en AWS.

**Google BigQuery**
- Serverless: no hay que gestionar infraestructura.
- Facturación por query (volumen de datos escaneados).
- Integración nativa con el ecosistema Google.
- Ideal para volúmenes masivos y equipos ágiles.

**Snowflake**
- Separación completa de almacenamiento y cómputo.
- Multi-cloud (AWS, GCP, Azure).
- Escala automática de recursos de cómputo.
- Costo moderado, muy flexible.

### ¿Cómo elegir?

```
VOLUMEN ESPERADO DE FACT TABLE:
  < 10 millones filas      → PostgreSQL puede ser suficiente
  10M - 500M filas         → Redshift, Snowflake, BigQuery
  > 500M filas             → BigQuery, Redshift, Snowflake (arquitecturas cloud)

EQUIPO / EXPERIENCIA:
  Ecosistema AWS           → Redshift
  Ecosistema Google Cloud  → BigQuery
  Multi-cloud / agnóstico  → Snowflake
  On-premise / open source → PostgreSQL + Citus, ClickHouse

PRESUPUESTO:
  Bajo (educativo/startup) → PostgreSQL
  Mediano (empresa)        → Snowflake, Redshift
  Alto (enterprise)        → Snowflake, Redshift, BigQuery (todos son similares)
```

---

## 2. Almacenamiento columnar vs. almacenamiento por filas

Esta es la diferencia técnica fundamental entre una base de datos OLTP y una diseñada para OLAP.

### Almacenamiento por filas (Row Store) — OLTP

```
Fila 1: [1, 2025-03-15, 'CLI-001', 'PROD-042', 10, 500.00, 4500.00]
Fila 2: [2, 2025-03-15, 'CLI-007', 'PROD-018',  5, 320.00, 1600.00]
Fila 3: [3, 2025-03-16, 'CLI-001', 'PROD-091',  2, 800.00, 1600.00]

→ Para recuperar TODA la fila de una transacción: muy eficiente (1 lectura)
→ Para sumar la columna total_neto de todos los registros:
  hay que leer TODAS las columnas de TODAS las filas (ineficiente)
```

### Almacenamiento columnar (Column Store) — OLAP

```
Columna total_neto: [4500.00, 1600.00, 1600.00, ...]  → comprimida, contigua en disco
Columna cantidad:   [10, 5, 2, ...]                   → comprimida, contigua en disco
Columna id_cliente: [1, 7, 1, ...]                    → comprimida, contigua en disco

→ Para sumar total_neto: se lee SOLO esa columna (ultra-eficiente)
→ Para recuperar una fila completa: hay que leer todas las columnas (ineficiente)
```

**El almacenamiento columnar es ideal para OLAP** porque las queries analíticas típicamente acceden a 3-5 columnas de millones de filas, nunca a todas las columnas de una fila.

**Ventajas adicionales del almacenamiento columnar:**
- **Compresión:** los datos de una misma columna son del mismo tipo y tienen patrones similares, lo que permite compresiones de 5x a 10x.
- **Vectorización:** los procesadores modernos pueden operar sobre bloques de valores del mismo tipo de forma muy eficiente (SIMD instructions).

---

## 3. Estrategias de indexación en el esquema estrella

### Índices en la tabla de hechos

La tabla de hechos debe tener índices en cada clave foránea. El motor los usa para hacer JOINs eficientes con las dimensiones.

```sql
-- Índices en la tabla de hechos (PostgreSQL)
CREATE INDEX idx_fact_ventas_tiempo   ON dm_ventas.fact_ventas (id_tiempo);
CREATE INDEX idx_fact_ventas_cliente  ON dm_ventas.fact_ventas (id_cliente);
CREATE INDEX idx_fact_ventas_producto ON dm_ventas.fact_ventas (id_producto);
CREATE INDEX idx_fact_ventas_vendedor ON dm_ventas.fact_ventas (id_vendedor);
CREATE INDEX idx_fact_ventas_canal    ON dm_ventas.fact_ventas (id_canal);

-- Índice compuesto para queries que filtran por tiempo + cliente simultáneamente
CREATE INDEX idx_fact_ventas_tiempo_cliente
    ON dm_ventas.fact_ventas (id_tiempo, id_cliente);
```

### Índices en las tablas de dimensiones

Las dimensiones se consultan con filtros de tipo `WHERE ciudad = 'Córdoba'` o `WHERE categoria = 'Electrónica'`. Estos filtros requieren índices en los atributos más usados.

```sql
-- Índices en dim_cliente (para filtros comunes)
CREATE INDEX idx_dim_cliente_ciudad   ON dm_ventas.dim_cliente (ciudad);
CREATE INDEX idx_dim_cliente_region   ON dm_ventas.dim_cliente (region);
CREATE INDEX idx_dim_cliente_segmento ON dm_ventas.dim_cliente (segmento);
CREATE INDEX idx_dim_cliente_nk       ON dm_ventas.dim_cliente (cliente_nk);

-- Índice en dim_producto
CREATE INDEX idx_dim_producto_cat  ON dm_ventas.dim_producto (categoria);
CREATE INDEX idx_dim_producto_nk   ON dm_ventas.dim_producto (producto_nk);

-- Índice en dim_tiempo (más frecuente: filtros por anio o mes)
CREATE INDEX idx_dim_tiempo_anio   ON dm_ventas.dim_tiempo (anio);
CREATE INDEX idx_dim_tiempo_mes    ON dm_ventas.dim_tiempo (anio, mes_numero);
```

### Índices en bases de datos columnares (Redshift, Snowflake, BigQuery)

En las bases de datos columnares cloud, la indexación tradicional no existe o funciona diferente:

- **Redshift:** usa **Sort Keys** (ordena los datos en disco) y **Distribution Keys** (cómo se distribuyen los datos entre los nodos del clúster).
- **Snowflake:** usa **Clustering Keys** (similar a sort keys); el sistema gestiona la mayor parte de la optimización automáticamente.
- **BigQuery:** usa **Partitioning** y **Clustering** (equivalentes a sort keys y clustering keys).

```sql
-- Redshift: Sort Key y Distribution Key
CREATE TABLE dm_ventas.fact_ventas (
    id_tiempo      INTEGER NOT NULL,
    id_cliente     INTEGER NOT NULL,
    id_producto    INTEGER NOT NULL,
    -- ... resto de columnas ...
)
DISTKEY (id_cliente)          -- distribuir por cliente (alta cardinalidad, JOIN frecuente)
SORTKEY (id_tiempo, id_cliente); -- ordenar por tiempo y cliente (filtros más comunes)

-- BigQuery: Partición por fecha + clustering por cliente y producto
CREATE TABLE dm_ventas.fact_ventas (
    id_tiempo      INT64,
    fecha          DATE,
    id_cliente     INT64,
    id_producto    INT64,
    total_neto     NUMERIC
)
PARTITION BY DATE_TRUNC(fecha, MONTH)   -- una partición por mes
CLUSTER BY id_cliente, id_producto;     -- dentro de cada partición, ordenar por cliente y producto
```

---

## 4. Particionamiento de la tabla de hechos

El **particionamiento** divide la tabla de hechos en segmentos físicos más pequeños basados en un criterio, típicamente el tiempo. Cuando una query filtra por una partición específica, el motor solo lee esa partición y omite el resto (*partition pruning*).

**Sin particionamiento:**
```
Query: "Ventas del mes de marzo 2025"
→ El motor lee TODA la tabla de 500 millones de filas para filtrar
  las que corresponden a marzo 2025 (costoso)
```

**Con particionamiento por mes:**
```
fact_ventas_2025_01  → 5M filas (enero 2025)
fact_ventas_2025_02  → 4.8M filas (febrero 2025)
fact_ventas_2025_03  → 5.2M filas (marzo 2025)  ← solo se lee esta partición
fact_ventas_2025_04  → ...
...

Query: "Ventas del mes de marzo 2025"
→ El motor lee SOLO la partición de marzo: 5.2M filas en vez de 500M (100x más rápido)
```

```sql
-- PostgreSQL: Particionamiento por rango de tiempo
CREATE TABLE dm_ventas.fact_ventas (
    id_tiempo      INTEGER NOT NULL,
    id_cliente     INTEGER NOT NULL,
    id_producto    INTEGER NOT NULL,
    total_neto     NUMERIC(14,2) NOT NULL,
    -- ... más columnas ...
    fecha          DATE NOT NULL  -- columna de particionamiento
) PARTITION BY RANGE (fecha);

-- Crear particiones por trimestre
CREATE TABLE dm_ventas.fact_ventas_2025_q1
    PARTITION OF dm_ventas.fact_ventas
    FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');

CREATE TABLE dm_ventas.fact_ventas_2025_q2
    PARTITION OF dm_ventas.fact_ventas
    FOR VALUES FROM ('2025-04-01') TO ('2025-07-01');
```

---

## 5. Agregados pre-calculados (*Aggregate Tables*)

Las tablas de agregados son resúmenes pre-calculados de la tabla de hechos para los niveles de análisis más frecuentes. Son opcionales, pero pueden acelerar dramáticamente los dashboards de uso intensivo.

**Ejemplo:** Si el 80% de las queries del dashboard ejecutivo consultan ventas totales por mes y región, pre-calcular esa agregación evita que cada query re-calcule lo mismo millones de veces.

```sql
-- Tabla de hechos atómica (granularidad: línea de factura)
dm_ventas.fact_ventas      → 500 millones de filas

-- Tabla de agregado mensual por región y categoría
CREATE TABLE dm_ventas.fact_ventas_mensual_region_cat AS
SELECT
    dt.anio_mes,
    dc.region,
    dp.categoria,
    SUM(f.cantidad)    AS total_cantidad,
    SUM(f.total_neto)  AS total_ventas,
    SUM(f.margen_bruto)AS total_margen,
    COUNT(DISTINCT f.numero_factura) AS num_facturas
FROM dm_ventas.fact_ventas f
JOIN dm_ventas.dim_tiempo  dt ON f.id_tiempo   = dt.id_tiempo
JOIN dm_ventas.dim_cliente dc ON f.id_cliente  = dc.id_cliente
JOIN dm_ventas.dim_producto dp ON f.id_producto = dp.id_producto
GROUP BY dt.anio_mes, dc.region, dp.categoria;

-- Esta tabla tiene < 100.000 filas en vez de 500 millones.
-- Las queries del dashboard ejecutivo se ejecutan en milisegundos.
```

**Regla de Kimball sobre los agregados:**
- Los agregados son una optimización de rendimiento, no una fuente de verdad.
- Siempre deben poder recalcularse a partir de la tabla atómica.
- Cuando la tabla atómica se actualiza, los agregados deben actualizarse también.
- **No deben exponerse directamente a los usuarios:** la capa semántica decide cuándo usar el agregado y cuándo la tabla atómica.

---

## 6. Consideraciones de hardware y sizing

### Estimación del tamaño de la tabla de hechos

Para planificar el almacenamiento necesario:

```
CÁLCULO DE SIZING — fact_ventas

Volumen histórico:
  - Facturas por día: ~500
  - Líneas por factura (promedio): 8
  - Filas por día: 500 × 8 = 4.000
  - Filas por año: 4.000 × 365 = 1.460.000
  - Historial requerido: 3 años
  - Filas totales: 1.460.000 × 3 = 4.380.000 filas

Tamaño por fila:
  - 6 FKs (INTEGER, 4 bytes c/u): 24 bytes
  - 2 VARCHAR (avg 15 bytes c/u): 30 bytes
  - 7 columnas numéricas (8 bytes c/u): 56 bytes
  - Overhead del motor: ~20 bytes
  - Total por fila: ~130 bytes

Tamaño total sin compresión:
  4.380.000 × 130 bytes = 569 MB ≈ 0.6 GB

Con compresión columnar (estimada 5x):
  0.6 GB / 5 = ~120 MB

→ Un Data Mart con 3 años de historial y este volumen de transacciones
  ocupa ~120 MB comprimido. PostgreSQL lo maneja trivialmente.
```

### SLA de rendimiento

El diseño físico debe garantizar que las queries de los dashboards cumplan un **SLA de tiempo de respuesta** definido con los usuarios:

```
SLA de Rendimiento — Data Mart de Ventas
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tipo de Query                     Tiempo Máximo
─────────────────────────────────────────────────
Dashboard ejecutivo (KPIs del mes)   < 3 segundos
Reporte mensual por región           < 10 segundos
Análisis ad-hoc (año completo)       < 30 segundos
Reporte histórico (3 años)           < 60 segundos
```

---

## 7. Estrategia de respaldo y recuperación

El Data Mart debe tener un plan de respaldo claro:

- **Backup completo:** semanal (los domingos).
- **Backup incremental:** diario (después de la carga nocturna).
- **Punto de recuperación (RPO):** máximo 24 horas de pérdida de datos.
- **Tiempo de recuperación (RTO):** el sistema debe estar operativo en menos de 4 horas después de una falla.
- **Prueba de restauración:** mensual, para verificar que los backups son funcionales.

---

## Entregables de la Etapa 3

1. ✅ **Plataforma seleccionada y justificada** (PostgreSQL, Redshift, Snowflake, BigQuery).
2. ✅ **DDL físico completo** con tipos de datos específicos del motor, índices, particionamiento, distribution/sort keys.
3. ✅ **Estimación de tamaño** (sizing) del Data Mart para los próximos 3-5 años.
4. ✅ **Estrategia de indexación** documentada con justificación de cada índice.
5. ✅ **Estrategia de particionamiento** (si aplica por volumen).
6. ✅ **Definición de SLA de rendimiento** validada con los usuarios.
7. ✅ **Plan de respaldo y recuperación** aprobado por el área de infraestructura.

---

## Relación con las etapas siguientes

```
ETAPA 3: Diseño Físico
    ↓ Produce: esquema físico implementado en la base de datos
    ↓ El entorno físico ya está listo para recibir datos

ETAPA 4: Diseño ETL
    → Necesita el esquema físico para escribir las queries de carga
    → Necesita los tipos de datos y constraints exactos

ETAPA 5: BI y Despliegue
    → Las herramientas de BI se conectan al esquema físico
    → Los índices y particiones afectan el rendimiento de los dashboards
```

---

## Lecturas recomendadas

- **Kimball, R., Ross, M., Thornthwaite, W., Mundy, J. & Becker, B.** — *The Data Warehouse Lifecycle Toolkit*, 2da edición. Capítulo 12: "Physical Design". Wiley.
- **Redshift** — Documentación oficial: *Amazon Redshift Database Developer Guide — Table Design*. [docs.aws.amazon.com/redshift](https://docs.aws.amazon.com/redshift/latest/dg/c_designing-tables-best-practices.html)
- **BigQuery** — *BigQuery best practices: Control costs — Partition and cluster tables*. [cloud.google.com/bigquery](https://cloud.google.com/bigquery/docs/best-practices-costs)
- **Snowflake** — *Snowflake Documentation: Clustering Keys & Clustered Tables*. [docs.snowflake.com](https://docs.snowflake.com/en/user-guide/tables-clustering-keys)
- **PostgreSQL** — *PostgreSQL Documentation: Table Partitioning*. [postgresql.org/docs](https://www.postgresql.org/docs/current/ddl-partitioning.html)
