# Arquitectura Inmon · Etapa 2 — Diseño del EDW Normalizado (*Enterprise Data Warehouse*)

> **Arquitectura:** Inmon — Top-Down  
> **Posición en el ciclo:** Segunda etapa. Se construye el núcleo central del sistema analítico.

---

## ¿Qué es el Enterprise Data Warehouse?

El **Enterprise Data Warehouse** (EDW) es el repositorio central y único de datos analíticos de toda la organización. Es la pieza más importante de la arquitectura Inmon y la que la distingue radicalmente del enfoque Kimball.

En la arquitectura Inmon, el EDW tiene tres características que lo definen:

1. **Es la única fuente de verdad** (*Single Source of Truth*): todos los datos analíticos de la organización pasan por aquí antes de llegar a cualquier herramienta de reporte o Data Mart. Nadie accede directamente a los sistemas fuente para análisis.

2. **Está en Tercera Forma Normal (3FN)**: a diferencia de los Data Marts (que usarán esquemas estrella desnormalizados), el EDW mantiene los datos en un modelo relacional normalizado. Esto garantiza la consistencia y elimina la redundancia.

3. **Cubre toda la empresa**: no está orientado a un área de negocio específica sino a la totalidad de los datos de la organización, estructurados según el Modelo Empresarial definido en la Etapa 1.

> **Analogía:** El EDW es la biblioteca central de una universidad. Tiene todos los libros de todas las facultades, organizados de forma rigurosa y consistente. Cada facultad tiene su propia sala de lectura (Data Mart), que contiene los libros más solicitados de su disciplina, organizados de la manera más cómoda para sus usuarios. Pero todos esos libros vienen de la biblioteca central, no de donaciones directas de editoriales.

---

## Por qué Tercera Forma Normal (3FN) en el EDW

Esta es la decisión de diseño más debatida de la arquitectura Inmon, porque parece ir en contra de los principios de performance para OLAP.

**¿Por qué Inmon insiste en la normalización del EDW?**

### Razón 1: Consistencia total

En un modelo normalizado, cada dato existe en un solo lugar. Si el precio de un producto cambia, se cambia en una sola tabla y todos los que dependen de ese dato lo ven actualizado automáticamente. En un modelo desnormalizado, la misma información aparece en múltiples tablas y deben actualizarse todas de forma coordinada.

**Ejemplo práctico:** El nombre de una ciudad aparece en la tabla `clientes` (ciudad del cliente), en `vendedores` (zona de cobertura), en `proveedores` (ciudad del proveedor) y en `entregas` (ciudad de destino). Si la ciudad "Gral. San Martín" debe escribirse consistentemente así, con 4FN basta cambiarla una vez en la tabla `ciudad`. En un esquema desnormalizado, habría que actualizar 4 tablas con el riesgo de que alguna quede desactualizada.

### Razón 2: Flexibilidad para nuevas preguntas

El EDW normalizado puede responder cualquier pregunta de negocio que pueda formularse con sus datos, sin importar si esa pregunta fue anticipada o no en el diseño inicial. Un Data Mart desnormalizado optimizado para "ventas por región" puede ser muy lento para responder "rotación de inventario por proveedor", porque no fue diseñado para eso.

### Razón 3: Integración de múltiples fuentes

Cuando los datos provienen de múltiples sistemas (ERP, CRM, SCM), cada uno usa convenciones distintas. El proceso de normalización en el EDW es el momento de resolver estas inconsistencias de forma definitiva y centralizada, una sola vez.

### La contrapartida

La normalización implica muchos JOINs en las consultas, lo que degrada la performance analítica. Por eso el EDW en Inmon **no está pensado para ser consultado directamente por los usuarios de negocio**: es una capa intermedia de la que se derivan los Data Marts (Etapa 4), que sí estarán optimizados para el análisis con esquemas desnormalizados.

---

## Estructura del EDW: los Sujetos de Datos

El EDW se organiza en **sujetos de datos** (*data subjects*), que corresponden a las áreas temáticas definidas en la Etapa 1. Cada sujeto de datos es un conjunto de tablas relacionadas que modelan una entidad central y todo lo que la describe.

### Ejemplo: Sujeto de datos CLIENTE en el EDW (3FN)

