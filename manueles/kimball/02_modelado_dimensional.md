# Arquitectura Kimball · Etapa 2 — Modelado Dimensional

> **Arquitectura:** Kimball — Bottom-Up  
> **Posición en el ciclo:** Segunda etapa. Es el corazón intelectual de la metodología: el diseño del esquema estrella.

---

## ¿Por qué el modelado dimensional?

El modelado dimensional es la técnica de diseño de bases de datos específicamente optimizada para las consultas analíticas. Fue desarrollado por Ralph Kimball y ha demostrado ser, durante más de 30 años, la forma más efectiva de organizar los datos para el análisis de negocio.

**Las dos metas del modelado dimensional:**

1. **Simplicidad:** el esquema debe ser tan intuitivo que un usuario de negocio, sin conocimiento técnico, pueda entender de qué se trata con solo ver el diagrama.

2. **Performance:** las consultas analíticas deben ejecutarse en segundos, incluso sobre miles de millones de filas.

El modelo dimensional logra ambas metas mediante dos tipos de tablas:
- **Tablas de hechos:** contienen los eventos medibles del negocio (transacciones, pedidos, pagos).
- **Tablas de dimensiones:** contienen el contexto descriptivo de esos eventos (quién, qué, cuándo, dónde, cómo).

---

## Los 4 pasos del proceso de modelado dimensional de Kimball

La metodología Kimball define un proceso de 4 pasos que debe seguirse **en este orden exacto**. Saltear o invertir pasos produce diseños defectuosos.

```
PASO 1          PASO 2              PASO 3           PASO 4
Seleccionar  →  Declarar        →  Identificar   →  Identificar
el proceso      la granularidad     las              los hechos
de negocio                         dimensiones      (métricas)
```

---

## Paso 1: Seleccionar el proceso de negocio

Un **proceso de negocio** es una actividad operativa realizada por la organización que genera datos medibles. Ejemplos:
- Procesar una venta.
- Recibir un pedido de un proveedor.
- Registrar un pago.
- Gestionar un reclamo de cliente.
- Controlar el inventario.

La elección del proceso define el tema central del Data Mart. En la metodología Kimball, **un Data Mart = un proceso de negocio**.

Este paso ya fue realizado en la Etapa 1 (Planificación), donde la Bus Matrix identificó los procesos y el equipo seleccionó el primero a desarrollar.

**Regla de Kimball:** Model events that actually happen in the business world, not the reports you want to produce.

> "Modela los eventos que realmente ocurren en el mundo del negocio, no los reportes que quieres producir."

---

## Paso 2: Declarar la granularidad

La **granularidad** define con precisión qué representa **una fila** en la tabla de hechos. Es la decisión más crítica del diseño.

La declaración de granularidad debe ser:
- **Específica:** no "datos de ventas" sino "una línea de cada factura de venta emitida".
- **Acordada:** validada con los usuarios de negocio y el equipo técnico.
- **Documentada:** escrita en el diccionario de datos del Data Mart.

### Niveles de granularidad posibles

```
PROCESO: Ventas al Cliente
────────────────────────────────────────────────────────────────────

GRANULARIDAD MÁS FINA (atómica):
  "Una fila por cada línea de cada factura"
  Pros: máxima flexibilidad, permite cualquier nivel de agregación
  Contras: mayor volumen de datos

GRANULARIDAD MEDIA:
  "Una fila por cada factura (total de la cabecera)"
  Pros: menos volumen, más simple
  Contras: no puede analizar por producto sin una tabla adicional

GRANULARIDAD AGREGADA:
  "Una fila por cliente por día"
  Pros: muy compacto, ultra-rápido
  Contras: solo permite análisis a nivel de cliente/día; no se puede
           drill-down a producto o transacción individual

RECOMENDACIÓN DE KIMBALL:
  Siempre elegir la granularidad más fina posible (atómica).
  Es más fácil agregar hacia arriba que desagregar hacia abajo.
  Los datos atómicos jamás se quedan sin responder una pregunta.
```

### Declaración formal de granularidad — Ejemplo

```
DECLARACIÓN DE GRANULARIDAD — Data Mart de Ventas
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Proceso:       Ventas al Cliente
Granularidad:  Una fila por cada producto en cada factura de venta
               emitida. Equivale a una línea de factura.

Una fila responde: "El día DD/MM/AAAA, el vendedor V vendió N
unidades del producto P al cliente C a través del canal X,
por un total de $T con un descuento del D%."

Excluye:
  - Devoluciones (proceso separado)
  - Cotizaciones que no se convirtieron en venta
  - Pedidos internos entre depósitos
```

