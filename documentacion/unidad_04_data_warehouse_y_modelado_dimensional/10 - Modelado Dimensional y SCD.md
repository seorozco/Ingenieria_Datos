# Clase 10 — Modelado Dimensional y Slowly Changing Dimensions

> **Asignatura:** Ingeniería de Datos  
> **Docente:** Ing. Sergio Orozco  
> **Unidad:** IV — Data Warehouse y Modelado Dimensional

---

## Objetivos de la Clase

Al finalizar esta clase, el alumno será capaz de:

- Comprender el **modelado dimensional** como metodología de diseño para Data Warehouses.
- Definir qué es una **tabla de hechos**, establecer su **granularidad** y distinguir sus tres tipos.
- Diseñar **tablas de dimensiones** con atributos, jerarquías y claves sustitutas.
- Construir un **esquema estrella** completo para un dominio de negocio.
- Comparar el esquema estrella con el **esquema copo de nieve**.
- Aplicar las tres estrategias de **Slowly Changing Dimensions (SCD)**.
- Implementar un esquema estrella y SCDs con SQL y Python.

---

## 1. ¿Qué es el Modelado Dimensional?

El **modelado dimensional** es una técnica de diseño de bases de datos desarrollada por **Ralph Kimball** para sistemas analíticos. Su objetivo es organizar los datos de forma que sean:

- **Intuitivos para los analistas de negocio:** el modelo refleja cómo el negocio piensa en sus datos, no cómo los sistemas los almacenan internamente.
- **Eficientes para consultas analíticas:** minimiza la cantidad de JOINs necesarios.
- **Consistentes y extensibles:** el modelo puede crecer con nuevas métricas y dimensiones sin romper lo existente.

### 1.1 El problema del modelo normalizado para el análisis

En la Clase 09 vimos que los sistemas OLTP usan modelos normalizados (3NF). Para una consulta analítica sobre datos normalizados, se necesitan muchos JOINs:

```sql
-- Pregunta: ¿Cuánto se vendió de Laptops en Patagonia en Q3 2024?
-- En una BD OLTP normalizada necesita 7 JOINs:
SELECT SUM(dp.cantidad * dp.precio_unit)
FROM detalle_pedidos dp
JOIN pedidos p ON dp.id_pedido = p.id_pedido
JOIN clientes c ON p.id_cliente = c.id_cliente
JOIN ciudades ci ON c.id_ciudad = ci.id_ciudad
JOIN provincias pr ON ci.id_provincia = pr.id_provincia
JOIN regiones r ON pr.id_region = r.id_region
JOIN productos prod ON dp.id_producto = prod.id_producto
WHERE r.nombre = 'Patagonia'
  AND prod.nombre = 'Laptop'
  AND p.fecha BETWEEN '2024-07-01' AND '2024-09-30';
-- Puede tardar MINUTOS en producción con millones de registros
```

Con un esquema dimensional (estrella), la misma consulta es:

```sql
-- En un DWH con esquema estrella: solo 4 JOINs sobre tablas pequeñas
SELECT SUM(f.total_neto)
FROM fact_ventas f
JOIN dim_producto p ON f.id_producto = p.id_producto
JOIN dim_cliente c ON f.id_cliente = c.id_cliente
JOIN dim_tiempo t ON f.id_tiempo = t.id_tiempo
WHERE p.nombre_producto = 'Laptop'
  AND c.region = 'Patagonia'
  AND t.trimestre = 3
  AND t.anio = 2024;
-- Tarda SEGUNDOS. Las dimensiones son pequeñas; la fact table usa almacenamiento columnar.
```

---

## 2. Los Dos Componentes: Tablas de Hechos y Tablas de Dimensiones

### 2.1 Tablas de Hechos (*Fact Tables*)

La tabla de hechos es el **corazón del modelo dimensional**. Contiene:

1. **Métricas del negocio** (hechos): los valores numéricos que queremos analizar. Ejemplos: `cantidad_vendida`, `monto_venta`, `costo`, `margen`.
2. **Claves foráneas** hacia cada dimensión: son los ejes de análisis (tiempo, cliente, producto, etc.).

#### Tipos de métricas

| Tipo | Descripción | Ejemplo | ¿Se puede sumar? |
|---|---|---|---|
| **Aditiva** | Se puede sumar en cualquier dimensión | `monto_venta`, `cantidad` | Sí, por cualquier eje |
| **Semi-aditiva** | Se puede sumar en algunas dimensiones pero no en todas | `saldo_cuenta` | Por cliente sí; en el tiempo no |
| **No aditiva** | No tiene sentido sumarla | `precio_unitario`, `margen_%` | Nunca sumar; promediar sí |

#### Granularidad: la decisión más importante

