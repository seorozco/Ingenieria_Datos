# Clase 09 — Introducción al Data Warehouse

> **Asignatura:** Ingeniería de Datos  
> **Docente:** Ing. Sergio Orozco  
> **Unidad:** IV — Data Warehouse y Modelado Dimensional

---

## Objetivos de la Clase

Al finalizar esta clase, el alumno será capaz de:

- Explicar qué es un **Data Warehouse** y el problema que vino a resolver.
- Describir las **4 características** de la definición de Inmon.
- Diferenciar con precisión **OLTP y OLAP**.
- Comparar los enfoques **top-down (Inmon)** y **bottom-up (Kimball)**.
- Entender qué es un **Data Mart** y su relación con el DWH.
- Conocer las características principales de **Snowflake**, **BigQuery** y **Redshift**.

---

## 1. El Problema que Motivó el Data Warehouse

Para entender el Data Warehouse, primero hay que entender el problema que vino a resolver.

### 1.1 Los sistemas operativos: diseñados para el presente

A partir de los años 70, las organizaciones empezaron a digitalizar sus operaciones con sistemas transaccionales: gestión de inventario, facturación, nómina, contabilidad. Cada área tenía su propia base de datos, optimizada para registrar transacciones rápidas y frecuentes.

Una empresa manufacturera típica tendría:
- Una BD de **compras** (proveedores, órdenes, recepciones).
- Una BD de **producción** (órdenes de trabajo, consumo de materiales).
- Una BD de **ventas** (pedidos, facturas, clientes).
- Una BD de **finanzas** (cuentas, presupuestos, pagos).

Estas bases de datos están diseñadas con un objetivo claro: **registrar transacciones del presente de forma rápida y confiable**. Están normalizadas, indexadas para escritura frecuente y optimizadas para operaciones individuales.

### 1.2 El problema: querer analizar lo que los sistemas operativos no pueden dar

Con el tiempo, los directivos empezaron a hacer preguntas que los sistemas operativos no podían responder bien:

- *"¿Cuáles fueron nuestros 10 productos más rentables en los últimos 3 años, trimestre a trimestre?"*
- *"¿Qué regiones tienen mayor tasa de devoluciones y en qué categorías?"*
- *"¿Cómo evolucionó el margen promedio por cliente desde que implementamos el programa de fidelidad?"*

Cuando alguien intentaba responder estas preguntas directamente contra los sistemas operativos, ocurrían cuatro problemas:

```
PROBLEMA 1 — LENTITUD
Una consulta analítica que agrega 3 años de transacciones puede tardar
HORAS en una base de datos transaccional (diseñada para milisegundos).

PROBLEMA 2 — BLOQUEO DEL SISTEMA PRODUCTIVO
Una consulta pesada consume CPU, RAM y I/O del servidor, ralentizando
o bloqueando las operaciones. La cajera no puede facturar porque alguien
está corriendo un reporte de análisis de 3 años.

PROBLEMA 3 — DATOS EN SILOS
Las ventas están en un sistema, los costos en otro, los clientes en un tercero.
Para un análisis de rentabilidad hay que cruzar datos de 3 sistemas con
distintos formatos, distintos IDs y distintas convenciones.

PROBLEMA 4 — SIN HISTORIA
Los sistemas transaccionales están optimizados para el estado ACTUAL.
El precio actual sobreescribe al anterior. No hay historial analítico.
```

> **Caso real:** Un director de ventas necesita el margen por categoría del último año vs. el año anterior. Su analista tarda 3 días cruzando manualmente Excels exportados del ERP con planillas de costos. El informe llega con 4 días de retraso y algunos números no cierran porque los sistemas usaban convenciones distintas. Esta situación se repetía en miles de organizaciones en los años 80 y fue lo que motivó la creación del Data Warehouse.

### 1.3 La solución: separar los mundos operativo y analítico

