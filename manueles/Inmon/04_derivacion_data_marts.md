# Arquitectura Inmon · Etapa 4 — Derivación de Data Marts desde el EDW

> **Arquitectura:** Inmon — Top-Down  
> **Posición en el ciclo:** Cuarta etapa. Es donde el EDW produce valor visible para el negocio.

---

## ¿Qué es un Data Mart en la arquitectura Inmon?

Un **Data Mart** es un subconjunto del Enterprise Data Warehouse orientado a un área de negocio específica, diseñado para responder las preguntas analíticas de un grupo particular de usuarios: el equipo de ventas, el área financiera, el departamento de logística, el equipo de marketing.

En el contexto Inmon, los Data Marts tienen dos características fundamentales que los distinguen de los que plantea Kimball:

1. **Se alimentan exclusivamente del EDW**, nunca directamente de los sistemas fuente. Esta regla es absoluta en la arquitectura Inmon. Si un Data Mart necesita un dato, ese dato debe primero estar en el EDW.

2. **Son dependientes** (*dependent Data Marts*): no tienen vida propia en cuanto a la fuente de sus datos. Su contenido es una proyección desnormalizada del EDW para un propósito específico.

Esta dependencia es precisamente la fortaleza más importante del enfoque Inmon: garantiza que **todos los Data Marts de la organización son consistentes entre sí**, porque todos provienen de la misma fuente de verdad.

> **Analogía:** Si el EDW es la panadería central que hornea el pan con los mismos ingredientes y procesos estandarizados, los Data Marts son los locales de venta que ofrecen ese pan en formatos distintos para distintos clientes: baguettes para unos, medialunas para otros, pan de molde para otros. Pero todos vienen de la misma masa, con la misma calidad.

---

## El problema que resuelven los Data Marts

El EDW en 3FN, aunque es consistente y completo, es técnicamente difícil de consultar directamente:

- Requiere muchos JOINs complejos para responder preguntas simples de negocio.
- Los usuarios de negocio no tienen el conocimiento técnico para navegar el modelo normalizado.
- Las herramientas de BI (Power BI, Tableau, Looker) están optimizadas para esquemas desnormalizados.
- Las consultas analíticas complejas sobre el modelo 3FN pueden ser lentas.

Los Data Marts resuelven este problema al **desnormalizar los datos del EDW** en un esquema estrella optimizado para las consultas de cada área, manteniendo la consistencia garantizada por el EDW.

---

## El proceso de derivación: ETL del EDW al Data Mart

La derivación de un Data Mart desde el EDW es en sí misma un proceso ETL, pero más simple que el ETL de los sistemas fuente al EDW, porque:

- Los datos ya están integrados, limpios y estandarizados en el EDW.
- Las reglas de negocio ya están aplicadas.
- El historial ya está resuelto.

El ETL de derivación se enfoca en **desnormalizar** (aplanar las jerarquías), **agregar** (pre-calcular totales si es necesario) y **modelar dimensionalmente** (crear el esquema estrella).

```
┌─────────────────────────────────────────┐
│         ENTERPRISE DATA WAREHOUSE        │
│           (3FN — normalizado)            │
│                                         │
│  edw.cliente  edw.ciudad  edw.provincia │
│  edw.pedido   edw.linea_pedido          │
│  edw.producto edw.categoria             │
│  edw.vendedor edw.zona                  │
└─────────────────┬───────────────────────┘
                  │
        ETL de derivación (desnormalización + modelado dimensional)
                  │
       ┌──────────┼──────────┬────────────┐
       ▼          ▼          ▼            ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│Data Mart │ │Data Mart │ │Data Mart │ │Data Mart │
│ Ventas   │ │Finanzas  │ │Logística │ │Marketing │
│(estrella)│ │(estrella)│ │(estrella)│ │(estrella)│
└──────────┘ └──────────┘ └──────────┘ └──────────┘
```

---

## Diseño dimensional de los Data Marts

En la arquitectura Inmon, el diseño de los Data Marts sigue la metodología dimensional de Kimball (esquema estrella con tablas de hechos y dimensiones). Inmon no tiene una metodología propia de diseño dimensional; reconoce la de Kimball como el estándar.

La diferencia es la **fuente**: en Inmon los Data Marts se alimentan del EDW; en Kimball se alimentan directamente de los sistemas fuente.

