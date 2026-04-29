# Arquitectura Kimball · Etapa 5 — Aplicaciones de BI y Despliegue

> **Arquitectura:** Kimball — Bottom-Up  
> **Posición en el ciclo:** Quinta y última etapa. Convierte los datos preparados en decisiones de negocio.

---

## El objetivo de la Etapa 5

Todo el trabajo de las cuatro etapas anteriores (planificación, modelado, diseño físico, ETL) es preparación para este momento: **que el usuario de negocio pueda obtener respuestas a sus preguntas con un click**.

La Etapa 5 comprende:
1. Especificación y desarrollo de las aplicaciones de BI (reportes, dashboards).
2. La capa semántica que conecta los Data Marts con las herramientas de BI.
3. El despliegue en producción del Data Mart y las aplicaciones.
4. La capacitación de los usuarios.
5. El mantenimiento, crecimiento y evolución del sistema.

---

## 1. Especificación de las Aplicaciones de BI

Antes de construir un reporte o dashboard, se debe especificar formalmente qué debe mostrar. La especificación conecta directamente con los requerimientos de la Etapa 1: cada REQ identificado debe tener una aplicación de BI que lo responda.

### Plantilla de especificación de reporte

```
ESPECIFICACIÓN DE APLICACIÓN BI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ID:            BI-VENTAS-001
Requerimiento: REQ-VENTAS-001 (Análisis de ventas por vendedor y región)
Nombre:        "Dashboard de Performance de Ventas"
Herramienta:   Power BI
Tipo:          Dashboard interactivo

USUARIOS:
  - Gerente de Ventas (acceso a todas las regiones)
  - Supervisores Regionales (acceso solo a su región — RLS)

COMPONENTES VISUALES:
  ┌────────────────────────────────────────────────────────┐
  │  KPI: Ventas del Mes    KPI: Cumpl. Meta   KPI: Margen │
  │  $4.523.810             87.3%              22.4%       │
  ├────────────────────────────────────────────────────────┤
  │  Gráfico de barras: Ventas por Vendedor vs. Meta       │
  │  (ordenado descendente, barra verde=superó, roja=no)   │
  ├────────────────────────────────────────────────────────┤
  │  Mapa de calor: Ventas por Provincia                   │
  ├────────────────────────────────────────────────────────┤
  │  Tabla: Top 10 Clientes del mes                        │
  │  Columnas: Cliente | Ventas | Margen | vs. Mes Anterior│
  └────────────────────────────────────────────────────────┘

FILTROS INTERACTIVOS:
  - Período (rango de fechas)
  - Región
  - Categoría de producto
  - Vendedor (solo visible para Gerente Nacional)

MÉTRICAS CALCULADAS (DAX / SQL):
  Ventas del Mes         = SUM(fact_ventas[total_neto]) filtrado por mes actual
  Meta del Mes           = SUM(dim_vendedor[meta_mensual]) filtrado por mes actual
  % Cumplimiento         = [Ventas del Mes] / [Meta del Mes]
  Margen %               = SUM(fact_ventas[margen_bruto]) / SUM(fact_ventas[total_neto])
  Ventas Mes Anterior    = CALCULATE([Ventas del Mes], DATEADD(dim_tiempo[fecha], -1, MONTH))

FUENTE DE DATOS:
  Tablas: dm_ventas.fact_ventas, dim_tiempo, dim_cliente, dim_vendedor, dim_producto
  Actualización: diaria (a las 06:00 AM, después de la carga ETL nocturna)

TIEMPO DE RESPUESTA ESPERADO:
  < 3 segundos para KPIs y gráfico de barras
  < 5 segundos para el mapa de calor

CRITERIO DE ACEPTACIÓN:
  El Gerente de Ventas valida que los KPIs coinciden con
  los datos del reporte manual de Excel que prepara actualmente.
  La diferencia máxima aceptable: 0% (datos exactos).
```

---