La **granularidad** define qué representa una fila en la tabla de hechos. Esta decisión determina todo lo demás del diseño.

**Ejemplo: distintas granularidades para ventas**

| Granularidad | ¿Qué es una fila? | Volumen estimado |
|---|---|---|
| Por línea de factura | Cada ítem de cada factura | Millones por año |
| Por factura | Cada factura completa | Cientos de miles por año |
| Por cliente por día | Total vendido a un cliente en un día | Decenas de miles por año |
| Por mes | Resumen mensual total | Cientos por año |

> **Regla de oro de Kimball:** siempre preferir la **granularidad más detallada posible**. Se puede agregar hacia arriba con un GROUP BY; si el dato no está al nivel de detalle, jamás se puede desagregar. Una fact table de línea de factura permite responder desde "¿cuánto vendimos en enero?" hasta "¿cuántas unidades del SKU X-4521 se vendieron el 15/01 a las 14:32?".

---

#### Tipos de tablas de hechos

**Tipo 1 — Fact Transaccional**  
Cada fila es un **evento puntual** del negocio. Es el tipo más común y más granular.

```
fact_ventas_linea — (una fila = una línea de producto en una factura)

id_tiempo | id_cliente | id_producto | id_vendedor | num_factura | cantidad | precio_unit | descuento | total_neto
──────────|────────────|─────────────|─────────────|─────────────|──────────|─────────────|───────────|───────────
20250115  | 4521       | 101         | 22          | FAC-10021   | 2        | 1500.00     | 0.10      | 2700.00
20250115  | 4521       | 203         | 22          | FAC-10021   | 1        | 850.00      | 0.00      |  850.00
20250116  | 3310       | 101         | 18          | FAC-10022   | 1        | 1500.00     | 0.05      | 1425.00
```

**Cuándo usarlo:** ventas, transacciones bancarias, clicks, eventos de log.

---

**Tipo 2 — Snapshot Periódico**  
Captura el **estado de un proceso en intervalos regulares** (diario, semanal, mensual).

```
fact_inventario_diario — (una fila = estado del inventario de un SKU al cierre del día)

id_tiempo | id_producto | id_deposito | stock_disponible | stock_reservado | stock_transito
──────────|─────────────|─────────────|─────────────────|─────────────────|───────────────
20250115  | 101         | 1           | 450             | 30              | 100
20250116  | 101         | 1           | 420             | 35              | 100
20250116  | 101         | 2           | 110             | 10              | 50
```

**Cuándo usarlo:** inventario diario, saldo de cuentas bancarias, métricas del funnel de ventas.

---

**Tipo 3 — Snapshot Acumulado**  
Modela un **proceso con etapas definidas**. Una misma fila se va actualizando a medida que el proceso avanza.

```
fact_ciclo_pedido — (una fila = ciclo de vida completo de un pedido)

id_pedido | id_tiempo_pedido | id_tiempo_pago | id_tiempo_despacho | id_tiempo_entrega | dias_pedido_pago | monto
──────────|──────────────────|────────────────|────────────────────|───────────────────|──────────────────|─────────
P-10021   | 20250110         | 20250112       | 20250114           | 20250118          | 2                | 12500.00
P-10022   | 20250111         | NULL           | NULL               | NULL              | NULL             | 8900.00
```

Cuando el pedido P-10022 sea pagado, **la fila se actualiza** con la fecha de pago. Diferencia clave con la fact transaccional: aquí sí se modifican registros.

**Cuándo usarlo:** ciclo de vida de pedidos, proceso de contratación, pipeline de oportunidades comerciales.

---

### 2.2 Tablas de Dimensiones (*Dimension Tables*)

Las dimensiones proveen el **contexto descriptivo** que da significado a las métricas. Responden: *¿quién?, ¿qué?, ¿cuándo?, ¿dónde?, ¿cómo?*

#### Características clave

**Muchas columnas, pocas filas:** `dim_producto` puede tener 60 columnas y 10.000 filas; `fact_ventas` puede tener 8 columnas y 500 millones de filas.

**Clave sustituta (Surrogate Key):** la dimensión tiene su propia clave numérica secuencial (`id_producto`, `id_cliente`) independiente del sistema fuente. Esto es fundamental para manejar cambios históricos (SCDs) y para aislar el DWH.

**Desnormalizadas (flat):** las jerarquías se aplanan en la misma tabla. Esto contrasta con el modelo relacional:

