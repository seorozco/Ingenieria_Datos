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