La solución fue conceptualmente elegante: **construir un sistema separado**, diseñado exclusivamente para responder preguntas analíticas, al que se le mueven periódicamente los datos de todos los sistemas operativos.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DOS MUNDOS SEPARADOS                             │
├───────────────────────────┬─────────────────────────────────────── │
│  MUNDO OPERATIVO (OLTP)   │  MUNDO ANALÍTICO (OLAP / DWH)         │
│                           │                                        │
│  Registrar transacciones  │  Analizar el negocio                   │
│  Rápido en escritura      │  Rápido en lectura masiva              │
│  Datos actuales           │  Historial de años                     │
│  Múltiples sistemas       │  Modelo unificado e integrado          │
│  Normalizado (3NF)        │  Desnormalizado (estrella)             │
│                           │                                        │
│  ERP, CRM, e-commerce     │  Data Warehouse                        │
│                           │                                        │
│                  ◄────── ETL ──────►                               │
│                  (pipeline que mueve                               │
│                   datos periódicamente)                            │
└───────────────────────────┴─────────────────────────────────────── │
```

---

## 2. ¿Qué es un Data Warehouse?

La definición clásica fue formulada por **Bill Inmon** en 1990, considerado el padre del Data Warehouse:

> *"Un Data Warehouse es una colección de datos orientada a temas, integrada, no volátil y variante en el tiempo, que soporta las decisiones de la gerencia."*

### Las 4 Características de la Definición de Inmon

#### 1️⃣ Orientada a Temas (Subject-Oriented)

El DWH no está organizado alrededor de las **aplicaciones** que generan los datos (como el ERP o el CRM), sino alrededor de los **temas de negocio** que interesan a la organización para el análisis.

```
Organización en el ERP (por aplicación):
  tablas BSEG, BKPF, VBAK, VBAP, KNA1, MARA... (nomenclatura SAP)
  → difícil de entender para un analista

Organización en el DWH (por tema de negocio):
  Ventas → Clientes → Productos → Finanzas → Logística
  → intuitivo para el analista de negocio
```

#### 2️⃣ Integrada (Integrated)

El DWH consolida datos de **múltiples fuentes heterogéneas** en un modelo único y consistente. Las distintas convenciones de cada sistema fuente se resuelven en el proceso ETL:

| Aspecto | ERP (Sistema A) | CRM (Sistema B) | Data Warehouse |
|---|---|---|---|
| Género | `M` / `F` | `Masculino` / `Femenino` | `M` / `F` |
| Moneda | `ARS` | `Pesos` | `ARS` |
| País | `AR` | `Argentina` | `AR` |
| ID cliente | `CLI-4521` | `4521` | `4521` |

#### 3️⃣ No Volátil (Non-Volatile)

Los datos que ingresan al DWH **no se modifican ni se eliminan**. A diferencia del sistema operativo (donde un cambio de precio sobreescribe el anterior), en el DWH se agregan nuevos registros pero los históricos permanecen intactos.

```
En el ERP (volátil):
  [cliente: "Ana García" → ciudad: "Buenos Aires"]  ← actualiza y pierde el valor anterior

En el DWH (no volátil):
  [Ana García | ciudad: "Córdoba" | válido_desde: 2020-01-01 | válido_hasta: 2024-03-14]
  [Ana García | ciudad: "Buenos Aires" | válido_desde: 2024-03-15 | válido_hasta: NULL]
  ← se pueden analizar compras antes y después de la mudanza
```

#### 4️⃣ Variante en el Tiempo (Time-Variant)

El DWH guarda el **historial completo** de los datos. Cada registro tiene una dimensión temporal que permite analizar evoluciones, tendencias y comparaciones período a período.

El horizonte temporal típico de un DWH es de **5 a 10 años**, mientras que los sistemas operativos suelen conservar solo 1-2 años.

---

## 3. Evolución Histórica del Data Warehouse

```
1970s         1990s          2005           2015           2020
  │              │              │              │              │
  ▼              ▼              ▼              ▼              ▼
Reportes     DWH On-Prem    Big Data       Cloud DWH     Lakehouse
del ERP      (Teradata)     + Hadoop       Snowflake     Delta Lake
             Inmon / Kimball  Spark         BigQuery      Apache Iceberg