## 2. La Capa Semántica en la práctica

La capa semántica es el conjunto de definiciones que transforma el modelo técnico del Data Mart en un modelo de negocio intuitivo para los usuarios.

### Power BI: el modelo semántico (Tabular Model)

En Power BI, la capa semántica se construye en el **modelo de datos** del reporte (o del dataset publicado). Incluye:

**Relaciones:**
```
dm_ventas.fact_ventas  →  dm_ventas.dim_tiempo   (muchos-a-uno, por id_tiempo)
dm_ventas.fact_ventas  →  dm_ventas.dim_cliente  (muchos-a-uno, por id_cliente)
dm_ventas.fact_ventas  →  dm_ventas.dim_producto (muchos-a-uno, por id_producto)
dm_ventas.fact_ventas  →  dm_ventas.dim_vendedor (muchos-a-uno, por id_vendedor)
```

**Medidas DAX (métricas calculadas):**
```dax
-- Ventas del período seleccionado
Ventas Totales = SUM(fact_ventas[total_neto])

-- Margen bruto en porcentaje
Margen % = DIVIDE(SUM(fact_ventas[margen_bruto]), SUM(fact_ventas[total_neto]), 0)

-- Comparación con el período anterior (inteligencia de tiempo)
Ventas Mes Anterior =
    CALCULATE(
        [Ventas Totales],
        DATEADD(dim_tiempo[fecha], -1, MONTH)
    )

-- Variación porcentual vs. mes anterior
Δ% vs. Mes Anterior =
    DIVIDE(
        [Ventas Totales] - [Ventas Mes Anterior],
        [Ventas Mes Anterior],
        BLANK()
    )

-- Cumplimiento de meta
Cumplimiento Meta % =
    DIVIDE(
        [Ventas Totales],
        SUM(dim_vendedor[meta_mensual]),
        0
    )
```

**Jerarquías:**
```
Jerarquía Tiempo:    Año → Trimestre → Mes → Semana → Día
Jerarquía Geografía: País → Región → Provincia → Ciudad
Jerarquía Producto:  Departamento → Categoría → Subcategoría → Producto
```

### LookML (Looker): definición de métricas como código

En Looker, la capa semántica se define en LookML, un lenguaje declarativo que se versiona en Git:

```yaml
# LookML — archivo de vista para fact_ventas
view: fact_ventas {
  sql_table_name: dm_ventas.fact_ventas ;;

  # Dimensiones (atributos para filtrar y agrupar)
  dimension: numero_factura {
    type: string
    sql: ${TABLE}.numero_factura ;;
    label: "N° de Factura"
  }

  dimension_group: fecha {
    type: time
    timeframes: [date, week, month, quarter, year]
    sql: ${dim_tiempo.fecha} ;;
    label: "Fecha de Venta"
  }

  # Métricas (siempre se calculan como agregaciones)
  measure: ventas_totales {
    type: sum
    sql: ${TABLE}.total_neto ;;
    label: "Ventas Totales ($)"
    value_format_name: "argentinian_pesos"
    description: "Suma del total neto de todas las ventas en el período seleccionado"
  }

  measure: margen_pct {
    type: number
    sql: ${margen_bruto_total} / NULLIF(${ventas_totales}, 0) ;;
    label: "Margen Bruto %"
    value_format_name: percent_2
    description: "Margen bruto como porcentaje de las ventas netas"
  }

  measure: ticket_promedio {
    type: average
    sql: ${TABLE}.total_neto ;;
    label: "Ticket Promedio ($)"
  }
}
```

---

## 3. El Despliegue en Producción

El despliegue es el proceso de llevar el sistema del ambiente de desarrollo al ambiente de producción. Debe ser ordenado, documentado y reversible.

### Plan de despliegue

