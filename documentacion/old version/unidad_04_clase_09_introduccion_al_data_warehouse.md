# Unidad IV · Clase 09 — Introducción al Data Warehouse

> **Asignatura:** Ingeniería de Datos  
> **Docente:** Ing. Sergio Orozco  
> **Unidad:** IV — Data Warehouse y Modelado Dimensional  
> **Modalidad:** Teórica

---

## Objetivos de la Clase

Al finalizar esta clase, el alumno será capaz de:

- Explicar qué es un **Data Warehouse**, para qué sirve y cuál es el problema que vino a resolver.
- Describir la evolución histórica del almacenamiento analítico de datos.
- Diferenciar con precisión los sistemas **OLTP** y **OLAP** en cuanto a diseño, uso y optimización.
- Comparar las dos grandes arquitecturas de Data Warehouse: el enfoque **top-down de Inmon** y el enfoque **bottom-up de Kimball**.
- Entender qué es un **Data Mart** y cuál es su relación con el DWH.
- Conocer las principales **plataformas cloud** de Data Warehouse del mercado y sus características.
- Aplicar los conceptos a un caso empresarial real analizando cuándo y cómo construir un DWH.

---

## 1. El Problema que Motivó el Data Warehouse

Para entender el Data Warehouse, primero hay que entender el problema que vino a resolver.

### 1.1 La situación original: los sistemas operativos

A partir de los años 70, las organizaciones empezaron a digitalizar sus operaciones. Surgieron los primeros **sistemas transaccionales**: sistemas de gestión de inventario, facturación, nómina, contabilidad. Cada área tenía su propia base de datos, optimizada para registrar transacciones rápidas y frecuentes.

El ERP (Enterprise Resource Planning) de una empresa manufacturera típica podría tener:
- Una base de datos de **compras** (proveedores, órdenes de compra, recepciones).
- Una base de datos de **producción** (órdenes de trabajo, consumo de materiales, tiempos).
- Una base de datos de **ventas** (pedidos, facturas, clientes, precios).
- Una base de datos de **finanzas** (cuentas contables, presupuestos, pagos).

Cada una de estas bases de datos fue diseñada con un objetivo claro: **registrar transacciones del presente de forma rápida y confiable**. Están normalizadas (sin redundancia), indexadas para escritura frecuente y optimizadas para operaciones individuales: insertar una factura, actualizar el stock de un producto, registrar un pago.

### 1.2 El problema: querer analizar lo que los sistemas operativos no pueden

Con el tiempo, los directivos y gerentes empezaron a hacer preguntas que los sistemas operativos no podían responder bien:

- *"¿Cuáles fueron nuestros 10 productos más rentables en los últimos 3 años, comparados trimestre a trimestre?"*
- *"¿Qué regiones tienen mayor tasa de devoluciones y en qué categorías?"*
- *"¿Cómo evolucionó el margen promedio por cliente desde que implementamos el programa de fidelidad?"*

Cuando alguien intentaba responder estas preguntas directamente contra los sistemas operativos, ocurrían varias cosas malas:

**1. Lentitud:** Una consulta analítica que agrega 3 años de transacciones de ventas cruzadas con datos de clientes, productos y logística puede tardar horas en una base de datos transaccional.

**2. Bloqueo del sistema productivo:** Al ejecutar esa consulta pesada, se consume CPU, memoria y I/O del servidor, lo que ralentiza o bloquea las operaciones del negocio. La cajera no puede facturar porque alguien está corriendo un reporte.

**3. Datos en silos:** Las ventas están en un sistema, los costos en otro, los datos de clientes en un tercero. Para un análisis de rentabilidad completo, habría que cruzar manualmente datos de tres sistemas distintos, con distintos formatos, distintos identificadores y distintas convenciones.

**4. Sin historia:** Los sistemas transaccionales están optimizados para el estado actual. A veces el stock actual sobreescribe al de ayer; el precio actual sobreescribe al anterior. No hay historial analítico completo.

> **Caso ilustrativo:** El director de ventas de una empresa de retail necesita saber el margen por categoría de producto del último año, comparado con el año anterior. Su asistente tarda 3 días en cruzar manualmente Excel exportado del ERP con una planilla de costos del área de compras y otra de logística. El resultado es un informe de 10 páginas que llega con 4 días de retraso. Cuando llega, algunos números no cierran porque cada Excel usaba una convención distinta de redondeo.

Este escenario, repetido en miles de organizaciones del mundo en los años 80, fue el que motivó la creación del Data Warehouse.

### 1.3 La solución: separar los mundos analítico y transaccional

