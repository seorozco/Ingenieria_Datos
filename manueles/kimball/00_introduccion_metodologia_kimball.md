# Metodología Kimball — Introducción: Filosofía y Visión General

> **Manual de referencia para la construcción de Data Warehouses**  
> **Enfoque:** Bottom-Up — Modelado Dimensional  
> **Autor de referencia:** Ralph Kimball (1944-2023)

---

## ¿Quién fue Ralph Kimball?

**Ralph Kimball** fue un informático, emprendedor y autor estadounidense reconocido como una de las dos figuras fundacionales del Data Warehousing (junto con Bill Inmon). Obtuvo su PhD en Ingeniería Eléctrica en la Universidad de Stanford y fue uno de los primeros empleados de Xerox PARC.

Kimball fundó **Red Brick Systems** (una de las primeras empresas de bases de datos analíticas) y luego el **Kimball Group**, una consultora que durante más de 20 años lideró la práctica de diseño dimensional y Data Warehousing a nivel mundial.

Sus libros son considerados la referencia canónica de la industria:

| Libro | Año | Enfoque |
|---|---|---|
| *The Data Warehouse Toolkit* (1ª ed.) | 1996 | Modelado dimensional |
| *The Data Warehouse Lifecycle Toolkit* | 1998 | Ciclo de vida completo del proyecto DWH |
| *The Data Warehouse ETL Toolkit* | 2004 | Diseño detallado del proceso ETL |
| *The Data Warehouse Toolkit* (3ª ed.) | 2013 | Edición definitiva con patrones actualizados |

El Kimball Group se retiró oficialmente en 2015, pero la metodología sigue siendo la más utilizada en la industria para el diseño de Data Warehouses analíticos.

---

## La Filosofía Kimball: Bottom-Up

La filosofía Kimball se resume en una idea central:

> **"El Data Warehouse es la unión de todos los Data Marts de la organización, conectados por dimensiones conformadas."**

A diferencia de Inmon, que propone construir primero un repositorio central normalizado (top-down), Kimball propone construir **un Data Mart a la vez**, empezando por el proceso de negocio que más valor genera, y luego ir expandiendo la arquitectura iterativamente.

### Analogía

Si construir un Data Warehouse fuera construir una ciudad:

- **Inmon (top-down):** primero diseña el plano maestro de toda la ciudad (calles, avenidas, servicios), luego construye los edificios uno a uno dentro de ese marco.
- **Kimball (bottom-up):** construye el primer barrio completo y funcional (con calles, servicios y todo), luego construye el segundo barrio conectándolo al primero mediante avenidas (dimensiones conformadas), y así sucesivamente hasta tener la ciudad.

Ambos terminan con una ciudad funcional, pero Kimball entrega el primer barrio habitable mucho antes.

---

## Los 4 Principios Fundamentales de la Metodología

### Principio 1: Enfocarse en el proceso de negocio, no en el departamento

Kimball modela **procesos de negocio** (ventas, compras, inventario, entregas), no departamentos (ventas, marketing, finanzas). Un proceso de negocio genera eventos medibles que atraviesan múltiples departamentos.

```
INCORRECTO: "Data Mart del departamento de Ventas"
  → ¿Qué datos incluye? Todo lo que "Ventas" quiera. Ambiguo.

CORRECTO: "Data Mart del proceso de Ventas al Cliente"
  → Granularidad clara: línea de factura de venta.
  → Métricas claras: cantidad, precio, descuento, margen.
  → Dimensiones claras: tiempo, cliente, producto, vendedor, canal.
  → Útil para Ventas, Marketing, Finanzas y Dirección.
```

### Principio 2: La granularidad es la decisión más importante

Antes de elegir dimensiones o métricas, hay que decidir **qué representa una fila** en la tabla de hechos. Esta decisión es irreversible (cambiarla equivale a reconstruir el Data Mart) y determina qué preguntas puede responder el modelo.

**Regla de Kimball:** siempre elegir la granularidad más fina posible (atómica). Los datos atómicos pueden agregarse hacia arriba para cualquier análisis; los datos pre-agregados no pueden desagregarse.

### Principio 3: Dimensiones conformadas para integrar

Las **dimensiones conformadas** son el mecanismo que convierte Data Marts independientes en un Data Warehouse coherente. Una dimensión conformada (como `dim_tiempo` o `dim_cliente`) tiene la misma estructura, los mismos datos y las mismas definiciones en todos los Data Marts que la utilizan.

Sin dimensiones conformadas, cada Data Mart es una isla aislada. Con ellas, la organización puede cruzar datos entre procesos de negocio con total consistencia.

### Principio 4: Simplicidad para el usuario, complejidad para el ingeniero

El modelo dimensional está diseñado para que el usuario de negocio lo entienda intuitivamente. La desnormalización deliberada de las dimensiones, el uso de nombres descriptivos y la estructura estrella hacen que el modelo sea auto-explicativo.

Toda la complejidad (integración de fuentes, limpieza de datos, gestión de historial, resolución de claves) queda oculta en el proceso ETL, lejos del usuario final.

