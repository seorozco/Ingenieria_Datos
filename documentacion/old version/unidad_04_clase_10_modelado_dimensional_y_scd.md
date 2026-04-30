# Unidad IV · Clase 10 — Modelado Dimensional y Slowly Changing Dimensions

> **Asignatura:** Ingeniería de Datos  
> **Docente:** Ing. Sergio Orozco  
> **Unidad:** IV — Data Warehouse y Modelado Dimensional  
> **Modalidad:** Teórico-Práctica

---

## Objetivos de la Clase

Al finalizar esta clase, el alumno será capaz de:

- Comprender el **modelado dimensional** como metodología de diseño para Data Warehouses analíticos.
- Definir qué es una **tabla de hechos**, identificar sus métricas, establecer su **granularidad** y distinguir sus tres tipos principales.
- Definir qué son las **tablas de dimensiones** y diseñar sus atributos, jerarquías y claves sustitutas.
- Construir un **esquema estrella** completo para un dominio de negocio.
- Comparar el esquema estrella con el **esquema copo de nieve** y justificar cuándo usar cada uno.
- Comprender el problema de los datos que cambian con el tiempo y aplicar las tres estrategias de **Slowly Changing Dimensions (SCD)**.
- Implementar un esquema estrella y SCDs con SQL y Python.

---

## 1. ¿Qué es el Modelado Dimensional?

El **modelado dimensional** es una técnica de diseño de bases de datos desarrollada por **Ralph Kimball** específicamente para sistemas analíticos (Data Warehouses y Data Marts). Su objetivo es organizar los datos de manera que sean:

- **Intuitivos para los analistas de negocio:** el modelo refleja cómo el negocio piensa en sus datos, no cómo los sistemas los almacenan.
- **Eficientes para las consultas analíticas:** minimiza la cantidad de JOINs necesarios y aprovecha el almacenamiento columnar.
- **Consistentes:** el mismo modelo puede crecer con nuevas métricas y dimensiones sin romper lo existente.

### El contraste con el modelo normalizado

El modelo relacional normalizado (3FN) que se usa en sistemas OLTP distribuye la información en muchas tablas pequeñas para eliminar la redundancia. Es perfecto para escritura transaccional, pero terrible para consultas analíticas.

**Ejemplo:** Para responder "¿Cuánto se vendió del producto Laptop en la región Patagonia en el Q3 2024?", un sistema normalizado necesitaría:

```sql
SELECT SUM(dp.cantidad * dp.precio_unit)
FROM detalle_pedidos dp
JOIN pedidos p ON dp.id_pedido = p.id_pedido
JOIN clientes c ON p.id_cliente = c.id_cliente
JOIN ciudades ci ON c.id_ciudad = ci.id_ciudad
JOIN provincias pr ON ci.id_provincia = pr.id_provincia
JOIN regiones r ON pr.id_region = r.id_region
JOIN productos prod ON dp.id_producto = prod.id_producto
JOIN categorias cat ON prod.id_categoria = cat.id_categoria
WHERE r.nombre = 'Patagonia'
  AND prod.nombre = 'Laptop'
  AND p.fecha BETWEEN '2024-07-01' AND '2024-09-30';
```

7 JOINs. En una tabla con 100 millones de filas de detalle de pedidos, esto puede tardar minutos.

Con un esquema dimensional, la misma consulta se convierte en:

```sql
SELECT SUM(f.total_venta)
FROM fact_ventas f
JOIN dim_producto p ON f.id_producto = p.id_producto
JOIN dim_cliente c ON f.id_cliente = c.id_cliente
JOIN dim_tiempo t ON f.id_tiempo = t.id_tiempo
WHERE p.nombre_producto = 'Laptop'
  AND c.region = 'Patagonia'
  AND t.trimestre = 3
  AND t.anio = 2024;
```

4 JOINs, y todos contra tablas pequeñas de dimensiones (miles de filas), no contra tablas de transacciones (millones de filas). La diferencia de performance puede ser de 10x a 100x.

---

## 2. Los Dos Componentes Fundamentales: Hechos y Dimensiones

El modelado dimensional se basa en dos tipos de tablas con roles completamente distintos:

### 2.1 Tablas de Hechos (*Fact Tables*)

La tabla de hechos es el **corazón del modelo dimensional**. Contiene:

1. **Las métricas del negocio** (hechos): los valores numéricos que el negocio quiere analizar. Ejemplos: cantidad vendida, monto de venta, margen, costo, kilómetros recorridos, segundos de reproducción.

2. **Las claves foráneas** hacia cada dimensión: son los ejes de análisis bajo los cuales se pueden cortar y filtrar las métricas.

#### Tipos de métricas (hechos)

**Métricas aditivas:** se pueden sumar en cualquier dimensión. Son las más útiles y comunes.
- Ejemplo: `cantidad_vendida`, `monto_venta`. Tiene sentido sumarlos por región, por mes, por producto o por cualquier combinación.

**Métricas semi-aditivas:** se pueden sumar en algunas dimensiones pero no en todas.
- Ejemplo: `saldo_cuenta_bancaria`. Tiene sentido sumarlo por cliente en un momento dado (saldo total del cliente), pero NO tiene sentido sumarlo en el tiempo (el saldo de enero + saldo de febrero no es el saldo del semestre).

**Métricas no aditivas:** no tiene sentido sumarlas.
- Ejemplo: `precio_unitario` (el precio de venta de un producto), `margen_porcentual`. Promediarlos puede tener sentido, sumarlos no.

#### Granularidad: la decisión más importante del modelado

La **granularidad** define qué representa **una fila** en la tabla de hechos. Es la decisión de diseño más crítica y debe tomarse antes de cualquier otra.

Granularidades posibles para una tabla de ventas:

| Nivel de granularidad | ¿Qué es una fila? | Filas estimadas |
|---|---|---|
| Por línea de factura | Cada producto de cada factura | Muy alto (millones/año) |
| Por factura | Cada factura | Alto (cientos de miles/año) |
| Por cliente por día | Total vendido a un cliente en un día | Medio |
| Por producto por día | Total de un producto vendido en un día | Medio |
| Por mes | Ventas mensuales totales | Bajo (cientos/año) |