```
                    ┌──────────────┐
                    │    PAIS      │
                    │──────────────│
                    │ id_pais (PK) │
                    │ nombre_pais  │
                    │ codigo_iso   │
                    └──────┬───────┘
                           │
                    ┌──────┴───────┐
                    │  PROVINCIA   │
                    │──────────────│
                    │ id_prov (PK) │
                    │ nombre_prov  │
                    │ id_pais (FK) │
                    └──────┬───────┘
                           │
                    ┌──────┴───────┐
                    │   CIUDAD     │
                    │──────────────│
                    │ id_ciudad(PK)│
                    │ nombre_ciudad│
                    │ id_prov (FK) │
                    └──────┬───────┘
                           │
         ┌─────────────────┼──────────────────┐
         │                 │                  │
┌────────┴───────┐  ┌──────┴───────┐  ┌──────┴───────────┐
│   SEGMENTO     │  │   CLIENTE    │  │ TIPO_CLIENTE     │
│────────────────│  │──────────────│  │──────────────────│
│ id_segmento(PK)│  │ id_cli (PK)  │  │ id_tipo (PK)     │
│ nombre_seg     │  │ razon_social │  │ descripcion      │
│ descripcion    │  │ id_tipo (FK) │  └──────────────────┘
│ criterio       │  │ id_ciudad(FK)│
└────────────────│  │ id_seg  (FK) │
                    │ fecha_alta   │
                    │ estado       │
                    └──────┬───────┘
                           │
               ┌───────────┼────────────┐
               │           │            │
      ┌────────┴──┐  ┌─────┴──────┐  ┌─┴────────────────┐
      │CLI_PERSONA│  │CLI_EMPRESA │  │ CONTACTO_CLIENTE │
      │───────────│  │────────────│  │──────────────────│
      │ id_cli(FK)│  │ id_cli(FK) │  │ id_contacto (PK) │
      │ nro_dni   │  │ nro_cuit   │  │ id_cli (FK)      │
      │ fecha_nac │  │ nro_iibb   │  │ nombre           │
      │ genero    │  │ id_sector  │  │ cargo            │
      └───────────┘  └────────────┘  │ email            │
                                     │ telefono         │
                                     └──────────────────┘
```

Cada tabla tiene una responsabilidad única y bien delimitada. Para obtener la ciudad de un cliente, se debe hacer JOIN de CLIENTE → CIUDAD → PROVINCIA → PAIS. Esto es "costoso" en términos de query, pero garantiza que la definición de "ciudad" sea única en todo el EDW.

---

## Gestión del Tiempo: el Historial en el EDW

El EDW de Inmon debe preservar el historial completo de todos los cambios en los datos. Para lograrlo, las tablas del EDW implementan un patrón de **versionado temporal**:

Cada tabla que necesita conservar historial tiene columnas de control:

```sql
-- Ejemplo: tabla CLIENTE con historial temporal en el EDW
CREATE TABLE edw.cliente (
    id_cliente        BIGSERIAL       PRIMARY KEY,
    cliente_src_key   VARCHAR(30)     NOT NULL,      -- Clave del sistema fuente
    tipo_cliente      CHAR(1)         NOT NULL,
    razon_social      VARCHAR(200)    NOT NULL,
    id_ciudad         INTEGER         NOT NULL REFERENCES edw.ciudad(id_ciudad),
    id_segmento       SMALLINT        REFERENCES edw.segmento(id_segmento),
    estado            CHAR(1)         NOT NULL DEFAULT 'A',

    -- Control de integración y origen
    id_sistema_fuente SMALLINT        NOT NULL,       -- ERP, CRM, etc.
    fecha_carga       TIMESTAMP       NOT NULL DEFAULT NOW(),

    -- Control de historial temporal
    fecha_efectiva    DATE            NOT NULL,       -- Desde cuándo es válido
    fecha_vencimiento DATE            NOT NULL DEFAULT '9999-12-31',
    es_vigente        BOOLEAN         NOT NULL DEFAULT TRUE,

    -- Auditoría
    hash_registro     CHAR(64),                      -- SHA-256 del registro para detectar cambios
    usuario_carga     VARCHAR(50)     NOT NULL,
    pipeline_id       VARCHAR(100)
);

-- Índices esenciales
CREATE UNIQUE INDEX uq_cliente_vigente
    ON edw.cliente(cliente_src_key, id_sistema_fuente)
    WHERE es_vigente = TRUE;

CREATE INDEX idx_cliente_src
    ON edw.cliente(cliente_src_key, fecha_efectiva);
```