### Proceso de diseño del Data Mart

**Paso 1: Identificar el proceso de negocio**

¿Qué proceso de negocio modela este Data Mart? Ejemplos:
- Ventas al cliente final.
- Gestión de pedidos a proveedores.
- Control de inventario.
- Desempeño de la fuerza de ventas.

**Paso 2: Definir la granularidad**

¿Qué representa una fila en la tabla de hechos? Esta es la decisión más importante del diseño.

Para el Data Mart de Ventas:
- ¿Una fila por línea de factura? (más detalle, más filas)
- ¿Una fila por factura total? (menos detalle, menos filas)
- ¿Una fila por cliente por día? (agregado, muy compacto)

Kimball (adoptado por Inmon para los Data Marts) recomienda la mayor granularidad posible.

**Paso 3: Identificar las dimensiones**

¿Bajo qué ejes se analizarán las métricas? Para ventas: tiempo, cliente, producto, vendedor, canal, región.

**Paso 4: Identificar las métricas (hechos)**

¿Qué se mide? Para ventas: cantidad, precio unitario, descuento, total neto, costo, margen.

---

### Ejemplo completo: Data Mart de Ventas derivado del EDW

**Tablas del EDW que participan (normalizadas 3FN):**

```
edw.pedido           → id_pedido, fecha_pedido, id_cliente, id_vendedor, numero_factura
edw.linea_pedido     → id_linea, id_pedido, id_producto, cantidad, precio_unitario, descuento
edw.cliente          → id_cliente, razon_social, id_ciudad, id_segmento, is_vigente
edw.ciudad           → id_ciudad, nombre, id_provincia
edw.provincia        → id_provincia, nombre, id_region
edw.region           → id_region, nombre
edw.segmento         → id_segmento, nombre_segmento
edw.producto         → id_producto, nombre, id_subcategoria, precio_lista, is_vigente
edw.subcategoria     → id_subcategoria, nombre, id_categoria
edw.categoria        → id_categoria, nombre, id_departamento
edw.vendedor         → id_vendedor, nombre, id_zona
edw.zona             → id_zona, nombre, id_region
```

**Data Mart de Ventas resultante (esquema estrella):**

```sql
-- DIMENSIÓN CLIENTE (aplanada desde 5 tablas del EDW)
CREATE TABLE dm_ventas.dim_cliente (
    id_cliente     SERIAL       PRIMARY KEY,
    cliente_key    BIGINT       NOT NULL,        -- id del EDW
    razon_social   VARCHAR(200) NOT NULL,
    segmento       VARCHAR(100),
    ciudad         VARCHAR(100),
    provincia      VARCHAR(100),
    region         VARCHAR(100),
    -- Columnas SCD Tipo 2
    valid_from     DATE         NOT NULL,
    valid_to       DATE,
    is_current     BOOLEAN      NOT NULL DEFAULT TRUE
);

-- DIMENSIÓN PRODUCTO (aplanada desde 4 tablas del EDW)
CREATE TABLE dm_ventas.dim_producto (
    id_producto    SERIAL       PRIMARY KEY,
    producto_key   BIGINT       NOT NULL,
    nombre         VARCHAR(200) NOT NULL,
    subcategoria   VARCHAR(100),
    categoria      VARCHAR(100),
    departamento   VARCHAR(100),
    precio_lista   NUMERIC(12,2),
    is_current     BOOLEAN      NOT NULL DEFAULT TRUE
);

-- DIMENSIÓN VENDEDOR (aplanada desde 2 tablas del EDW)
CREATE TABLE dm_ventas.dim_vendedor (
    id_vendedor    SERIAL       PRIMARY KEY,
    vendedor_key   BIGINT       NOT NULL,
    nombre         VARCHAR(200) NOT NULL,
    zona           VARCHAR(100),
    region         VARCHAR(100),
    is_current     BOOLEAN      NOT NULL DEFAULT TRUE
);

-- DIMENSIÓN TIEMPO (generada programáticamente)
CREATE TABLE dm_ventas.dim_tiempo (
    id_tiempo      INTEGER      PRIMARY KEY,   -- YYYYMMDD
    fecha          DATE         NOT NULL,
    dia_nombre     VARCHAR(15),
    semana_iso     SMALLINT,
    mes_numero     SMALLINT,
    mes_nombre     VARCHAR(15),
    trimestre      SMALLINT,
    anio           SMALLINT,
    es_dia_habil   BOOLEAN
);

-- TABLA DE HECHOS (granularidad: línea de factura)
CREATE TABLE dm_ventas.fact_ventas (
    -- Claves a dimensiones
    id_tiempo      INTEGER      NOT NULL REFERENCES dm_ventas.dim_tiempo,
    id_cliente     INTEGER      NOT NULL REFERENCES dm_ventas.dim_cliente,
    id_producto    INTEGER      NOT NULL REFERENCES dm_ventas.dim_producto,
    id_vendedor    INTEGER      REFERENCES dm_ventas.dim_vendedor,
    -- Clave de degeneración
    numero_factura VARCHAR(30)  NOT NULL,
    linea          SMALLINT     NOT NULL,
    -- Métricas
    cantidad       NUMERIC(10,3) NOT NULL,
    precio_unit    NUMERIC(12,2) NOT NULL,
    descuento_pct  NUMERIC(5,4)  NOT NULL DEFAULT 0,
    total_neto     NUMERIC(14,2) NOT NULL,
    costo          NUMERIC(14,2),
    margen_bruto   NUMERIC(14,2),
    PRIMARY KEY (numero_factura, linea)
);
```