---

## Paso 3: Identificar las dimensiones

Con la granularidad declarada, las dimensiones son las **entidades que describen el contexto** de cada fila de hechos. Responden a las preguntas: ¿Quién? ¿Qué? ¿Cuándo? ¿Dónde? ¿Cómo?

Para la granularidad "una línea de factura de venta", las dimensiones naturales son:

| Pregunta | Dimensión | Columnas descriptivas |
|---|---|---|
| ¿Cuándo? | `dim_tiempo` | fecha, día, mes, trimestre, año, día de semana |
| ¿A quién vendemos? | `dim_cliente` | nombre, segmento, ciudad, región |
| ¿Qué vendemos? | `dim_producto` | nombre, categoría, subcategoría, marca |
| ¿Quién vendió? | `dim_vendedor` | nombre, zona, región |
| ¿Por qué canal? | `dim_canal` | tipo (tienda, e-commerce, telefónico) |
| ¿En qué punto de venta? | `dim_sucursal` | nombre, ciudad, provincia |

### Principios de diseño de dimensiones

#### Principio 1: Desnormalización deliberada

Las dimensiones en el modelo Kimball están **intencionalmente desnormalizadas**. Una jerarquía geográfica que en un modelo 3FN requeriría 3 tablas (ciudad → provincia → región), en el modelo dimensional está completamente aplanada en una sola tabla.

**En 3FN:**
```sql
-- 3 tablas, 2 JOINs necesarios para ver región de un cliente
SELECT c.nombre, p.nombre, r.nombre
FROM cliente c
JOIN provincia p ON c.id_provincia = p.id_provincia
JOIN region r   ON p.id_region     = r.id_region;
```

**En modelo dimensional:**
```sql
-- Todo en una sola tabla, 0 JOINs para ver región
SELECT dc.nombre, dc.provincia, dc.region
FROM dim_cliente dc;
```

**Por qué desnormalizar en las dimensiones:**
- Reduce la cantidad de JOINs en las queries analíticas.
- Las herramientas de BI manejan mejor tablas únicas que jerarquías normalizadas.
- El espacio en disco adicional es insignificante comparado con la tabla de hechos.
- Simplifica el modelo hasta el punto en que un usuario de negocio puede entenderlo.

#### Principio 2: Claves sustitutas (*Surrogate Keys*)

Las dimensiones deben usar claves sustitutas (enteros secuenciales generados por el DWH) en lugar de las claves naturales de los sistemas fuente.

**¿Por qué no usar las claves naturales?**

1. **Cambios históricos:** si el cliente_id=1001 en el sistema fuente cambia de empresa (fusión), el surrogate key en el DWH permite versionar ese cambio sin perder el historial.

2. **Integración de múltiples fuentes:** el cliente_id=1001 en el ERP puede ser un cliente diferente al cliente_id=1001 en el CRM.

3. **Rendimiento:** los enteros son más rápidos para hacer JOINs que strings o UUIDs.

4. **Independencia:** el DWH no depende de las decisiones de numeración de los sistemas operativos.