La solución fue conceptualmente simple: **construir un sistema separado**, diseñado exclusivamente para responder preguntas analíticas, al que se le mueven periódicamente los datos de todos los sistemas operativos.

Este sistema tiene características opuestas a los sistemas transaccionales:
- **Orientado al análisis**, no a las transacciones.
- **Integra** datos de múltiples fuentes en un modelo unificado.
- **Guarda historia** completa de los datos.
- **Está optimizado para consultas de lectura** complejas con grandes volúmenes.
- **No interfiere** con los sistemas productivos.

A este sistema lo llamamos **Data Warehouse**.

---

## 2. ¿Qué es un Data Warehouse?

La definición clásica fue formulada por **Bill Inmon**, considerado el padre del Data Warehouse, en 1990:

> *"Un Data Warehouse es una colección de datos orientada a temas, integrada, no volátil y variante en el tiempo, que soporta las decisiones de la gerencia."*

Analicemos cada término de esta definición:

### Orientada a temas (*Subject-Oriented*)

El DWH no está organizado alrededor de las aplicaciones que generan los datos (como el ERP o el CRM), sino alrededor de los **temas de negocio** que interesan a la organización para el análisis: **Ventas**, **Clientes**, **Productos**, **Finanzas**, **Logística**.

En el ERP, los datos de una venta están distribuidos en tablas como `BSEG`, `BKPF`, `VBAK`, `VBAP`, `KNA1` (nomenclatura SAP). En el DWH, toda esa información se consolida en un modelo simple orientado al analista: tabla de hechos de ventas con sus dimensiones de cliente, producto, tiempo y territorio.

### Integrada (*Integrated*)

Consolida datos de **múltiples fuentes heterogéneas** en un modelo único y consistente. Las distintas convenciones, formatos y nomenclaturas de cada sistema fuente se resuelven en el proceso ETL:

| Aspecto | Sistema A (ERP) | Sistema B (CRM) | Data Warehouse |
|---|---|---|---|
| Género | `M` / `F` | `Masculino` / `Femenino` | `M` / `F` |
| Moneda | `ARS` | `Pesos` | `ARS` |
| País | `AR` | `Argentina` | `AR` |
| ID cliente | `CLI-4521` | `4521` | `4521` |

### No Volátil (*Non-Volatile*)

Los datos que ingresan al DWH **no se modifican ni se eliminan**. A diferencia del sistema operativo (donde un cambio de precio sobreescribe el anterior), en el DWH se agregan nuevos registros con la nueva información pero los históricos permanecen intactos.

Si un cliente cambió de ciudad en marzo, el DWH tiene:
- Un registro que dice que vivía en Córdoba hasta el 15 de marzo.
- Un registro que dice que desde el 16 de marzo vive en Buenos Aires.

Esto permite analizar cómo el comportamiento de compra cambió antes y después de la mudanza.

### Variante en el Tiempo (*Time-Variant*)

El DWH guarda el **historial completo** de los datos a lo largo del tiempo. Cada registro tiene una dimensión temporal que permite analizar evoluciones, tendencias y comparaciones período a período.

El horizonte temporal típico de un DWH es de **5 a 10 años** de historia, mientras que los sistemas operativos a menudo conservan solo los últimos 1-2 años por razones de performance.

---

## 3. Evolución Histórica del Data Warehouse

La historia del Data Warehouse es la historia de cómo las organizaciones aprendieron a usar sus datos como activo estratégico.

### 3.1 Era Pre-DWH: los reportes del ERP (años 70–80)

Las primeras herramientas de reporte eran módulos adicionales del propio ERP. Generaban informes estáticos pre-definidos directamente contra la base de datos transaccional. Eran lentos, inflexibles y bloqueaban el sistema productivo. Los analistas exportaban datos a hojas de cálculo para cualquier análisis más sofisticado.

### 3.2 El Data Warehouse On-Premise (años 90–2000)

**Bill Inmon** publica en 1992 el libro *Building the Data Warehouse*, estableciendo el primer marco teórico completo. Surgen las primeras plataformas de DWH empresarial: **Teradata**, **IBM DB2 Warehouse**, **Oracle Data Warehouse**.

Al mismo tiempo, **Ralph Kimball** propone un enfoque alternativo más pragmático con su metodología dimensional (*The Data Warehouse Toolkit*, 1996). Nace también el concepto de **OLAP** y las herramientas de **Business Intelligence** como Business Objects y Cognos.