---

## La Zona de Staging: antesala del EDW

Antes de cargar datos al EDW, existe un área temporal llamada **Staging Area** (Zona de Staging) que sirve como zona de trabajo del proceso ETL.

```
Sistemas Fuente
      │
      ▼
┌─────────────────────────────────────────────────┐
│              STAGING AREA (temporal)             │
│                                                  │
│  • Copia exacta de los datos extraídos           │
│  • Sin transformaciones aún                      │
│  • Visibilidad solo para el proceso ETL          │
│  • Se borra o trunca en cada ciclo de carga      │
│  • Sin índices complejos (velocidad de carga)    │
└──────────────────────┬──────────────────────────┘
                       │  ETL (transformación, limpieza,
                       │  integración, carga del historial)
                       ▼
┌─────────────────────────────────────────────────┐
│              ENTERPRISE DATA WAREHOUSE            │
│                                                  │
│  • Datos integrados, limpios e históricos         │
│  • Modelo 3FN                                    │
│  • Persistente (los datos nunca se borran)        │
│  • Acceso solo para procesos ETL de Data Marts   │
└─────────────────────────────────────────────────┘
```

La Staging Area es una zona **invisible para los usuarios de negocio**. Su único propósito es facilitar el trabajo del proceso ETL sin afectar la integridad del EDW durante la carga.

---

## Capas internas del EDW

Inmon suele describir el EDW con capas internas que organizan los datos por nivel de transformación:

### Capa de Integración (*Integration Layer*)

Primera capa donde aterrizan los datos desde el Staging. Aquí se realizan:
- Conversión de tipos de dato y formatos.
- Resolución de identificadores (distintos IDs en distintos sistemas para el mismo cliente).
- Aplicación de reglas del glosario corporativo.
- Eliminación de duplicados entre fuentes.

### Capa de Acceso (*Access Layer*)

Parte del EDW que es accesible (de forma controlada) para la capa de Data Marts. Contiene vistas o tablas derivadas que facilitan la construcción de los Data Marts sin exponer la complejidad interna del modelo 3FN.

---

## Reglas de diseño del EDW en Inmon

Inmon establece un conjunto de principios que deben respetarse en el diseño del EDW:

| Regla | Descripción |
|---|---|
| **Atomicidad** | El EDW almacena el nivel más granular posible. Las agregaciones se calculan en los Data Marts. |
| **No volatilidad** | Los datos del EDW no se actualizan ni borran. Se agregan nuevas versiones históricas. |
| **Integración** | Todos los datos siguen las mismas definiciones y convenciones del glosario corporativo. |
| **Separación** | El EDW es inaccesible para los usuarios de negocio. Solo los procesos ETL acceden a él. |
| **Trazabilidad** | Cada registro del EDW debe poder rastrearse hasta su sistema fuente y la fecha de carga. |
| **Completitud** | El EDW contiene todos los datos de la organización relevantes para el análisis, no solo los de un área. |

---

## Lo que el EDW NO es

Para evitar confusiones comunes:

- ❌ **No es un Data Mart:** el EDW no está optimizado para consultas de usuarios de negocio. Es una capa de integración.
- ❌ **No es una réplica del ERP:** el EDW integra múltiples fuentes y guarda historial. El ERP solo tiene el estado actual.
- ❌ **No reemplaza los sistemas operativos:** el ERP sigue siendo la fuente de verdad transaccional. El EDW lo complementa con perspectiva analítica.
- ❌ **No tiene esquemas estrella:** eso corresponde a los Data Marts de la Etapa 4.

---

## Revisión de las Formas Normales aplicadas al EDW

Para comprender por qué Inmon elige la 3FN, es importante repasar las formas normales con ejemplos concretos del contexto de un Data Warehouse.

### Primera Forma Normal (1FN): Valores Atómicos

