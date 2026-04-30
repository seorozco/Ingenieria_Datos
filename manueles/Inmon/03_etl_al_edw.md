# Arquitectura Inmon · Etapa 3 — ETL: Extracción, Transformación y Carga al EDW

> **Arquitectura:** Inmon — Top-Down  
> **Posición en el ciclo:** Tercera etapa. Es el motor que alimenta el EDW con datos de los sistemas fuente.

---

## ¿Qué es el ETL en el contexto Inmon?

El proceso **ETL** (Extract, Transform, Load) es la ingeniería de integración que conecta los **sistemas operativos fuente** con el **Enterprise Data Warehouse**. Es el proceso más complejo y costoso de mantener en la arquitectura Inmon, y suele representar entre el 60% y el 80% del esfuerzo total de construcción del DWH.

En la arquitectura Inmon, el ETL tiene un doble rol:

1. **ETL hacia el EDW:** lleva los datos desde los sistemas fuente hacia el repositorio central 3FN. Este proceso debe resolver la integración, limpiar los datos y gestionar el historial.

2. **ETL desde el EDW hacia los Data Marts:** en la Etapa 4, un segundo proceso ETL toma los datos ya integrados del EDW y los desnormaliza para alimentar los Data Marts con esquemas estrella.

Esta etapa se enfoca en el primero de estos dos procesos.

---

## El flujo completo del ETL Inmon

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  ERP (SAP)   │    │  CRM (SF)    │    │  Planillas   │
│  PostgreSQL  │    │  API REST    │    │  Excel/CSV   │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │ EXTRACCIÓN
                           ▼
              ┌────────────────────────┐
              │     STAGING AREA       │
              │  (copia cruda, sin     │
              │   transformaciones)    │
              └────────────┬───────────┘
                           │ TRANSFORMACIÓN
                           │  • Limpieza
                           │  • Integración de identificadores
                           │  • Resolución de conflictos
                           │  • Aplicación del glosario
                           │  • Gestión del historial
                           ▼
              ┌────────────────────────┐
              │ ENTERPRISE DATA        │
              │ WAREHOUSE (3FN)        │
              │  (datos integrados,    │
              │   históricos, limpios) │
              └────────────────────────┘
```

---

## Etapa 3A — Extracción (*Extract*)

### ¿Qué significa extraer?

Extraer es obtener los datos de cada sistema fuente y copiarlos a la Staging Area, sin modificarlos. El principio fundamental es: **extraer los datos tal como están en la fuente** y hacer todas las decisiones de transformación más adelante, de forma controlada.

### Estrategias de extracción

#### Full Extract (Extracción Completa)

Se copia la totalidad de los datos de la tabla fuente en cada ciclo de carga.

**Cuándo aplicarla:**
- Tablas pequeñas o medianas donde el costo de la extracción completa es aceptable.
- Tablas de referencia (catálogos, listas de valores, tablas maestras) que cambian poco pero cuando cambian lo hacen de forma no rastreable.
- Primera carga histórica (*initial load*) de cualquier tabla.

**Ventaja:** Simplicidad. No requiere marcas ni mecanismos de detección de cambios.  
**Desventaja:** No escala para tablas de millones de registros que se actualizan diariamente.

---

#### Incremental Extract (Extracción Incremental)

Solo se extraen los registros modificados o creados desde la última extracción exitosa.

**Mecanismos para identificar registros modificados:**

**Timestamp de modificación:** la fuente tiene una columna `updated_at` o `fecha_modificacion`. Se extraen solo los registros donde ese timestamp es mayor que el de la última extracción.

```
Ejemplo de consulta de extracción incremental:

SELECT *
FROM erp.ventas.pedido
WHERE fecha_modificacion > '2025-03-14 06:00:00'
  AND fecha_modificacion <= '2025-03-15 06:00:00'