**Limitaciones de esta era:**
- Hardware extremadamente costoso (servidores propietarios de Teradata costaban millones).
- Proyectos de implementación de 12 a 36 meses.
- Escalabilidad limitada: agregar capacidad requería comprar nuevo hardware.
- Solo grandes corporaciones podían permitírselo.

### 3.3 El Big Data y el desafío del volumen (2005–2015)

La explosión de internet generó volúmenes de datos que los DWH tradicionales no podían manejar. **Google** publica en 2004 el paper sobre su sistema de ficheros distribuido (GFS) y en 2004 sobre MapReduce. Esto inspira la creación de **Apache Hadoop** (2006): un sistema de procesamiento distribuido que permite analizar petabytes de datos sobre clusters de servidores baratos.

Surge el concepto de **Data Lake**: almacenar los datos en su formato crudo sin esquema previo, procesarlos más tarde con herramientas como Hive o Spark.

El DWH tradicional coexiste con el Data Lake: el primero para datos estructurados y alta demanda analítica; el segundo para grandes volúmenes sin estructura.

### 3.4 El Cloud Data Warehouse (2015–presente)

Las plataformas cloud transformaron radicalmente el ecosistema:

- **Amazon Redshift** (2013): primer DWH cloud masivamente adoptado. Basado en columnas, pay-per-use.
- **Google BigQuery** (2012, GA 2017): serverless, escala automáticamente, pago por bytes procesados.
- **Snowflake** (2014): arquitectura separada de cómputo y almacenamiento, multi-cloud, comparte datos sin copiarlos.

**Ventajas del cloud DWH:**
- Sin inversión de capital inicial (OpEx vs. CapEx).
- Escala elásticamente en segundos.
- Administración reducida (sin DBA para hardware, storage, backups).
- Accesible para organizaciones de cualquier tamaño.

### 3.5 El Data Lakehouse (2020–presente)

La nueva generación busca combinar la flexibilidad del Data Lake con las capacidades analíticas del DWH. Formatos como **Delta Lake** (Databricks), **Apache Iceberg** y **Apache Hudi** traen transacciones ACID y versionado de datos al almacenamiento en objetos cloud. Lo estudiaremos en profundidad en la Unidad V.

---

## 4. OLTP vs. OLAP: El Contraste Fundamental

Comprender profundamente la diferencia entre OLTP y OLAP es esencial para entender por qué los Data Warehouses existen y cómo deben diseñarse.

### 4.1 Sistemas OLTP — Online Transaction Processing

Son los sistemas que **sostienen las operaciones diarias del negocio**. Cada acción de un usuario (hacer un pedido, registrar un pago, actualizar el stock) genera una transacción en la base de datos OLTP.

**Características técnicas del diseño OLTP:**

**Normalización (3FN o superior):** Los datos están divididos en muchas tablas pequeñas para eliminar la redundancia. Si el precio de un producto cambia, se cambia en un solo lugar (tabla `productos`) y todas las tablas que lo referencian lo ven automáticamente. Esto es eficiente para escritura.

```
Tabla: clientes          Tabla: productos         Tabla: pedidos
─────────────────        ─────────────────         ────────────────────────
id_cliente (PK)          id_producto (PK)          id_pedido (PK)
nombre                   nombre                    id_cliente (FK)
email                    precio_unit               fecha_pedido
id_ciudad (FK)           id_categoria (FK)         ─────────────────
                                                   Tabla: detalle_pedidos
Tabla: ciudades          Tabla: categorias          ────────────────────────
───────────────          ─────────────────          id_pedido (FK)
id_ciudad (PK)           id_categoria (PK)          id_producto (FK)
nombre                   nombre                     cantidad
id_pais (FK)                                        precio_al_momento
```

Para obtener "los pedidos del cliente Juan López incluyendo nombre de producto y categoría", se necesitan 5 JOINs. Esto es aceptable para una consulta puntual, pero catastrófico para un análisis de millones de filas.

**Índices para escritura frecuente:** Los índices están optimizados para buscar registros individuales rápidamente (por ID de cliente, por número de factura).

**Transacciones ACID:** Crítico para la integridad. Si un pago se registra, tanto el débito como el crédito deben concretarse o ninguno (atomicidad).

**Concurrencia masiva:** Miles de usuarios simultáneos ejecutando operaciones pequeñas.

### 4.2 Sistemas OLAP — Online Analytical Processing

Son los sistemas diseñados para **responder preguntas analíticas complejas** sobre grandes volúmenes de datos históricos.

**Características técnicas del diseño OLAP:**

**Desnormalización:** Las tablas se fusionan intencionalmente para evitar JOINs costosos en consultas analíticas. La redundancia de datos es aceptable a cambio de velocidad de lectura.

