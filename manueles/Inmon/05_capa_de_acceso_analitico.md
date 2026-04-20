# Arquitectura Inmon · Etapa 5 — Capa de Acceso Analítico y BI

> **Arquitectura:** Inmon — Top-Down  
> **Posición en el ciclo:** Quinta y última etapa. Es donde el negocio finalmente consume el valor del sistema.

---

## ¿Qué es la Capa de Acceso Analítico?

La **Capa de Acceso Analítico** es la interfaz entre los datos del Data Warehouse y los usuarios que los consumen. Es el punto de encuentro entre la infraestructura técnica (EDW + Data Marts) y las necesidades de análisis del negocio.

Esta capa no es solo una herramienta de software: es un conjunto de componentes técnicos, semánticos y organizacionales que en conjunto permiten que los usuarios de negocio obtengan respuestas a sus preguntas sin necesidad de conocer la estructura interna del DWH.

En la arquitectura Inmon, la capa de acceso se conecta **exclusivamente a los Data Marts** (nunca directamente al EDW), respetando la separación de responsabilidades del sistema.

---

## Los componentes de la capa de acceso

### 1. La Capa Semántica (*Semantic Layer*)

Es el componente más importante y más frecuentemente subestimado de la arquitectura de BI. La capa semántica es una **traducción** entre el lenguaje técnico del Data Mart (tablas, columnas, claves foráneas) y el lenguaje de negocio del usuario (métricas, dimensiones, jerarquías, KPIs).

**Ejemplo:** En el Data Mart, la métrica "margen bruto" se calcula así:

```sql
SUM(fact_ventas.total_neto) - SUM(fact_ventas.costo)
```

En la capa semántica, el usuario ve simplemente una métrica llamada **"Margen Bruto ($)"** con su descripción, y puede arrastrarla a cualquier visualización sin saber nada de SQL.

**¿Qué define la capa semántica?**

- **Métricas calculadas:** definiciones de KPIs complejos que se reutilizan en múltiples reportes.
- **Jerarquías de drill-down:** Año → Trimestre → Mes → Semana → Día. País → Región → Provincia → Ciudad.
- **Relaciones entre tablas:** los JOINs que la herramienta de BI debe realizar automáticamente.
- **Nombres amigables:** la columna `id_cliente_sk` se muestra como "Cliente" en la interfaz.
- **Formateo:** cómo se muestran los números (moneda, porcentaje, miles) y las fechas.
- **Seguridad por fila (*Row-Level Security*):** el usuario del área de ventas de la región Norte solo ve los datos de su región.

**Herramientas con capa semántica:** Power BI (modelo semántico / antes llamado "Tabular Model"), Tableau (published data sources), Looker (LookML), MicroStrategy (schema objects), dbt Metrics (metrics layer).

---

### 2. Tipos de Reportes y Análisis

La capa de acceso soporta distintos tipos de análisis según el perfil del usuario:

#### Reportes Operativos (*Operational Reports*)

Reportes estáticos o semi-estáticos que responden preguntas recurrentes y predefinidas. Se ejecutan diariamente, semanalmente o mensualmente. Ejemplos:

- Reporte diario de ventas por sucursal.
- Informe mensual de gestión para la dirección ejecutiva.
- Reporte de stock crítico (productos con stock < punto de reorden).

**Características:** estructura fija, generación automática, distribución por email o portal.

---

#### Dashboards y Tableros de Control

Son visualizaciones interactivas que muestran el estado actual de los KPIs del negocio en tiempo real o cuasi-real. Permiten filtrar, comparar períodos y hacer drill-down sin modificar el diseño del reporte.

**Componentes típicos de un dashboard:**
- **KPI Cards:** métricas puntuales con comparación vs. período anterior y semáforo de estado.
- **Gráficos de tendencia:** evolución temporal de las métricas principales.
- **Tablas de ranking:** top 10 productos, clientes, vendedores.
- **Mapas:** distribución geográfica de ventas o clientes.
- **Filtros interactivos:** período, región, categoría, canal.

**Ejemplo de jerarquía de dashboards:**