```sql
-- Dimensión Cliente con surrogate key
CREATE TABLE dm_ventas.dim_cliente (
    id_cliente    SERIAL       PRIMARY KEY,  -- surrogate key (DWH)
    cliente_nk    VARCHAR(30)  NOT NULL,     -- natural key (sistema fuente)
    razon_social  VARCHAR(200) NOT NULL,
    segmento      VARCHAR(50),
    ciudad        VARCHAR(100),
    provincia     VARCHAR(100),
    region        VARCHAR(100),
    tipo_cliente  VARCHAR(50),
    -- Control SCD
    valid_from    DATE         NOT NULL,
    valid_to      DATE,
    is_current    BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

#### Principio 3: La Dimensión Tiempo

La dimensión tiempo es la única que siempre existe en cualquier modelo dimensional. Tiene características especiales:

- **Se popula una vez** (para 10-20 años) y raramente cambia.
- **No tiene surrogate key convencional:** se usa el formato `YYYYMMDD` como integer (ej: 20250315 = 15 de marzo de 2025). Esto permite hacer filtros directamente: `WHERE id_tiempo BETWEEN 20250101 AND 20251231`.
- **Contiene todas las descomposiciones del tiempo** que el negocio necesita para analizar: día de semana, semana ISO, mes, trimestre, año fiscal, indicador de día hábil, indicadores de feriados.

```sql
CREATE TABLE dm_ventas.dim_tiempo (
    id_tiempo         INTEGER     PRIMARY KEY,   -- YYYYMMDD
    fecha             DATE        NOT NULL UNIQUE,
    dia_nombre        VARCHAR(15) NOT NULL,       -- 'Lunes', 'Martes', etc.
    dia_numero        SMALLINT    NOT NULL,       -- 1=Lunes, 7=Domingo (ISO)
    semana_iso        SMALLINT    NOT NULL,       -- semana 1-53 según ISO 8601
    dia_del_anio      SMALLINT    NOT NULL,       -- 1-365
    mes_numero        SMALLINT    NOT NULL,       -- 1-12
    mes_nombre        VARCHAR(15) NOT NULL,       -- 'Enero', 'Febrero', etc.
    mes_nombre_corto  CHAR(3)     NOT NULL,       -- 'Ene', 'Feb', etc.
    trimestre         SMALLINT    NOT NULL,       -- 1-4
    semestre          SMALLINT    NOT NULL,       -- 1-2
    anio              SMALLINT    NOT NULL,
    anio_mes          INTEGER     NOT NULL,       -- YYYYMM → útil para agrupar
    -- Indicadores
    es_dia_habil      BOOLEAN     NOT NULL,
    es_feriado        BOOLEAN     NOT NULL DEFAULT FALSE,
    nombre_feriado    VARCHAR(100),
    es_fin_de_semana  BOOLEAN     NOT NULL,
    -- Período fiscal (si aplica)
    mes_fiscal        SMALLINT,
    trimestre_fiscal  SMALLINT,
    anio_fiscal       SMALLINT
);
```

#### Principio 4: Dimensiones de Rol (*Role-Playing Dimensions*)

Una misma dimensión puede participar múltiples veces en la misma tabla de hechos con distintos roles. El ejemplo más clásico es la dimensión tiempo:

```sql
-- Tabla de hechos con múltiples roles de la dimensión tiempo
CREATE TABLE dm_pedidos.fact_pedido (
    id_fecha_pedido   INTEGER NOT NULL,   -- rol 1: fecha en que se hizo el pedido
    id_fecha_entrega  INTEGER NOT NULL,   -- rol 2: fecha en que se entregó
    id_fecha_factura  INTEGER NOT NULL,   -- rol 3: fecha de facturación
    id_cliente        INTEGER NOT NULL,
    id_producto       INTEGER NOT NULL,
    -- métricas...
    FOREIGN KEY (id_fecha_pedido)  REFERENCES dm_pedidos.dim_tiempo(id_tiempo),
    FOREIGN KEY (id_fecha_entrega) REFERENCES dm_pedidos.dim_tiempo(id_tiempo),
    FOREIGN KEY (id_fecha_factura) REFERENCES dm_pedidos.dim_tiempo(id_tiempo)
);
```

La misma tabla `dim_tiempo` cumple tres roles distintos en el mismo hecho. En la herramienta de BI, se presentan como tres dimensiones separadas: "Fecha del Pedido", "Fecha de Entrega", "Fecha de Facturación".

---

## Paso 4: Identificar los hechos (métricas)

Los **hechos** son las métricas numéricas que se miden en cada evento. Son los valores que los usuarios quieren sumar, promediar, contar o comparar.

### Tipos de hechos

| Tipo | Descripción | Ejemplo |
|---|---|---|
| **Aditivo** | Se puede sumar por cualquier dimensión | cantidad vendida, total_neto |
| **Semi-aditivo** | Se puede sumar por algunas dimensiones pero no otras | saldo de cuenta bancaria (no suma por tiempo) |
| **No aditivo** | No tiene sentido sumarlo | precio unitario, % descuento |

Los hechos no aditivos deben transformarse en métricas aditivas para ser útiles en el análisis:

```
precio_unitario (no aditivo) → SUM(cantidad * precio_unitario) = total_neto (aditivo)
% descuento (no aditivo)    → SUM(monto_descuento) (aditivo)
```

### Hechos derivados vs. hechos base

Los hechos derivados se calculan a partir de hechos base y **pueden o no almacenarse** en la tabla de hechos:

```
Hechos BASE almacenados:
  cantidad       = 10 unidades
  precio_unit    = $500
  descuento_pct  = 0.10