ORDER BY fecha_modificacion ASC;
```

**Columna de versión:** algunos sistemas mantienen un número de versión o secuencia que incrementa con cada modificación. Se extraen los registros con versión mayor a la última procesada.

**Change Data Capture (CDC):** herramientas como **Debezium** leen directamente el log de transacciones de la base de datos (WAL en PostgreSQL, binlog en MySQL, redo log en Oracle) y capturan cada INSERT, UPDATE y DELETE en tiempo casi real. Es el método más potente pero también el más complejo de implementar.

**Flags de procesamiento:** el sistema fuente tiene una columna booleana `ya_procesado` o `pendiente_sync` que el proceso ETL usa para identificar registros nuevos y luego marca como procesados.

---

#### Extracción desde APIs

Muchos sistemas fuente exponen sus datos a través de APIs REST. La extracción desde APIs tiene consideraciones especiales:

- **Paginación:** las APIs suelen limitar la cantidad de registros por llamada. El proceso ETL debe iterar por páginas.
- **Rate limiting:** la API limita la cantidad de llamadas por minuto. El proceso debe respetar esos límites.
- **Autenticación:** las APIs requieren tokens o API Keys que deben almacenarse de forma segura (nunca en el código fuente).
- **Idempotencia:** si la llamada falla a mitad del proceso, debe poder re-ejecutarse sin duplicar datos.

---

#### Extracción de archivos planos

Muchos sistemas legacy o procesos manuales entregan datos en archivos CSV, Excel o TXT. Consideraciones:

- **Detección de llegada:** el proceso ETL debe monitorear una carpeta o bucket de S3 para detectar cuando llega un nuevo archivo.
- **Validación del archivo:** antes de procesar, verificar que el archivo tiene el formato esperado (cantidad de columnas, delimitador, encoding).
- **Archivos parciales:** si el proceso que genera el archivo falla a mitad, puede aparecer un archivo incompleto. Usar archivos de señal (*flag files*) que se generan cuando el archivo principal está completo.
- **Archivado:** una vez procesado, mover el archivo a una carpeta de archivado con timestamp para trazabilidad.

---

## Etapa 3B — Transformación (*Transform*)

La transformación es el corazón del ETL. Es donde los datos crudos de los sistemas fuente se convierten en datos integrados, limpios y conformes con el modelo del EDW.

### Transformaciones de limpieza

**Tratamiento de nulos:** definir para cada campo qué hacer con los valores nulos según el glosario corporativo. Opciones:
- Mantener el nulo (si el campo es opcional).
- Imputar un valor por defecto según la regla de negocio (`'SIN DATOS'`, `0`, `'9999-12-31'`).
- Rechazar el registro si el campo es obligatorio y está nulo (y enviarlo a la cola de errores).

**Estandarización de formatos:**
- Fechas: convertir todos los formatos posibles (`15/03/2025`, `2025-03-15`, `March 15 2025`) a un formato único (`YYYY-MM-DD`).
- Textos: strip de espacios, unificación de mayúsculas/minúsculas según el estándar del glosario.
- Numéricos: resolución del separador decimal (`,` vs `.`) y de miles.

**Validación de dominio:** verificar que los valores pertenecen al conjunto de valores válidos definido en el glosario. Por ejemplo, verificar que el código de moneda está en la lista oficial ISO 4217.

---

### Transformaciones de integración

Esta es la parte más compleja y valiosa del ETL en Inmon: resolver las diferencias entre sistemas fuente para crear una visión unificada.

**Resolución de identificadores (*Entity Resolution*):**

El mismo cliente puede tener identificadores distintos en sistemas distintos:
- En el ERP: `CUST-00004521`
- En el CRM: `C_4521`
- En el sistema de logística: `45210`

Para integrarlos en el EDW como un único cliente, se necesita una **tabla de mapeo de claves** (*crosswalk table*) que relaciona los identificadores de cada sistema:

```
Tabla: edw.mapeo_claves_cliente
─────────────────────────────────────────────────────────────────
id_cliente_edw  │ id_sistema │ clave_origen  │ fecha_mapeo
────────────────│────────────│───────────────│────────────
10001           │ ERP        │ CUST-00004521 │ 2024-01-15
10001           │ CRM        │ C_4521        │ 2024-01-15
10001           │ LOGISTICA  │ 45210         │ 2024-01-15
10002           │ ERP        │ CUST-00003310 │ 2024-01-15
10002           │ CRM        │ C_3310        │ 2024-01-15
```

Esta tabla de mapeo es uno de los activos más valiosos del EDW: representa el conocimiento acumulado sobre cómo se relacionan los datos entre sistemas.

**Resolución de conflictos entre fuentes:**

Cuando el mismo dato existe en dos sistemas y tiene valores distintos, ¿cuál prevalece? Esta decisión debe estar documentada en las **reglas de integración**:

| Atributo | Sistema A (ERP) | Sistema B (CRM) | Regla de resolución |
|---|---|---|---|
| `email_cliente` | `maria@old.com` | `maria@nuevo.com` | Prevalece CRM (más reciente) |
| `razon_social` | `GARCIA MARIA` | `María García` | Prevalece ERP (registro legal) |
| `id_segmento` | Vacío | `Premium` | Prevalece CRM (campo solo existe allí) |

---

### Gestión del historial en el EDW

Cuando un registro cambia en la fuente, el ETL debe preservar el historial en el EDW. El mecanismo es similar al SCD Tipo 2 pero aplicado sistemáticamente a todas las entidades del EDW:

```
Proceso de actualización histórica en el ETL:

1. Extraer el registro modificado de la Staging Area.
2. Buscar el registro vigente en el EDW (is_vigente = TRUE).
3. Si no existe → INSERT como nuevo registro con fecha_efectiva = hoy.
4. Si existe y hay diferencias:
   a. Calcular el hash del registro fuente.
   b. Si el hash difiere del hash del registro EDW → hay cambio.
   c. UPDATE del registro vigente: fecha_vencimiento = hoy-1, is_vigente = FALSE.
   d. INSERT del nuevo registro con los nuevos valores y fecha_efectiva = hoy.
5. Si existe y no hay diferencias → no hacer nada (eficiencia).
```

---

## Etapa 3C — Carga (*Load*)

### Principios de la carga al EDW

**Idempotencia:** el proceso de carga puede ejecutarse múltiples veces con el mismo resultado. Si falla a la mitad y se re-ejecuta, no genera duplicados ni corrompe el historial.

**Atomicidad por lote:** un lote de registros se carga completo o no se carga. Si falla a mitad del lote, se hace rollback y se reintenta desde el principio del lote.

**Orden de carga:** las tablas deben cargarse en el orden correcto respetando las dependencias de claves foráneas:
1. Primero las tablas maestras sin dependencias (PAIS, TIPO_CLIENTE).
2. Luego las tablas que dependen de las anteriores (PROVINCIA → CIUDAD).
3. Finalmente las tablas transaccionales que dependen de todas las anteriores (PEDIDO, VENTA).

**Sin locks prolongados:** la carga debe diseñarse para minimizar el tiempo de bloqueo de tablas, especialmente si el EDW debe estar disponible para los procesos de actualización de Data Marts durante la ventana de carga.

---

### Ventana de Carga

La **ventana de carga** (*load window*) es el período durante el cual el proceso ETL puede ejecutarse sin interferir con los procesos de negocio. En organizaciones con actividad 24/7, definir esta ventana es un desafío crítico.

```
Ejemplo de ventana de carga para un DWH con operaciones en múltiples zonas horarias:

22:00 UTC │ Inicio del proceso de extracción desde fuentes
          │ (horario de menor actividad en todas las zonas)