```
NIVEL 1 — Dashboard Ejecutivo (CEO/Gerentes)
   Granularidad: mensual / trimestral
   Métricas: ventas totales, margen, NPS, rentabilidad

   → Drill-down a:

NIVEL 2 — Dashboard Gerencial (Gerente de Ventas)
   Granularidad: semanal
   Métricas: ventas por región, por vendedor, por categoría, cumplimiento de meta

   → Drill-down a:

NIVEL 3 — Dashboard Operativo (Supervisor / Analista)
   Granularidad: diaria / por transacción
   Métricas: ventas por cliente, por producto, análisis de descuentos
```

---

#### Análisis Ad-Hoc (*Self-Service BI*)

Permite a los analistas de negocio explorar los datos libremente, formulando sus propias preguntas sin depender del equipo de TI para cada nuevo reporte. Es posible gracias a la capa semántica, que abstrae la complejidad técnica.

**Ejemplo de flujo de análisis ad-hoc:**
1. El analista de marketing quiere saber si los clientes que recibieron la campaña de enero compraron más en febrero que los que no la recibieron.
2. Arrastra "Campaña (Sí/No)", "Mes", "Total Compras", "Ticket Promedio" al lienzo de análisis.
3. La herramienta genera automáticamente el SQL necesario, lo ejecuta contra el Data Mart y muestra el resultado en segundos.
4. El analista descubre que sí hay diferencia: los que recibieron la campaña compraron un 23% más en febrero.

---

#### OLAP (*Online Analytical Processing*)

Los cubos OLAP son estructuras de datos pre-calculadas que permiten analizar métricas según múltiples dimensiones simultáneamente con tiempos de respuesta casi instantáneos, incluso para preguntas complejas.

**Operaciones OLAP fundamentales:**

| Operación | Descripción | Ejemplo |
|---|---|---|
| **Roll-up** | Agregar hacia un nivel superior de la jerarquía | De ventas por día a ventas por mes |
| **Drill-down** | Desagregar hacia un nivel inferior | De ventas por trimestre a ventas por semana |
| **Slice** | Filtrar por un valor de una dimensión | Solo ventas en la región Patagonia |
| **Dice** | Filtrar por múltiples dimensiones simultáneamente | Ventas en Patagonia, categoría Electrónica, Q3 |
| **Pivot** | Rotar los ejes de análisis | Poner meses en columnas y regiones en filas |

---

#### Minería de Datos y Machine Learning

La capa de acceso también habilita análisis más sofisticados que van más allá del reporte tradicional:

- **Segmentación de clientes:** clustering de clientes por comportamiento de compra usando algoritmos de ML.
- **Predicción de demanda:** modelos de series de tiempo que predicen las ventas de los próximos 3 meses.
- **Detección de anomalías:** identificar transacciones o patrones inusuales que podrían indicar fraude.
- **Análisis de cohortes:** seguimiento del comportamiento de grupos de clientes a lo largo del tiempo.

En la arquitectura moderna, estos análisis se realizan directamente sobre los datos del Data Mart o el EDW usando herramientas como Python (pandas, scikit-learn), R, o las capacidades de ML integradas en plataformas cloud (BigQuery ML, Snowpark ML).

---

### 3. Herramientas de BI del mercado

#### Microsoft Power BI

La herramienta de BI más utilizada en el mundo corporativo (especialmente en América Latina). Se conecta a los Data Marts (PostgreSQL, SQL Server, Snowflake, BigQuery, etc.) y construye modelos semánticos sobre ellos.

**Características principales:**
- DAX (Data Analysis Expressions): lenguaje de fórmulas para métricas calculadas complejas.
- Power Query: transformaciones adicionales en el modelo de datos del reporte.
- Publicación en la nube de Microsoft (Power BI Service) con actualización programada.
- Row-Level Security: control de acceso por usuario o rol.
- Integración con Teams, SharePoint, Excel.

**Cuándo usarlo:** organizaciones del ecosistema Microsoft, presupuesto moderado, necesidad de amplia distribución interna.

---

#### Tableau

Herramienta líder en visualización de datos. Históricamente reconocida por la calidad de sus visualizaciones y la facilidad para crear análisis ad-hoc de forma visual.