```
PLAN DE DESPLIEGUE — Data Mart de Ventas v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SEMANA -2: Carga histórica
  ✅ Crear esquema y tablas en producción
  ✅ Cargar 24 meses de datos históricos
  ✅ Validar que los totales históricos coinciden con el sistema fuente
  ✅ Probar el ETL incremental en producción con datos del día anterior

SEMANA -1: Prueba de aceptación de usuarios (UAT)
  ✅ Publicar el dashboard en Power BI (acceso solo para usuarios UAT)
  ✅ Gerente de Ventas valida los KPIs del mes actual
  ✅ 2 supervisores regionales validan sus datos regionales
  ✅ Comparar 5 reportes del dashboard vs. 5 reportes del Excel actual
  ✅ Documentar y resolver discrepancias encontradas

DÍA 0: Go-Live
  ✅ Comunicado a todos los usuarios sobre el nuevo sistema
  ✅ Activar el DAG de Airflow en producción
  ✅ Dar acceso a todos los usuarios finales en Power BI
  ✅ Desactivar el reporte Excel manual que reemplaza (previo acuerdo con los usuarios)
  ✅ Monitor de guardia durante las primeras 48 horas

SEMANA +1: Post Go-Live
  ✅ Relevamiento de feedback de usuarios
  ✅ Corrección de bugs prioritarios
  ✅ Revisión del SLA de actualización (¿está llegando a tiempo la carga nocturna?)
```

### Validación de datos antes del Go-Live

Antes de dar acceso a los usuarios, el equipo debe ejecutar un checklist de validación:

```sql
-- 1. Verificar que no hay hechos sin dimensión correspondiente (FK huérfanas)
SELECT COUNT(*) AS hechos_sin_cliente
FROM dm_ventas.fact_ventas f
LEFT JOIN dm_ventas.dim_cliente dc ON f.id_cliente = dc.id_cliente
WHERE dc.id_cliente IS NULL;
-- Resultado esperado: 0

-- 2. Verificar que los totales del Data Mart coinciden con el sistema fuente
-- (ejecutar en el ERP y comparar con el resultado del Data Mart)
SELECT SUM(total_neto) AS total_dm FROM dm_ventas.fact_ventas
WHERE id_tiempo BETWEEN 20250101 AND 20250331;
-- Comparar contra:
-- SELECT SUM(total_neto) FROM erp.ventas WHERE fecha BETWEEN '2025-01-01' AND '2025-03-31';

-- 3. Verificar que no hay duplicados en la tabla de hechos
SELECT numero_factura, linea, COUNT(*) AS duplicados
FROM dm_ventas.fact_ventas
GROUP BY numero_factura, linea
HAVING COUNT(*) > 1;
-- Resultado esperado: 0 filas

-- 4. Verificar que los períodos están completos en dim_tiempo
SELECT
    MIN(fecha) AS primer_dia,
    MAX(fecha) AS ultimo_dia,
    COUNT(*) AS total_dias,
    (MAX(fecha) - MIN(fecha) + 1) AS dias_esperados,
    COUNT(*) = (MAX(fecha) - MIN(fecha) + 1) AS sin_huecos
FROM dm_ventas.dim_tiempo;
```

---

## 4. Capacitación de Usuarios

La capacitación no es un evento opcional: es el componente que determina si el sistema es adoptado o ignorado. Un Data Mart técnicamente perfecto que nadie usa es un fracaso.

### Tipos de capacitación

**Capacitación para usuarios de dashboards (mayoría):**
- Duración: 2-3 horas.
- Contenido: cómo navegar el dashboard, cómo usar los filtros, cómo interpretar cada visualización, cómo exportar datos.
- Formato: taller presencial o virtual con ejercicios prácticos.

**Capacitación para usuarios de análisis ad-hoc (analistas):**
- Duración: 4-8 horas.
- Contenido: además de lo anterior, cómo crear nuevas visualizaciones, cómo construir medidas básicas, cómo compartir análisis con colegas.
- Formato: taller con ejercicios usando datos reales de la organización.