Una tabla está en 1FN si:
- Cada celda contiene un único valor (no hay listas ni conjuntos).
- Todas las filas son únicas (existe una clave primaria).
- No hay grupos repetitivos de columnas.

**Ejemplo de violación de 1FN:**

```
CLIENTE (tabla no normalizada)
─────────────────────────────────────────────────────────────────
id_cliente │ nombre        │ telefonos              │ email
───────────│───────────────│────────────────────────│──────────
1001       │ García María  │ 011-4555-1234,         │ m@a.com
           │               │ 011-4555-5678          │
```

El campo `telefonos` contiene múltiples valores → viola 1FN.

**Versión en 1FN:**

```
CLIENTE                            CLIENTE_TELEFONO
──────────────────────             ──────────────────────────
id_cliente │ nombre │ email        id_cliente │ telefono
───────────│────────│──────        ───────────│────────────────
1001       │ García │ m@a.com      1001       │ 011-4555-1234
                                   1001       │ 011-4555-5678
```

---

### Segunda Forma Normal (2FN): Dependencia Total de la Clave

Una tabla está en 2FN si:
- Está en 1FN.
- Todos los atributos no-clave dependen de **toda** la clave primaria (no de una parte de ella).

Solo aplica cuando la clave primaria es compuesta.

**Ejemplo de violación de 2FN:**

```
VENTA (PK compuesta: id_pedido, id_producto)
──────────────────────────────────────────────────────────────
id_pedido │ id_producto │ cantidad │ precio_unit │ nombre_producto │ categoria
──────────│─────────────│──────────│─────────────│─────────────────│──────────
5001      │ P-100       │ 3        │ 1500.00     │ Monitor LED 24" │ Electrónica
```

`nombre_producto` y `categoria` dependen solo de `id_producto`, no de la clave compuesta completa → viola 2FN.

**Versión en 2FN:**

```
VENTA                                    PRODUCTO
───────────────────────────              ───────────────────────────
id_pedido │ id_producto │ cantidad       id_producto │ nombre │ categoria
──────────│─────────────│──────          ────────────│────────│──────────
5001      │ P-100       │ 3              P-100       │ Monitor│ Electrónica
```

---

### Tercera Forma Normal (3FN): Sin Dependencias Transitivas

Una tabla está en 3FN si:
- Está en 2FN.
- Ningún atributo no-clave depende de otro atributo no-clave (solo de la clave primaria).

**Ejemplo de violación de 3FN:**

```
CLIENTE
──────────────────────────────────────────────────────────
id_cliente │ nombre │ id_ciudad │ nombre_ciudad │ id_provincia │ nombre_provincia
───────────│────────│───────────│───────────────│──────────────│─────────────────
1001       │ García │ 201       │ Rosario       │ SF           │ Santa Fe
```

`nombre_ciudad` depende de `id_ciudad`, y `nombre_provincia` depende de `id_provincia` → dependencias transitivas que violan 3FN.

**Versión en 3FN (como se usa en el EDW):**

```
CLIENTE            CIUDAD                   PROVINCIA
───────────────    ────────────────────     ────────────────────
id_cli │ id_ciu    id_ciudad │ nombre │     id_prov │ nombre
───────│────────   ──────────│────────│     ────────│──────────
1001   │ 201       201       │ Rosario│     SF      │ Santa Fe
                             │ id_prov│
                             │ SF     │
```

> **Regla mnemotécnica para 3FN:** *"Cada atributo no-clave debe depender de la clave, de toda la clave y de nada más que la clave."*

---

## Diseño Físico del EDW: Consideraciones de Implementación

El diseño lógico en 3FN debe traducirse a un diseño físico que funcione eficientemente en el motor de base de datos elegido. Estas son las consideraciones clave:

### Convenciones de Nomenclatura

Una convención de nombres consistente es fundamental para la mantenibilidad del EDW a largo plazo:

```
Esquemas:
  edw.*           → tablas del Enterprise Data Warehouse
  stg.*           → tablas de la Staging Area
  dm_ventas.*     → Data Mart de Ventas
  meta.*          → metadatos y control

Tablas:
  [esquema].[entidad]                  → edw.cliente, edw.pedido
  [esquema].[entidad_padre_hijo]       → edw.cliente_contacto

Columnas:
  id_[entidad]           → clave primaria: id_cliente, id_producto
  [entidad]_src_key      → clave del sistema fuente: cliente_src_key
  fk_[entidad_referida]  → clave foránea: fk_ciudad
  fecha_*                → campos de fecha: fecha_alta, fecha_carga
  es_*                   → booleanos: es_vigente, es_activo
  hash_*                 → checksums: hash_registro
```