```

### Era 1 — Reportes del ERP (1970s-1980s)
Módulos de reporte integrados al ERP. Corrían directamente sobre la BD transaccional. Lentos, rígidos y bloqueaban el sistema productivo.

### Era 2 — Data Warehouse On-Premise (1990s-2005)
Bill Inmon (1992) y Ralph Kimball (1996) formalizaron el concepto. Surgieron plataformas como **Teradata**, **Oracle Data Warehouse** e **IBM DB2**. Potentes pero extremadamente costosas (proyectos de millones de dólares y 12-36 meses). Solo accesibles para grandes corporaciones.

### Era 3 — Big Data (2005-2015)
La explosión de internet generó volúmenes que los DWH tradicionales no podían manejar. Surgió **Apache Hadoop** (2006) y **Apache Spark** (2014). Nació el concepto de **Data Lake**: almacenar datos en formato crudo sin esquema previo para procesarlos después.

### Era 4 — Cloud Data Warehouse (2015-presente)
Las plataformas cloud democratizaron el acceso:
- **Amazon Redshift** (2013): primer DWH cloud masivo, basado en PostgreSQL columnar.
- **Google BigQuery** (2017): serverless, pago por bytes procesados.
- **Snowflake** (2014): separación cómputo-almacenamiento, multi-cloud.

### Era 5 — Data Lakehouse (2020-presente)
Formatos como **Delta Lake** (Databricks), **Apache Iceberg** y **Apache Hudi** traen transacciones ACID al almacenamiento en objetos cloud. Combina la flexibilidad del Data Lake con las garantías del DWH.

---

## 4. OLTP vs. OLAP: El Contraste Fundamental

Esta distinción es **absolutamente crítica** en arquitectura de datos.

### Diseño OLTP: normalización para escritura eficiente

El diseño normalizado divide la información en muchas tablas pequeñas para eliminar la redundancia. Es perfecto para escritura, pero problemático para análisis:

```sql
-- En una base OLTP normalizada, esta consulta analítica requiere 7 JOINs:
SELECT SUM(dp.cantidad * dp.precio_unit) AS total_ventas
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
-- Puede tardar MINUTOS en tablas con millones de registros
```

### Diseño OLAP: desnormalización para lectura eficiente

```sql
-- En un DWH con esquema estrella (modelado dimensional):
SELECT SUM(f.total_venta) AS total_ventas
FROM fact_ventas f
JOIN dim_producto p ON f.id_producto = p.id_producto
JOIN dim_cliente c ON f.id_cliente = c.id_cliente
JOIN dim_tiempo t ON f.id_tiempo = t.id_tiempo
WHERE p.nombre_producto = 'Laptop'
  AND c.region = 'Patagonia'
  AND t.trimestre = 3
  AND t.anio = 2024;
-- 4 JOINs sobre tablas pequeñas (dimensiones). Puede tardar SEGUNDOS.
```

### Tabla comparativa

| Dimensión | OLTP | OLAP |
|---|---|---|
| **Propósito** | Procesar transacciones | Responder preguntas analíticas |
| **Operaciones** | INSERT, UPDATE, DELETE | SELECT + GROUP BY + agregaciones |
| **Filas por consulta** | 1 a miles | Millones a miles de millones |
| **Usuarios** | Miles (empleados) | Decenas (analistas, gerentes) |
| **Diseño** | Normalizado (3NF) | Desnormalizado (esquema estrella) |
| **Almacenamiento** | Por filas | Por columnas |
| **Horizonte temporal** | Estado actual | Años de historia |
| **Tiempo de respuesta** | Milisegundos | Segundos a minutos |
| **Ejemplos** | SAP ERP, Salesforce | Snowflake, BigQuery, Redshift |

---

## 5. Las Dos Grandes Arquitecturas: Inmon vs. Kimball

### 5.1 Inmon: Top-Down (de arriba hacia abajo)

Construir primero un **Enterprise Data Warehouse (EDW) normalizado** con todos los datos de la empresa, y a partir de él derivar Data Marts para cada área.

```
Sistemas Fuente  ──►  Staging  ──►  EDW (3NF)  ──►  Data Mart Ventas
                                   (normalizado)  ──►  Data Mart Finanzas
                                                  ──►  Data Mart Logística
```

**✅ Ventajas:**
- Consistencia total: todos los Data Marts vienen de la misma fuente de verdad.
- Flexibilidad para agregar nuevas áreas sin romper las existentes.
- Ideal para organizaciones grandes con mucha diversidad de fuentes.

**❌ Desventajas:**
- Largo tiempo hasta el primer resultado (12-36 meses).
- Alto costo inicial de modelado y desarrollo.
- Requiere equipos muy experimentados en diseño de datos.

### 5.2 Kimball: Bottom-Up (de abajo hacia arriba)

Construir primero los **Data Marts individuales** por área de negocio usando modelado dimensional, garantizando que se puedan integrar a través de **dimensiones conformadas**.

```
Sistemas Fuente  ──►  Staging  ──►  Data Mart Ventas (esquema ★)
                               ──►  Data Mart Finanzas (esquema ★)
                               ──►  Data Mart Logística (esquema ★)