22:30 UTC │ Finalización de extracciones → Staging Area completa
22:30 UTC │ Inicio de transformaciones
23:30 UTC │ Inicio de carga al EDW
01:00 UTC │ EDW actualizado → inicio de actualización de Data Marts
03:00 UTC │ Data Marts actualizados → informes disponibles para el día
06:00 UTC │ Inicio del día hábil (primer zona horaria)
```

---

## Gestión de errores y reintentos

El ETL debe ser **robusto ante fallos**. Los fallos son inevitables: la red puede caerse, un sistema fuente puede estar inaccesible, un registro puede violar una restricción de integridad. El diseño del ETL debe contemplar:

**Cola de errores (*Error Queue*):** los registros que no pueden procesarse (por error de validación, referencia huérfana, etc.) no deben detener el proceso completo. Se derivan a una tabla de errores con el motivo del rechazo para revisión manual posterior.

```
Tabla: staging.errores_carga
──────────────────────────────────────────────────────────────────────
id_error │ entidad      │ clave_origen │ motivo_error             │ fecha
─────────│──────────────│──────────────│──────────────────────────│──────
1001     │ edw.pedido   │ PED-99812    │ id_cliente no encontrado │ 2025-03-15
1002     │ edw.producto │ SKU-X9991    │ id_categoria nulo        │ 2025-03-15
```

**Registro de auditoría (*Audit Log*):** cada ejecución del ETL debe registrarse con:
- Fecha y hora de inicio y fin.
- Sistema fuente procesado.
- Registros extraídos, transformados y cargados.
- Registros rechazados y enviados a la cola de errores.
- Estado final: éxito o fallo (con mensaje de error).

**Reintentos con backoff:** si un paso falla por un error transitorio (timeout de red, sistema fuente temporalmente no disponible), el proceso debe reintentarlo automáticamente con un tiempo de espera creciente entre intentos.

---

## El Metadato del ETL

Un componente frecuentemente subestimado del ETL es la gestión de sus propios **metadatos de ejecución**: cuándo corrió, qué procesó, qué última fecha fue procesada por cada entidad.

```
Tabla: meta.control_carga
────────────────────────────────────────────────────────────────────────────
entidad_destino  │ sistema_fuente │ ultima_ejecucion_ok │ ultimo_valor_marca
─────────────────│────────────────│─────────────────────│────────────────────
edw.cliente      │ ERP            │ 2025-03-15 01:23:45 │ 2025-03-15 06:00:00
edw.cliente      │ CRM            │ 2025-03-15 01:45:12 │ 2025-03-15 06:00:00
edw.pedido       │ ERP            │ 2025-03-15 02:10:33 │ 2025-03-15 06:00:00
edw.producto     │ ERP            │ 2025-03-15 01:31:08 │ 2025-03-15 06:00:00
```

El campo `ultimo_valor_marca` guarda el "punto de corte" de la última extracción incremental exitosa. Si el proceso falla y se reinicia, sabe desde dónde retomar.

---

## ELT vs. ETL: El Debate Moderno en el Contexto Inmon

En la arquitectura original de Inmon (años 90-2000), la transformación ocurría **fuera** del data warehouse, en un servidor ETL dedicado. Con la llegada de motores cloud de alto rendimiento, el paradigma está cambiando a **ELT**: cargar primero y transformar dentro del motor.

### ¿Se puede aplicar ELT en la arquitectura Inmon?

Sí, pero con matices. El principio Inmon de integración y normalización no cambia; lo que cambia es **dónde** se ejecuta la lógica de transformación.

```
ETL clásico (Inmon original):
  Fuente → [Servidor ETL externo] → Staging → [Servidor ETL] → EDW (3FN)
  La transformación consume recursos del servidor ETL.

ELT moderno (Inmon + Cloud):
  Fuente → [Ingesta directa] → Staging (en el DWH) → [SQL/dbt dentro del DWH] → EDW (3FN)
  La transformación consume recursos del motor cloud (Snowflake, BigQuery, etc.).
```

### Implementación con dbt para el EDW Inmon

```sql
-- models/staging/stg_erp__clientes.sql
-- Modelo de staging: limpieza y tipado desde la capa raw
{{ config(materialized='view') }}

SELECT
    CAST(id_cliente AS BIGINT)           AS cliente_src_key,
    UPPER(TRIM(razon_social))            AS razon_social,
    CASE tipo_cliente
        WHEN 'PF' THEN 'F'
        WHEN 'PE' THEN 'E'
        WHEN 'PG' THEN 'G'
        ELSE 'F'
    END                                  AS tipo_cliente,
    CAST(id_ciudad AS INTEGER)           AS id_ciudad,
    CAST(id_segmento AS SMALLINT)        AS id_segmento,
    CASE WHEN activo = 1 THEN 'A' ELSE 'I' END AS estado,
    CAST(fecha_modificacion AS TIMESTAMP) AS fecha_modificacion,
    'ERP' AS sistema_fuente