**Regla de oro de Kimball:** siempre preferir la **granularidad más detallada posible**. Se puede agregar hacia arriba en cualquier momento; si el dato no está al nivel de detalle, no se puede desagregar. Una tabla de hechos con granularidad de línea de factura permite responder tanto "¿cuánto se vendió en enero?" como "¿cuántas unidades del SKU X-4521 se vendieron el 15 de enero a las 14:32?".

#### Tipos de tablas de hechos

**1. Fact Table Transaccional (Transaction Fact Table)**

Cada fila representa un **evento puntual** del negocio en el tiempo. Es el tipo más común y el más granular.

```
Ejemplo: fact_ventas_linea
Una fila = una línea de producto en una factura

id_tiempo     | id_cliente | id_producto | id_vendedor | id_tienda | cantidad | precio_unit | descuento | total_neto
──────────────|────────────|─────────────|─────────────|───────────|──────────|─────────────|───────────|───────────
20250115      | 4521       | 101         | 22          | 5         | 2        | 1500.00     | 0.10      | 2700.00
20250115      | 4521       | 203         | 22          | 5         | 1        | 850.00      | 0.00      |  850.00
20250116      | 3310       | 101         | 18          | 3         | 1        | 1500.00     | 0.05      | 1425.00
```

**Cuándo usarlo:** análisis de ventas, transacciones bancarias, clicks en e-commerce, eventos de log.

---

**2. Fact Table de Snapshot Periódico (Periodic Snapshot Fact Table)**

Captura el **estado de un proceso en intervalos regulares** (diario, semanal, mensual). Cada fila es una fotografía de la situación en un momento dado.

```
Ejemplo: fact_inventario_diario
Una fila = estado del inventario de un SKU al cierre de cada día

id_tiempo     | id_producto | id_deposito | stock_disponible | stock_reservado | stock_transito
──────────────|─────────────|─────────────|─────────────────|─────────────────|───────────────
20250115      | 101         | 1           | 450             | 30              | 100
20250115      | 101         | 2           | 120             | 10              | 0
20250116      | 101         | 1           | 420             | 35              | 100
20250116      | 101         | 2           | 110             | 10              | 50
```

**Cuándo usarlo:** inventario diario, saldo de cuentas bancarias, métricas de pipeline de ventas (oportunidades en cada etapa del funnel).

---

**3. Fact Table de Snapshot Acumulado (Accumulating Snapshot Fact Table)**

Modela un **proceso de flujo con etapas definidas**, donde una misma fila se actualiza a medida que el proceso avanza. Cada fila representa el ciclo de vida completo de una instancia del proceso.

```
Ejemplo: fact_ciclo_pedido
Una fila = el ciclo de vida completo de un pedido

id_pedido | id_tiempo_pedido | id_tiempo_pago | id_tiempo_despacho | id_tiempo_entrega | dias_pedido_pago | dias_pago_despacho | dias_despacho_entrega | monto
──────────|──────────────────|────────────────|────────────────────|───────────────────|──────────────────|────────────────────|───────────────────────|─────────
P-10021   | 20250110         | 20250112       | 20250114           | 20250118          | 2                | 2                  | 4                     | 12500.00
P-10022   | 20250111         | NULL           | NULL               | NULL              | NULL             | NULL               | NULL                  | 8900.00
```

Cuando el pedido P-10022 sea pagado, la fila se **actualiza** con la fecha de pago y los días transcurridos. Esto contrasta con la fact transaccional, donde los registros nunca se modifican.

**Cuándo usarlo:** ciclo de vida de pedidos, proceso de contratación de empleados, flujo de reclamaciones de seguros, pipeline de oportunidades comerciales.

---

### 2.2 Tablas de Dimensiones (*Dimension Tables*)

Las dimensiones son el **contexto descriptivo** que da significado a las métricas de la tabla de hechos. Responden las preguntas: *¿quién?, ¿qué?, ¿cuándo?, ¿dónde?, ¿cómo?*

#### Características de las tablas de dimensiones

- **Muchas columnas, pocas filas:** tienen decenas o incluso cientos de columnas descriptivas (atributos), pero pocas filas comparadas con la fact table. Una dimensión de productos puede tener 10.000 filas con 60 columnas; la fact table puede tener 500 millones de filas con 8 columnas.

- **Clave sustituta (Surrogate Key):** la dimensión tiene su propia clave numérica secuencial (`id_producto`, `id_cliente`) que es independiente de la clave del sistema fuente. Esto es esencial para manejar SCDs y para aislar el DWH de cambios en los sistemas operativos.

- **Desnormalizadas (flat):** en el modelo dimensional, las dimensiones no se normalizan internamente. Los atributos de jerarquía se mantienen en la misma tabla. Esto es una diferencia radical respecto al modelo relacional normalizado.

**Ejemplo: dim_producto normalizado vs. desnormalizado**

```
Modelo NORMALIZADO (como vendría del ERP — incorrecto para el DWH):

Tabla producto:          Tabla subcategoria:      Tabla categoria:
id_producto (PK)         id_subcategoria (PK)     id_categoria (PK)
nombre_producto          nombre_subcategoria      nombre_categoria
id_subcategoria (FK)  →  id_categoria (FK)     →  departamento

Modelo DESNORMALIZADO (correcto para el DWH — dim_producto plana):

dim_producto:
  id_producto (SK)           ← clave sustituta
  codigo_sku                 ← clave del negocio (del ERP)
  nombre_producto
  descripcion
  peso_kg
  color
  talla
  nombre_subcategoria        ← aplanado desde tabla subcategoria
  nombre_categoria           ← aplanado desde tabla categoria
  departamento               ← aplanado desde tabla categoria
  marca
  proveedor_principal
  fecha_lanzamiento
  activo (S/N)
```

#### La Dimensión Tiempo (*dim_tiempo*)

Es la dimensión presente en prácticamente todos los Data Marts. No se usa simplemente el campo de fecha en la fact table: se crea una dimensión explícita con todos los atributos temporales posibles precalculados.

**¿Por qué no usar directamente el campo fecha?**