**Características principales:**
- VizQL: tecnología de visualización patentada que convierte interacciones visuales en SQL automáticamente.
- Tableau Prep: herramienta visual de transformación de datos.
- Tableau Server / Cloud: plataforma de publicación y colaboración.
- Extensions API: integración con Python y R para análisis avanzados.

**Cuándo usarlo:** equipos con analistas de datos sofisticados, necesidad de visualizaciones complejas o personalizadas, análisis exploratorio frecuente.

---

#### Looker / Looker Studio

Herramienta de Google que introduce el concepto de **código como definición de métricas** (LookML): las métricas y dimensiones se definen en código versionado en Git, lo que garantiza consistencia y trazabilidad.

**Características principales:**
- LookML: lenguaje declarativo para definir la capa semántica como código.
- "Single source of truth" para métricas: si la definición de "margen bruto" cambia, cambia en un solo lugar y todos los reportes se actualizan automáticamente.
- Integración nativa con BigQuery.
- API para embeber analítica en aplicaciones propias.

**Cuándo usarlo:** organizaciones data-driven con equipos técnicos, necesidad de gobernanza estricta de métricas, ecosistema Google Cloud.

---

### 4. Seguridad y Gobernanza del Acceso

La capa de acceso también es responsable de controlar **quién puede ver qué datos**.

#### Autenticación y Autorización

```
Usuario solicita acceso al Data Mart de Ventas
          │
          ▼
┌─────────────────────────────────────────────────┐
│  IDENTITY PROVIDER (Azure AD, Okta, Google)     │
│  Verifica: ¿Quién eres? (Autenticación)         │
│  Otorga token de acceso con roles del usuario   │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│  CAPA DE BI (Power BI, Tableau)                 │
│  Verifica: ¿Qué puedes ver? (Autorización)      │
│  Aplica Row-Level Security según rol            │
│    Rol "Ventas_Norte" → solo región Norte       │
│    Rol "Ventas_Global" → todas las regiones     │
└─────────────────────────────────────────────────┘
```

#### Row-Level Security (RLS)

El RLS garantiza que dos usuarios que abren el mismo reporte ven datos distintos según su perfil de acceso, sin necesidad de crear reportes separados.

**Ejemplo:** El reporte "Ventas por Vendedor" muestra:
- Al Gerente Nacional: todos los vendedores de todas las regiones.
- Al Gerente Regional Norte: solo los vendedores de la región Norte.
- Al Vendedor Juan López: solo sus propias ventas.

La misma visualización, el mismo reporte, datos distintos según el usuario autenticado.

---

## El ciclo de vida de un reporte: del dato a la decisión

```
1. El negocio tiene una pregunta:
   "¿Cuáles son nuestros 5 clientes más rentables del trimestre
    y cómo evolucionaron sus compras en el último año?"

          ↓

2. El analista abre Power BI / Tableau:
   Selecciona "Data Mart Ventas" → arrastra "Cliente", "Margen Bruto",
   "Período" → aplica filtro Trimestre Actual → ordena descendente

          ↓

3. La herramienta genera SQL automáticamente:
   SELECT dc.razon_social, SUM(f.margen_bruto) AS margen,
          dt.trimestre, dt.anio
   FROM dm_ventas.fact_ventas f
   JOIN dm_ventas.dim_cliente dc ON f.id_cliente = dc.id_cliente
   JOIN dm_ventas.dim_tiempo dt  ON f.id_tiempo  = dt.id_tiempo
   WHERE dt.anio = 2025 AND dt.trimestre = 1
   GROUP BY dc.razon_social, dt.trimestre, dt.anio
   ORDER BY margen DESC LIMIT 5;

          ↓

4. El resultado llega en segundos (gracias al esquema estrella y los índices).

          ↓

5. El analista presenta el reporte en la reunión de directorio.
   La dirección decide enfocarse en retener a los 5 clientes más rentables
   con un programa de fidelización dedicado.

          ↓

6. Los datos se convirtieron en una decisión de negocio.
   El ciclo DIKW se completó.
```

---

## El centro de excelencia de datos (*Data Center of Excellence*)

En organizaciones maduras, la capa de acceso analítico está soportada por un **Centro de Excelencia de Datos** (CoE): un equipo mixto de técnicos y expertos de negocio que:

- Mantiene y gobierna la capa semántica.
- Define y publica las métricas oficiales de la organización.
- Capacita a los usuarios en el uso de las herramientas de BI.
- Valida nuevos reportes antes de que sean publicados como "oficiales".
- Resuelve discrepancias cuando dos reportes muestran números distintos.
- Gestiona el ciclo de vida de los reportes (creación, publicación, depreciación).

---

## La arquitectura Inmon completa: visión de conjunto

Después de completar las 5 etapas, la arquitectura Inmon se ve así:

```
SISTEMAS OPERATIVOS (fuentes)
ERP | CRM | SCM | Logística | Excel
              │
              │  ETL (Etapa 3)
              ▼
      ┌──────────────┐
      │ STAGING AREA │  ← Área temporal de trabajo ETL
      └──────┬───────┘
             │
             ▼
┌────────────────────────────────┐
│  ENTERPRISE DATA WAREHOUSE     │  ← Núcleo 3FN (Etapa 2)
│  (modelo normalizado 3FN)      │    diseñado sobre el Modelo
│                                │    Empresarial (Etapa 1)
│  Datos integrados, históricos  │
│  y consistentes de TODA la     │
│  organización                  │
└───────────────┬────────────────┘
                │
                │  ETL de derivación (Etapa 4)
       ┌────────┼────────┬──────────┐
       ▼        ▼        ▼          ▼
  ┌────────┐ ┌──────┐ ┌──────┐ ┌──────┐
  │DM      │ │DM    │ │DM    │ │DM    │
  │Ventas  │ │Finan.│ │Logís.│ │Mktg. │  ← Data Marts (Etapa 4)
  │(★)    │ │(★)  │ │(★)  │ │(★)  │    (esquemas estrella)
  └────────┘ └──────┘ └──────┘ └──────┘
       │        │        │          │
       └────────┴────────┴──────────┘
                         │
                         ▼
          ┌──────────────────────────┐
          │   CAPA SEMÁNTICA         │  ← Modelos semánticos,
          │   (métricas, jerarquías, │    métricas calculadas,
          │    seguridad, nombres)   │    seguridad por rol
          └──────────────┬───────────┘
                         │
             ┌───────────┼────────────┐
             ▼           ▼            ▼
        Power BI     Tableau      Python/ML     ← Herramientas (Etapa 5)
        Dashboards   Ad-hoc       Predicción
        Reportes     Análisis     Segmentación
             │
             ▼
     USUARIOS DE NEGOCIO
     (Gerentes, Analistas, Directores)
             │
             ▼
      DECISIONES DE NEGOCIO
```

---

## Entregables de la Etapa 5

1. ✅ **Modelo semántico publicado** en la herramienta de BI seleccionada, con todas las métricas, jerarquías y relaciones definidas.
2. ✅ **Diccionario de métricas** (Business Glossary de KPIs): nombre, definición, fórmula, fuente, responsable.
3. ✅ **Dashboard ejecutivo** validado por la dirección.
4. ✅ **Reportes operativos** implementados y programados para distribución automática.
5. ✅ **Configuración de Row-Level Security** por rol y área.
6. ✅ **Capacitación a usuarios** en el uso de las herramientas de BI y las prácticas de self-service.
7. ✅ **Plan de mantenimiento** del entorno analítico: SLA de actualización, responsables, procesos de cambio.

---

## Lecturas recomendadas

- **Few, S.** — *Show Me the Numbers: Designing Tables and Graphs to Enlighten*. Analytics Press.
- **Few, S.** — *Information Dashboard Design*. Analytics Press.
- **Microsoft** — Documentación oficial de Power BI — [docs.microsoft.com/power-bi](https://docs.microsoft.com/es-es/power-bi/).
- **Tableau** — Documentación oficial — [help.tableau.com](https://help.tableau.com/current/pro/desktop/es-es/gettingstarted_overview.htm).
- **Inmon, W.H.** — *Building the Data Warehouse*, 4ta edición. Capítulo 9: "The End User Interface". Wiley.
- **DAMA International** — *DAMA-DMBOK*, Capítulo 14: "Data Warehousing and Business Intelligence".