### Estrategias de Particionamiento

Para tablas de gran volumen (millones a miles de millones de filas), el particionamiento es esencial:

**Particionamiento por rango de fechas** (el más común para un EDW):

```sql
-- PostgreSQL: tabla de pedidos particionada por mes
CREATE TABLE edw.pedido (
    id_pedido        BIGSERIAL,
    fecha_pedido     DATE         NOT NULL,
    id_cliente       BIGINT       NOT NULL,
    total            NUMERIC(14,2),
    fecha_efectiva   DATE         NOT NULL,
    es_vigente       BOOLEAN      NOT NULL DEFAULT TRUE
) PARTITION BY RANGE (fecha_pedido);

-- Crear particiones mensuales
CREATE TABLE edw.pedido_2025_01 PARTITION OF edw.pedido
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
CREATE TABLE edw.pedido_2025_02 PARTITION OF edw.pedido
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
-- ... y así para cada mes
```

**Beneficios del particionamiento en el EDW:**
- **Partition pruning:** las queries que filtran por fecha solo escanean las particiones relevantes.
- **Carga más eficiente:** se puede cargar datos en una partición nueva sin bloquear las existentes.
- **Archivado selectivo:** las particiones antiguas pueden moverse a almacenamiento más barato.
- **Mantenimiento:** `VACUUM`, `ANALYZE` y reconstrucción de índices se hacen por partición.

### Estrategia de Indexación

```sql
-- Índices esenciales para cada tabla del EDW:

-- 1. Primary Key (automática con la restricción PK)
-- 2. Índice de búsqueda por clave fuente (para ETL incremental)
CREATE INDEX idx_cliente_src_key ON edw.cliente(cliente_src_key);

-- 3. Índice para el registro vigente (para la resolución de SCD)
CREATE UNIQUE INDEX uq_cliente_vigente 
    ON edw.cliente(cliente_src_key, id_sistema_fuente) 
    WHERE es_vigente = TRUE;

-- 4. Índices de fecha para partición y consultas temporales
CREATE INDEX idx_pedido_fecha ON edw.pedido(fecha_pedido);

-- 5. Índices de FK para JOINs frecuentes del ETL de derivación
CREATE INDEX idx_pedido_cliente ON edw.pedido(id_cliente);
CREATE INDEX idx_linea_pedido ON edw.linea_pedido(id_pedido);
```

**Regla práctica:** en el EDW, los índices se diseñan para optimizar el **ETL de derivación** (lectura para los Data Marts), no para queries ad-hoc de usuarios.

---

## Gestión de Metadatos en el EDW

Los metadatos son "datos sobre los datos" y su gestión sistemática es un pilar de la arquitectura Inmon que muchos proyectos subestiman.

### Tipos de metadatos en el EDW

| Tipo | Descripción | Ejemplos |
|---|---|---|
| **Técnicos** | Estructura y configuración del EDW | DDL de tablas, tipos de datos, índices, particiones |
| **De negocio** | Significado y contexto de los datos | Glosario corporativo, definiciones de KPIs, reglas de cálculo |
| **Operacionales** | Estado y ejecución de los procesos | Última carga exitosa, registros procesados, errores detectados |
| **De linaje** | Trazabilidad origen→destino | De qué tabla fuente viene cada columna del EDW, qué transformaciones se aplicaron |

### Catálogo de Datos

El catálogo de datos es la implementación técnica de los metadatos. Herramientas modernas:

| Herramienta | Tipo | Características |
|---|---|---|
| **Apache Atlas** | Open source | Linaje, clasificación, gobernanza. Ecosistema Hadoop |
| **DataHub (LinkedIn)** | Open source | Linaje automático, búsqueda, documentación colaborativa |
| **Amundsen (Lyft)** | Open source | Descubrimiento de datos, perfiles, propiedad |
| **Atlan** | Comercial | Catálogo activo con gobernanza y colaboración |
| **Collibra** | Comercial | Plataforma empresarial de gobernanza y catálogo |
| **Microsoft Purview** | Cloud | Gobernanza unificada para Azure y entornos híbridos |