Porque el usuario de negocio no piensa en fechas sino en períodos: "el trimestre 3", "los fines de semana", "el año fiscal 2024 (que va de julio a junio)", "los días hábiles". Precalcular todos estos atributos en `dim_tiempo` permite filtrar y agrupar con SQL simple sin funciones de fecha en cada consulta.

```
dim_tiempo — estructura completa:

id_tiempo          → 20250315 (formato YYYYMMDD, clave sustituta)
fecha              → 2025-03-15 (tipo DATE)
dia_numero         → 15
dia_nombre         → Sábado
dia_semana_numero  → 7 (1=Lunes, 7=Domingo)
es_fin_de_semana   → TRUE
es_dia_habil       → FALSE
semana_iso         → 11
mes_numero         → 3
mes_nombre         → Marzo
mes_nombre_corto   → Mar
trimestre          → 1
nombre_trimestre   → Q1-2025
semestre           → 1
anio               → 2025
anio_mes           → 202503
anio_trimestre     → 20251
es_feriado_arg     → FALSE
periodo_fiscal     → FY2025-Q3  (si el año fiscal es julio-junio)
```

Con esta dimensión, una consulta como "ventas en días hábiles de Q1 2025" es simplemente:

```sql
SELECT SUM(f.total_venta)
FROM fact_ventas f
JOIN dim_tiempo t ON f.id_tiempo = t.id_tiempo
WHERE t.trimestre = 1
  AND t.anio = 2025
  AND t.es_dia_habil = TRUE;
```

#### Jerarquías en las Dimensiones

Una jerarquía es una estructura de niveles de agregación dentro de una dimensión. En la dimensión de geografía, por ejemplo:

```
País
  └── Región
        └── Provincia
              └── Ciudad
                    └── Código Postal
```

En el modelo dimensional (desnormalizado), todos estos niveles viven como columnas en la misma tabla `dim_geografia`:

```
id_geografia | codigo_postal | ciudad       | provincia  | region     | pais
─────────────|───────────────|──────────────|────────────|────────────|──────────
1001         | C1001AAB      | Buenos Aires | CABA       | Centro     | Argentina
1002         | X5000         | Córdoba      | Córdoba    | Centro     | Argentina
1003         | M5500         | Mendoza      | Mendoza    | Cuyo       | Argentina
```

Esto permite agregar las ventas en cualquier nivel de la jerarquía con un simple GROUP BY.

---

## 3. El Esquema Estrella

El **esquema estrella** (*star schema*) es el patrón de diseño más utilizado en el modelado dimensional. Se llama así porque visualmente la tabla de hechos está al centro y las dimensiones la rodean como puntas de una estrella.

### 3.1 Estructura del Esquema Estrella

```
                    ┌───────────────────┐
                    │   dim_tiempo      │
                    │───────────────────│
                    │ id_tiempo (PK)    │
                    │ fecha             │
                    │ dia_nombre        │
                    │ mes_nombre        │
                    │ trimestre         │
                    │ anio              │
                    │ es_fin_de_semana  │
                    └─────────┬─────────┘
                              │
┌─────────────────┐           │           ┌──────────────────────┐
│  dim_cliente    │           │           │    dim_producto       │
│─────────────────│           │           │──────────────────────│
│ id_cliente (PK) │           │           │ id_producto (PK)     │
│ nombre_cliente  │           │           │ nombre_producto       │
│ segmento        │           │           │ subcategoria          │
│ ciudad          │           │           │ categoria             │
│ provincia       │─────────► ◄ ─────────│ departamento          │
│ region          │    ┌──────────────┐   │ marca                 │
│ pais            │    │ fact_ventas  │   │ proveedor             │
│ canal           │    │──────────────│   │ precio_lista          │
└─────────────────┘    │ id_tiempo    │   └──────────────────────┘
                       │ id_cliente   │
┌─────────────────┐    │ id_producto  │    ┌──────────────────────┐
│  dim_vendedor   │    │ id_vendedor  │    │    dim_canal_venta   │
│─────────────────│    │ id_canal     │    │──────────────────────│
│ id_vendedor(PK) │    │──────────────│    │ id_canal (PK)        │
│ nombre          │    │ cantidad     │    │ nombre_canal          │
│ region          │◄───│ precio_unit  │───►│ tipo_canal            │
│ zona            │    │ descuento    │    │ es_digital            │
│ meta_mensual    │    │ total_venta  │    └──────────────────────┘
│ comision_pct    │    │ costo        │
└─────────────────┘    │ margen       │
                       └──────────────┘
```

### 3.2 Ventajas del Esquema Estrella

- **Simplicidad:** el analista de negocio puede entender el modelo mirando el diagrama. No hay que explicar 40 tablas normalizadas; hay una fact table y sus dimensiones.

- **Rendimiento:** los JOINs son siempre entre la fact table (grande) y las dimensiones (pequeñas). El optimizador de consultas del DWH puede procesar estos patrones de forma muy eficiente.

- **Compatibilidad con herramientas de BI:** Power BI, Tableau y Looker están optimizadas para trabajar con esquemas estrella. Detectan automáticamente las relaciones y construyen la capa semántica.

- **Facilidad de extensión:** agregar una nueva dimensión o una nueva métrica requiere alterar solo la fact table y crear la nueva dimensión. Los análisis existentes no se rompen.

### 3.3 Diseñar el Esquema Estrella: Proceso Paso a Paso

Kimball propone los siguientes 4 pasos para diseñar cualquier modelo dimensional:

**Paso 1: Elegir el proceso de negocio**  
Identificar el proceso que se va a modelar. Ejemplos: ventas minoristas, gestión de pedidos, control de inventario, llamadas de call center, reproducción de contenido streaming.

**Paso 2: Establecer la granularidad**  
Definir qué representa una fila en la fact table. Esta decisión determina todo lo demás.

**Paso 3: Identificar las dimensiones**  
Listar todos los ejes de análisis posibles para ese proceso. Para ventas: tiempo, producto, cliente, vendedor, tienda, canal, promoción.

**Paso 4: Identificar los hechos (métricas)**  
Listar todas las métricas numéricas que deben medirse en esa granularidad. Para ventas: cantidad, precio unitario, descuento, total neto, costo, margen.