```
Modelo NORMALIZADO (OLTP — incorrecto para DWH):
  tabla producto → subcategoria (FK) → categoria (FK) → departamento (FK)
  Necesita 3 JOINs solo para ver el departamento de un producto.

Modelo DESNORMALIZADO (DWH — correcto):
  dim_producto:
    id_producto           ← clave sustituta
    codigo_sku            ← clave de negocio (del ERP)
    nombre_producto
    nombre_subcategoria   ← aplanado desde tabla subcategoria
    nombre_categoria      ← aplanado desde tabla categoria
    departamento          ← aplanado desde tabla departamento
    marca
    proveedor_principal
    precio_lista
    activo
```

#### La Dimensión Tiempo — La más importante de todas

Está presente en prácticamente todos los Data Marts. No se usa simplemente un campo DATE en la fact table: se crea una **dimensión explícita** con todos los atributos temporales posibles precalculados.

**¿Por qué una tabla y no solo el campo fecha?**

Porque el usuario de negocio no piensa en fechas sino en períodos: "el Q3", "los fines de semana", "el año fiscal 2024 (que va de julio a junio)", "los días hábiles". Precalcular estos atributos en `dim_tiempo` elimina la necesidad de funciones de fecha en cada consulta.

```
dim_tiempo — estructura completa:

id_tiempo          → 20250315        ← formato YYYYMMDD (clave sustituta)
fecha              → 2025-03-15
dia_numero         → 15
dia_nombre         → Sábado
dia_semana_numero  → 7 (1=Lunes, 7=Domingo)
es_fin_de_semana   → TRUE
es_feriado_arg     → FALSE
es_dia_habil       → FALSE           ← FALSE porque es sábado
semana_iso         → 11
mes_numero         → 3
mes_nombre         → Marzo
trimestre          → 1
nombre_trimestre   → Q1-2025
semestre           → 1
anio               → 2025
anio_mes           → 202503
periodo_fiscal     → FY2025-Q3       ← si el año fiscal es julio-junio
```

Con esta dimensión, "ventas en días hábiles del Q1 2025" es simplemente:

```sql
SELECT SUM(f.total_neto)
FROM fact_ventas f
JOIN dim_tiempo t ON f.id_tiempo = t.id_tiempo
WHERE t.trimestre = 1 AND t.anio = 2025 AND t.es_dia_habil = TRUE;
```

---

## 3. El Esquema Estrella

El **esquema estrella** (*star schema*) es el patrón de diseño más usado en modelado dimensional. Visualmente, la tabla de hechos está en el centro y las dimensiones la rodean como puntas de una estrella.

### 3.1 Diagrama del Esquema Estrella

```
                    ┌────────────────────┐
                    │   dim_tiempo       │
                    │────────────────────│
                    │ id_tiempo (PK)     │
                    │ fecha              │
                    │ dia_nombre         │
                    │ mes_nombre         │
                    │ trimestre          │
                    │ anio               │
                    │ es_fin_de_semana   │
                    │ es_dia_habil       │
                    └──────────┬─────────┘
                               │
┌──────────────────┐           │           ┌──────────────────────┐
│  dim_cliente     │           │           │  dim_producto        │
│──────────────────│           │           │──────────────────────│
│ id_cliente (PK)  │           │           │ id_producto (PK)     │
│ nombre           │           │           │ nombre_producto       │
│ segmento         │           │           │ subcategoria          │
│ ciudad           │           │           │ categoria             │
│ provincia        │──────────►│◄──────────│ departamento          │
│ region           │   ┌───────────────┐   │ marca                 │
│ canal_adquis.    │   │  fact_ventas  │   │ precio_lista          │
└──────────────────┘   │───────────────│   └──────────────────────┘
                       │ id_tiempo     │
┌──────────────────┐   │ id_cliente    │   ┌──────────────────────┐
│  dim_vendedor    │   │ id_producto   │   │  dim_canal_venta     │
│──────────────────│   │ id_vendedor   │   │──────────────────────│
│ id_vendedor (PK) │   │ id_canal      │   │ id_canal (PK)        │
│ nombre_vendedor  │   │───────────────│   │ nombre_canal          │
│ zona             │◄──│ cantidad      │──►│ tipo_canal            │
│ region           │   │ precio_unit   │   │ es_digital            │
│ equipo           │   │ descuento_pct │   └──────────────────────┘
│ meta_mensual     │   │ total_neto    │
└──────────────────┘   │ costo         │
                       │ margen_bruto  │
                       └───────────────┘
```

### 3.2 Los 4 Pasos para Diseñar un Esquema Estrella

Kimball define un proceso de 4 pasos:

**1. Elegir el proceso de negocio:** ¿Qué proceso vamos a modelar? Ventas, inventario, reclamos, streaming, pagos.

**2. Establecer la granularidad:** ¿Qué es una fila? Esta decisión impacta todo lo demás.

**3. Identificar las dimensiones:** ¿Cuáles son los ejes de análisis? Para ventas: tiempo, cliente, producto, vendedor, canal, tienda.