---

## La query de derivación: del EDW al Data Mart

La carga del Data Mart se realiza mediante una consulta que desnormaliza el EDW y aplana todas las jerarquías:

```sql
-- Query de derivación: popula fact_ventas desde el EDW
-- (versión simplificada para ilustración)
INSERT INTO dm_ventas.fact_ventas (
    id_tiempo, id_cliente, id_producto, id_vendedor,
    numero_factura, linea,
    cantidad, precio_unit, descuento_pct, total_neto, costo, margen_bruto
)
SELECT
    -- Clave de tiempo (formato YYYYMMDD)
    TO_CHAR(p.fecha_pedido, 'YYYYMMDD')::INTEGER                AS id_tiempo,

    -- Resolver la clave sustituta del cliente en el Data Mart
    -- usando la versión vigente en la fecha del pedido
    dc.id_cliente                                                AS id_cliente,

    -- Resolver la clave sustituta del producto
    dp.id_producto                                               AS id_producto,

    -- Resolver la clave sustituta del vendedor
    dv.id_vendedor                                               AS id_vendedor,

    p.numero_factura,
    lp.id_linea                                                  AS linea,
    lp.cantidad,
    lp.precio_unitario                                           AS precio_unit,
    lp.descuento,
    lp.cantidad * lp.precio_unitario * (1 - lp.descuento)        AS total_neto,
    lp.costo_unitario * lp.cantidad                              AS costo,
    (lp.cantidad * lp.precio_unitario * (1 - lp.descuento))
        - (lp.costo_unitario * lp.cantidad)                     AS margen_bruto

FROM edw.linea_pedido lp
JOIN edw.pedido p              ON lp.id_pedido   = p.id_pedido
-- JOIN a la versión del cliente vigente en la fecha del pedido (SCD Tipo 2)
JOIN dm_ventas.dim_cliente dc  ON dc.cliente_key = p.id_cliente
                               AND p.fecha_pedido BETWEEN dc.valid_from
                               AND COALESCE(dc.valid_to, '9999-12-31')
-- JOIN a la versión del producto vigente en la fecha del pedido
JOIN dm_ventas.dim_producto dp ON dp.producto_key = lp.id_producto
                               AND dp.is_current = TRUE
-- JOIN al vendedor
LEFT JOIN dm_ventas.dim_vendedor dv ON dv.vendedor_key = p.id_vendedor
                                    AND dv.is_current = TRUE
-- Solo cargar registros más nuevos que la última carga
WHERE p.fecha_pedido > (
    SELECT COALESCE(MAX(t.fecha), '2020-01-01')
    FROM dm_ventas.fact_ventas fv
    JOIN dm_ventas.dim_tiempo t ON fv.id_tiempo = t.id_tiempo
);
```

---

## Consistencia entre Data Marts: el valor diferencial de Inmon

La ventaja más poderosa de la arquitectura Inmon se hace evidente cuando la organización tiene múltiples Data Marts.