---

### 3.4 Implementación SQL del Esquema Estrella

```sql
-- ─────────────────────────────────────────
-- DIMENSIÓN TIEMPO
-- ─────────────────────────────────────────
CREATE TABLE dim_tiempo (
    id_tiempo         INTEGER      PRIMARY KEY,  -- Formato YYYYMMDD
    fecha             DATE         NOT NULL,
    dia_numero        SMALLINT     NOT NULL,
    dia_nombre        VARCHAR(10)  NOT NULL,
    es_fin_de_semana  BOOLEAN      NOT NULL,
    es_dia_habil      BOOLEAN      NOT NULL,
    semana_iso        SMALLINT     NOT NULL,
    mes_numero        SMALLINT     NOT NULL,
    mes_nombre        VARCHAR(15)  NOT NULL,
    trimestre         SMALLINT     NOT NULL,
    anio              SMALLINT     NOT NULL,
    anio_trimestre    VARCHAR(10)  NOT NULL,   -- Ej: '2025-Q1'
    semestre          SMALLINT     NOT NULL
);

-- ─────────────────────────────────────────
-- DIMENSIÓN CLIENTE
-- ─────────────────────────────────────────
CREATE TABLE dim_cliente (
    id_cliente        SERIAL       PRIMARY KEY,  -- Clave sustituta
    cliente_key       VARCHAR(20)  NOT NULL,     -- Clave del sistema fuente (CRM)
    razon_social      VARCHAR(200) NOT NULL,
    tipo_cliente      VARCHAR(30)  NOT NULL,     -- 'Persona Física' | 'Empresa'
    segmento          VARCHAR(30)  NOT NULL,     -- 'Premium' | 'Estándar' | 'Mayorista'
    ciudad            VARCHAR(100),
    provincia         VARCHAR(100),
    region            VARCHAR(50),
    pais              VARCHAR(50)  NOT NULL DEFAULT 'Argentina',
    canal_adquisicion VARCHAR(50),              -- 'Orgánico' | 'Referido' | 'Digital'
    fecha_alta        DATE,
    -- Columnas SCD Tipo 2 (se explican en la sección 5)
    valid_from        DATE         NOT NULL DEFAULT CURRENT_DATE,
    valid_to          DATE,
    is_current        BOOLEAN      NOT NULL DEFAULT TRUE
);

-- ─────────────────────────────────────────
-- DIMENSIÓN PRODUCTO
-- ─────────────────────────────────────────
CREATE TABLE dim_producto (
    id_producto       SERIAL       PRIMARY KEY,
    producto_key      VARCHAR(30)  NOT NULL,     -- SKU del ERP
    nombre_producto   VARCHAR(200) NOT NULL,
    descripcion       TEXT,
    unidad_medida     VARCHAR(20)  NOT NULL,
    peso_kg           NUMERIC(8,3),
    nombre_subcategoria VARCHAR(100),
    nombre_categoria  VARCHAR(100) NOT NULL,
    departamento      VARCHAR(100) NOT NULL,
    marca             VARCHAR(100),
    proveedor         VARCHAR(200),
    precio_lista      NUMERIC(12,2),
    activo            BOOLEAN      NOT NULL DEFAULT TRUE
);

-- ─────────────────────────────────────────
-- DIMENSIÓN VENDEDOR
-- ─────────────────────────────────────────
CREATE TABLE dim_vendedor (
    id_vendedor       SERIAL       PRIMARY KEY,
    vendedor_key      VARCHAR(20)  NOT NULL,
    nombre_vendedor   VARCHAR(200) NOT NULL,
    zona              VARCHAR(100),
    region            VARCHAR(100),
    equipo            VARCHAR(100),
    cargo             VARCHAR(100),
    fecha_ingreso     DATE,
    activo            BOOLEAN      NOT NULL DEFAULT TRUE
);

-- ─────────────────────────────────────────
-- TABLA DE HECHOS: VENTAS (granularidad: línea de factura)
-- ─────────────────────────────────────────
CREATE TABLE fact_ventas (
    -- Claves foráneas a las dimensiones
    id_tiempo         INTEGER      NOT NULL REFERENCES dim_tiempo(id_tiempo),
    id_cliente        INTEGER      NOT NULL REFERENCES dim_cliente(id_cliente),
    id_producto       INTEGER      NOT NULL REFERENCES dim_producto(id_producto),
    id_vendedor       INTEGER      REFERENCES dim_vendedor(id_vendedor),

    -- Clave de degeneración (datos de la transacción sin dimensión propia)
    numero_factura    VARCHAR(20)  NOT NULL,
    linea_factura     SMALLINT     NOT NULL,

    -- Métricas (hechos)
    cantidad          NUMERIC(10,3) NOT NULL,
    precio_unitario   NUMERIC(12,2) NOT NULL,
    descuento_pct     NUMERIC(5,4)  NOT NULL DEFAULT 0,
    descuento_monto   NUMERIC(12,2) NOT NULL DEFAULT 0,
    total_bruto       NUMERIC(14,2) NOT NULL,
    total_neto        NUMERIC(14,2) NOT NULL,
    costo_unitario    NUMERIC(12,2),
    costo_total       NUMERIC(14,2),
    margen_bruto      NUMERIC(14,2),

    -- Clave compuesta como PK
    PRIMARY KEY (numero_factura, linea_factura)
);

-- Índices para mejorar el rendimiento de las consultas más frecuentes
CREATE INDEX idx_fv_tiempo    ON fact_ventas(id_tiempo);
CREATE INDEX idx_fv_cliente   ON fact_ventas(id_cliente);
CREATE INDEX idx_fv_producto  ON fact_ventas(id_producto);
```

### 3.5 Consultas analíticas sobre el Esquema Estrella

Una vez construido el modelo, las consultas de negocio son directas e intuitivas:

```sql
-- ¿Cuáles fueron los 5 productos más vendidos (por monto) en Q1 2025?
SELECT
    p.nombre_producto,
    p.nombre_categoria,
    SUM(f.total_neto)       AS total_ventas,
    SUM(f.cantidad)         AS unidades_vendidas,
    AVG(f.precio_unitario)  AS precio_promedio
FROM fact_ventas f
JOIN dim_producto p ON f.id_producto = p.id_producto
JOIN dim_tiempo t   ON f.id_tiempo   = t.id_tiempo
WHERE t.anio      = 2025
  AND t.trimestre = 1
GROUP BY p.nombre_producto, p.nombre_categoria
ORDER BY total_ventas DESC
LIMIT 5;


-- ¿Cuál fue la evolución mensual de ventas por región en 2024?
SELECT
    t.mes_nombre,
    t.mes_numero,
    c.region,
    SUM(f.total_neto)  AS total_ventas,
    COUNT(DISTINCT f.numero_factura) AS num_facturas
FROM fact_ventas f
JOIN dim_tiempo   t ON f.id_tiempo  = t.id_tiempo
JOIN dim_cliente  c ON f.id_cliente = c.id_cliente
WHERE t.anio = 2024
GROUP BY t.mes_nombre, t.mes_numero, c.region
ORDER BY t.mes_numero, total_ventas DESC;


-- ¿Cuál es el margen bruto promedio por categoría y canal?
-- (Solo para categorías con más de $500.000 en ventas)
SELECT
    p.nombre_categoria,
    v.zona,
    SUM(f.total_neto)                        AS ventas_totales,
    SUM(f.margen_bruto)                      AS margen_total,
    ROUND(AVG(f.margen_bruto / NULLIF(f.total_neto, 0)) * 100, 2) AS margen_pct_promedio
FROM fact_ventas f
JOIN dim_producto p  ON f.id_producto = p.id_producto
JOIN dim_vendedor v  ON f.id_vendedor = v.id_vendedor
GROUP BY p.nombre_categoria, v.zona
HAVING SUM(f.total_neto) > 500000
ORDER BY margen_pct_promedio DESC;
```

---

## 4. El Esquema Copo de Nieve

El **esquema copo de nieve** (*snowflake schema*) es una variación del esquema estrella donde las dimensiones están **normalizadas internamente**: sus jerarquías se separan en tablas adicionales relacionadas.

### 4.1 Comparación Visual

**Esquema Estrella** (dim_producto plana):
```
fact_ventas ──► dim_producto
                  nombre_producto
                  nombre_subcategoria  ← aplanado
                  nombre_categoria     ← aplanado
                  departamento         ← aplanado
```

**Esquema Copo de Nieve** (dim_producto normalizada):
```
fact_ventas ──► dim_producto
                  nombre_producto
                  id_subcategoria (FK) ──► dim_subcategoria
                                              nombre_subcategoria
                                              id_categoria (FK) ──► dim_categoria
                                                                        nombre_categoria
                                                                        id_departamento (FK) ──► dim_departamento
                                                                                                   departamento
```

### 4.2 Cuándo Usar Copo de Nieve

La elección entre estrella y copo de nieve es un balance entre tres factores:

| Factor | Estrella | Copo de Nieve |
|---|---|---|
| **Performance de queries** | Mejor (menos JOINs) | Peor (más JOINs) |
| **Espacio en disco** | Más (datos redundantes en dims) | Menos (normalizado) |
| **Complejidad de mantenimiento** | Menor | Mayor |
| **Mantenibilidad al cambiar jerarquías** | Más impacto | Menos impacto |
| **Comprensibilidad para el analista** | Mayor | Menor |

**Cuándo preferir el Copo de Nieve:**
- Las dimensiones son muy grandes (millones de filas con muchos atributos redundantes) y el ahorro de espacio es significativo.
- Las jerarquías cambian con mucha frecuencia y actualizarlas en una tabla plana sería costoso.
- El equipo tiene fuerte background en modelado relacional y se siente más cómodo.

**En la práctica:** La gran mayoría de las implementaciones modernas prefiere el **esquema estrella**. Los Data Warehouses cloud tienen almacenamiento barato, por lo que la redundancia no es un problema relevante, y la ganancia en performance y simplicidad supera ampliamente el ahorro de espacio.

---

## 5. Slowly Changing Dimensions (SCD): El Problema del Cambio

Hasta ahora asumimos que los datos de las dimensiones son estáticos. Pero en la realidad, los datos descriptivos **cambian con el tiempo**:

- Un cliente se muda a otra ciudad.
- Un producto cambia de categoría o de nombre.
- Un vendedor cambia de zona o de equipo.
- Un proveedor cambia sus condiciones.

¿Qué hacemos cuando un cliente que antes vivía en Córdoba se muda a Buenos Aires y luego hace una compra? ¿La asignamos a Córdoba (su ciudad histórica) o a Buenos Aires (su ciudad actual)?

La respuesta correcta depende del contexto de análisis:
- Para un análisis de "¿dónde viven nuestros clientes actualmente?": Buenos Aires.
- Para un análisis de "¿qué compraron los clientes de Córdoba en 2023?": Córdoba (la ciudad que tenían en ese momento).

Este dilema es lo que Ralph Kimball denominó el problema de las **Slowly Changing Dimensions** (Dimensiones de Cambio Lento): cómo manejar atributos de dimensiones que cambian gradualmente con el tiempo.

Kimball definió tres estrategias principales:

---

### 5.1 SCD Tipo 1: Sobrescribir (Overwrite)

La estrategia más simple: **se sobreescribe el valor antiguo con el nuevo**. No se guarda ningún historial del valor anterior.

**Cuándo usarlo:** cuando el valor anterior no tiene ningún valor analítico. Por ejemplo, corregir un error de tipeo en el nombre del cliente, o actualizar un número de teléfono.

#### Ejemplo: Cliente cambia su número de teléfono

**Estado antes del cambio:**
```
id_cliente | nombre         | telefono       | ciudad
──────────|────────────────|────────────────|──────────────
4521      | María García   | +54 11 1234-56 | Buenos Aires
```

**Operación SCD Tipo 1 (UPDATE):**
```sql
UPDATE dim_cliente
SET telefono = '+54 11 9876-54'
WHERE id_cliente = 4521;
```