Hechos DERIVADOS:
  subtotal       = cantidad * precio_unit     = $5.000        (puede calcularse)
  descuento_monto= subtotal * descuento_pct  = $500          (puede calcularse)
  total_neto     = subtotal - descuento_monto = $4.500       (puede calcularse)
  margen_bruto   = total_neto - costo         = $1.800       (requiere costo)
```

La decisión de almacenar o calcular los derivados depende del volumen de datos y la complejidad de las fórmulas.

### La tabla de hechos completa — Ejemplo

```sql
CREATE TABLE dm_ventas.fact_ventas (
    -- Claves foráneas a dimensiones
    id_tiempo       INTEGER       NOT NULL REFERENCES dm_ventas.dim_tiempo,
    id_cliente      INTEGER       NOT NULL REFERENCES dm_ventas.dim_cliente,
    id_producto     INTEGER       NOT NULL REFERENCES dm_ventas.dim_producto,
    id_vendedor     INTEGER                REFERENCES dm_ventas.dim_vendedor,
    id_canal        INTEGER                REFERENCES dm_ventas.dim_canal,
    id_sucursal     INTEGER                REFERENCES dm_ventas.dim_sucursal,

    -- Clave degenerada (identifica la transacción sin necesitar dimensión propia)
    numero_factura  VARCHAR(30)   NOT NULL,
    linea           SMALLINT      NOT NULL,

    -- Hechos BASE (aditivos salvo precio_unit y descuento_pct)
    cantidad        NUMERIC(10,3) NOT NULL,
    precio_unit     NUMERIC(12,2) NOT NULL,     -- no aditivo
    descuento_pct   NUMERIC(5,4)  NOT NULL DEFAULT 0,  -- no aditivo
    costo_unit      NUMERIC(12,2),

    -- Hechos DERIVADOS almacenados (aditivos)
    descuento_monto NUMERIC(14,2) GENERATED ALWAYS AS (cantidad * precio_unit * descuento_pct) STORED,
    total_neto      NUMERIC(14,2) GENERATED ALWAYS AS (cantidad * precio_unit * (1 - descuento_pct)) STORED,
    costo_total     NUMERIC(14,2) GENERATED ALWAYS AS (cantidad * costo_unit) STORED,
    margen_bruto    NUMERIC(14,2) GENERATED ALWAYS AS (
                        cantidad * precio_unit * (1 - descuento_pct) - cantidad * costo_unit
                    ) STORED,

    PRIMARY KEY (numero_factura, linea)
);

-- Índices para optimizar las consultas más frecuentes
CREATE INDEX idx_fv_tiempo    ON dm_ventas.fact_ventas (id_tiempo);
CREATE INDEX idx_fv_cliente   ON dm_ventas.fact_ventas (id_cliente);
CREATE INDEX idx_fv_producto  ON dm_ventas.fact_ventas (id_producto);
CREATE INDEX idx_fv_vendedor  ON dm_ventas.fact_ventas (id_vendedor);
```

---

## El esquema estrella completo

El resultado final de los 4 pasos es el **esquema estrella** del Data Mart:

```
                        dim_tiempo
                       ┌──────────┐
                       │id_tiempo │
                       │fecha     │
                       │mes       │
                       │trimestre │
                       │anio      │
                       │...       │
                       └────┬─────┘
                            │
dim_vendedor                │                dim_cliente
┌──────────┐                │               ┌──────────┐
│id_vendedor│               │               │id_cliente│
│nombre    │                │               │nombre    │
│zona      │                │               │segmento  │
│region    │──────────┐     │     ┌─────────│ciudad    │
└──────────┘          │     │     │         │provincia │
                      │     │     │         │region    │
dim_canal             ▼     ▼     ▼         └──────────┘
┌──────────┐    ┌─────────────────────┐
│id_canal  │───▶│   fact_ventas       │◀── dim_sucursal
│tipo      │    │                     │   ┌──────────┐
│nombre    │    │id_tiempo   (FK)     │   │id_sucursal│
└──────────┘    │id_cliente  (FK)     │   │nombre    │
                │id_producto (FK)     │   │ciudad    │
                │id_vendedor (FK)     │   │provincia │
                │id_canal    (FK)     │   └──────────┘
                │id_sucursal (FK)     │
                │numero_factura       │
                │linea                │
                │cantidad             │
                │precio_unit          │
                │total_neto           │
                │margen_bruto         │
                └─────────────────────┘
                            ▲
                            │
                       dim_producto
                       ┌──────────┐
                       │id_producto│
                       │nombre    │
                       │categoria │
                       │subcateg. │
                       │marca     │
                       └──────────┘