FROM {{ source('raw', 'erp_clientes') }}
WHERE id_cliente IS NOT NULL
```

```sql
-- models/edw/edw__cliente.sql
-- Modelo del EDW: integración con SCD Tipo 2
{{ config(
    materialized='incremental',
    unique_key='cliente_src_key',
    strategy='timestamp',
    updated_at='fecha_modificacion'
) }}

WITH fuentes_unificadas AS (
    SELECT * FROM {{ ref('stg_erp__clientes') }}
    UNION ALL
    SELECT * FROM {{ ref('stg_crm__clientes') }}
),
priorizada AS (
    -- Regla de integración: ERP prevalece sobre CRM para razon_social
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY cliente_src_key
            ORDER BY CASE sistema_fuente WHEN 'ERP' THEN 1 ELSE 2 END
        ) AS prioridad
    FROM fuentes_unificadas
)
SELECT
    cliente_src_key,
    razon_social,
    tipo_cliente,
    id_ciudad,
    id_segmento,
    estado,
    CURRENT_DATE AS fecha_efectiva,
    '9999-12-31'::DATE AS fecha_vencimiento,
    TRUE AS es_vigente,
    {{ dbt_utils.generate_surrogate_key(['cliente_src_key', 'razon_social', 'tipo_cliente', 'id_ciudad']) }} AS hash_registro
FROM priorizada
WHERE prioridad = 1

{% if is_incremental() %}
    AND fecha_modificacion > (SELECT MAX(fecha_efectiva) FROM {{ this }})
{% endif %}
```

---

## Orquestación del ETL: Pipelines Completos

El ETL de Inmon involucra muchas más dependencias que el de Kimball (porque carga un EDW completo, no un solo Data Mart). La orquestación debe manejar:

1. **Orden de carga por dependencias de FK** (tablas maestras antes que transaccionales).
2. **Paralelismo donde sea posible** (fuentes independientes se extraen en paralelo).
3. **Checkpoints de consistencia** entre etapas.

### DAG de Airflow para el EDW completo

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta

default_args = {
    'owner': 'equipo-datos',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
    'email': ['datos@empresa.com'],
}

with DAG(
    dag_id='etl_edw_inmon_completo',
    description='ETL nocturno: fuentes → staging → EDW → data marts',
    schedule_interval='0 22 * * *',  # 22:00 UTC
    start_date=datetime(2025, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=['edw', 'inmon'],
) as dag:

    # ═══════════════════════════════════════════════════
    # FASE 1: EXTRACCIÓN (paralela por sistema fuente)
    # ═══════════════════════════════════════════════════
    with TaskGroup('extraccion') as grupo_extraccion:
        ext_erp = PythonOperator(
            task_id='extraer_erp',
            python_callable=extraer_incremental_erp,
        )
        ext_crm = PythonOperator(
            task_id='extraer_crm',
            python_callable=extraer_completo_crm,
        )
        ext_archivos = PythonOperator(
            task_id='extraer_archivos_csv',
            python_callable=extraer_archivos_planos,
        )
        # Se ejecutan en paralelo (sin dependencia entre ellas)

    # ═══════════════════════════════════════════════════
    # FASE 2: TRANSFORMACIÓN Y CARGA AL EDW
    # ═══════════════════════════════════════════════════
    with TaskGroup('carga_edw') as grupo_edw:
        # Nivel 1: Tablas maestras sin dependencias
        carga_pais = PythonOperator(task_id='edw_pais', python_callable=cargar_edw_pais)
        carga_tipo_cli = PythonOperator(task_id='edw_tipo_cliente', python_callable=cargar_edw_tipo_cliente)
        carga_segmento = PythonOperator(task_id='edw_segmento', python_callable=cargar_edw_segmento)

        # Nivel 2: Dependen del nivel 1
        carga_provincia = PythonOperator(task_id='edw_provincia', python_callable=cargar_edw_provincia)
        carga_categoria = PythonOperator(task_id='edw_categoria', python_callable=cargar_edw_categoria)

        # Nivel 3: Dependen del nivel 2
        carga_ciudad = PythonOperator(task_id='edw_ciudad', python_callable=cargar_edw_ciudad)
        carga_producto = PythonOperator(task_id='edw_producto', python_callable=cargar_edw_producto)

        # Nivel 4: Dependen de todo lo anterior
        carga_cliente = PythonOperator(task_id='edw_cliente', python_callable=cargar_edw_cliente)

        # Nivel 5: Transaccionales
        carga_pedido = PythonOperator(task_id='edw_pedido', python_callable=cargar_edw_pedido)
        carga_linea = PythonOperator(task_id='edw_linea_pedido', python_callable=cargar_edw_linea)

        # Dependencias internas
        [carga_pais] >> carga_provincia >> carga_ciudad
        [carga_tipo_cli, carga_segmento, carga_ciudad] >> carga_cliente
        carga_categoria >> carga_producto
        [carga_cliente, carga_producto] >> carga_pedido >> carga_linea

    # ═══════════════════════════════════════════════════
    # FASE 3: DERIVACIÓN DE DATA MARTS
    # ═══════════════════════════════════════════════════
    with TaskGroup('derivacion_data_marts') as grupo_dm:
        dm_ventas = BashOperator(
            task_id='derivar_dm_ventas',
            bash_command='dbt run --select dm_ventas --target prod',
        )
        dm_finanzas = BashOperator(
            task_id='derivar_dm_finanzas',
            bash_command='dbt run --select dm_finanzas --target prod',
        )

    # ═══════════════════════════════════════════════════
    # FASE 4: VALIDACIÓN
    # ═══════════════════════════════════════════════════
    validacion = BashOperator(
        task_id='tests_consistencia',
        bash_command='dbt test --target prod',
    )

    # Flujo principal
    grupo_extraccion >> grupo_edw >> grupo_dm >> validacion
```