**Capacitación para Data Stewards y usuarios avanzados:**
- Duración: 1-2 días.
- Contenido: el modelo de datos del Data Mart (comprensión del esquema estrella), cómo solicitar cambios, cómo detectar y reportar problemas de calidad.

### Material de capacitación — qué incluir

```
PAQUETE DE CAPACITACIÓN — Data Mart de Ventas
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. GUÍA DE USUARIO (PDF / online)
   - Descripción de cada dashboard y reporte disponible
   - Captura de pantalla de cada componente con explicación
   - Glosario de métricas: qué significa cada KPI y cómo se calcula
   - FAQ: preguntas frecuentes y sus respuestas

2. GLOSARIO DE MÉTRICAS (documento oficial)
   - Nombre oficial de cada métrica
   - Definición de negocio (en lenguaje no técnico)
   - Fórmula de cálculo
   - Fuente de los datos
   - Responsable (quién es el Data Owner)
   - Ejemplo numérico

3. CANAL DE SOPORTE
   - Canal de Teams/Slack exclusivo para preguntas sobre el Data Mart
   - SLA de respuesta: 4 horas hábiles para preguntas, 24 horas para correcciones
   - Formulario de reporte de problemas
```

---

## 5. Mantenimiento y Crecimiento del Sistema

### El ciclo de vida iterativo de Kimball

Una de las mayores ventajas de la metodología Kimball es que cada Data Mart puede construirse y desplegarse en forma independiente, y luego **integrarse** con los demás mediante las dimensiones conformadas (el DW Bus).

```
ITERACIÓN 1 — Mes 1-2:
  Construir DM Ventas
  Dimensiones conformadas: dim_tiempo, dim_cliente, dim_producto

ITERACIÓN 2 — Mes 3-4:
  Construir DM Compras
  Reutilizar dim_tiempo y dim_producto (ya conformadas)
  Agregar dim_proveedor (nueva)
  → Ahora se puede comparar compras vs. ventas por producto y período

ITERACIÓN 3 — Mes 5-6:
  Construir DM Logística
  Reutilizar dim_tiempo, dim_producto, dim_cliente
  Agregar dim_deposito, dim_transportista
  → Ahora se puede analizar el ciclo completo: venta → preparación → entrega

RESULTADO: una arquitectura coherente construida incrementalmente
           donde cada iteración entrega valor mientras construye la siguiente
```

### Evolución del modelo dimensional

Los modelos dimensionales evolucionan con el negocio. Las modificaciones más comunes y cómo manejarlas:

| Cambio | Impacto | Manejo recomendado |
|---|---|---|
| Agregar una columna a una dimensión | Bajo | `ALTER TABLE dim_x ADD COLUMN nueva_col` |
| Agregar una dimensión nueva a la fact | Medio | Agregar FK en fact, poblar con `NULL` para el historial, luego llenar |
| Cambiar el tipo de SCD de una dimensión | Alto | Requiere rediseño del ETL y posiblemente recargar el historial |
| Cambiar la granularidad de la fact | Muy Alto | Equivale a crear un nuevo Data Mart; mantener el anterior para el historial |
| Agregar un nuevo proceso de negocio | Bajo | Nueva fact table y nuevas dimensiones; las conformadas se reutilizan |

---

## 6. Monitoreo del sistema en producción

### Dashboard de operaciones ETL

El equipo de datos debe tener visibilidad del estado del proceso ETL:

```sql
-- Query para el dashboard operativo de ETL
SELECT
    nombre_proceso,
    fecha_inicio::DATE                                AS fecha,
    fecha_inicio::TIME                                AS hora_inicio,
    fecha_fin::TIME                                   AS hora_fin,
    EXTRACT(EPOCH FROM (fecha_fin - fecha_inicio))/60 AS duracion_minutos,
    estado,
    filas_extraidas,
    filas_cargadas,
    filas_rechazadas,
    ROUND(100.0 * filas_rechazadas / NULLIF(filas_extraidas, 0), 2) AS pct_rechazo
FROM etl_control.ejecucion_etl
WHERE fecha_inicio >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY fecha_inicio DESC;
```