```

---

## Las Dimensiones Conformadas: el corazón del DW Bus

Una **dimensión conformada** es aquella que tiene el mismo significado y el mismo contenido en todos los Data Marts que la usan. Es el mecanismo que permite que los análisis cruzados entre Data Marts sean consistentes.

**Ejemplo:** Si la dimensión `dim_tiempo` del Data Mart de Ventas y la dimensión `dim_tiempo` del Data Mart de Compras tienen exactamente la misma estructura y los mismos datos, entonces se puede comparar ventas contra compras por período con total consistencia.

Si no estuvieran conformadas (cada Data Mart define su propia versión del tiempo), podría haber diferencias en cómo se define la semana, el año fiscal o los días hábiles.

**Las dimensiones conformadas son lo que une todos los Data Marts de la organización en una arquitectura coherente.** A esto Kimball lo llama el **DW Bus** (Bus de Datos del DWH): la autopista de datos común a todos los Data Marts.

```
DW Bus (Dimensiones Conformadas):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

dim_tiempo ──────┬────────────────┬──────────┐
                 │                │          │
dim_cliente ─────┤                │          │
                 ▼                ▼          ▼
          DM Ventas        DM Finanzas   DM Logística
          ─────────        ──────────    ────────────
          fact_ventas      fact_pagos    fact_envios

dim_producto ────┴────────────────┴──────────┘

Las dimensiones conformadas conectan los Data Marts
y permiten análisis cruzados consistentes.
```

---

## Cambios de Dimensión en el Tiempo: SCD (Slowly Changing Dimensions)

Las entidades del mundo real cambian con el tiempo: los clientes se mudan, los vendedores cambian de zona, los productos cambian de categoría. El diseño del Data Mart debe decidir cómo manejar estos cambios.

### SCD Tipo 1: Sobreescribir el valor (sin historia)

El valor anterior se sobreescribe con el nuevo. No se guarda historia del cambio.

**Cuándo usar:** cuando el cambio corrige un error (el nombre estaba mal escrito) o cuando el historial del valor anterior no importa para ningún análisis.

```sql
-- El cliente cambió de ciudad. Se actualiza directamente.
UPDATE dm_ventas.dim_cliente
SET ciudad    = 'Rosario',
    provincia = 'Santa Fe',
    region    = 'Centro'
WHERE cliente_nk = 'CLI-0042'
  AND is_current = TRUE;
-- El historial de ventas anteriores "parece" que siempre fue de Rosario.
```

### SCD Tipo 2: Agregar nueva fila (con historia completa)

Cuando el valor cambia, la fila actual se cierra y se inserta una nueva fila con el nuevo valor. Se conserva el historial completo.

**Cuándo usar:** cuando el análisis requiere conocer el valor que tenía la entidad en el momento de la transacción.

```sql
-- El vendedor Juan López cambia de zona: de "Norte" a "Centro".
-- Se cierra la fila actual:
UPDATE dm_ventas.dim_vendedor
SET valid_to   = CURRENT_DATE - 1,
    is_current = FALSE
WHERE vendedor_nk = 'VEND-0015'
  AND is_current  = TRUE;

-- Se inserta la nueva versión:
INSERT INTO dm_ventas.dim_vendedor
    (vendedor_nk, nombre, zona, region, valid_from, valid_to, is_current)
VALUES
    ('VEND-0015', 'Juan López', 'Centro', 'Litoral',
     CURRENT_DATE, NULL, TRUE);

-- Resultado: dos filas en la dimensión para el mismo vendedor.
-- Las ventas antiguas quedan asociadas a la zona "Norte".
-- Las ventas nuevas se asociarán a la zona "Centro".
```

### SCD Tipo 3: Columna de valor anterior (historia limitada)

Se agrega una columna extra con el valor anterior. Solo guarda el último cambio.

**Cuándo usar:** cuando el negocio necesita comparar el valor actual con el anterior, pero no el historial completo.

```sql
ALTER TABLE dm_ventas.dim_vendedor
    ADD COLUMN zona_anterior VARCHAR(100);

UPDATE dm_ventas.dim_vendedor
SET zona_anterior = zona,
    zona          = 'Centro'
WHERE vendedor_nk = 'VEND-0015'
  AND is_current  = TRUE;