**Estado después del cambio:**
```
id_cliente | nombre         | telefono       | ciudad
──────────|────────────────|────────────────|──────────────
4521      | María García   | +54 11 9876-54 | Buenos Aires
```

El número anterior desapareció. Si alguien intenta saber cuál era el teléfono de María antes de marzo, no podrá saberlo. Esto es aceptable cuando ese historial no interesa.

**Implicancias:** Todos los reportes históricos que usen ese atributo mostrarán el nuevo valor, incluso para análisis de períodos pasados. Si alguien analiza "ventas por ciudad en 2023" y María se mudó en 2024, el análisis correcto mostrará sus ventas de 2023 asignadas a Buenos Aires (donde vive ahora), no a la ciudad donde vivía en 2023. Esto puede ser incorrecto analíticamente.

---

### 5.2 SCD Tipo 2: Agregar Nueva Fila con Historial Completo

La estrategia más poderosa y más utilizada. Cuando un atributo cambia, **se cierra el registro vigente y se agrega un registro nuevo** con el nuevo valor. Se conserva el historial completo.

**Mecanismo:**
- Cada fila tiene tres columnas de control: `valid_from` (desde cuándo es válida), `valid_to` (hasta cuándo), `is_current` (si es la versión vigente).
- La fact table apunta siempre a la clave sustituta (`id_cliente`), no a la clave del negocio. Cada versión histórica tiene su propia `id_cliente`.

**Cuándo usarlo:** cuando es necesario analizar datos históricos con los atributos que el registro tenía *en ese momento*. Cambio de ciudad, cambio de segmento, cambio de zona de un vendedor.

#### Ejemplo: Cliente María García se muda de Córdoba a Buenos Aires

**Estado inicial (01/01/2023):**
```
id_cliente | cliente_key | nombre       | ciudad       | valid_from | valid_to   | is_current
──────────|─────────────|──────────────|──────────────|────────────|────────────|───────────
1001      | CLI-4521    | María García | Córdoba      | 2023-01-01 | NULL       | TRUE
```

**Proceso SCD Tipo 2 (cuando se detecta el cambio el 15/03/2024):**

```sql
-- PASO 1: Cerrar el registro vigente
UPDATE dim_cliente
SET
    valid_to    = '2024-03-14',
    is_current  = FALSE
WHERE cliente_key = 'CLI-4521'
  AND is_current  = TRUE;

-- PASO 2: Insertar el nuevo registro con el valor actualizado
INSERT INTO dim_cliente
    (cliente_key, nombre,         ciudad,         valid_from,   valid_to, is_current)
VALUES
    ('CLI-4521',  'María García', 'Buenos Aires', '2024-03-15', NULL,     TRUE);
```

**Estado después del cambio:**
```
id_cliente | cliente_key | nombre       | ciudad        | valid_from | valid_to   | is_current
──────────|─────────────|──────────────|───────────────|────────────|────────────|───────────
1001      | CLI-4521    | María García | Córdoba       | 2023-01-01 | 2024-03-14 | FALSE
1002      | CLI-4521    | María García | Buenos Aires  | 2024-03-15 | NULL       | TRUE
```

**Consulta analítica: ventas de María García por ciudad HISTÓRICA**

Cuando la fact table registró las ventas de 2023, apuntaba a `id_cliente = 1001` (la versión de Córdoba). Cuando registre ventas de 2024, apuntará a `id_cliente = 1002` (la versión de Buenos Aires).

```sql
-- Esta consulta retorna correctamente las ventas de 2023 asignadas a Córdoba
-- y las de 2024 asignadas a Buenos Aires
SELECT
    c.ciudad,
    t.anio,
    SUM(f.total_neto) AS ventas
FROM fact_ventas f
JOIN dim_cliente c ON f.id_cliente = c.id_cliente  -- Usa la SK, no la NK
JOIN dim_tiempo  t ON f.id_tiempo  = t.id_tiempo
WHERE c.cliente_key = 'CLI-4521'
GROUP BY c.ciudad, t.anio
ORDER BY t.anio;

-- Resultado esperado:
-- ciudad        | anio | ventas
-- Córdoba       | 2023 | 45000.00
-- Buenos Aires  | 2024 | 28500.00
```

**Implicancias del SCD Tipo 2:**
- La fact table **no cambia**: las relaciones históricas están preservadas por las claves sustitutas.
- La dimensión crece con el tiempo (más filas por cada cambio).
- Para ver el estado actual del cliente, siempre filtrar por `is_current = TRUE` o `valid_to IS NULL`.
- La clave de negocio (`cliente_key`) permite rastrear todas las versiones históricas de un mismo cliente real.

---

### 5.3 SCD Tipo 3: Agregar Columna con Valor Anterior

Se agrega una nueva columna a la dimensión para guardar el **valor anterior** del atributo. Conserva el historial de un único cambio (el más reciente).

**Cuándo usarlo:** cuando solo interesa comparar el estado actual con el estado inmediatamente anterior, y no se necesita historial completo. Por ejemplo: análisis del impacto de una reorganización comercial (zona anterior vs. zona actual de los vendedores).

#### Ejemplo: Vendedor cambia de zona

**Estado inicial:**
```
id_vendedor | nombre         | zona_actual | zona_anterior | fecha_cambio_zona
───────────|────────────────|─────────────|───────────────|───────────────────
22         | Juan López     | Norte       | NULL          | NULL
```

**Operación SCD Tipo 3:**
```sql
UPDATE dim_vendedor
SET
    zona_anterior      = zona_actual,
    zona_actual        = 'Sur',
    fecha_cambio_zona  = '2024-06-01'
WHERE id_vendedor = 22;
```

**Estado después:**
```
id_vendedor | nombre         | zona_actual | zona_anterior | fecha_cambio_zona
───────────|────────────────|─────────────|───────────────|───────────────────
22         | Juan López     | Sur         | Norte         | 2024-06-01
```

Ahora se puede comparar las ventas del vendedor por su zona anterior vs. su zona actual, pero solo para esos dos estados. Si el vendedor cambia de zona una tercera vez, se perdería el primer registro histórico.

**Limitación:** Solo conserva un nivel de historial. Para cambios frecuentes o cuando se necesita historial completo, es insuficiente.