---

## El Bus de Datos del DWH (*Data Warehouse Bus*)

El concepto más poderoso de la arquitectura Kimball es el **DW Bus**: la arquitectura que conecta todos los Data Marts de la organización a través de dimensiones conformadas.

```
              dim_tiempo ─────────────────────────────────────────
                 │              │              │              │
              dim_cliente ──────┤              │              │
                 │              │              │              │
              dim_producto ─────┤──────────────┤              │
                 │              │              │              │
                 ▼              ▼              ▼              ▼
           ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
           │DM Ventas │  │DM Compras│  │DM Invent.│  │DM RRHH   │
           │──────────│  │──────────│  │──────────│  │──────────│
           │fact_venta│  │fact_compra│ │fact_stock │  │fact_asist│
           └──────────┘  └──────────┘  └──────────┘  └──────────┘

Las dimensiones conformadas (líneas horizontales) conectan
todos los Data Marts y permiten análisis cruzados:
  "¿Qué productos compramos más caros y vendemos con menor margen?"
  (cruza DM Compras con DM Ventas por dim_producto y dim_tiempo)
```

La **Bus Matrix** es la herramienta que documenta estas conexiones:

```
                          dim_tiempo  dim_cliente  dim_producto  dim_vendedor  dim_proveedor
                          ──────────  ───────────  ────────────  ────────────  ─────────────
Proceso: Ventas               X           X            X             X
Proceso: Compras              X                        X                            X
Proceso: Inventario           X                        X
Proceso: RRHH                 X                                      X
```

---

## Comparación con Inmon: ¿Cuándo usar cada enfoque?

Kimball e Inmon no son mutuamente excluyentes. La elección depende del contexto organizacional:

| Factor | Kimball (Bottom-Up) | Inmon (Top-Down) |
|---|---|---|
| **Tiempo hasta el primer resultado** | 2-3 meses (un Data Mart) | 6-18 meses (EDW completo) |
| **Inversión inicial** | Menor | Mayor |
| **Complejidad inicial** | Menor | Mayor |
| **Consistencia entre áreas** | Garantizada por dimensiones conformadas (si se respetan) | Garantizada por el EDW normalizado (por construcción) |
| **Riesgo principal** | Data Marts desconectados si no se usan dimensiones conformadas | Parálisis de análisis; proyecto que nunca entrega |
| **Ideal para** | Organizaciones que necesitan resultados rápidos; equipos ágiles | Organizaciones grandes con gobernanza fuerte; regulaciones estrictas |
| **Acceso de usuarios** | Directo a los Data Marts (esquema estrella, intuitivo) | A los Data Marts derivados (no al EDW directamente) |
| **ETL** | Fuente → Data Mart (un solo salto) | Fuente → EDW → Data Mart (dos saltos) |

### La realidad híbrida

En la práctica moderna, muchas organizaciones usan un **enfoque híbrido**:

```
Datos crudos (raw)        → Data Lake (almacenamiento barato)
Datos integrados (curados) → EDW normalizado (Inmon) o zona "curada" del lake
Datos analíticos           → Data Marts dimensionales (Kimball)
Acceso de usuarios         → Capa semántica + herramientas de BI

                                    Data Lakehouse
                        ┌─────────────────────────────────────┐
  Fuentes ──────────►   │  Raw     │  Curated   │  Analytics  │
                        │  (lake)  │  (Inmon)   │  (Kimball)  │
                        └─────────────────────────────────────┘
                                                      │
                                                      ▼
                                                   Power BI
                                                   Tableau
```

---

## El Ciclo de Vida Dimensional (*Business Dimensional Lifecycle*)

La metodología Kimball organiza el proyecto de DWH en un ciclo de vida con tres pistas paralelas:

```
                    ┌─────────────────────────┐
                    │  1. PLANIFICACIÓN Y      │
                    │     REQUERIMIENTOS       │
                    │     (Entrevistas, Bus    │
                    │      Matrix, Alcance)    │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                   ▼
    ┌─────────────────┐ ┌───────────────┐  ┌────────────────┐
    │ PISTA DE DATOS  │ │ PISTA DE      │  │ PISTA DE BI    │
    │                 │ │ TECNOLOGÍA    │  │                │
    │ 2. Modelado     │ │ 3. Diseño     │  │ 5. Aplicaciones│
    │    dimensional  │ │    físico     │  │    de BI       │
    │                 │ │               │  │                │
    │ 4. Diseño e     │ │ Selección de  │  │ Dashboards,    │
    │    implementa-  │ │ plataforma,   │  │ reportes,      │
    │    ción ETL     │ │ indexación,   │  │ capa semántica │
    │                 │ │ particiones   │  │                │
    └────────┬────────┘ └───────┬───────┘  └────────┬───────┘
             │                  │                    │
             └──────────────────┼────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │    DESPLIEGUE         │
                    │    Capacitación       │
                    │    Go-Live            │
                    │    Soporte            │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │   MANTENIMIENTO Y     │
                    │   CRECIMIENTO         │
                    │   (siguiente Data Mart│
                    │    → siguiente fila   │
                    │    de la Bus Matrix)  │
                    └───────────────────────┘
```