```

---

## Entregables de la Etapa 2

1. ✅ **Declaración formal de granularidad** (por escrito, validada con el negocio).
2. ✅ **Diagrama del esquema estrella** con todas las tablas y sus columnas.
3. ✅ **DDL SQL** de todas las tablas del esquema estrella.
4. ✅ **Diccionario de datos** del Data Mart: descripción de cada tabla y columna.
5. ✅ **Definición de SCD** por dimensión: qué tipo aplica y por qué.
6. ✅ **Identificación de dimensiones conformadas** y compromiso de usarlas en futuros Data Marts.
7. ✅ **Validación del modelo con los usuarios clave** (revisión formal del esquema con las personas de negocio).

---

## Patrones Avanzados de Modelado Dimensional

Más allá del esquema estrella básico, Kimball identifica patrones recurrentes que resuelven situaciones de diseño comunes.

### Tabla de Hechos sin Hechos (*Factless Fact Table*)

Una tabla de hechos sin métricas numéricas. Registra la **ocurrencia** de un evento, no una medición.

**Ejemplo 1: Cobertura de estudiantes en cursos**

¿Qué alumnos están inscriptos en qué materias en qué cuatrimestre?

```sql
CREATE TABLE dm_academico.fact_inscripcion (
    id_tiempo       INTEGER NOT NULL REFERENCES dim_tiempo,
    id_alumno       INTEGER NOT NULL REFERENCES dim_alumno,
    id_materia      INTEGER NOT NULL REFERENCES dim_materia,
    id_cuatrimestre INTEGER NOT NULL REFERENCES dim_cuatrimestre,
    -- Sin métricas numéricas. La "métrica" es COUNT(*).
    PRIMARY KEY (id_alumno, id_materia, id_cuatrimestre)
);

-- Pregunta que responde: ¿Cuántos alumnos hay inscriptos en Álgebra en 2025-1C?
SELECT COUNT(*)
FROM dm_academico.fact_inscripcion f
JOIN dim_materia m ON f.id_materia = m.id_materia
JOIN dim_cuatrimestre c ON f.id_cuatrimestre = c.id_cuatrimestre
WHERE m.nombre = 'Álgebra' AND c.periodo = '2025-1C';
```

**Ejemplo 2: Eventos de cobertura (qué vendedores cubren qué zonas)**

```sql
-- ¿Qué vendedor NO cubre ninguna zona de la región Patagonia?
SELECT dv.nombre
FROM dim_vendedor dv
WHERE dv.id_vendedor NOT IN (
    SELECT DISTINCT f.id_vendedor
    FROM fact_cobertura f
    JOIN dim_zona dz ON f.id_zona = dz.id_zona
    WHERE dz.region = 'Patagonia'
);
```

---

### Dimensión Basura (*Junk Dimension*)

Cuando hay múltiples flags y atributos de baja cardinalidad que no pertenecen naturalmente a ninguna dimensión, se agrupan en una **dimensión basura** que evita ensuciar la tabla de hechos con columnas sueltas.

```sql
-- Sin dimensión basura: flags sueltos en la fact
CREATE TABLE fact_ventas (
    id_tiempo      INTEGER,
    id_cliente     INTEGER,
    -- ... FKs ...
    es_venta_online   BOOLEAN,      -- flag suelto
    es_primera_compra BOOLEAN,      -- flag suelto
    tipo_pago         CHAR(3),      -- cod suelto
    tiene_descuento   BOOLEAN,      -- flag suelto
    total_neto        NUMERIC
);

-- Con dimensión basura: los flags se combinan en una dimensión
CREATE TABLE dm_ventas.dim_indicadores_venta (
    id_indicador       SERIAL PRIMARY KEY,
    es_venta_online    BOOLEAN NOT NULL,
    es_primera_compra  BOOLEAN NOT NULL,
    tipo_pago          VARCHAR(20) NOT NULL,
    tiene_descuento    BOOLEAN NOT NULL
);
-- Combinaciones posibles: 2 × 2 × 3 × 2 = 24 filas máximo

