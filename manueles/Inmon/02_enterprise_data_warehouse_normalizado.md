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