El DWH = suma de los Data Marts integrados por dimensiones conformadas
```

**✅ Ventajas:**
- Time-to-value rápido (3-6 meses para el primer Data Mart).
- Orientado al usuario de negocio: el esquema estrella es intuitivo.
- Iterativo: se entrega valor en incrementos.

**❌ Desventajas:**
- Riesgo de inconsistencias si los Data Marts no usan dimensiones conformadas.
- Puede acumular deuda técnica si no hay gobernanza.

> **La práctica actual:** La mayoría de las implementaciones modernas son híbridas. Lo que sí persiste es la **metodología dimensional de Kimball** (esquema estrella, tablas de hechos y dimensiones) como el estándar de facto para modelado analítico, independientemente de la arquitectura macro.

---

## 6. Plataformas Cloud de Data Warehouse

### Amazon Redshift

Primer DWH cloud en ganar adopción masiva (2013). Basado en PostgreSQL con almacenamiento columnar y procesamiento paralelo (MPP).

**Fortalezas:** Profunda integración con AWS (S3, Glue, SageMaker). Maduro y con amplia comunidad. Redshift Serverless (2022) agrega elasticidad.  
**Ideal para:** organizaciones ya invertidas en AWS.

### Google BigQuery

Pionero en el modelo serverless (2012). No hay clusters que configurar. El sistema escala automáticamente.

**Modelo de costo:** Pago por bytes procesados en cada consulta. Con buenas prácticas (particionamiento, clustering), el costo puede reducirse drásticamente.  
**Fortalezas:** Cero administración. Integración nativa con ML (BigQuery ML permite modelos con SQL).  
**Ideal para:** organizaciones que priorizan simplicidad operativa y escala extrema.

### Snowflake

La innovación central de Snowflake es la **separación completa de cómputo y almacenamiento**:

```
┌─────────────────────────────────────────────────────────┐
│  SNOWFLAKE — ARQUITECTURA                               │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │          CAPA DE SERVICIOS CLOUD               │   │
│  │   (metadata, optimizador, seguridad, catalogo) │   │
│  └───────────────────┬─────────────────────────────┘   │
│                      │                                  │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐               │
│  │ Virtual │  │ Virtual │  │ Virtual │  ← cada equipo │
│  │Warehouse│  │Warehouse│  │Warehouse│    tiene el    │
│  │(Ventas) │  │(ML)     │  │(Finance)│    suyo propio │
│  └────┬────┘  └────┬────┘  └────┬────┘               │
│       └────────────┴────────────┘                      │
│                        │ todos acceden a los           │
│                        ▼ mismos datos                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │    ALMACENAMIENTO S3 / GCS / Azure Blob         │   │
│  │    (columnar comprimido — compartido)           │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

**Beneficio clave:** El equipo de ML puede correr modelos intensivos con 16 nodos sin afectar la performance de las consultas de reportes del equipo de ventas. Cada Virtual Warehouse se pausa automáticamente cuando está inactivo (no se paga cómputo ocioso).

**Características destacadas:**
- **Multi-cloud:** corre en AWS, GCP y Azure.
- **Time Travel:** acceder a versiones anteriores de los datos hasta 90 días atrás.
- **Zero-copy cloning:** clonar una tabla completa en segundos sin duplicar almacenamiento.
- **Data Sharing:** compartir datos con otras organizaciones sin copiarlos.

---

## Resumen de la Clase

| Concepto | Definición en una frase |
|---|---|
| **Data Warehouse** | Sistema analítico separado de los operativos, optimizado para responder preguntas de negocio históricas |
| **4 características (Inmon)** | Orientado a temas, integrado, no volátil, variante en el tiempo |
| **OLTP** | Sistemas operativos diseñados para transacciones frecuentes y rápidas |
| **OLAP** | Sistemas analíticos diseñados para consultas masivas sobre datos históricos |
| **Inmon** | Top-down: EDW normalizado primero, Data Marts después |
| **Kimball** | Bottom-up: Data Marts dimensionales primero, integración incremental |
| **Data Mart** | Subconjunto temático del DWH para un área de negocio específica |
| **Snowflake** | DWH cloud con separación de cómputo y almacenamiento, multi-cloud |
| **BigQuery** | DWH cloud serverless de Google, pago por consulta |
| **Redshift** | DWH cloud de AWS, basado en PostgreSQL columnar |

---

> 💡 **Para la próxima clase:** Ahora sabemos qué es el DWH y qué arquitecturas existen. En la **Clase 10** vamos a aprender a *diseñar* el modelo de datos dentro del DWH: el modelado dimensional, el esquema estrella y cómo manejar los datos que cambian con el tiempo con las estrategias SCD.