**4. Identificar los hechos (métricas):** ¿Qué medimos? Cantidad, precio, descuento, total, costo, margen.

### 3.3 Implementación SQL del Esquema Estrella

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
-- DIMENSIÓN CLIENTE (con columnas SCD Tipo 2)
-- ─────────────────────────────────────────
CREATE TABLE dim_cliente (
    id_cliente        SERIAL       PRIMARY KEY,  -- Clave sustituta
    cliente_key       VARCHAR(20)  NOT NULL,     -- Clave del CRM
    razon_social      VARCHAR(200) NOT NULL,
    tipo_cliente      VARCHAR(30)  NOT NULL,     -- 'Persona Física' | 'Empresa'
    segmento          VARCHAR(30)  NOT NULL,     -- 'Premium' | 'Estándar' | 'Mayorista'
    ciudad            VARCHAR(100),
    provincia         VARCHAR(100),
    region            VARCHAR(50),
    pais              VARCHAR(50)  NOT NULL DEFAULT 'Argentina',
    canal_adquisicion VARCHAR(50),
    fecha_alta        DATE,
    -- Columnas para SCD Tipo 2
    valid_from        DATE         NOT NULL DEFAULT CURRENT_DATE,
    valid_to          DATE,
    is_current        BOOLEAN      NOT NULL DEFAULT TRUE
);