**Alertas automáticas:**
- Si el ETL no completó antes de las 06:00 AM → alerta al equipo de datos.
- Si el porcentaje de rechazo supera el 1% → alerta al Data Steward.
- Si las filas cargadas son 0 → alerta crítica (posible problema en el sistema fuente).

---

## La arquitectura Kimball completa: visión de conjunto

```
SISTEMAS OPERATIVOS (fuentes)
  ERP | CRM | SCM | Logística | APIs | Excel
              │
              │
   ┌──────────▼──────────┐
   │    STAGING AREA     │  ← Área temporal ETL
   │ (tablas espejo de   │
   │  los sistemas fuente│
   └──────────┬──────────┘
              │
              │ Limpieza → Transformación → Conformación → Carga de dims (SCD)
              │                                         → Resolución de surrogates
              │                                         → Carga de hechos
              ▼
┌──────────────────────────────────────────────────────┐
│                  DATA MART DE VENTAS                 │
│  dim_tiempo  dim_cliente  dim_producto  dim_vendedor  │
│                   ↑           ↑                      │
│              fact_ventas (granularidad: línea fact.)  │
└──────────────────┬───────────────────────────────────┘
                   │  (dimensiones conformadas)
┌──────────────────┼───────────────────────────────────┐
│                  │   DATA MART DE COMPRAS             │
│  dim_tiempo  dim_proveedor  dim_producto              │
│                       ↑                              │
│              fact_compras                            │
└──────────────────┬───────────────────────────────────┘
                   │
              DW BUS (dim_tiempo + dim_producto conformadas)
              permite análisis cruzados entre Data Marts
                   │
   ┌───────────────▼────────────────────────┐
   │         CAPA SEMÁNTICA                 │
   │  Métricas calculadas, jerarquías, RLS  │
   └───────────────┬────────────────────────┘
                   │
         ┌─────────┼──────────┐
         ▼         ▼          ▼
     Power BI   Tableau   Python/ML
     Dashboards Ad-hoc    Predicción
         │
         ▼
  USUARIOS DE NEGOCIO
  → Decisiones de negocio basadas en datos
```

---

## Entregables de la Etapa 5

1. ✅ **Especificaciones de BI** formalizadas para cada reporte y dashboard.
2. ✅ **Capa semántica implementada** en la herramienta de BI seleccionada.
3. ✅ **Dashboards y reportes desarrollados** y validados por los usuarios.
4. ✅ **Row-Level Security** configurada por rol y área.
5. ✅ **Plan de despliegue** ejecutado con acta de Go-Live firmada.
6. ✅ **Capacitación completada** para todos los grupos de usuarios.
7. ✅ **Glosario de métricas** publicado y accesible para todos los usuarios.
8. ✅ **Dashboard de monitoreo ETL** operativo con alertas configuradas.
9. ✅ **SLA de soporte** documentado y comunicado a los usuarios.
10. ✅ **Roadmap de la siguiente iteración** con los procesos de negocio a cubrir.

---

## 7. Gobernanza de Métricas: la Metrics Layer

En organizaciones con múltiples Data Marts y equipos de análisis, un problema recurrente es que distintos reportes calculan la misma métrica de formas diferentes. La **Metrics Layer** (capa de métricas) centraliza las definiciones.

### El problema de las "métricas duplicadas"

```
Reporte A (del equipo de Ventas):
  "Ventas Totales" = SUM(fact_ventas.total_neto)
  
Reporte B (del equipo de Finanzas):
  "Ventas Totales" = SUM(fact_ventas.total_neto) - SUM(fact_devoluciones.monto)

Reporte C (del equipo de Marketing):
  "Ventas Totales" = SUM(fact_ventas.total_neto) WHERE canal = 'E-commerce'

→ Tres equipos dicen "Ventas Totales" y obtienen tres números distintos.
→ En la reunión de directorio, nadie sabe cuál es el correcto.
```