---

### 5.4 Resumen Comparativo de SCDs

| Tipo | Estrategia | ¿Conserva historial? | Complejidad | Cuándo usarlo |
|---|---|---|---|---|
| **Tipo 1** | Sobreescribir | No | Baja | Corrección de errores, atributos sin valor histórico |
| **Tipo 2** | Nueva fila | Sí (completo) | Alta | Ciudad, segmento, zona — análisis histórico crítico |
| **Tipo 3** | Nueva columna | Sí (solo 1 cambio) | Media | Comparar estado actual vs. anterior tras reorganización |

> **Nota práctica:** En la mayoría de los Data Warehouses, la **dim_tiempo nunca aplica SCD** (el tiempo no cambia su descripción). La **dim_producto** suele ser Tipo 1 o Tipo 2 según el atributo. La **dim_cliente** y **dim_vendedor** suelen ser Tipo 2 para los atributos geográficos y de segmento.

---

## 6. Implementación de SCD Tipo 2 con Python

Cuando el proceso ETL corre diariamente y detecta cambios en las fuentes, debe aplicar automáticamente la lógica SCD correspondiente.

```python
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from datetime import date

def aplicar_scd_tipo2(
    df_fuente: pd.DataFrame,
    conexion_str: dict,
    tabla_dimension: str,
    clave_negocio: str,
    columnas_a_monitorear: list[str],
    fecha_proceso: date
) -> dict:
    """
    Aplica la lógica SCD Tipo 2 sobre una tabla de dimensión.

    Para cada registro en df_fuente:
    - Si no existe en la dimensión → INSERT como nuevo registro.
    - Si existe y algún atributo monitorado cambió → cierra el registro vigente
      (UPDATE valid_to y is_current=FALSE) e INSERT el nuevo.
    - Si existe y no hubo cambios → no hace nada.

    Retorna un diccionario con estadísticas del proceso.
    """
    conn = psycopg2.connect(**conexion_str)
    cursor = conn.cursor()

    stats = {"sin_cambios": 0, "nuevos": 0, "actualizados": 0}

    for _, fila_fuente in df_fuente.iterrows():
        clave = fila_fuente[clave_negocio]

        # Obtener el registro vigente de la dimensión para esta clave
        cursor.execute(
            f"""
            SELECT {', '.join(columnas_a_monitorear)}
            FROM {tabla_dimension}
            WHERE {clave_negocio} = %s
              AND is_current = TRUE;
            """,
            (clave,)
        )
        registro_actual = cursor.fetchone()

        if registro_actual is None:
            # CASO 1: Registro nuevo — no existe en la dimensión
            valores_nuevos = {col: fila_fuente[col] for col in columnas_a_monitorear}
            valores_nuevos[clave_negocio] = clave
            valores_nuevos["valid_from"]  = fecha_proceso
            valores_nuevos["valid_to"]    = None
            valores_nuevos["is_current"]  = True

            cols = list(valores_nuevos.keys())
            vals = list(valores_nuevos.values())
            placeholders = ", ".join(["%s"] * len(cols))
            cursor.execute(
                f"INSERT INTO {tabla_dimension} ({', '.join(cols)}) VALUES ({placeholders})",
                vals
            )
            stats["nuevos"] += 1

        else:
            # Comparar atributos monitoreados con los valores de la fuente
            hay_cambio = any(
                str(registro_actual[i]) != str(fila_fuente[col])
                for i, col in enumerate(columnas_a_monitorear)
            )

            if hay_cambio:
                # CASO 2: Cambio detectado — aplicar SCD Tipo 2

                # Paso A: Cerrar el registro vigente
                cursor.execute(
                    f"""
                    UPDATE {tabla_dimension}
                    SET valid_to   = %s,
                        is_current = FALSE
                    WHERE {clave_negocio} = %s
                      AND is_current = TRUE;
                    """,
                    (fecha_proceso - pd.Timedelta(days=1), clave)
                )

                # Paso B: Insertar el nuevo registro actualizado
                valores_nuevos = {col: fila_fuente[col] for col in columnas_a_monitorear}
                valores_nuevos[clave_negocio] = clave
                valores_nuevos["valid_from"]  = fecha_proceso
                valores_nuevos["valid_to"]    = None
                valores_nuevos["is_current"]  = True

                cols = list(valores_nuevos.keys())
                vals = list(valores_nuevos.values())
                placeholders = ", ".join(["%s"] * len(cols))
                cursor.execute(
                    f"INSERT INTO {tabla_dimension} ({', '.join(cols)}) VALUES ({placeholders})",
                    vals
                )
                stats["actualizados"] += 1

            else:
                # CASO 3: Sin cambios — no hacer nada
                stats["sin_cambios"] += 1

    conn.commit()
    cursor.close()
    conn.close()

    print(f"SCD Tipo 2 completado en '{tabla_dimension}':")
    print(f"  Nuevos:       {stats['nuevos']}")
    print(f"  Actualizados: {stats['actualizados']}")
    print(f"  Sin cambios:  {stats['sin_cambios']}")
    return stats


# ─────────────────────────────────────────
# Uso de ejemplo
# ─────────────────────────────────────────
# Datos frescos desde el CRM (la fuente de verdad de clientes)
df_clientes_hoy = pd.DataFrame({
    "cliente_key": ["CLI-4521", "CLI-3310", "CLI-8800"],
    "nombre":      ["María García", "Juan López",  "Ana Torres"],
    "ciudad":      ["Buenos Aires", "Rosario",     "Mendoza"],   # María cambió de Córdoba
    "segmento":    ["Premium",      "Estándar",    "Premium"],
    "region":      ["Centro",       "Litoral",     "Cuyo"],
})

conexion = {
    "host": "localhost",
    "dbname": "dw_ventas",
    "user": "data_engineer",
    "password": "contraseña"
}

resultado = aplicar_scd_tipo2(
    df_fuente=df_clientes_hoy,
    conexion_str=conexion,
    tabla_dimension="dim_cliente",
    clave_negocio="cliente_key",
    columnas_a_monitorear=["nombre", "ciudad", "segmento", "region"],
    fecha_proceso=date.today()
)
```