-- ─────────────────────────────────────────
-- DIMENSIÓN PRODUCTO
-- ─────────────────────────────────────────
CREATE TABLE dim_producto (
    id_producto       SERIAL       PRIMARY KEY,
    producto_key      VARCHAR(30)  NOT NULL,    -- SKU del ERP
    nombre_producto   VARCHAR(200) NOT NULL,
    unidad_medida     VARCHAR(20)  NOT NULL,
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
-- TABLA DE HECHOS: VENTAS
-- (granularidad: línea de factura)
-- ─────────────────────────────────────────
CREATE TABLE fact_ventas (
    id_tiempo         INTEGER      NOT NULL REFERENCES dim_tiempo(id_tiempo),
    id_cliente        INTEGER      NOT NULL REFERENCES dim_cliente(id_cliente),
    id_producto       INTEGER      NOT NULL REFERENCES dim_producto(id_producto),
    id_vendedor       INTEGER      REFERENCES dim_vendedor(id_vendedor),
    -- Clave degenerada (identificador de la transacción)
    numero_factura    VARCHAR(20)  NOT NULL,
    linea_factura     SMALLINT     NOT NULL,
    -- Métricas
    cantidad          NUMERIC(10,3) NOT NULL,
    precio_unitario   NUMERIC(12,2) NOT NULL,
    descuento_pct     NUMERIC(5,4)  NOT NULL DEFAULT 0,
    descuento_monto   NUMERIC(12,2) NOT NULL DEFAULT 0,
    total_bruto       NUMERIC(14,2) NOT NULL,
    total_neto        NUMERIC(14,2) NOT NULL,
    costo_unitario    NUMERIC(12,2),
    costo_total       NUMERIC(14,2),
    margen_bruto      NUMERIC(14,2),
    PRIMARY KEY (numero_factura, linea_factura)
);

-- Índices para mejorar performance en consultas frecuentes
CREATE INDEX idx_fv_tiempo   ON fact_ventas(id_tiempo);
CREATE INDEX idx_fv_cliente  ON fact_ventas(id_cliente);
CREATE INDEX idx_fv_producto ON fact_ventas(id_producto);
```

### 3.4 Consultas analíticas sobre el Esquema Estrella

```sql
-- Top 5 productos más vendidos en Q1 2025
SELECT
    p.nombre_producto,
    p.nombre_categoria,
    SUM(f.total_neto)      AS total_ventas,
    SUM(f.cantidad)        AS unidades_vendidas,
    AVG(f.precio_unitario) AS precio_promedio
FROM fact_ventas f
JOIN dim_producto p ON f.id_producto = p.id_producto
JOIN dim_tiempo   t ON f.id_tiempo   = t.id_tiempo
WHERE t.anio = 2025 AND t.trimestre = 1
GROUP BY p.nombre_producto, p.nombre_categoria
ORDER BY total_ventas DESC
LIMIT 5;


-- Evolución mensual de ventas por región en 2024
SELECT
    t.mes_nombre,
    t.mes_numero,
    c.region,
    SUM(f.total_neto)                    AS total_ventas,
    COUNT(DISTINCT f.numero_factura)     AS num_facturas
FROM fact_ventas f
JOIN dim_tiempo  t ON f.id_tiempo  = t.id_tiempo
JOIN dim_cliente c ON f.id_cliente = c.id_cliente
WHERE t.anio = 2024
GROUP BY t.mes_nombre, t.mes_numero, c.region
ORDER BY t.mes_numero, total_ventas DESC;


-- Margen bruto promedio por categoría (solo categorías > $500.000 en ventas)
SELECT
    p.nombre_categoria,
    v.zona,
    SUM(f.total_neto)                                              AS ventas_totales,
    SUM(f.margen_bruto)                                            AS margen_total,
    ROUND(SUM(f.margen_bruto) / NULLIF(SUM(f.total_neto), 0) * 100, 2) AS margen_pct
FROM fact_ventas f
JOIN dim_producto p ON f.id_producto = p.id_producto
JOIN dim_vendedor v ON f.id_vendedor = v.id_vendedor
GROUP BY p.nombre_categoria, v.zona
HAVING SUM(f.total_neto) > 500000
ORDER BY margen_pct DESC;
```

---

## 4. Esquema Estrella vs. Esquema Copo de Nieve

El **esquema copo de nieve** (*snowflake schema*) es una variación donde las dimensiones se **normalizan internamente**: sus jerarquías se separan en tablas adicionales.

```
ESTRELLA (dim_producto plana):
  fact_ventas ──► dim_producto
                    nombre_producto
                    nombre_subcategoria  ← aplanado
                    nombre_categoria     ← aplanado
                    departamento         ← aplanado

COPO DE NIEVE (dim_producto normalizada):
  fact_ventas ──► dim_producto
                    nombre_producto
                    id_subcategoria (FK) ──► dim_subcategoria
                                               nombre
                                               id_categoria (FK) ──► dim_categoria
                                                                        nombre
                                                                        id_depto (FK) ──► dim_departamento
```

| Factor | Estrella | Copo de Nieve |
|---|---|---|
| **Performance de queries** | Mejor (menos JOINs) | Peor (más JOINs) |
| **Espacio en disco** | Más (datos redundantes) | Menos (normalizado) |
| **Complejidad** | Menor | Mayor |
| **Facilidad para el analista** | Mayor | Menor |

**Conclusión práctica:** La gran mayoría de las implementaciones modernas prefiere el esquema **estrella**. Los DWH cloud tienen almacenamiento barato y la ganancia en performance y simplicidad supera ampliamente el ahorro de espacio del copo de nieve.

---

## 5. Slowly Changing Dimensions (SCD)

### 5.1 El Problema

Los atributos de las dimensiones **no son estáticos**: los datos descriptivos cambian con el tiempo.

- Un cliente se muda de Córdoba a Buenos Aires.
- Un producto cambia de categoría o de nombre.
- Un vendedor cambia de zona o de equipo.

**El dilema:** Cuando María García se muda y luego hace una compra, ¿la asignamos a su ciudad antigua (Córdoba) o a la nueva (Buenos Aires)?

- Para "¿dónde viven nuestros clientes hoy?": Buenos Aires.
- Para "¿qué compraron los clientes de Córdoba en 2023?": Córdoba (la que tenía en ese momento).

Este es el problema de las **Slowly Changing Dimensions**: cómo manejar atributos que cambian gradualmente con el tiempo. Kimball definió tres estrategias principales.

---

### 5.2 SCD Tipo 1: Sobrescribir

La estrategia más simple: **se sobreescribe el valor antiguo**. No se guarda historial.

**Cuándo usarlo:** cuando el valor anterior no tiene valor analítico. Corrección de errores tipográficos, actualización de teléfono o email.

```sql
-- Cliente María García actualiza su teléfono
UPDATE dim_cliente
SET telefono = '+54 11 9876-54'
WHERE cliente_key = 'CLI-4521' AND is_current = TRUE;
```

**Estado antes → después:**
```
ANTES:  | 4521 | María García | +54 11 1234-56 | Córdoba      |
DESPUÉS:| 4521 | María García | +54 11 9876-54 | Córdoba      |
```

**⚠️ Implicancia:** todos los reportes históricos mostrarán el nuevo valor. Si alguien analiza las ventas de 2023 y María se mudó en 2024, el análisis mostrará sus ventas de 2023 asignadas a la ciudad nueva (Buenos Aires). Si eso es un problema, usar Tipo 2.

---

### 5.3 SCD Tipo 2: Agregar Nueva Fila (Historial Completo)

La estrategia más poderosa. Cuando un atributo cambia, **se cierra el registro vigente y se agrega uno nuevo** con el valor actualizado. Se conserva el **historial completo**.

Cada fila tiene tres columnas de control:
- `valid_from`: desde cuándo es válida esta versión.
- `valid_to`: hasta cuándo (NULL si es la versión vigente).
- `is_current`: si es la versión activa.

**Cuándo usarlo:** cuando es necesario analizar datos históricos con los atributos que el registro tenía *en ese momento*. Ciudad, segmento de cliente, zona de vendedor.

**Ejemplo: María García se muda de Córdoba a Buenos Aires el 15/03/2024**

```sql
-- PASO 1: Cerrar el registro vigente
UPDATE dim_cliente
SET valid_to   = '2024-03-14',
    is_current = FALSE
WHERE cliente_key = 'CLI-4521' AND is_current = TRUE;

-- PASO 2: Insertar el nuevo registro con la ciudad actualizada
INSERT INTO dim_cliente (cliente_key, nombre, ciudad, valid_from, valid_to, is_current)
VALUES ('CLI-4521', 'María García', 'Buenos Aires', '2024-03-15', NULL, TRUE);
```

**Estado de la dimensión después del cambio:**

```
id_cliente | cliente_key | nombre        | ciudad        | valid_from | valid_to   | is_current
──────────|─────────────|───────────────|───────────────|────────────|────────────|───────────
1001      | CLI-4521    | María García  | Córdoba       | 2023-01-01 | 2024-03-14 | FALSE  ← CERRADO
1002      | CLI-4521    | María García  | Buenos Aires  | 2024-03-15 | NULL       | TRUE   ← VIGENTE
```

**La magia del SCD Tipo 2 con claves sustitutas:**

Cuando el ETL registró ventas de 2023, apuntó a `id_cliente = 1001` (la versión de Córdoba). Cuando registre ventas de 2024, apuntará a `id_cliente = 1002` (la versión de Buenos Aires). Las fact tables históricas **no cambian nunca**.

```sql
-- Ventas de María por ciudad HISTÓRICA — correctas automáticamente
SELECT
    c.ciudad,
    t.anio,
    SUM(f.total_neto) AS ventas
FROM fact_ventas f
JOIN dim_cliente c ON f.id_cliente = c.id_cliente  -- usa la SK, no la NK
JOIN dim_tiempo  t ON f.id_tiempo  = t.id_tiempo
WHERE c.cliente_key = 'CLI-4521'   -- filtra por clave de negocio
GROUP BY c.ciudad, t.anio
ORDER BY t.anio;

-- Resultado:
-- ciudad        | anio | ventas
-- Córdoba       | 2023 | 45000.00   ← correcto: en 2023 vivía en Córdoba
-- Buenos Aires  | 2024 | 28500.00   ← correcto: en 2024 vive en Buenos Aires
```

---

### 5.4 SCD Tipo 3: Agregar Columna con Valor Anterior

Se agrega una columna extra para guardar el **valor anterior** del atributo. Conserva el historial de un único cambio.

**Cuándo usarlo:** cuando solo interesa comparar el estado actual con el inmediatamente anterior. Por ejemplo: análisis del impacto de una reorganización comercial (zona anterior vs. zona actual).

**Ejemplo: Vendedor Juan López cambia de zona Norte a zona Sur**

```sql
-- Agregar columna de historial (se hace una sola vez al diseñar la dimensión)
-- ALTER TABLE dim_vendedor ADD COLUMN zona_anterior VARCHAR(100);
-- ALTER TABLE dim_vendedor ADD COLUMN fecha_cambio_zona DATE;

-- Aplicar el cambio
UPDATE dim_vendedor
SET zona_anterior     = zona_actual,
    zona_actual       = 'Sur',
    fecha_cambio_zona = '2024-06-01'
WHERE vendedor_key = 'VEN-22';
```

**Estado antes → después:**
```
ANTES:  | VEN-22 | Juan López | Norte | NULL     | NULL       |
DESPUÉS:| VEN-22 | Juan López | Sur   | Norte    | 2024-06-01 |
```

**Limitación:** solo conserva un nivel de historial. Si Juan cambia de zona una tercera vez, se pierde el primer valor histórico.

---

### 5.5 Resumen Comparativo de SCDs

```
┌─────────────────────────────────────────────────────────────────────┐
│                    RESUMEN DE ESTRATEGIAS SCD                       │
├──────────┬──────────────────┬───────────────────┬───────────────────│
│ Tipo     │ Estrategia       │ ¿Conserva         │ Cuándo usarlo     │
│          │                  │ historial?        │                   │
├──────────┼──────────────────┼───────────────────┼───────────────────│
│ Tipo 1   │ Sobreescribir    │ NO                │ Corrección de     │
│          │                  │                   │ errores, atrib.   │
│          │                  │                   │ sin valor hist.   │
├──────────┼──────────────────┼───────────────────┼───────────────────│
│ Tipo 2   │ Nueva fila con   │ SÍ (completo)     │ Ciudad, segmento, │
│          │ valid_from/to    │                   │ zona — análisis   │
│          │ y is_current     │                   │ histórico crítico │
├──────────┼──────────────────┼───────────────────┼───────────────────│
│ Tipo 3   │ Nueva columna    │ SÍ (1 solo        │ Comparar estado   │
│          │ valor anterior   │ cambio)           │ actual vs         │
│          │                  │                   │ anterior          │
└──────────┴──────────────────┴───────────────────┴───────────────────┘
```

> **Regla práctica:** `dim_tiempo` nunca necesita SCD. `dim_producto` suele ser Tipo 1 o Tipo 2 según el atributo (el nombre: Tipo 1; la categoría: Tipo 2). `dim_cliente` y `dim_vendedor` suelen ser Tipo 2 para atributos geográficos y de segmento.

---

## 6. Implementación de SCD Tipo 2 con Python

```python
import pandas as pd
import psycopg2
from datetime import date

def aplicar_scd_tipo2(
    df_fuente: pd.DataFrame,
    conexion_params: dict,
    tabla_dimension: str,
    clave_negocio: str,
    columnas_a_monitorear: list,
    fecha_proceso: date
) -> dict:
    """
    Aplica lógica SCD Tipo 2 sobre una tabla de dimensión.

    Para cada registro en df_fuente:
    - Si no existe en la dimensión → INSERT (registro nuevo).
    - Si existe y algún atributo cambió → cierra el vigente + INSERT nuevo.
    - Si existe y no cambió → sin acción.
    """
    conn = psycopg2.connect(**conexion_params)
    cursor = conn.cursor()
    stats = {"sin_cambios": 0, "nuevos": 0, "actualizados": 0}

    for _, fila in df_fuente.iterrows():
        clave = fila[clave_negocio]

        # Consultar el registro vigente en la dimensión
        cursor.execute(
            f"""
            SELECT {', '.join(columnas_a_monitorear)}
            FROM {tabla_dimension}
            WHERE {clave_negocio} = %s AND is_current = TRUE;
            """,
            (clave,)
        )
        registro_actual = cursor.fetchone()

        if registro_actual is None:
            # Caso 1: Registro nuevo
            valores = {col: fila[col] for col in columnas_a_monitorear}
            valores[clave_negocio] = clave
            valores["valid_from"] = fecha_proceso
            valores["valid_to"] = None
            valores["is_current"] = True
            cols = list(valores.keys())
            placeholders = ", ".join(["%s"] * len(cols))
            cursor.execute(
                f"INSERT INTO {tabla_dimension} ({', '.join(cols)}) "
                f"VALUES ({placeholders})",
                list(valores.values())
            )
            stats["nuevos"] += 1

        else:
            # Comparar atributos monitoreados
            hay_cambio = any(
                str(registro_actual[i]) != str(fila[col])
                for i, col in enumerate(columnas_a_monitorear)
            )

            if hay_cambio:
                # Caso 2: Cambio detectado → SCD Tipo 2
                # Paso A: Cerrar el registro vigente
                cursor.execute(
                    f"""
                    UPDATE {tabla_dimension}
                    SET valid_to = %s, is_current = FALSE
                    WHERE {clave_negocio} = %s AND is_current = TRUE;
                    """,
                    (fecha_proceso, clave)
                )
                # Paso B: Insertar nuevo registro
                valores = {col: fila[col] for col in columnas_a_monitorear}
                valores[clave_negocio] = clave
                valores["valid_from"] = fecha_proceso
                valores["valid_to"] = None
                valores["is_current"] = True
                cols = list(valores.keys())
                placeholders = ", ".join(["%s"] * len(cols))
                cursor.execute(
                    f"INSERT INTO {tabla_dimension} ({', '.join(cols)}) "
                    f"VALUES ({placeholders})",
                    list(valores.values())
                )
                stats["actualizados"] += 1
            else:
                # Caso 3: Sin cambios
                stats["sin_cambios"] += 1

    conn.commit()
    cursor.close()
    conn.close()

    print(f"SCD Tipo 2 en '{tabla_dimension}':")
    print(f"  Nuevos:       {stats['nuevos']}")
    print(f"  Actualizados: {stats['actualizados']}")
    print(f"  Sin cambios:  {stats['sin_cambios']}")
    return stats


# Ejemplo de uso:
# df_clientes_hoy viene del CRM — María García cambió de Córdoba a Buenos Aires
df_clientes_hoy = pd.DataFrame({
    "cliente_key": ["CLI-4521", "CLI-3310", "CLI-8800"],
    "nombre":      ["María García", "Juan López",  "Ana Torres"],
    "ciudad":      ["Buenos Aires", "Rosario",     "Mendoza"],
    "segmento":    ["Premium",      "Estándar",    "Premium"],
    "region":      ["Centro",       "Litoral",     "Cuyo"],
})

resultado = aplicar_scd_tipo2(
    df_fuente=df_clientes_hoy,
    conexion_params={
        "host": "localhost", "dbname": "dw_ventas",
        "user": "data_engineer", "password": "contraseña"
    },
    tabla_dimension="dim_cliente",
    clave_negocio="cliente_key",
    columnas_a_monitorear=["nombre", "ciudad", "segmento", "region"],
    fecha_proceso=date.today()
)
```

---

## 7. Generación Automática de la Dimensión Tiempo

```python
import pandas as pd
from sqlalchemy import create_engine
import holidays  # pip install holidays

def generar_dim_tiempo(fecha_inicio: str, fecha_fin: str) -> pd.DataFrame:
    """
    Genera la tabla dim_tiempo completa para un rango de fechas.
    Incluye feriados nacionales de Argentina.
    """
    fechas = pd.date_range(start=fecha_inicio, end=fecha_fin, freq="D")
    feriados_arg = holidays.Argentina(years=fechas.year.unique().tolist())

    filas = []
    for fecha in fechas:
        dia_semana = fecha.weekday()  # 0=Lunes, 6=Domingo
        filas.append({
            "id_tiempo":         int(fecha.strftime("%Y%m%d")),
            "fecha":             fecha.date(),
            "dia_numero":        fecha.day,
            "dia_nombre":        fecha.strftime("%A"),
            "dia_semana_numero": dia_semana + 1,
            "es_fin_de_semana":  dia_semana >= 5,
            "es_feriado_arg":    fecha.date() in feriados_arg,
            "es_dia_habil":      dia_semana < 5 and fecha.date() not in feriados_arg,
            "semana_iso":        fecha.isocalendar()[1],
            "mes_numero":        fecha.month,
            "mes_nombre":        fecha.strftime("%B"),
            "mes_nombre_corto":  fecha.strftime("%b"),
            "trimestre":         fecha.quarter,
            "anio_trimestre":    f"{fecha.year}-Q{fecha.quarter}",
            "semestre":          1 if fecha.month <= 6 else 2,
            "anio":              fecha.year,
            "anio_mes":          int(fecha.strftime("%Y%m")),
        })

    return pd.DataFrame(filas)


# Generar dim_tiempo para 10 años y cargar en el DWH
df_tiempo = generar_dim_tiempo("2020-01-01", "2030-12-31")

engine = create_engine(
    "postgresql+psycopg2://data_engineer:contraseña@localhost:5432/dw_ventas"
)
df_tiempo.to_sql(
    name="dim_tiempo", con=engine, schema="dw",
    if_exists="replace", index=False, method="multi", chunksize=500
)
print(f"dim_tiempo: {len(df_tiempo)} fechas generadas.")
```

---

## Resumen de la Clase

| Concepto | Definición en una frase |
|---|---|
| **Modelado dimensional** | Técnica de diseño de DWH que organiza los datos en hechos y dimensiones para facilitar el análisis |
| **Tabla de hechos** | Contiene las métricas del negocio y las claves foráneas a las dimensiones |
| **Granularidad** | Qué representa una fila en la fact table — la decisión de diseño más importante |
| **Fact Transaccional** | Una fila por evento del negocio (venta, click, pago) |
| **Fact Snapshot Periódico** | Estado de un proceso en intervalos regulares (stock diario, saldo mensual) |
| **Fact Snapshot Acumulado** | Ciclo de vida de un proceso con etapas (pedido → pago → despacho → entrega) |
| **Dimensión** | Tabla con el contexto descriptivo de los hechos (cliente, producto, tiempo) |
| **Surrogate Key** | Clave sustituta numérica de la dimensión, independiente del sistema fuente |
| **Esquema Estrella** | Fact table central rodeada de dimensiones desnormalizadas |
| **Esquema Copo de Nieve** | Variación del estrella con dimensiones normalizadas internamente |
| **SCD Tipo 1** | Sobreescribir — sin historial. Para corrección de errores |
| **SCD Tipo 2** | Nueva fila por cada cambio con `valid_from`/`valid_to` — historial completo |
| **SCD Tipo 3** | Nueva columna para el valor anterior — historial de un solo cambio |

---

> 🎓 **Cierre de la unidad y del programa:** Con esta clase completamos el ciclo completo de la Ingeniería de Datos: desde los fundamentos y fuentes de datos (Unidad I), pasando por los procesos ETL y extracción (Unidad II), la calidad y gobierno del dato (Unidad III), hasta el destino final: el Data Warehouse con su modelado dimensional (Unidad IV). El próximo paso en la carrera de un Data Engineer es profundizar en plataformas específicas (dbt, Airflow, Spark) y arquitecturas modernas como el Lakehouse.