---

## El EDW en Plataformas Modernas

Si bien los conceptos de Inmon fueron formulados para motores relacionales tradicionales (Oracle, SQL Server, DB2), los principios se aplican perfectamente en plataformas modernas:

### Cloud Data Warehouses

| Plataforma | Ventajas para el EDW Inmon | Consideraciones |
|---|---|---|
| **Snowflake** | Separación compute/storage, escalado automático, Time Travel (historial nativo) | Costo por uso; requiere gestión de warehouses virtuales |
| **Google BigQuery** | Serverless, particionamiento automático, integración con GCP | Modelo de pricing por bytes escaneados; requiere optimizar queries |
| **Amazon Redshift** | Integración con ecosistema AWS, Redshift Spectrum para datos en S3 | Requiere gestión de clusters; less serverless que BigQuery |
| **Azure Synapse** | Integración con ecosistema Microsoft, pools dedicados y serverless | Complejidad de configuración; múltiples motores |
| **Databricks** | Lakehouse; combina data lake con capacidades de DWH; Delta Lake para ACID | Curva de aprendizaje; ideal si ya se usa Spark |

### EDW vs. Data Lake vs. Data Lakehouse

El EDW de Inmon coexiste con otras arquitecturas modernas. Entender las diferencias es clave:

```
                    EDW (Inmon)              Data Lake           Data Lakehouse
──────────────── ──────────────────── ──────────────────── ─────────────────────
Esquema           Schema-on-Write      Schema-on-Read       Schema-on-Write +
                  (3FN definido        (esquema flexible,   Schema-on-Read
                   antes de cargar)     se define al leer)  (ambos modelos)

Datos             Estructurados        Todos los tipos      Todos los tipos
                  (tablas)             (raw, semi, no-      con capa tabular
                                        estructurados)      (Delta, Iceberg)

Calidad           Alta (validado       Variable (puede      Alta (con
                   en ETL)              contener basura)    validación)

Usuarios          Analistas de BI      Data Scientists,     Todos
                                        Ingenieros

Latencia          Batch (diario/       Near-real-time       Near-real-time
                   horario)             a batch              a batch

Costo             Alto (compute +      Bajo (storage        Medio (storage
                   storage premium)     barato, S3/GCS)     barato + compute)
```

> **Posición de Inmon:** El EDW sigue siendo necesario como capa de integración y consistencia, independientemente de si los datos se almacenan en un data lake. El Data Lakehouse puede ser el sustrato tecnológico del EDW moderno, pero los principios de integración, historial y consistencia siguen siendo válidos.

---

## Política de Retención y Archivado

El EDW de Inmon, por definición, no borra datos. Pero el crecimiento indefinido tiene costos. Una política de retención define cuánto tiempo los datos permanecen en almacenamiento caliente (rápido, caro) vs. frío (lento, barato):

```
Política de retención ejemplo:

┌─────────────────────────────────────────────────────────────────────┐
│ Tier 1 — HOT (últimos 2 años)                                      │
│   Almacenamiento: SSD / Storage premium                            │
│   Acceso: queries directas, ETL de Data Marts                      │
│   Latencia: milisegundos                                           │
├─────────────────────────────────────────────────────────────────────┤
│ Tier 2 — WARM (2 a 5 años)                                        │
│   Almacenamiento: HDD / Standard storage                          │
│   Acceso: queries bajo demanda con mayor latencia                  │
│   Latencia: segundos                                               │
├─────────────────────────────────────────────────────────────────────┤
│ Tier 3 — COLD (más de 5 años)                                      │
│   Almacenamiento: Archive (S3 Glacier, Azure Archive, GCS Archive) │
│   Acceso: restauración bajo solicitud (horas)                      │
│   Latencia: horas                                                  │
│   Uso: cumplimiento regulatorio, auditorías                        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Ejemplo Ampliado: EDW Completo para Empresa de Distribución

A continuación, un esquema más completo del EDW 3FN, mostrando múltiples sujetos de datos interconectados:

```sql
-- ============================================================
-- SUJETO: GEOGRAFÍA
-- ============================================================
CREATE TABLE edw.pais (
    id_pais       SMALLSERIAL PRIMARY KEY,
    codigo_iso    CHAR(3)     NOT NULL UNIQUE,
    nombre        VARCHAR(100) NOT NULL
);