**Almacenamiento columnar:** En lugar de guardar los datos fila por fila, se guardan columna por columna. Si una consulta solo necesita `monto_venta` y `fecha` de una tabla con 50 columnas, el motor solo lee esas 2 columnas en lugar de las 50. Esto puede reducir el I/O de disco en un 90%.

```
Almacenamiento por filas (OLTP):
Fila 1: [1, "2025-01-05", "María García", "Laptop", 1, 85000.00, "ARS"]
Fila 2: [2, "2025-01-06", "Juan López",   "Mouse",  2,  3500.00, "ARS"]
...

Almacenamiento por columnas (OLAP):
Columna id_venta:    [1, 2, 3, 4, ...]
Columna fecha:       [2025-01-05, 2025-01-06, ...]
Columna monto:       [85000.00, 3500.00, ...]
```

**Compresión avanzada:** Las columnas con alta repetición (ej: `moneda = "ARS"` en el 95% de los registros) se comprimen dramáticamente, reduciendo el espacio en disco y el tiempo de lectura.

**Optimizado para lecturas masivas:** Pocas consultas concurrentes, pero cada una puede escanear millones o miles de millones de filas.

### 4.3 Tabla Comparativa OLTP vs. OLAP

| Dimensión | OLTP | OLAP |
|---|---|---|
| **Propósito** | Procesar transacciones del negocio | Responder preguntas analíticas |
| **Fuente de datos** | Datos operacionales en tiempo real | Datos históricos integrados del DWH |
| **Operaciones dominantes** | INSERT, UPDATE, DELETE | SELECT con GROUP BY, agregaciones |
| **Volumen por consulta** | 1 a cientos de filas | Millones a miles de millones de filas |
| **Concurrencia** | Miles de usuarios simultáneos | Decenas de usuarios simultáneos |
| **Diseño de esquema** | Normalizado (3NF) | Desnormalizado (esquema estrella) |
| **Almacenamiento** | Por filas | Por columnas |
| **Horizonte temporal** | Estado actual / últimos meses | Años o décadas de historia |
| **Tiempo de respuesta** | Milisegundos | Segundos a minutos |
| **Integridad** | ACID estricto | Eventual o ACID relajado |
| **Usuarios** | Empleados operativos | Analistas, gerentes, científicos |
| **Ejemplos de sistemas** | SAP ERP, Salesforce, MySQL | Snowflake, BigQuery, Redshift |
| **Ejemplos de consultas** | "¿Cuál es el stock del producto X?" | "¿Cuál fue el margen por categoría en el Q3 vs Q4?" |

> **Caso ilustrativo:** Retomemos el ejemplo del director de ventas. Con un DWH correctamente implementado en Snowflake con esquema dimensional, la consulta que antes tardaba 45 minutos y bloqueaba el ERP ahora tarda **4 segundos** y corre independientemente del sistema productivo. El analista puede explorarla interactivamente, agregar filtros, cambiar el período y obtener resultados en tiempo real desde su herramienta de BI.

---

## 5. Las Dos Grandes Arquitecturas: Inmon vs. Kimball

A lo largo de los años 90, se desarrollaron dos filosofías opuestas sobre cómo construir un Data Warehouse. Sus creadores, **Bill Inmon** y **Ralph Kimball**, tuvieron un debate intelectual que aún hoy influye en cómo se diseñan los sistemas analíticos.

### 5.1 La Arquitectura de Inmon: Top-Down

**Bill Inmon** propone construir primero un repositorio centralizado y normalizado con todos los datos de la empresa, y a partir de él derivar vistas o Data Marts específicos para cada área de negocio.

La metáfora es **construir primero la ciudad y luego los barrios**: se planifica el todo antes de construir las partes.

#### Flujo de datos en la arquitectura Inmon

```
Sistemas Fuente
(ERP, CRM, SCM)
      │
      ▼
Área de Staging
(datos crudos temporales)
      │
      ▼
┌─────────────────────────────────────────┐
│     ENTERPRISE DATA WAREHOUSE (EDW)     │
│   (modelo normalizado 3NF — el "núcleo")│
│                                         │
│  dim_cliente   dim_producto   dim_tiempo │
│     fact_venta   fact_compra            │
│  (en 3NF: muchas tablas relacionadas)   │
└─────────────────────────────────────────┘
      │              │              │
      ▼              ▼              ▼
Data Mart       Data Mart       Data Mart
  Ventas        Finanzas        Logística
(desnormalizado)(desnormalizado)(desnormalizado)
      │
      ▼
Herramientas de BI
(Power BI, Tableau, Looker)
```