---

## 7. Cargar la Dimensión Tiempo con Python

La dimensión tiempo no viene de ningún sistema fuente: se genera programáticamente para un rango de fechas determinado.

```python
import pandas as pd
from sqlalchemy import create_engine
import holidays  # pip install holidays

def generar_dim_tiempo(fecha_inicio: str, fecha_fin: str) -> pd.DataFrame:
    """
    Genera la tabla dim_tiempo completa para el rango de fechas especificado.
    Incluye feriados nacionales de Argentina.
    """
    fechas = pd.date_range(start=fecha_inicio, end=fecha_fin, freq="D")
    feriados_arg = holidays.Argentina(years=fechas.year.unique().tolist())

    filas = []
    for fecha in fechas:
        dia_semana = fecha.weekday()  # 0=Lunes, 6=Domingo
        filas.append({
            "id_tiempo":        int(fecha.strftime("%Y%m%d")),
            "fecha":            fecha.date(),
            "dia_numero":       fecha.day,
            "dia_nombre":       fecha.strftime("%A"),
            "dia_semana_numero": dia_semana + 1,
            "es_fin_de_semana": dia_semana >= 5,
            "es_feriado_arg":   fecha.date() in feriados_arg,
            "es_dia_habil":     dia_semana < 5 and fecha.date() not in feriados_arg,
            "semana_iso":       fecha.isocalendar()[1],
            "mes_numero":       fecha.month,
            "mes_nombre":       fecha.strftime("%B"),
            "mes_nombre_corto": fecha.strftime("%b"),
            "trimestre":        fecha.quarter,
            "anio_trimestre":   f"{fecha.year}-Q{fecha.quarter}",
            "semestre":         1 if fecha.month <= 6 else 2,
            "anio":             fecha.year,
            "anio_mes":         int(fecha.strftime("%Y%m")),
        })

    return pd.DataFrame(filas)


# Generar y cargar en el DWH
df_tiempo = generar_dim_tiempo("2020-01-01", "2030-12-31")

engine = create_engine(
    "postgresql+psycopg2://data_engineer:contraseña@localhost:5432/dw_ventas"
)
df_tiempo.to_sql(
    name="dim_tiempo",
    con=engine,
    schema="dw",
    if_exists="replace",
    index=False,
    method="multi",
    chunksize=500
)

print(f"dim_tiempo cargada: {len(df_tiempo)} fechas generadas.")
print(df_tiempo[["id_tiempo", "fecha", "dia_nombre", "es_dia_habil", "trimestre", "anio"]].head(10))
```

---

## 8. Actividad de la Clase: Modelado Dimensional Completo

### Caso de Estudio: Plataforma de Streaming de Contenido

**Contexto:** Una empresa de streaming tiene los siguientes datos disponibles:
- Cada vez que un usuario inicia la reproducción de un episodio o película, se genera un evento con: timestamp, id_usuario, id_contenido, dispositivo, país, minutos_reproducidos, si completó el contenido.
- Los usuarios tienen: plan de suscripción (básico, estándar, premium), país de registro, edad, género, fecha de alta.
- El contenido tiene: título, tipo (serie/película), género, año de producción, duración, idioma original, si es producción propia.

**Consigna:**

1. **Definir la granularidad** de la tabla de hechos principal. Justificar la elección.

2. **Diseñar el esquema estrella completo**: nombrar todas las tablas (fact y dims) con sus columnas principales.

3. **Identificar las métricas** de la tabla de hechos y clasificarlas como aditivas, semi-aditivas o no aditivas.

4. **Identificar qué atributos de las dimensiones deberían ser SCD Tipo 2** y cuáles SCD Tipo 1. Justificar.

5. **Escribir 3 consultas SQL analíticas** sobre el modelo diseñado que respondan preguntas de negocio relevantes.

---

## Resumen de la Clase

| Concepto | Definición resumida |
|---|---|
| **Modelado dimensional** | Técnica de diseño de DWH que organiza los datos en hechos y dimensiones para facilitar el análisis. |
| **Tabla de hechos** | Contiene las métricas numéricas del negocio y las claves foráneas a las dimensiones. |
| **Granularidad** | Qué representa una fila en la fact table. La decisión más importante del modelo. |
| **Fact Transaccional** | Una fila por evento del negocio (venta, click, pago). Tipo más común. |
| **Fact Snapshot** | Estado de un proceso en intervalos regulares (stock diario, saldo mensual). |
| **Fact Acumulado** | Ciclo de vida completo de un proceso con múltiples etapas (pedido → pago → entrega). |
| **Tabla de dimensión** | Contexto descriptivo de las métricas. Muchos atributos, pocas filas. Desnormalizada. |
| **Clave sustituta (SK)** | Clave numérica propia del DWH, independiente del sistema fuente. Esencial para SCD. |
| **dim_tiempo** | Dimensión con todos los atributos temporales precalculados. Presente en todo Data Mart. |
| **Esquema estrella** | Fact table al centro, dimensiones desnormalizadas alrededor. El estándar de facto. |
| **Esquema copo de nieve** | Variante del estrella con dimensiones normalizadas internamente. Menos común en cloud. |
| **SCD Tipo 1** | Sobreescribir el valor anterior. Sin historial. Para corrección de errores. |
| **SCD Tipo 2** | Agregar nueva fila con el valor nuevo. Historial completo. El más potente y utilizado. |
| **SCD Tipo 3** | Agregar columna con valor anterior. Historial de un solo cambio. |

---

## Bibliografía de la Clase

- **Kimball, R. & Ross, M.** — *The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling*, 3ra edición. Capítulos 2, 3, 4 y 5. Wiley.
- **Kimball, R. & Caserta, J.** — *The Data Warehouse ETL Toolkit*. Wiley.
- **dbt Documentation — Dimensional Modeling Guide** — [docs.getdbt.com](https://docs.getdbt.com/).
- **Documentación oficial de Snowflake — Designing Tables** — [docs.snowflake.com](https://docs.snowflake.com/en/user-guide/table-considerations.html).
- **Documentación de la librería `holidays` para Python** — [pypi.org/project/holidays](https://pypi.org/project/holidays/).