### Solución: definir métricas una sola vez

**Con dbt Metrics (Semantic Layer):**

```yaml
# models/metrics/ventas_metrics.yml
metrics:
  - name: ventas_netas
    label: "Ventas Netas ($)"
    description: >
      Suma del total neto de todas las ventas facturadas,
      sin deducir devoluciones. Definición oficial del
      glosario corporativo (GOB-MET-001).
    type: simple
    type_params:
      measure: total_neto
    filter: null  # Sin filtro → incluye todos los canales

  - name: ventas_netas_ecommerce
    label: "Ventas Netas E-commerce ($)"
    description: "Ventas netas filtradas por canal E-commerce."
    type: derived
    type_params:
      expr: ventas_netas
    filter:
      - "{{ Dimension('canal__tipo') }} = 'E-commerce'"

  - name: ventas_netas_post_devoluciones
    label: "Ventas Netas Ajustadas ($)"
    description: >
      Ventas netas menos devoluciones aceptadas.
      Usada por Finanzas para conciliación contable.
    type: derived
    type_params:
      expr: "ventas_netas - devoluciones_aceptadas"
```

**Con LookML (Looker):**

```yaml
measure: ventas_netas {
  type: sum
  sql: ${TABLE}.total_neto ;;
  label: "Ventas Netas ($)"
  description: "Definición oficial GOB-MET-001. No incluye devoluciones."
  value_format_name: decimal_2
  drill_fields: [dim_cliente.razon_social, dim_producto.nombre, total_neto]
}
```

La ventaja de la Metrics Layer es que **cualquier herramienta de BI** que se conecte consume la misma definición. No importa si es Power BI, Tableau, un notebook de Python o una API interna.

---

## 8. Self-Service BI: Habilitando al Usuario

El objetivo final de la arquitectura Kimball es que los usuarios puedan responder sus propias preguntas sin depender del equipo de TI para cada nuevo análisis.

### Niveles de madurez del Self-Service

```
NIVEL 1 — Consumo pasivo (la mayoría de los usuarios)
  El usuario abre un dashboard existente, aplica filtros,
  lee los KPIs. No crea nada nuevo.
  Herramientas: Power BI (lectura), Tableau (viewer)

NIVEL 2 — Exploración guiada (analistas de negocio)
  El usuario explora los datos dentro del modelo semántico
  existente. Arrastra dimensiones y métricas, crea gráficos,
  guarda visualizaciones personales.
  Herramientas: Power BI Desktop, Tableau Creator, Looker Explore

NIVEL 3 — Creación de contenido (analistas avanzados)
  El usuario crea nuevos reportes, nuevas métricas (dentro de
  las reglas del modelo semántico), y los comparte con colegas.
  Herramientas: Power BI Service (workspaces), Tableau Cloud

NIVEL 4 — Integración con código (data scientists / analistas técnicos)
  El usuario conecta el Data Mart directamente desde Python,
  R o SQL para análisis estadísticos y machine learning.
  Herramientas: Jupyter Notebooks, DBeaver, DataGrip
```

### Gobernanza del Self-Service

El Self-Service sin gobernanza es caos. Reglas recomendadas:

| Regla | Descripción |
|---|---|
| **Datasets certificados** | Solo los datasets aprobados por el CoE de datos pueden usarse como fuente de reportes oficiales |
| **Métricas del glosario** | Las métricas oficiales se definen en la Metrics Layer; los usuarios pueden crear métricas propias pero no pueden llamarlas con el mismo nombre |
| **Espacios de trabajo** | Los reportes "oficiales" viven en un workspace controlado; los análisis ad-hoc en workspaces personales |
| **Revisión antes de publicar** | Todo reporte que se comparta con más de 5 personas debe ser revisado por el Data Steward |
| **Lineage visible** | Cada reporte debe mostrar de qué Data Mart se alimenta y cuándo se actualizó por última vez |