#### Características del enfoque Inmon

**Ventajas:**
- **Consistencia total:** como hay una única fuente de verdad normalizada, no puede haber contradicciones entre Data Marts. Todos los Data Marts se alimentan del mismo núcleo.
- **Flexibilidad:** al estar normalizado, agregar nuevas áreas de análisis o nuevas fuentes de datos es más sencillo sin romper los existentes.
- **Visión empresarial integral:** el EDW representa el modelo de datos completo de la organización.
- **Mejor para grandes organizaciones** con muchas áreas y necesidad de consistencia entre reportes de distintos departamentos.

**Desventajas:**
- **Largo tiempo hasta el primer resultado:** construir el EDW normalizado puede tomar 12 a 36 meses. El negocio empieza a ver valor solo cuando los Data Marts están listos, que es otro proceso adicional.
- **Alto costo inicial:** requiere modelado de datos exhaustivo, equipo grande y mucha coordinación.
- **Complejidad de mantenimiento:** los cambios en el modelo normalizado pueden impactar todos los Data Marts derivados.
- **Requiere mayor expertise técnico** en diseño de datos relacionales.

### 5.2 La Arquitectura de Kimball: Bottom-Up

**Ralph Kimball** propone el enfoque opuesto: construir primero los **Data Marts** individuales por área de negocio, usando una metodología de modelado dimensional estándar que garantiza que se puedan integrar entre sí en el futuro.

La metáfora es **construir primero los barrios y luego integrarlos en la ciudad**: se entrega valor al negocio rápidamente y se va construyendo el todo de manera incremental.

El Data Warehouse en Kimball **es la suma de los Data Marts**: no hay un núcleo central normalizado separado.

#### Flujo de datos en la arquitectura Kimball

```
Sistemas Fuente
(ERP, CRM, SCM)
      │
      ▼
Área de Staging
(datos crudos temporales — nunca visible para el usuario)
      │
      ├──────────────────────────────────┐
      ▼                                  ▼
┌────────────────┐              ┌────────────────┐
│  Data Mart     │              │  Data Mart     │
│  Ventas        │              │  Finanzas      │
│ (esquema ★)   │              │ (esquema ★)   │
│                │              │                │
│ fact_ventas    │              │ fact_pagos     │
│ dim_cliente    │◄ ─ ─ ─ ─ ─ ─│ dim_cliente    │
│ dim_producto   │  Dimensiones │ dim_proveedor  │
│ dim_tiempo     │◄ ─ ─ ─ ─ ─ ─│ dim_tiempo     │
└────────────────┘  conformadas └────────────────┘
      │                                  │
      └──────────────┬───────────────────┘
                     ▼
           Data Warehouse Bus
         (conjunto de dimensiones
          conformadas compartidas)
                     │
                     ▼
           Herramientas de BI
```

#### El concepto de Dimensiones Conformadas

La clave que permite integrar los Data Marts en Kimball es la **dimensión conformada**: una dimensión que tiene el mismo contenido y significado en todos los Data Marts donde aparece.

Si `dim_tiempo` y `dim_cliente` son exactamente iguales en el Data Mart de Ventas y en el de Finanzas, entonces se puede hacer un análisis cruzado entre ambos sin inconsistencias. El "contrato" de cada dimensión se define una vez y todos los Data Marts lo adoptan.

#### Características del enfoque Kimball

**Ventajas:**
- **Time-to-value rápido:** el primer Data Mart puede estar listo en 3 a 6 meses. El negocio empieza a recibir valor rápidamente.
- **Orientado al usuario de negocio:** el modelado dimensional (esquema estrella) es intuitivo para analistas y herramientas de BI.
- **Menos costoso inicialmente:** no requiere modelar toda la empresa antes de empezar.
- **Iterativo:** se construye un Data Mart a la vez, incorporando feedback del negocio.

**Desventajas:**
- **Riesgo de inconsistencias:** si los Data Marts no se construyen con dimensiones conformadas estrictamente, se pueden crear silos analíticos donde los números no coinciden entre áreas.
- **Deuda técnica acumulada:** la arquitectura puede volverse difícil de mantener si crece sin gobierno claro.
- **Visión parcial:** sin planificación del Bus, la suma de Data Marts no siempre da una visión empresarial completa.

### 5.3 ¿Cuál elegir?

En la práctica, la mayoría de las implementaciones modernas son **híbridas**: toman lo mejor de ambos enfoques.