---

## La Carga Inicial (*Initial Load*): El Primer Gran Desafío

La carga inicial es el proceso de cargar por primera vez todo el historial disponible en los sistemas fuente al EDW. Es cualitativamente distinta a la carga incremental diaria:

### Diferencias entre carga inicial e incremental

| Aspecto | Carga Inicial | Carga Incremental |
|---|---|---|
| **Volumen** | Todo el historial (años) | Solo cambios del período |
| **Duración** | Horas a días | Minutos a horas |
| **Frecuencia** | Una sola vez | Diaria/horaria |
| **Detección de cambios** | No aplica (todo es nuevo) | Timestamp, CDC, hash |
| **Riesgo** | Alto (si falla, se pierde mucho tiempo) | Medio (se puede reintentar) |
| **Validación** | Exhaustiva (comparar totales completos) | Diferencial (solo lo nuevo) |

### Estrategia de carga inicial por fases

```
Fase 1 — Tablas de referencia (catálogos)
  Volumen: pequeño (miles de registros)
  Tiempo: minutos
  Validación: COUNT(*) y muestreo manual

Fase 2 — Tablas maestras (clientes, productos, vendedores)
  Volumen: medio (decenas de miles a millones)
  Tiempo: minutos a horas
  Validación: COUNT(*), SUM de campos numéricos, claves huérfanas

Fase 3 — Tablas transaccionales (pedidos, facturas, movimientos)
  Volumen: alto (millones a miles de millones)
  Tiempo: horas a días
  Estrategia: cargar por períodos (año por año o mes por mes)
  Validación: totales por mes/año contra el sistema fuente

Fase 4 — Derivación inicial de Data Marts
  Precondición: EDW completamente cargado y validado
  Tiempo: horas
  Validación: cruce de totales EDW vs. Data Mart
```

---

## Monitoreo y Observabilidad del ETL

Un ETL en producción necesita observabilidad para detectar problemas antes de que los usuarios los reporten.

### Métricas clave a monitorear