CREATE TABLE edw.provincia (
    id_provincia  SERIAL PRIMARY KEY,
    nombre        VARCHAR(100) NOT NULL,
    id_pais       SMALLINT    NOT NULL REFERENCES edw.pais
);

CREATE TABLE edw.ciudad (
    id_ciudad     SERIAL PRIMARY KEY,
    nombre        VARCHAR(100) NOT NULL,
    codigo_postal VARCHAR(10),
    id_provincia  INTEGER     NOT NULL REFERENCES edw.provincia
);

-- ============================================================
-- SUJETO: CLIENTES (con historial temporal)
-- ============================================================
CREATE TABLE edw.segmento (
    id_segmento   SMALLSERIAL PRIMARY KEY,
    nombre        VARCHAR(50) NOT NULL,
    descripcion   TEXT,
    criterio      TEXT
);

CREATE TABLE edw.tipo_cliente (
    id_tipo       SMALLSERIAL PRIMARY KEY,
    descripcion   VARCHAR(50) NOT NULL
);

CREATE TABLE edw.cliente (
    id_cliente        BIGSERIAL PRIMARY KEY,
    cliente_src_key   VARCHAR(30) NOT NULL,
    id_tipo           SMALLINT    NOT NULL REFERENCES edw.tipo_cliente,
    razon_social      VARCHAR(200) NOT NULL,
    id_ciudad         INTEGER     NOT NULL REFERENCES edw.ciudad,
    id_segmento       SMALLINT    REFERENCES edw.segmento,
    estado            CHAR(1)     NOT NULL DEFAULT 'A',
    -- Control temporal
    fecha_efectiva    DATE        NOT NULL,
    fecha_vencimiento DATE        NOT NULL DEFAULT '9999-12-31',
    es_vigente        BOOLEAN     NOT NULL DEFAULT TRUE,
    -- Auditoría
    id_sistema_fuente SMALLINT    NOT NULL,
    hash_registro     CHAR(64),
    fecha_carga       TIMESTAMP   NOT NULL DEFAULT NOW()
);

-- ============================================================
-- SUJETO: PRODUCTOS
-- ============================================================
CREATE TABLE edw.departamento (
    id_departamento SMALLSERIAL PRIMARY KEY,
    nombre          VARCHAR(100) NOT NULL
);

CREATE TABLE edw.categoria (
    id_categoria    SERIAL PRIMARY KEY,
    nombre          VARCHAR(100) NOT NULL,
    id_departamento SMALLINT NOT NULL REFERENCES edw.departamento
);

CREATE TABLE edw.subcategoria (
    id_subcategoria SERIAL PRIMARY KEY,
    nombre          VARCHAR(100) NOT NULL,
    id_categoria    INTEGER NOT NULL REFERENCES edw.categoria
);

CREATE TABLE edw.producto (
    id_producto       BIGSERIAL PRIMARY KEY,
    producto_src_key  VARCHAR(30) NOT NULL,
    nombre            VARCHAR(200) NOT NULL,
    id_subcategoria   INTEGER     NOT NULL REFERENCES edw.subcategoria,
    precio_lista      NUMERIC(12,2),
    costo_unitario    NUMERIC(12,2),
    unidad_medida     VARCHAR(20),
    -- Control temporal
    fecha_efectiva    DATE        NOT NULL,
    fecha_vencimiento DATE        NOT NULL DEFAULT '9999-12-31',
    es_vigente        BOOLEAN     NOT NULL DEFAULT TRUE,
    -- Auditoría
    id_sistema_fuente SMALLINT    NOT NULL,
    hash_registro     CHAR(64),
    fecha_carga       TIMESTAMP   NOT NULL DEFAULT NOW()
);