---

## Los 5 Documentos de este Manual

Este manual desarrolla cada una de las 5 etapas del ciclo de vida dimensional:

| # | Etapa | Contenido principal |
|---|---|---|
| **01** | [Planificación y Requerimientos](01_planificacion_y_requerimientos.md) | Caso de negocio, entrevistas, Bus Matrix, alcance del primer Data Mart |
| **02** | [Modelado Dimensional](02_modelado_dimensional.md) | Los 4 pasos: proceso → granularidad → dimensiones → hechos. Esquema estrella, SCD, dimensiones conformadas |
| **03** | [Diseño Físico](03_diseno_fisico.md) | Plataformas, almacenamiento columnar, indexación, particionamiento, sizing, agregados |
| **04** | [Diseño e Implementación del ETL](04_diseno_etl.md) | Los 34 subsistemas de Kimball, staging, carga de dimensiones (SCD), carga de hechos, orquestación con Airflow, ELT con dbt |
| **05** | [BI y Despliegue](05_bi_y_despliegue.md) | Capa semántica, especificación de dashboards, DAX/LookML, despliegue, capacitación, mantenimiento |

---

## Glosario Rápido de la Terminología Kimball

| Término | Definición |
|---|---|
| **Data Mart** | Subconjunto del DWH orientado a un proceso de negocio. Contiene una tabla de hechos y sus dimensiones. |
| **Tabla de Hechos** (*Fact Table*) | Tabla central del esquema estrella. Contiene las métricas numéricas medibles de cada evento de negocio. |
| **Tabla de Dimensiones** (*Dimension Table*) | Tabla descriptiva que provee el contexto de los hechos: quién, qué, cuándo, dónde, cómo. |
| **Esquema Estrella** (*Star Schema*) | Estructura de BD donde una tabla de hechos está rodeada por tablas de dimensiones. |
| **Granularidad** (*Grain*) | Lo que representa una fila en la tabla de hechos. Decisión más importante del diseño. |
| **Dimensión Conformada** (*Conformed Dimension*) | Dimensión con la misma estructura y contenido en múltiples Data Marts. Mecanismo de integración. |
| **Bus Matrix** | Matriz que cruza procesos de negocio con dimensiones. Mapa de toda la arquitectura DWH. |
| **DW Bus** | Arquitectura que conecta todos los Data Marts a través de dimensiones conformadas. |
| **Clave Sustituta** (*Surrogate Key*) | Entero secuencial generado por el DWH como PK de dimensiones. Independiente del sistema fuente. |
| **Clave Natural** (*Natural Key*) | Identificador del registro en el sistema fuente (ej: código de cliente en el ERP). |
| **SCD** (*Slowly Changing Dimension*) | Estrategia para manejar cambios en las dimensiones: Tipo 1 (sobreescribir), Tipo 2 (versionar), Tipo 3 (columna anterior). |
| **Dimensión Degenerada** (*Degenerate Dimension*) | Atributo de transacción almacenado directamente en la fact (ej: número de factura). |
| **Dimensión Basura** (*Junk Dimension*) | Agrupa flags y atributos de baja cardinalidad para limpiar la tabla de hechos. |
| **Staging Area** | Área temporal donde se cargan los datos crudos de los fuentes antes de transformarlos. |
| **Capa Semántica** (*Semantic Layer*) | Capa de traducción entre el modelo técnico y el lenguaje de negocio del usuario. |

---

## Lecturas Recomendadas

### Textos fundacionales

- **Kimball, R. & Ross, M.** — *The Data Warehouse Toolkit*, 3ra edición (2013). Wiley. **La referencia definitiva** para modelado dimensional.
- **Kimball, R. & Ross, M.** — *The Data Warehouse Lifecycle Toolkit*, 2da edición (2008). Wiley. Ciclo de vida completo del proyecto.
- **Kimball, R. & Caserta, J.** — *The Data Warehouse ETL Toolkit* (2004). Wiley. Los 34 subsistemas ETL en detalle.

### Contexto moderno

- **Reis, J. & Housley, M.** — *Fundamentals of Data Engineering* (2022). O'Reilly. Visión moderna que integra Kimball con data lakes, streaming y cloud.
- **Dehghani, Z.** — *Data Mesh: Delivering Data-Driven Value at Scale* (2022). O'Reilly. Cómo Kimball se adapta a arquitecturas descentralizadas.
- **Kleppmann, M.** — *Designing Data-Intensive Applications* (2017). O'Reilly. Fundamentos de almacenamiento y procesamiento.
- **dbt Labs** — Documentación oficial de dbt. [docs.getdbt.com](https://docs.getdbt.com). La herramienta moderna para implementar transformaciones Kimball como código.

### Artículos históricos

- **Kimball, R.** — *Kimball Design Tips*. Colección de artículos técnicos breves disponibles en [kimballgroup.com](https://web.archive.org/web/2023/https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/) (archive.org).