| Criterio | Kimball | Inmon |
|---|---|---|
| Tamaño de la organización | Mediana y grande | Grande y muy grande |
| Urgencia del primer resultado | Alta | Puede esperar |
| Presupuesto inicial | Moderado | Alto |
| Madurez del equipo de datos | Media | Alta |
| Diversidad de fuentes | Moderada | Alta |
| Necesidad de consistencia absoluta | Moderada | Crítica |

> **Tendencia actual:** Con las plataformas cloud modernas (Snowflake, BigQuery), la distinción se vuelve menos relevante. Lo que sí persiste es la **metodología dimensional de Kimball** como el estándar de facto para el modelado de tablas de hechos y dimensiones, independientemente de si la arquitectura sigue el enfoque Inmon o Kimball en lo macro.

---

## 6. El Data Mart: el Subconjunto Temático

Un **Data Mart** es un subconjunto del Data Warehouse orientado a un **área de negocio específica** o a un grupo de usuarios con necesidades analíticas similares.

Si el DWH es la biblioteca completa de la organización, el Data Mart es la sección de una disciplina específica: la sección de ciencias, la sección de historia, la sección de literatura.

### Tipos de Data Mart

**Dependiente:** Se alimenta directamente del DWH central (enfoque Inmon). Es la forma más consistente porque tiene una única fuente de verdad.

**Independiente:** Se construye directamente desde las fuentes operacionales, sin pasar por un DWH central (frecuente en el enfoque Kimball inicial). Es más rápido de implementar pero puede generar inconsistencias si no se gobiernan bien.

**Lógico (virtual):** No tiene almacenamiento físico propio; son vistas o capas semánticas sobre el DWH central. Moderno y eficiente con herramientas cloud que tienen cómputo elástico.

### Ejemplo: Data Mart de Ventas

El Data Mart de Ventas de una empresa de retail incluiría:

- **Tabla de hechos:** `fact_ventas` — cada fila es una línea de transacción de venta con métricas como cantidad, precio unitario, descuento y total.
- **Dimensiones:** `dim_tiempo`, `dim_cliente`, `dim_producto`, `dim_vendedor`, `dim_tienda`, `dim_canal`.
- **Queries típicas:** ventas por período, por región, por categoría de producto, análisis de cesta de compra, comparativos año a año.

**¿Quién lo usa?** El equipo de ventas, el gerente comercial, el analista de trade marketing, el equipo de pricing.

---

## 7. Plataformas Cloud de Data Warehouse

### 7.1 Amazon Redshift

Lanzado en 2013 por Amazon Web Services, fue el primer DWH cloud en ganar adopción masiva.

**Arquitectura:** Basado en PostgreSQL, almacenamiento columnar, procesamiento masivamente paralelo (MPP). Los datos se distribuyen en múltiples nodos del cluster.

**Modelo de costo:** Se paga por los nodos del cluster, estén siendo usados o no. Esto puede ser costoso en entornos con uso intermitente.

**Fortalezas:**
- Profunda integración con el ecosistema AWS (S3, Glue, Lambda, SageMaker).
- Muy maduro y con amplia comunidad.
- Redshift Serverless (2022) permite escalar automáticamente y pagar solo por lo que se usa.

**Debilidades:**
- El modelo de cluster fijo original implica pagar por capacidad ociosa.
- Menos flexible para multi-cloud que Snowflake.
- Rendimiento con datasets muy grandes puede requerir tuning cuidadoso.

**Ideal para:** organizaciones ya invertidas en AWS que procesan datos estructurados y semi-estructurados a escala.

---

### 7.2 Google BigQuery

Lanzado en 2012, fue pionero en el modelo **serverless**: no hay clusters que configurar ni nodos que administrar. El sistema escala automáticamente según la demanda.

**Arquitectura:** Almacenamiento columnar en Colossus (sistema de archivos de Google). El cómputo (Dremel) y el almacenamiento son completamente separados y elásticos.

**Modelo de costo:** Pago por bytes procesados en cada consulta (modelo de demanda) o tarifa plana por capacidad reservada. Con buenas prácticas (particionamiento, clustering, uso de columnas necesarias), el costo puede reducirse drásticamente.

**Fortalezas:**
- **Cero administración:** no hay clusters, no hay DBA de infraestructura.
- Escala a petabytes sin configuración.
- Integración nativa con el ecosistema de ML de Google (Vertex AI, BigQuery ML).
- BigQuery ML permite entrenar modelos de machine learning directamente con SQL.
- Tablas externas sobre Google Cloud Storage (consultar datos sin cargarlos).

**Debilidades:**
- El costo por consulta puede dispararse si los analistas no tienen buenas prácticas de uso.
- Menor flexibilidad para cargas de trabajo con muchas escrituras concurrentes frecuentes.
- El ecosistema GCP puede sentirse más "cerrado" que AWS para algunas integraciones.