-- ============================================================
-- SUJETO: VENTAS (transaccional)
-- ============================================================
CREATE TABLE edw.pedido (
    id_pedido         BIGSERIAL PRIMARY KEY,
    pedido_src_key    VARCHAR(30) NOT NULL,
    fecha_pedido      DATE        NOT NULL,
    id_cliente        BIGINT      NOT NULL REFERENCES edw.cliente,
    id_vendedor       BIGINT,
    numero_factura    VARCHAR(30),
    estado_pedido     VARCHAR(20) NOT NULL,
    moneda            CHAR(3)     NOT NULL DEFAULT 'ARS',
    -- Auditoría
    id_sistema_fuente SMALLINT    NOT NULL,
    fecha_carga       TIMESTAMP   NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (fecha_pedido);

CREATE TABLE edw.linea_pedido (
    id_linea          BIGSERIAL PRIMARY KEY,
    id_pedido         BIGINT      NOT NULL,
    id_producto       BIGINT      NOT NULL REFERENCES edw.producto,
    cantidad          NUMERIC(10,3) NOT NULL,
    precio_unitario   NUMERIC(12,2) NOT NULL,
    descuento         NUMERIC(5,4)  NOT NULL DEFAULT 0,
    costo_unitario    NUMERIC(12,2),
    -- Auditoría
    fecha_carga       TIMESTAMP   NOT NULL DEFAULT NOW()
);
```

---

## Entregables de la Etapa 2

1. ✅ **Esquema físico del EDW** en 3FN, con todas las tablas, columnas, tipos y restricciones.
2. ✅ **Scripts DDL** de creación de todas las tablas del EDW.
3. ✅ **Diseño de la Staging Area** con sus tablas de trabajo temporales.
4. ✅ **Matriz de Mapeo Fuente-Destino** (*Source-to-Target Mapping*): qué campo de qué sistema fuente va a qué columna del EDW, con las transformaciones necesarias.
5. ✅ **Documento de Reglas de Integración**: cómo se resuelven conflictos entre fuentes, cómo se generan las claves, qué prioridad tiene cada sistema.
6. ✅ **Estimación de volúmenes**: cantidad de registros esperados por tabla, crecimiento anual, política de retención.

---

## Duración típica y esfuerzo

| Factor | Referencia |
|---|---|
| **Alcance inicial (3-5 sujetos)** | 2 a 4 meses |
| **Alcance empresarial completo** | 6 a 18 meses |
| **Principal desafío** | Resolver la integración de identificadores entre sistemas: el mismo cliente tiene ID distinto en el ERP y en el CRM. |
| **Principal riesgo** | Scope creep: intentar incluir todos los datos de todos los sistemas en la primera iteración. |

---

## Relación con las etapas siguientes

```
ETAPA 2: EDW Normalizado (3FN)
        │
        │ Produce:
        │  • Repositorio central integrado
        │  • Historial completo de datos
        │  • Única fuente de verdad
        │
        ▼
ETAPA 3: ETL (Extracción, Transformación y Carga)
        │ El ETL es el proceso que lleva los datos
        │ desde los sistemas fuente hasta el EDW.
        ▼
ETAPA 4: Data Marts
        │ Los Data Marts se alimentan del EDW,
        │ desnormalizando solo lo necesario
        │ para cada área de negocio.
        ▼
```

---

## Lecturas recomendadas

- **Inmon, W.H.** — *Building the Data Warehouse*, 4ta edición. Capítulos 4, 5 y 6. Wiley.
- **Inmon, W.H. & Linstedt, D.** — *Data Architecture: A Primer for the Data Scientist*. Morgan Kaufmann.
- **Kimball, R.** (perspectiva crítica) — *The Data Warehouse Toolkit*, 3ra edición. Capítulo 1, sección "The Data Warehouse vs. the Operational System". Wiley.
- **Golfarelli, M. & Rizzi, S.** — *Data Warehouse Design: Modern Principles and Methodologies*. McGraw-Hill.
- **Date, C.J.** — *An Introduction to Database Systems*, 8va edición. Addison-Wesley. (Referencia canónica de normalización).
- **Kleppmann, M.** — *Designing Data-Intensive Applications*. O'Reilly. (Contexto moderno de almacenamiento y procesamiento de datos).
- **Reis, J. & Housley, M.** — *Fundamentals of Data Engineering*. O'Reilly. (Perspectiva moderna del EDW en cloud).