CREATE TABLE fact_ventas (
    id_tiempo      INTEGER,
    id_cliente     INTEGER,
    id_indicador   INTEGER REFERENCES dim_indicadores_venta,
    total_neto     NUMERIC
);
```

**Ventaja:** la tabla de hechos queda más limpia y se reduce el ancho de cada fila (ahorro de espacio significativo con millones de filas).

---

### Dimensión Degenerada (*Degenerate Dimension*)

Es un atributo que identifica una transacción pero no justifica tener su propia tabla de dimensión. Se almacena directamente en la tabla de hechos como una columna.

El ejemplo más clásico es el **número de factura**: identifica la transacción, pero no tiene atributos descriptivos propios. No tiene sentido crear una `dim_factura` con una sola columna.

```sql
CREATE TABLE dm_ventas.fact_ventas (
    -- ... FKs a dimensiones ...
    numero_factura  VARCHAR(30) NOT NULL,  -- dimensión degenerada
    linea           SMALLINT    NOT NULL,  -- dimensión degenerada
    -- ... métricas ...
);
```

---

### Mini-Dimensiones

Cuando una dimensión tiene un subconjunto de atributos que cambian frecuentemente, se puede extraer ese subconjunto a una **mini-dimensión** para evitar que el SCD Tipo 2 genere demasiadas filas.

**Ejemplo:** La dimensión `dim_cliente` tiene atributos estables (nombre, DNI, fecha de nacimiento) y atributos volátiles (segmento, score crediticio, categoría de consumo). En vez de generar una nueva fila SCD2 cada vez que cambia el score:

```sql
-- Mini-dimensión de perfil dinámico del cliente
CREATE TABLE dm_ventas.dim_perfil_cliente (
    id_perfil           SERIAL PRIMARY KEY,
    rango_edad          VARCHAR(20),     -- '18-25', '26-35', '36-50', '51+'
    segmento_consumo    VARCHAR(20),     -- 'Bajo', 'Medio', 'Alto', 'Premium'
    score_crediticio    VARCHAR(20),     -- 'A', 'B', 'C', 'D'
    frecuencia_compra   VARCHAR(20)      -- 'Esporádico', 'Regular', 'Frecuente'
);
-- Todas las combinaciones posibles: 4 × 4 × 4 × 3 = 192 filas

-- La fact table referencia tanto dim_cliente como dim_perfil_cliente
CREATE TABLE dm_ventas.fact_ventas (
    id_tiempo          INTEGER NOT NULL,
    id_cliente         INTEGER NOT NULL REFERENCES dim_cliente,
    id_perfil_cliente  INTEGER NOT NULL REFERENCES dim_perfil_cliente,
    -- ...
);
```

---

### Esquema Copo de Nieve (*Snowflake Schema*)

El esquema copo de nieve normaliza parcialmente las dimensiones, creando sub-tablas para las jerarquías. Es lo **opuesto** a la recomendación de Kimball.

```
ESQUEMA ESTRELLA (Kimball recomendado):
  dim_producto: id_producto | nombre | subcategoria | categoria | departamento

ESQUEMA COPO DE NIEVE (normalizado):
  dim_producto:      id_producto | nombre | id_subcategoria
  dim_subcategoria:  id_subcategoria | nombre | id_categoria
  dim_categoria:     id_categoria | nombre | id_departamento
  dim_departamento:  id_departamento | nombre