**Ideal para:** organizaciones que priorizan simplicidad operativa, escala extrema y capacidades de ML integradas.

---

### 7.3 Snowflake

Fundado en 2012, Snowflake no es solo un DWH: se autodefine como una "Data Cloud". Su arquitectura fue diseñada desde cero para la nube, resolviendo las limitaciones de los DWH on-premise.

**Arquitectura única — Separación de Cómputo y Almacenamiento:**

Esta es la innovación central de Snowflake. El almacenamiento (datos) y el cómputo (procesamiento de queries) son completamente independientes:

```
┌─────────────────────────────────────┐
│         CAPA DE SERVICIOS CLOUD     │
│  (metadata, seguridad, optimizador) │
└──────────────────┬──────────────────┘
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ Virtual  │ │ Virtual  │ │ Virtual  │
│Warehouse │ │Warehouse │ │Warehouse │
│ (Ventas) │ │(Finanzas)│ │  (ML)   │
│ 2 nodos  │ │ 4 nodos  │ │ 8 nodos  │
└──────────┘ └──────────┘ └──────────┘
       │           │           │
       └───────────┼───────────┘
                   ▼
       ┌───────────────────────┐
       │  ALMACENAMIENTO S3    │
       │  (datos compartidos,  │
       │  columnar comprimido) │
       └───────────────────────┘
```

Cada equipo o caso de uso tiene su propio **Virtual Warehouse** (cluster de cómputo) que puede pausarse cuando no se usa (no se paga) y escalarse en segundos cuando se necesita más potencia. Todos acceden a los mismos datos en el almacenamiento compartido.

**Implicancias prácticas:**
- El equipo de ML puede correr modelos pesados con 8 nodos sin afectar las consultas de reporting de ventas.
- Los Virtual Warehouses se pausan automáticamente cuando están inactivos (ahorro de costos).
- Se puede escalar horizontalmente (más nodos) en 30 segundos sin downtime.

**Fortalezas:**
- **Multi-cloud:** corre en AWS, GCP y Azure simultáneamente.
- **Data Sharing:** compartir datos con otras organizaciones o clientes sin copiarlos (acceso directo a los datos propios).
- **Time Travel:** acceder a versiones anteriores de los datos hasta 90 días atrás (ideal para recuperación de errores o auditoría).
- **Zero-copy cloning:** clonar una tabla o base de datos completa en segundos sin duplicar el almacenamiento.
- Soporte nativo de datos semi-estructurados (JSON, Parquet, Avro) con el tipo `VARIANT`.

**Debilidades:**
- Costo total puede ser alto si no se gestiona el uso de Virtual Warehouses.
- Latencia para consultas muy simples sobre tablas pequeñas puede ser mayor que en bases de datos tradicionales (overhead de la arquitectura distribuida).
- No tiene capacidades de ML propias tan integradas como BigQuery.

**Ideal para:** organizaciones que necesitan flexibilidad multi-cloud, compartir datos con terceros y separar cargas de trabajo analíticas entre equipos.

---

### 7.4 Comparativa de las plataformas

| Dimensión | Amazon Redshift | Google BigQuery | Snowflake |
|---|---|---|---|
| **Modelo de costo** | Por cluster / serverless | Por bytes procesados / capacidad | Por cómputo + almacenamiento |
| **Administración** | Moderada | Mínima (serverless) | Moderada-Baja |
| **Ecosistema nativo** | AWS | Google Cloud | Multi-cloud |
| **ML integrado** | SageMaker (externo) | BigQuery ML (SQL) | Snowpark ML |
| **Compartir datos** | Limitado | BigQuery Analytics Hub | Data Sharing nativo |
| **Escalabilidad** | MPP (vertical + horizontal) | Automática ilimitada | Virtual Warehouses |
| **Time Travel** | Limitado (Snapshot) | Hasta 7 días | Hasta 90 días |
| **Ideal para** | Ecosistema AWS | Simplicidad + ML | Flexibilidad + Data Sharing |

---

## 8. Cuándo Construir un Data Warehouse: Señales de Madurez

No toda organización necesita un DWH desde el primer día. Estas son las señales que indican que es momento de construirlo:

1. **Los reportes tardan demasiado:** las consultas analíticas sobre el ERP demoran horas y bloquean el sistema productivo.

2. **Silos de datos:** hay múltiples sistemas que no se hablan entre sí y los analistas cruzan manualmente Excel de distintas áreas.