---

## 9. Real-Time BI: Más allá del Batch

En algunos escenarios, la carga nocturna no es suficiente. Los usuarios necesitan datos en tiempo real o cuasi-real.

### Streaming al Data Mart

```
Arquitectura para near-real-time:

Sistema fuente
      │ CDC (Debezium)
      ▼
Kafka / Event Hub
      │ Stream Processing (Spark Streaming / Flink)
      ▼
Data Mart (fact table)
      │
      ▼
Dashboard (refresco automático cada 5 min)
```

### Estrategia híbrida (batch + streaming)

```
Datos del día anterior    → Carga batch nocturna (100% correcto)
Datos del día actual      → Streaming cuasi-real-time (99% correcto)
                             Se reconcilia con el batch nocturno

El dashboard muestra:
  "Ventas Marzo 2025 (cerrado): $4.523.810"     ← batch, 100% exacto
  "Ventas Hoy (provisional): $187.420"           ← streaming, actualización cada 5 min
```

---

## 10. Kimball en la Era del Data Mesh

El **Data Mesh** (Zhamak Dehghani, 2019) propone que cada dominio de negocio sea responsable de sus propios datos como "productos de datos". ¿Cómo se relaciona con Kimball?

### Compatibilidad Kimball + Data Mesh

| Principio Data Mesh | Cómo se implementa con Kimball |
|---|---|
| **Domain Ownership** | Cada equipo de dominio es responsable de su Data Mart |
| **Data as Product** | El Data Mart es el "producto de datos" que el dominio ofrece a la organización |
| **Self-serve Platform** | La infraestructura compartida (Snowflake, Airflow, dbt) es la plataforma self-serve |
| **Federated Governance** | Las dimensiones conformadas son el mecanismo de interoperabilidad gobernado centralmente |

```
Data Mesh + Kimball:

Dominio Ventas          Dominio Finanzas        Dominio Logística
(equipo autónomo)       (equipo autónomo)       (equipo autónomo)
      │                       │                       │
      ▼                       ▼                       ▼
  DM Ventas              DM Finanzas            DM Logística
  (fact_ventas           (fact_pagos             (fact_envios
   + sus dims)            + sus dims)             + sus dims)
      │                       │                       │
      └───────────────────────┼───────────────────────┘
                              │
                    Dimensiones Conformadas
                    (gobernanza federada)
                    dim_tiempo, dim_cliente, dim_producto
```

> **Conclusión de Kimball:** Las dimensiones conformadas y el DW Bus son el mecanismo natural para implementar la "interoperabilidad federada" que Data Mesh requiere. Kimball y Data Mesh no son opuestos; son complementarios.

---

## Lecturas recomendadas

- **Kimball, R., Ross, M., Thornthwaite, W., Mundy, J. & Becker, B.** — *The Data Warehouse Lifecycle Toolkit*, 2da edición. Capítulos 18-21: "BI Application Development", "Deployment", "Growth and Maintenance". Wiley.
- **Few, S.** — *Show Me the Numbers: Designing Tables and Graphs to Enlighten*, 2da edición. Analytics Press.
- **Few, S.** — *Information Dashboard Design: Displaying Data for At-a-Glance Monitoring*, 2da edición. Analytics Press.
- **Microsoft** — *The Definitive Guide to DAX*, 2da edición — Ferrari & Russo. Sqlbi.com / Microsoft Press.
- **Looker** — *LookML Reference Documentation*. [cloud.google.com/looker/docs/lookml-reference](https://cloud.google.com/looker/docs/lookml-reference)
- **Dehghani, Z.** — *Data Mesh: Delivering Data-Driven Value at Scale*. O'Reilly Media.
- **dbt Labs** — *dbt Semantic Layer documentation*. [docs.getdbt.com/docs/build/metrics](https://docs.getdbt.com/docs/build/metrics)