**Escenario:** El CFO compara el reporte de ventas del Data Mart de Ventas con el reporte de ingresos del Data Mart de Finanzas. En una organización con Data Marts independientes (Kimball sin dimensiones conformadas), estos números frecuentemente no coinciden porque cada Data Mart tiene su propia lógica de cálculo y sus propios datos.

En Inmon, como **ambos Data Marts se alimentan del mismo EDW**, y el EDW tiene las reglas del glosario corporativo aplicadas de forma centralizada, los números son consistentes por construcción.

```
Dato: "Venta neta de marzo 2025"

Data Mart Ventas:    $4.523.810,00
Data Mart Finanzas:  $4.523.810,00  ← SIEMPRE COINCIDEN (misma fuente: el EDW)

vs. arquitectura sin EDW central:

Data Mart Ventas:    $4.523.810,00  (cuenta facturas emitidas)
Data Mart Finanzas:  $4.298.420,00  (cuenta cobros efectivos, que no son lo mismo)
                     ↑ DIFERENCIA LEGÍTIMA: pero requiere una nota explicativa
                       que solo el EDW puede proveer con definiciones precisas
```

---

## Tipos de Data Marts en la arquitectura Inmon

### Data Mart de resumen (*Summary Data Mart*)

Contiene datos **pre-agregados** para responder consultas de alto nivel de forma instantánea. Ideal para dashboards ejecutivos donde el tiempo de respuesta es crítico.

```
Ejemplo: fact_resumen_ventas_mensual

Una fila = ventas totales de un producto en una región en un mes

region     | categoria | anio | mes | total_ventas | margen_total | num_facturas
───────────|───────────|───────|─────|──────────────|──────────────|─────────────
Patagonia  | Electrónica| 2025 | 3   | 1.250.000,00 | 312.500,00   | 847
Centro     | Electrónica| 2025 | 3   | 3.100.000,00 | 775.000,00   | 2.103
```

**Ventaja:** consultas instantáneas para reportes de alto nivel.  
**Desventaja:** no permite drill-down al detalle transaccional. Debe complementarse con un Data Mart de detalle.

### Data Mart de detalle (*Atomic Data Mart*)

Contiene los datos al nivel más granular posible (línea de transacción). Permite cualquier nivel de análisis, desde el detalle individual hasta el resumen completo.

---

## Patrones Avanzados en los Data Marts Inmon

### Data Marts con múltiples tablas de hechos

Un mismo Data Mart puede contener más de una tabla de hechos si ambas comparten las mismas dimensiones y pertenecen al mismo dominio de negocio.

**Ejemplo: Data Mart de Ventas con hechos de venta y hechos de devolución**

```sql
-- Hecho principal: ventas
CREATE TABLE dm_ventas.fact_ventas (
    id_tiempo      INTEGER NOT NULL REFERENCES dm_ventas.dim_tiempo,
    id_cliente     INTEGER NOT NULL REFERENCES dm_ventas.dim_cliente,
    id_producto    INTEGER NOT NULL REFERENCES dm_ventas.dim_producto,
    numero_factura VARCHAR(30) NOT NULL,
    linea          SMALLINT    NOT NULL,
    cantidad       NUMERIC(10,3) NOT NULL,
    total_neto     NUMERIC(14,2) NOT NULL,
    margen_bruto   NUMERIC(14,2),
    PRIMARY KEY (numero_factura, linea)
);

-- Hecho complementario: devoluciones (mismas dimensiones)
CREATE TABLE dm_ventas.fact_devoluciones (
    id_tiempo         INTEGER NOT NULL REFERENCES dm_ventas.dim_tiempo,
    id_cliente        INTEGER NOT NULL REFERENCES dm_ventas.dim_cliente,
    id_producto       INTEGER NOT NULL REFERENCES dm_ventas.dim_producto,
    numero_nc         VARCHAR(30) NOT NULL,  -- nota de crédito
    linea             SMALLINT    NOT NULL,
    factura_original  VARCHAR(30) NOT NULL,  -- referencia a la venta
    cantidad_devuelta NUMERIC(10,3) NOT NULL,
    monto_devuelto    NUMERIC(14,2) NOT NULL,
    motivo_devolucion VARCHAR(50),
    PRIMARY KEY (numero_nc, linea)
);

-- Ahora el usuario puede analizar:
-- "Ventas netas ajustadas" = fact_ventas.total_neto - fact_devoluciones.monto_devuelto
-- "Tasa de devolución" = fact_devoluciones.cantidad / fact_ventas.cantidad
```