```

**¿Por qué Kimball NO recomienda el copo de nieve?**
- Agrega JOINs innecesarios a cada query analítica.
- Complica el modelo para los usuarios de negocio.
- El ahorro de espacio es insignificante (las dimensiones son pequeñas).
- Las herramientas de BI manejan peor los esquemas normalizados.

**¿Cuándo puede tener sentido?** En bases de datos cloud con pricing por bytes escaneados (BigQuery), la normalización de dimensiones muy grandes (millones de filas) puede reducir costos de query. Pero esto es una excepción, no la regla.

---

## Patrones de Tablas de Hechos Especiales

### Tabla de Hechos Periódica (*Periodic Snapshot*)

Captura el estado de un proceso a intervalos regulares. Cada fila = un "corte" en un momento del tiempo.

**Ejemplo: Inventario diario por producto y depósito**

```sql
CREATE TABLE dm_inventario.fact_inventario_diario (
    id_tiempo       INTEGER NOT NULL,
    id_producto     INTEGER NOT NULL,
    id_deposito     INTEGER NOT NULL,
    -- Métricas (semi-aditivas: no se suman por tiempo)
    stock_disponible  INTEGER  NOT NULL,
    stock_reservado   INTEGER  NOT NULL DEFAULT 0,
    stock_total       INTEGER  NOT NULL,
    costo_stock       NUMERIC(14,2),
    dias_sin_movimiento INTEGER,
    PRIMARY KEY (id_tiempo, id_producto, id_deposito)
);
-- Granularidad: un producto en un depósito en un día.
-- Se carga un snapshot completo cada noche.
```

### Tabla de Hechos Acumulada (*Accumulating Snapshot*)

Sigue un proceso de negocio **de principio a fin**, actualizando la misma fila a medida que el proceso avanza.

**Ejemplo: Ciclo de vida de un pedido**

```sql
CREATE TABLE dm_pedidos.fact_ciclo_pedido (
    -- Dimensiones de rol (múltiples fechas)
    id_fecha_pedido       INTEGER REFERENCES dim_tiempo,
    id_fecha_aprobacion   INTEGER REFERENCES dim_tiempo,
    id_fecha_preparacion  INTEGER REFERENCES dim_tiempo,
    id_fecha_envio        INTEGER REFERENCES dim_tiempo,
    id_fecha_entrega      INTEGER REFERENCES dim_tiempo,
    -- Otras dimensiones
    id_cliente            INTEGER NOT NULL,
    id_producto           INTEGER NOT NULL,
    numero_pedido         VARCHAR(30) PRIMARY KEY,
    -- Métricas
    cantidad              INTEGER NOT NULL,
    total_pedido          NUMERIC(14,2),
    -- Métricas de duración (derivadas)
    dias_aprobacion       INTEGER,  -- fecha_aprobacion - fecha_pedido
    dias_preparacion      INTEGER,  -- fecha_preparacion - fecha_aprobacion
    dias_envio            INTEGER,  -- fecha_envio - fecha_preparacion
    dias_entrega          INTEGER,  -- fecha_entrega - fecha_envio
    dias_total            INTEGER   -- fecha_entrega - fecha_pedido
);
```

A medida que el pedido avanza, el ETL **actualiza** la misma fila llenando las fechas faltantes y recalculando las duraciones.

---

## Ejercicio Práctico: Diseño Dimensional para una Biblioteca

**Contexto:** Una biblioteca universitaria quiere analizar los préstamos de libros para optimizar la compra de nuevos ejemplares.

**Paso 1: Proceso de negocio** → Préstamos de libros

**Paso 2: Granularidad** → Un préstamo de un ejemplar a un socio en una fecha

**Paso 3: Dimensiones:**

| Dimensión | Atributos principales |
|---|---|
| `dim_tiempo` | fecha, mes, trimestre, año, es_periodo_examen |
| `dim_socio` | nombre, carrera, año_cursado, tipo (alumno/docente) |
| `dim_libro` | titulo, autor, editorial, isbn, tema, año_publicacion |
| `dim_sucursal` | nombre_biblioteca, campus, horario |

**Paso 4: Hechos:**

```sql
CREATE TABLE dm_biblioteca.fact_prestamo (
    id_tiempo_prestamo   INTEGER NOT NULL,
    id_tiempo_devolucion INTEGER,           -- NULL si no se devolvió aún
    id_socio             INTEGER NOT NULL,
    id_libro             INTEGER NOT NULL,
    id_sucursal          INTEGER NOT NULL,
    -- Métricas
    dias_prestamo        INTEGER,           -- devolucion - prestamo
    es_devolucion_tardia BOOLEAN,           -- > 15 días
    multa                NUMERIC(8,2) DEFAULT 0,
    PRIMARY KEY (id_tiempo_prestamo, id_socio, id_libro)
);
```

**Preguntas que responde:**
- ¿Cuáles son los 10 libros más prestados del cuatrimestre?
- ¿Qué carrera genera más préstamos?
- ¿Cuál es el porcentaje de devoluciones tardías por sucursal?
- ¿Qué temas necesitan más ejemplares?

---

## Lecturas recomendadas

- **Kimball, R. & Ross, M.** — *The Data Warehouse Toolkit*, 3ra edición. Capítulos 2-5. Wiley. (Referencia obligatoria para el modelado dimensional).
- **Kimball, R.** — *Kimball Design Tips* (serie de artículos técnicos disponibles en kimballgroup.com y archive.org).
- **Inmon, W.H. & Linstedt, D.** — *Data Architecture: A Primer for the Data Scientist*. Capítulo 6. Academic Press.
- **Adamson, C.** — *Star Schema: The Complete Reference*. McGraw-Hill. (Referencia exhaustiva sobre patrones de esquema estrella).
- **Corr, L. & Stagnitto, J.** — *Agile Data Warehouse Design*. DecisionOne Press. (Técnicas de modelado dimensional con metodologías ágiles).