| Métrica | Umbral de alerta | Acción |
|---|---|---|
| **Duración del ETL** | > 150% del promedio histórico | Investigar cuello de botella |
| **Filas rechazadas** | > 1% del total extraído | Notificar al Data Steward |
| **Filas cargadas = 0** | Siempre | Alerta crítica: posible fallo de extracción |
| **Diferencia EDW vs. fuente** | > 0.01% | Investigar pérdida de datos |
| **Espacio en disco** | > 80% capacidad | Planificar expansión o archivado |
| **Ventana de carga excedida** | ETL no terminó antes del SLA | Alerta al equipo + plan de contingencia |

### Dashboard operativo del ETL

```sql
-- Vista para el dashboard operativo del ETL
CREATE VIEW meta.v_estado_etl AS
SELECT
    e.nombre_proceso,
    e.fecha_inicio::DATE AS fecha,
    e.estado,
    EXTRACT(EPOCH FROM (e.fecha_fin - e.fecha_inicio)) / 60 AS duracion_min,
    e.filas_extraidas,
    e.filas_cargadas,
    e.filas_rechazadas,
    ROUND(100.0 * e.filas_rechazadas / NULLIF(e.filas_extraidas, 0), 2) AS pct_rechazo,
    CASE
        WHEN e.estado = 'FALLIDO' THEN '🔴 FALLO'
        WHEN e.filas_rechazadas > e.filas_extraidas * 0.01 THEN '🟡 RECHAZO ALTO'
        WHEN EXTRACT(EPOCH FROM (e.fecha_fin - e.fecha_inicio)) / 60 > 120 THEN '🟡 LENTO'
        ELSE '🟢 OK'
    END AS semaforo
FROM meta.control_carga e
WHERE e.fecha_inicio >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY e.fecha_inicio DESC;
```

---

## Entregables de la Etapa 3

1. ✅ **Diseño detallado del flujo ETL** por cada entidad y sistema fuente.
2. ✅ **Matriz Fuente-Destino completa** con transformaciones campo a campo.
3. ✅ **Tablas de mapeo de claves** entre sistemas fuente y el EDW.
4. ✅ **Reglas de integración documentadas** (qué prevalece cuando hay conflicto).
5. ✅ **Diseño del esquema de errores y auditoría** del ETL.
6. ✅ **Código ETL** (Python, dbt, Airflow, o herramienta seleccionada).
7. ✅ **Plan de carga inicial** (*initial load*): estrategia para cargar los datos históricos por primera vez.
8. ✅ **Diseño de la ventana de carga** y acuerdo de SLA con el negocio.

---

## Relación con las etapas siguientes

```
ETAPA 3: ETL hacia el EDW
        │
        │ Produce:
        │  • EDW alimentado con datos integrados e históricos
        │  • Metadatos de control y auditoría
        │  • Cola de errores para revisión
        │
        ▼
ETAPA 4: Data Marts (derivación desde el EDW)
        │ Un segundo proceso ETL toma los datos del EDW
        │ y los desnormaliza en esquemas estrella para
        │ cada área de negocio.
        ▼
```

---

## Lecturas recomendadas

- **Kimball, R. & Caserta, J.** — *The Data Warehouse ETL Toolkit: Practical Techniques for Extracting, Cleaning, Conforming, and Delivering Data*. Wiley.
- **Inmon, W.H.** — *Building the Data Warehouse*, 4ta edición. Capítulo 7: "The ETL Process". Wiley.
- **Reis, J. & Housley, M.** — *Fundamentals of Data Engineering*, Capítulo 8. O'Reilly Media.
- **Documentación de Apache Airflow** — [airflow.apache.org](https://airflow.apache.org/docs/) (orquestación de pipelines ETL).
- **Documentación de Debezium** — [debezium.io](https://debezium.io/documentation/) (Change Data Capture).
- **dbt Labs** — Documentación oficial de dbt: [docs.getdbt.com](https://docs.getdbt.com) (transformaciones ELT modernas).
- **Kleppmann, M.** — *Designing Data-Intensive Applications*. O'Reilly. Capítulos 10-11: "Batch Processing" y "Stream Processing".
- **Narayan, A. et al.** — *Fundamentals of Data Observability*. O'Reilly. (Monitoreo y calidad de pipelines de datos).