---

### Dimensiones Conformadas entre Data Marts Inmon

En la arquitectura Inmon, las dimensiones conformadas tienen una fuente garantizada: **todas provienen del EDW**. Esto simplifica enormemente la conformación comparado con Kimball (donde las dimensiones se construyen desde los sistemas fuente).

```
EDW (3FN)
├── edw.cliente → genera → dm_ventas.dim_cliente
│                        → dm_finanzas.dim_cliente
│                        → dm_logistica.dim_cliente
│   (misma fuente = mismo contenido = conformadas por construcción)
│
├── edw.producto → genera → dm_ventas.dim_producto
│                         → dm_compras.dim_producto
│                         → dm_inventario.dim_producto
│
└── edw.tiempo → genera → dm_ventas.dim_tiempo
                        → dm_finanzas.dim_tiempo
                        → dm_logistica.dim_tiempo
```

**Implementación práctica: un proceso compartido de generación de dimensiones**

```sql
-- Vista compartida que alimenta dim_cliente en TODOS los Data Marts
CREATE OR REPLACE VIEW edw.v_dim_cliente AS
SELECT
    c.id_cliente       AS cliente_key,
    c.cliente_src_key,
    c.razon_social,
    tc.descripcion     AS tipo_cliente,
    s.nombre           AS segmento,
    ci.nombre          AS ciudad,
    p.nombre           AS provincia,
    pa.nombre          AS pais,
    c.estado,
    c.fecha_efectiva   AS valid_from,
    c.fecha_vencimiento AS valid_to,
    c.es_vigente       AS is_current
FROM edw.cliente c
JOIN edw.tipo_cliente tc ON c.id_tipo     = tc.id_tipo
JOIN edw.ciudad ci       ON c.id_ciudad   = ci.id_ciudad
JOIN edw.provincia p     ON ci.id_provincia = p.id_provincia
JOIN edw.pais pa         ON p.id_pais     = pa.id_pais
LEFT JOIN edw.segmento s ON c.id_segmento = s.id_segmento;

-- Cada Data Mart usa la misma vista para popular su dim_cliente:
INSERT INTO dm_ventas.dim_cliente    SELECT * FROM edw.v_dim_cliente;
INSERT INTO dm_finanzas.dim_cliente  SELECT * FROM edw.v_dim_cliente;
INSERT INTO dm_logistica.dim_cliente SELECT * FROM edw.v_dim_cliente;
```

---

### Tablas de Hechos Periódicas (*Periodic Snapshot*) en el contexto Inmon

El EDW puede generar Data Marts con snapshots periódicos que no existen como tales en el modelo normalizado:

```sql
-- Snapshot mensual de saldos de cuenta corriente
-- (derivado del EDW que almacena cada movimiento individual)
CREATE TABLE dm_finanzas.fact_saldo_mensual (
    id_tiempo_mes  INTEGER NOT NULL,  -- último día del mes
    id_cliente     INTEGER NOT NULL,
    saldo_inicio   NUMERIC(14,2) NOT NULL,
    total_debitos  NUMERIC(14,2) NOT NULL,
    total_creditos NUMERIC(14,2) NOT NULL,
    saldo_cierre   NUMERIC(14,2) NOT NULL,
    dias_mora      INTEGER DEFAULT 0,
    PRIMARY KEY (id_tiempo_mes, id_cliente)
);

-- Query de derivación desde el EDW
INSERT INTO dm_finanzas.fact_saldo_mensual
SELECT
    TO_CHAR(DATE_TRUNC('MONTH', m.fecha) + INTERVAL '1 MONTH - 1 DAY', 'YYYYMMDD')::INT AS id_tiempo_mes,
    dc.id_cliente,
    -- Saldo de inicio: saldo de cierre del mes anterior
    LAG(SUM(CASE WHEN m.tipo = 'D' THEN m.monto ELSE -m.monto END))
        OVER (PARTITION BY m.id_cliente ORDER BY DATE_TRUNC('MONTH', m.fecha)) AS saldo_inicio,
    SUM(CASE WHEN m.tipo = 'D' THEN m.monto ELSE 0 END)  AS total_debitos,
    SUM(CASE WHEN m.tipo = 'C' THEN m.monto ELSE 0 END)   AS total_creditos,
    SUM(CASE WHEN m.tipo = 'D' THEN m.monto ELSE -m.monto END) AS saldo_cierre,
    -- Días de mora: diferencia entre vencimiento y último pago
    MAX(m.dias_mora)                                        AS dias_mora
FROM edw.movimiento_cuenta m
JOIN dm_finanzas.dim_cliente dc ON dc.cliente_key = m.id_cliente AND dc.is_current = TRUE
GROUP BY DATE_TRUNC('MONTH', m.fecha), m.id_cliente, dc.id_cliente;
```