3. **Números que no cierran:** el área de ventas, finanzas y logística tienen distintos números para la misma métrica porque cada uno la calcula de forma diferente con sus propios datos.

4. **Decisiones basadas en intuición:** los gerentes toman decisiones importantes sin datos o con datos muy desactualizados porque obtener la información es muy costoso.

5. **Crecimiento del volumen de datos:** los datos históricos ya no caben cómodamente en los sistemas operativos y ralentizan las operaciones.

6. **Regulaciones de auditoría:** hay necesidad de conservar y auditar el historial completo de ciertas transacciones o cambios de datos.

> **Concepto clave:** El DWH no reemplaza la base operacional: la complementa. El ERP guarda las transacciones del presente con máxima confiabilidad; el DWH guarda el historial optimizado para que los analistas respondan preguntas estratégicas sin impactar las operaciones. Son dos mundos diseñados para propósitos distintos y deben coexistir.

---

## 9. Actividad de la Clase: Análisis Comparativo de Arquitecturas

### Caso de Estudio: Distribuidora Regional de Alimentos

**Contexto:** Una distribuidora de alimentos con 8 años de operaciones tiene:
- Un ERP (SAP Business One) con los datos de ventas, compras, inventario y contabilidad.
- Un CRM (Salesforce) con los datos de clientes, oportunidades comerciales y seguimiento de vendedores.
- Una hoja de cálculo compartida donde el área de logística registra manualmente los kilómetros recorridos y el costo de cada ruta.
- 45 empleados, 1.200 clientes activos y 8.000 productos en catálogo.
- El gerente general pide mensualmente un informe de rentabilidad por cliente y por zona que el analista tarda 3 días en preparar.

**Consigna:**

1. Identificar al menos **3 problemas concretos** que el Data Warehouse vendría a resolver en este caso.

2. Diseñar a nivel conceptual la arquitectura de DWH usando el **enfoque Kimball**: indicar cuántos Data Marts tendría, qué temas cubrirían y cuáles serían las dimensiones conformadas compartidas.

3. Justificar la elección de **plataforma cloud** (Redshift, BigQuery o Snowflake) argumentando al menos 3 criterios.

4. Describir **qué datos del pipeline ETL** deberían fluir desde cada sistema fuente (SAP B1, Salesforce, planilla de logística) hacia el DWH.

---

## Resumen de la Clase

| Concepto | Definición resumida |
|---|---|
| **Data Warehouse** | Sistema analítico integrado, orientado a temas, no volátil y variante en el tiempo. |
| **Inmon (Top-Down)** | Construir primero el EDW normalizado central, luego derivar Data Marts. Alta consistencia, mayor tiempo inicial. |
| **Kimball (Bottom-Up)** | Construir Data Marts dimensionales por área de negocio, integrarlos con dimensiones conformadas. Valor rápido. |
| **Data Mart** | Subconjunto temático del DWH orientado a un área de negocio específica. |
| **Dimensión conformada** | Dimensión con igual contenido y significado en todos los Data Marts (garantiza consistencia entre áreas). |
| **OLTP** | Sistemas transaccionales para registrar operaciones presentes. Normalizados, optimizados para escritura. |
| **OLAP** | Sistemas analíticos para responder preguntas sobre datos históricos. Desnormalizados, optimizados para lectura. |
| **Amazon Redshift** | DWH cloud de AWS. MPP, columnar. Fuerte integración con ecosistema AWS. |
| **Google BigQuery** | DWH cloud serverless de GCP. Cero administración, pago por uso, ML integrado con SQL. |
| **Snowflake** | Data Cloud multi-cloud. Separación cómputo/almacenamiento, Data Sharing, Time Travel. |

---

## Bibliografía de la Clase

- **Kimball, R. & Ross, M.** — *The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling*, 3ra edición. Capítulos 1 y 2. Wiley.
- **Inmon, W.H.** — *Building the Data Warehouse*, 4ta edición. Wiley.
- **Documentación oficial de Snowflake** — [docs.snowflake.com](https://docs.snowflake.com/).
- **Documentación oficial de Google BigQuery** — [cloud.google.com/bigquery/docs](https://cloud.google.com/bigquery/docs).
- **Documentación oficial de Amazon Redshift** — [docs.aws.amazon.com/redshift](https://docs.aws.amazon.com/redshift/).
- **Reis, J. & Housley, M.** — *Fundamentals of Data Engineering*, Capítulo 8. O'Reilly Media.
- **Golfarelli, M. & Rizzi, S.** — *Data Warehouse Design: Modern Principles and Methodologies*. McGraw-Hill.