---

## Tests de Consistencia EDW ↔ Data Mart

La regla de oro de Inmon es que **los totales del Data Mart deben coincidir exactamente con los del EDW**. Estos tests se ejecutan automáticamente después de cada derivación:

```sql
-- Test 1: Total de ventas del mes debe coincidir
WITH edw_total AS (
    SELECT SUM(lp.cantidad * lp.precio_unitario * (1 - lp.descuento)) AS total_edw
    FROM edw.linea_pedido lp
    JOIN edw.pedido p ON lp.id_pedido = p.id_pedido
    WHERE p.fecha_pedido BETWEEN '2025-03-01' AND '2025-03-31'
),
dm_total AS (
    SELECT SUM(total_neto) AS total_dm
    FROM dm_ventas.fact_ventas f
    JOIN dm_ventas.dim_tiempo t ON f.id_tiempo = t.id_tiempo
    WHERE t.anio = 2025 AND t.mes_numero = 3
)
SELECT
    edw_total.total_edw,
    dm_total.total_dm,
    ABS(edw_total.total_edw - dm_total.total_dm) AS diferencia,
    CASE WHEN ABS(edw_total.total_edw - dm_total.total_dm) < 0.01
         THEN 'PASS' ELSE 'FAIL' END AS resultado
FROM edw_total, dm_total;

-- Test 2: Cantidad de clientes únicos debe coincidir
WITH edw_cli AS (
    SELECT COUNT(DISTINCT p.id_cliente) AS clientes_edw
    FROM edw.pedido p
    WHERE p.fecha_pedido BETWEEN '2025-03-01' AND '2025-03-31'
),
dm_cli AS (
    SELECT COUNT(DISTINCT f.id_cliente) AS clientes_dm
    FROM dm_ventas.fact_ventas f
    JOIN dm_ventas.dim_tiempo t ON f.id_tiempo = t.id_tiempo
    WHERE t.anio = 2025 AND t.mes_numero = 3
)
SELECT
    edw_cli.clientes_edw,
    dm_cli.clientes_dm,
    CASE WHEN edw_cli.clientes_edw = dm_cli.clientes_dm
         THEN 'PASS' ELSE 'FAIL' END AS resultado
FROM edw_cli, dm_cli;
```

---

## Ejercicio Práctico: Data Mart de Logística

**Contexto:** La empresa necesita analizar los tiempos de entrega para mejorar su servicio logístico.

**Tablas del EDW involucradas:**

```
edw.pedido, edw.entrega, edw.ruta, edw.deposito,
edw.cliente, edw.ciudad, edw.producto
```

**Diseño del Data Mart:**

```sql
-- Dimensiones (conformadas con DM Ventas)
dm_logistica.dim_tiempo     -- reutilizada
dm_logistica.dim_cliente    -- reutilizada
dm_logistica.dim_producto   -- reutilizada

-- Dimensiones propias
CREATE TABLE dm_logistica.dim_deposito (
    id_deposito    SERIAL PRIMARY KEY,
    deposito_key   BIGINT NOT NULL,
    nombre         VARCHAR(100),
    ciudad         VARCHAR(100),
    provincia      VARCHAR(100),
    capacidad_m3   NUMERIC(10,2),
    is_current     BOOLEAN DEFAULT TRUE
);

CREATE TABLE dm_logistica.dim_transportista (
    id_transportista SERIAL PRIMARY KEY,
    nombre           VARCHAR(200),
    tipo             VARCHAR(50),  -- 'Propio', 'Tercerizado'
    is_current       BOOLEAN DEFAULT TRUE
);

-- Tabla de hechos: accumulating snapshot (un pedido = una fila que se actualiza)
CREATE TABLE dm_logistica.fact_ciclo_entrega (
    id_fecha_pedido       INTEGER REFERENCES dim_tiempo,
    id_fecha_preparacion  INTEGER REFERENCES dim_tiempo,
    id_fecha_despacho     INTEGER REFERENCES dim_tiempo,
    id_fecha_entrega      INTEGER REFERENCES dim_tiempo,
    id_cliente            INTEGER NOT NULL REFERENCES dim_cliente,
    id_deposito_origen    INTEGER REFERENCES dim_deposito,
    id_transportista      INTEGER REFERENCES dim_transportista,
    numero_pedido         VARCHAR(30) PRIMARY KEY,
    -- Métricas de duración
    dias_preparacion      INTEGER,  -- preparacion - pedido
    dias_transito         INTEGER,  -- entrega - despacho
    dias_total            INTEGER,  -- entrega - pedido
    -- Métricas de volumen
    bultos                INTEGER,
    peso_kg               NUMERIC(10,2),
    -- Indicadores
    entrega_a_tiempo      BOOLEAN,  -- dias_total <= SLA prometido
    motivo_demora         VARCHAR(100)
);
```

**Preguntas que responde:**
- ¿Cuál es el tiempo promedio de entrega por región?
- ¿Qué transportista tiene mejor tasa de entrega a tiempo?
- ¿Qué depósitos están generando más demoras en la preparación?
- ¿La promesa de entrega se está cumpliendo por segmento de cliente?

---

## Gobierno de los Data Marts

En la arquitectura Inmon, los Data Marts tienen reglas de gobierno que el equipo de datos debe hacer cumplir:

1. **Ningún Data Mart puede conectarse directamente a los sistemas fuente.** Todo dato debe venir del EDW. Esta regla es no negociable.

2. **Cualquier nueva necesidad de datos que no esté en el EDW debe primero agregarse al EDW** (Etapas 2 y 3) antes de llegar al Data Mart.

3. **Los Data Marts no deben contener lógica de negocio nueva** que no haya pasado por el glosario corporativo. Si el área de ventas quiere calcular "venta neta" de forma diferente a la definición del glosario, se debe actualizar el glosario con el acuerdo de todos los Data Owners.

4. **Los Data Marts son de solo lectura** para los usuarios de negocio. Nadie puede insertar ni modificar datos directamente en ellos.

---

## Entregables de la Etapa 4

1. ✅ **Diseño dimensional** de cada Data Mart (esquema estrella con DDL).
2. ✅ **Queries de derivación** documentadas y probadas.
3. ✅ **Definición de granularidad** de cada tabla de hechos, acordada con el área de negocio.
4. ✅ **Diccionario de datos** de cada Data Mart (qué significa cada columna, cómo se calcula).
5. ✅ **Proceso ETL de derivación** implementado y orquestado (Airflow, dbt, etc.).
6. ✅ **Plan de actualización**: con qué frecuencia se actualiza cada Data Mart (diario, horario, en tiempo real).
7. ✅ **Tests de consistencia**: queries que verifican que los números del Data Mart coinciden con los del EDW.

---

## Relación con la etapa siguiente

```
ETAPA 4: Data Marts (derivados del EDW)
        │
        │ Produce:
        │  • Esquemas estrella por área de negocio
        │  • Datos listos para herramientas de BI
        │  • Consistencia garantizada por origen común
        │
        ▼
ETAPA 5: Capa de Acceso Analítico
        │ Las herramientas de BI se conectan a los Data Marts
        │ para construir reportes, dashboards y análisis.
        ▼
```

---

## Lecturas recomendadas

- **Inmon, W.H.** — *Building the Data Warehouse*, 4ta edición. Capítulo 8: "The Data Mart". Wiley.
- **Kimball, R. & Ross, M.** — *The Data Warehouse Toolkit*, 3ra edición. Capítulo 2: "Retail Sales". Wiley. (Para el diseño del esquema estrella del Data Mart).
- **Golfarelli, M. & Rizzi, S.** — *Data Warehouse Design: Modern Principles and Methodologies*. Capítulo 7. McGraw-Hill.
- **Adamson, C.** — *Star Schema: The Complete Reference*. McGraw-Hill. (Patrones avanzados de esquemas estrella).
- **Linstedt, D. & Olschimke, M.** — *Building a Scalable Data Warehouse with Data Vault 2.0*. Morgan Kaufmann. (Alternativa moderna al EDW 3FN de Inmon).
