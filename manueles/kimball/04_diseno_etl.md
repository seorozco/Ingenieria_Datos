# Arquitectura Kimball · Etapa 4 — Diseño e Implementación del ETL

> **Arquitectura:** Kimball — Bottom-Up  
> **Posición en el ciclo:** Cuarta etapa. Según Kimball, el ETL representa el 70% del esfuerzo total de un proyecto de Data Warehouse. Es la etapa más larga y la que más riesgos concentra.

---

## El ETL en la arquitectura Kimball

A diferencia de Inmon, donde hay dos ETLs separados (uno a la fuente→EDW y otro del EDW→Data Mart), en Kimball el ETL va **directamente desde los sistemas fuente hacia los Data Marts**. No hay un repositorio normalizado central intermedio.

```
ARQUITECTURA KIMBALL — FLUJO ETL:

Sistemas Fuente (ERP, CRM, Excel, APIs)
              │
              │  Un solo ETL
              ▼
    ┌──────────────────┐
    │  STAGING AREA    │  ← Área temporal de trabajo
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │   DATA MART      │  ← Esquema estrella (Etapa 2 + 3)
    │  (fact + dims)   │
    └──────────────────┘
             │
             ▼
    Herramientas de BI (Etapa 5)
```

---

## El Staging Area

El Staging Area (área de montaje) es un espacio temporal de trabajo del proceso ETL. Sus características:

- **No es permanente:** los datos se cargan, se procesan y se eliminan al final de cada ciclo ETL.
- **No es accesible por los usuarios:** es territorio exclusivo del proceso ETL.
- **Replica la estructura de los sistemas fuente:** las tablas del staging tienen el mismo formato que los datos extraídos, sin transformaciones todavía.
- **Permite reinicios seguros:** si el proceso ETL falla en mitad de la ejecución, se puede reiniciar desde el staging sin volver a extraer de los sistemas fuente.

```sql
-- Staging para datos de ventas (réplica de la tabla fuente)
CREATE SCHEMA staging;

CREATE TABLE staging.s_ventas (
    factura_id     VARCHAR(30),
    fecha          VARCHAR(20),   -- todavía como string, sin parsear
    cliente_id     VARCHAR(30),
    producto_id    VARCHAR(30),
    cantidad       VARCHAR(20),   -- todavía como string
    precio         VARCHAR(20),
    descuento      VARCHAR(20),
    vendedor_id    VARCHAR(30),
    -- Columnas de control ETL
    stg_loaded_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    stg_source     VARCHAR(50) NOT NULL DEFAULT 'ERP_SAP',
    stg_batch_id   BIGINT     NOT NULL
);
```

---

## Los subsistemas ETL de Kimball

Ralph Kimball identificó **34 subsistemas ETL** que componen el proceso completo de un Data Warehouse. Estos subsistemas se organizan en cuatro grupos funcionales:

```
┌────────────────────────────────────────────────────────────────────────┐
│                    34 SUBSISTEMAS ETL DE KIMBALL                       │
├───────────────────┬────────────────────────────────────────────────────┤
│  GRUPO 1          │  Extracción (capturar datos de los fuentes)        │
│  Subsistemas 1-4  │                                                    │
├───────────────────┼────────────────────────────────────────────────────┤
│  GRUPO 2          │  Limpieza y Conformación (calidad y estandarización│
│  Subsistemas 5-15 │                                                    │
├───────────────────┼────────────────────────────────────────────────────┤
│  GRUPO 3          │  Entrega (carga al Data Mart)                      │
│  Subsistemas 16-23│                                                    │
├───────────────────┼────────────────────────────────────────────────────┤
│  GRUPO 4          │  Gestión (monitoreo, control de calidad, auditoría)│
│  Subsistemas 24-34│                                                    │
└───────────────────┴────────────────────────────────────────────────────┘
```

Para una tecnicatura, trabajamos con los subsistemas más importantes de cada grupo.

---

## Grupo 1: Extracción

### Subsistema 1: Extracción de datos maestros

La extracción puede ser de dos tipos:

**Extracción completa (Full Extract):**
Se extrae toda la tabla del sistema fuente en cada ciclo. Simple de implementar, costoso en términos de volumen transferido.

```python
import psycopg2
import pandas as pd

def extraer_completo(tabla_fuente: str, conn_erp) -> pd.DataFrame:
    """Extrae todos los registros de una tabla del ERP."""
    query = f"SELECT * FROM {tabla_fuente}"
    return pd.read_sql(query, conn_erp)

# Uso
conn_erp = psycopg2.connect("host=erp-server dbname=erp_db user=etl_user password=***")
df_clientes = extraer_completo("clientes", conn_erp)
```

**Extracción incremental (Incremental Extract):**
Solo se extraen los registros nuevos o modificados desde la última extracción. Requiere una columna de control (timestamp de última modificación o un campo de "marca de agua").

```python
def extraer_incremental(tabla_fuente: str, conn_erp, ultima_carga: str) -> pd.DataFrame:
    """
    Extrae solo los registros modificados desde la última carga.
    Requiere columna 'updated_at' en el sistema fuente.
    """
    query = f"""
        SELECT *
        FROM {tabla_fuente}
        WHERE updated_at > '{ultima_carga}'
        ORDER BY updated_at
    """
    return pd.read_sql(query, conn_erp)

# Leer la última marca de agua del control ETL
def obtener_ultima_marca(tabla: str, conn_dwh) -> str:
    cursor = conn_dwh.cursor()
    cursor.execute("""
        SELECT COALESCE(MAX(ultima_extraccion), '2020-01-01 00:00:00')
        FROM etl_control.marcas_agua
        WHERE tabla_fuente = %s
    """, (tabla,))
    return cursor.fetchone()[0]
```

### Subsistema 2: Captura de Cambios (*Change Data Capture — CDC*)

CDC es la técnica más eficiente para detectar cambios en los sistemas fuente sin necesidad de columnas `updated_at`. Lee el **log de transacciones** de la base de datos para identificar INSERT, UPDATE y DELETE.

```
Log de transacciones del ERP (PostgreSQL WAL):
  2025-03-15 10:23:41 | UPDATE | clientes | id=1042 | ciudad: Córdoba → Rosario
  2025-03-15 10:24:55 | INSERT | ventas   | id=8901 | cliente=1042, producto=205
  2025-03-15 10:31:12 | DELETE | clientes | id=0099 | (cliente dado de baja)

El ETL lee el WAL y aplica solo estos cambios al Data Mart,
sin necesidad de extraer toda la tabla.
```

Herramientas de CDC populares: **Debezium** (open source), **AWS DMS**, **Fivetran**.

---

## Grupo 2: Limpieza y Conformación

### Subsistema 5: Limpieza de datos (*Data Cleansing*)

En esta etapa se corrigen los problemas de calidad detectados en los datos del staging:

```python
import pandas as pd
import re

def limpiar_ventas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica reglas de limpieza al staging de ventas.
    """
    df = df.copy()

    # 1. Parsear fechas (el ERP las envía como string 'DD/MM/YYYY')
    df['fecha'] = pd.to_datetime(df['fecha'], format='%d/%m/%Y', errors='coerce')

    # 2. Convertir cantidades numéricas (pueden tener coma decimal)
    df['cantidad'] = df['cantidad'].str.replace(',', '.').astype(float)
    df['precio']   = df['precio'].str.replace(',', '.').str.replace('$', '').astype(float)
    df['descuento'] = pd.to_numeric(df['descuento'], errors='coerce').fillna(0)

    # 3. Estandarizar IDs de cliente (quitar espacios, llevar a mayúsculas)
    df['cliente_id'] = df['cliente_id'].str.strip().str.upper()

    # 4. Registrar filas con errores críticos (fecha nula = registro irrecuperable)
    mask_error = df['fecha'].isna()
    df_errores = df[mask_error].copy()
    df_errores['motivo_error'] = 'fecha_invalida'

    # 5. Retornar solo registros válidos
    df_valido = df[~mask_error]

    return df_valido, df_errores

df_ventas_stg = pd.read_sql("SELECT * FROM staging.s_ventas", conn_dwh)
df_ventas_limpio, df_ventas_errores = limpiar_ventas(df_ventas_stg)

# Registrar errores en la tabla de errores ETL
if not df_ventas_errores.empty:
    df_ventas_errores.to_sql('errores_etl', conn_dwh, schema='etl_control',
                              if_exists='append', index=False)
    print(f"ADVERTENCIA: {len(df_ventas_errores)} registros rechazados.")
```

### Subsistema 6: Conformación de dimensiones

La conformación es el proceso de estandarizar los datos para que sean consistentes entre los distintos sistemas fuente.

**Ejemplo:** El código de región en el ERP es "CEN" y en el CRM es "Centro". Ambos se conforman al valor estándar del glosario: "Centro".

```python
# Tabla de conformación: mapeo de códigos de fuentes al estándar
mapeo_region = {
    # ERP
    'CEN':     'Centro',
    'PAT':     'Patagonia',
    'NEA':     'Noreste',
    'NOA':     'Noroeste',
    'CUY':     'Cuyo',
    # CRM
    'Centro':  'Centro',
    'Sur':     'Patagonia',
    'NE':      'Noreste',
    'NO':      'Noroeste',
    'Cuyo':    'Cuyo',
    # Casos históricos (datos antiguos)
    'REG_C':   'Centro',
    'REG_S':   'Patagonia',
}

def conformar_region(valor_fuente: str) -> str:
    """Devuelve el valor estándar de región o lanza error si no está mapeado."""
    resultado = mapeo_region.get(valor_fuente)
    if resultado is None:
        raise ValueError(f"Código de región no mapeado: '{valor_fuente}'")
    return resultado

df_clientes['region'] = df_clientes['region_fuente'].apply(conformar_region)
```

---

## Grupo 3: Entrega al Data Mart

### Subsistema 16: Carga de dimensiones con SCD

La carga de dimensiones es el proceso más complejo del ETL porque debe manejar correctamente los distintos tipos de SCD definidos en el diseño.

**Algoritmo de carga SCD Tipo 2:**

```python
import pandas as pd
from sqlalchemy import create_engine
from datetime import date

def cargar_dimension_scd2(df_nuevo: pd.DataFrame, tabla_dim: str,
                           natural_key: str, engine) -> None:
    """
    Carga una dimensión con SCD Tipo 2.
    Detecta cambios, cierra las filas anteriores e inserta las nuevas versiones.

    Args:
        df_nuevo: DataFrame con los datos nuevos del sistema fuente
        tabla_dim: nombre de la tabla de dimensión en el DWH
        natural_key: columna que identifica la entidad en el fuente
        engine: conexión SQLAlchemy al DWH
    """
    hoy = date.today()

    with engine.begin() as conn:
        # 1. Traer la versión actual de cada entidad del DWH
        df_actual = pd.read_sql(
            f"SELECT * FROM {tabla_dim} WHERE is_current = TRUE",
            conn
        )

        # 2. Hacer merge para detectar cambios
        df_merge = df_nuevo.merge(
            df_actual,
            on=natural_key,
            suffixes=('_nuevo', '_actual'),
            how='outer',
            indicator=True
        )

        # 3. Registros NUEVOS (existen en fuente pero no en DWH)
        df_nuevos = df_merge[df_merge['_merge'] == 'left_only'].copy()
        if not df_nuevos.empty:
            # Preparar para inserción
            df_insertar = df_nuevo[df_nuevo[natural_key].isin(df_nuevos[natural_key])]
            df_insertar = df_insertar.assign(
                valid_from=hoy,
                valid_to=None,
                is_current=True
            )
            df_insertar.to_sql(tabla_dim.split('.')[-1], conn,
                               schema=tabla_dim.split('.')[0],
                               if_exists='append', index=False)
            print(f"  → {len(df_insertar)} registros NUEVOS insertados en {tabla_dim}")

        # 4. Registros MODIFICADOS (diferencias en columnas que no son la natural key)
        cols_descriptivas = [c for c in df_nuevo.columns if c != natural_key]
        cambios_mask = False
        for col in cols_descriptivas:
            if f'{col}_nuevo' in df_merge.columns and f'{col}_actual' in df_merge.columns:
                cambios_mask |= (df_merge[f'{col}_nuevo'] != df_merge[f'{col}_actual'])

        df_modificados = df_merge[(df_merge['_merge'] == 'both') & cambios_mask]

        if not df_modificados.empty:
            nks_mod = df_modificados[natural_key].tolist()
            # Cerrar las filas actuales
            conn.execute(f"""
                UPDATE {tabla_dim}
                SET valid_to   = '{hoy - pd.Timedelta(days=1)}',
                    is_current = FALSE
                WHERE {natural_key} = ANY(%s)
                  AND is_current = TRUE
            """, (nks_mod,))
            # Insertar nuevas versiones
            df_insertar_mod = df_nuevo[df_nuevo[natural_key].isin(nks_mod)]
            df_insertar_mod = df_insertar_mod.assign(
                valid_from=hoy, valid_to=None, is_current=True
            )
            df_insertar_mod.to_sql(tabla_dim.split('.')[-1], conn,
                                    schema=tabla_dim.split('.')[0],
                                    if_exists='append', index=False)
            print(f"  → {len(df_modificados)} registros MODIFICADOS (SCD2) en {tabla_dim}")

        # 5. Registros ELIMINADOS (existen en DWH pero no en fuente)
        df_eliminados = df_merge[df_merge['_merge'] == 'right_only']
        if not df_eliminados.empty:
            # Política: no eliminar del DWH, sino marcar como inactivos
            nks_eli = df_eliminados[natural_key].tolist()
            conn.execute(f"""
                UPDATE {tabla_dim}
                SET valid_to   = '{hoy}',
                    is_current = FALSE
                WHERE {natural_key} = ANY(%s)
                  AND is_current = TRUE
            """, (nks_eli,))
            print(f"  → {len(df_eliminados)} registros INACTIVADOS en {tabla_dim}")
```

### Subsistema 17: Carga de la tabla de hechos

La carga de hechos es más simple que la de dimensiones porque los hechos son (generalmente) inmutables. Una transacción que ocurrió no cambia.

```python
def cargar_hechos(df_ventas: pd.DataFrame, engine) -> None:
    """
    Carga registros nuevos en la tabla de hechos fact_ventas.
    Resuelve las claves sustitutas de las dimensiones.
    """
    with engine.begin() as conn:
        # 1. Resolver clave sustituta de tiempo
        df_tiempos = pd.read_sql("SELECT id_tiempo, fecha FROM dm_ventas.dim_tiempo", conn)
        df_ventas['fecha'] = pd.to_datetime(df_ventas['fecha'])
        df_ventas = df_ventas.merge(
            df_tiempos,
            on='fecha',
            how='left'
        )

        # 2. Resolver clave sustituta de cliente (versión vigente en la fecha de la venta)
        df_clientes = pd.read_sql("""
            SELECT id_cliente, cliente_nk, valid_from, valid_to
            FROM dm_ventas.dim_cliente
        """, conn)
        # Para cada venta, el cliente vigente en esa fecha
        # (lógica simplificada; en producción se haría en SQL con BETWEEN)
        df_clientes_vigente = df_clientes[df_clientes['is_current'] == True][
            ['id_cliente', 'cliente_nk']
        ].rename(columns={'id_cliente': 'id_cliente_dm'})

        df_ventas = df_ventas.merge(
            df_clientes_vigente,
            left_on='cliente_id',
            right_on='cliente_nk',
            how='left'
        )

        # 3. Calcular métricas derivadas
        df_ventas['total_neto']  = df_ventas['cantidad'] * df_ventas['precio'] * (1 - df_ventas['descuento'])
        df_ventas['margen_bruto']= df_ventas['total_neto'] - (df_ventas['cantidad'] * df_ventas['costo_unit'])

        # 4. Detectar y excluir duplicados (idempotencia)
        facturas_existentes = pd.read_sql("""
            SELECT numero_factura, linea FROM dm_ventas.fact_ventas
        """, conn)
        key_existentes = set(zip(facturas_existentes['numero_factura'], facturas_existentes['linea']))
        mask_nuevo = ~df_ventas.apply(
            lambda r: (r['factura_id'], r['linea']) in key_existentes, axis=1
        )
        df_nuevo = df_ventas[mask_nuevo]

        # 5. Insertar en la tabla de hechos
        cols_fact = ['id_tiempo', 'id_cliente_dm', 'id_producto', 'id_vendedor',
                     'factura_id', 'linea', 'cantidad', 'precio',
                     'descuento', 'total_neto', 'margen_bruto']
        df_nuevo[cols_fact].to_sql(
            'fact_ventas', conn, schema='dm_ventas', if_exists='append', index=False
        )
        print(f"  → {len(df_nuevo)} filas cargadas en fact_ventas")
```

---

## Grupo 4: Gestión del proceso ETL

### Subsistema 24: Metadata del ETL y Auditoría

Cada ejecución del ETL debe registrar su metadata para poder monitorear, auditar y depurar problemas:

```sql
-- Tabla de control de ejecuciones ETL
CREATE TABLE etl_control.ejecucion_etl (
    id_ejecucion    BIGSERIAL    PRIMARY KEY,
    nombre_proceso  VARCHAR(100) NOT NULL,   -- 'ETL_DM_VENTAS'
    fecha_inicio    TIMESTAMP    NOT NULL,
    fecha_fin       TIMESTAMP,
    estado          VARCHAR(20)  NOT NULL DEFAULT 'EN_CURSO',
                                            -- 'EN_CURSO', 'EXITOSO', 'FALLIDO'
    filas_extraidas BIGINT,
    filas_cargadas  BIGINT,
    filas_rechazadas BIGINT,
    mensaje_error   TEXT,
    iniciado_por    VARCHAR(50)  NOT NULL DEFAULT 'scheduler'
);

-- Tabla de marcas de agua para extracción incremental
CREATE TABLE etl_control.marcas_agua (
    tabla_fuente      VARCHAR(100) PRIMARY KEY,
    ultima_extraccion TIMESTAMP    NOT NULL,
    ultima_ejecucion  BIGINT       REFERENCES etl_control.ejecucion_etl
);
```

### Subsistema 25: Manejo de errores y cola de rechazo

```sql
-- Cola de errores: registros rechazados con el motivo
CREATE TABLE etl_control.cola_errores (
    id_error        BIGSERIAL    PRIMARY KEY,
    id_ejecucion    BIGINT       NOT NULL REFERENCES etl_control.ejecucion_etl,
    tabla_origen    VARCHAR(100) NOT NULL,
    registro_raw    JSONB        NOT NULL,   -- el registro tal como llegó del fuente
    motivo_rechazo  VARCHAR(200) NOT NULL,
    campo_problema  VARCHAR(100),
    valor_problema  TEXT,
    timestamp_error TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resuelto        BOOLEAN      NOT NULL DEFAULT FALSE,
    resuelto_por    VARCHAR(50),
    resuelto_at     TIMESTAMP
);
```

---

## Orquestación del proceso ETL

El proceso ETL completo se orquesta mediante una herramienta de scheduling. Apache Airflow es el estándar open source de la industria.

```python
# DAG de Airflow para el ETL del Data Mart de Ventas
# pip install apache-airflow apache-airflow-providers-postgres

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.sql import SQLCheckOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'equipo-datos',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
    'email': ['datos@empresa.com'],
}

with DAG(
    dag_id='etl_dm_ventas',
    description='ETL diario del Data Mart de Ventas',
    schedule_interval='0 2 * * *',    # todos los días a las 2:00 AM
    start_date=datetime(2025, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=['data-mart', 'ventas'],
) as dag:

    t1_extraer_ventas = PythonOperator(
        task_id='extraer_ventas_del_erp',
        python_callable=extraer_incremental,
        op_kwargs={'tabla_fuente': 'ventas', 'conn': '...', 'ultima_carga': '{{ ds }}'},
    )

    t2_extraer_clientes = PythonOperator(
        task_id='extraer_clientes_del_crm',
        python_callable=extraer_completo,
        op_kwargs={'tabla_fuente': 'clientes'},
    )

    t3_limpiar = PythonOperator(
        task_id='limpiar_y_conformar',
        python_callable=limpiar_y_conformar,
    )

    t4_dim_cliente = PythonOperator(
        task_id='cargar_dim_cliente_scd2',
        python_callable=cargar_dimension_scd2,
        op_kwargs={'tabla_dim': 'dm_ventas.dim_cliente', 'natural_key': 'cliente_nk'},
    )

    t5_dim_producto = PythonOperator(
        task_id='cargar_dim_producto',
        python_callable=cargar_dimension_scd2,
        op_kwargs={'tabla_dim': 'dm_ventas.dim_producto', 'natural_key': 'producto_nk'},
    )

    t6_fact_ventas = PythonOperator(
        task_id='cargar_fact_ventas',
        python_callable=cargar_hechos,
    )

    t7_validar = SQLCheckOperator(
        task_id='validar_consistencia',
        sql="""
            SELECT
                CASE WHEN COUNT(*) > 0 THEN 1 ELSE 0 END
            FROM dm_ventas.fact_ventas f
            LEFT JOIN dm_ventas.dim_tiempo dt ON f.id_tiempo = dt.id_tiempo
            WHERE dt.id_tiempo IS NULL
              AND f.id_tiempo IN (
                  SELECT id_tiempo FROM dm_ventas.fact_ventas
                  WHERE id_tiempo::TEXT LIKE '2025%'
                  ORDER BY id_tiempo DESC LIMIT 1000
              )
        """,
        conn_id='postgres_dwh',
    )

    # Dependencias
    [t1_extraer_ventas, t2_extraer_clientes] >> t3_limpiar
    t3_limpiar >> [t4_dim_cliente, t5_dim_producto]
    [t4_dim_cliente, t5_dim_producto] >> t6_fact_ventas
    t6_fact_ventas >> t7_validar
```

---

## Los principios de idempotencia en el ETL

Un ETL idempotente puede ejecutarse múltiples veces con el mismo resultado. Si el proceso falla a la mitad y se reinicia, no duplica datos ni produce inconsistencias.

**Técnicas para garantizar idempotencia:**

1. **Truncate + Insert:** limpiar la tabla antes de cargar. Simple pero borra datos hasta que la carga nueva termina.
2. **Upsert (INSERT ON CONFLICT):** insertar registros nuevos y actualizar los existentes.
3. **Partición por período:** cargar solo el período del día actual en una partición nueva.
4. **Tabla de control de carga:** registrar qué registros ya fueron procesados.

```sql
-- Carga idempotente con UPSERT (PostgreSQL)
INSERT INTO dm_ventas.fact_ventas (
    id_tiempo, id_cliente, id_producto, numero_factura, linea,
    cantidad, precio_unit, total_neto
)
SELECT
    ... -- datos calculados
FROM staging.s_ventas_procesado
ON CONFLICT (numero_factura, linea)
DO UPDATE SET
    -- Si el registro ya existía, actualizar métricas (por correcciones del fuente)
    total_neto  = EXCLUDED.total_neto,
    margen_bruto = EXCLUDED.margen_bruto;
```

---

## Entregables de la Etapa 4

1. ✅ **Diseño del Staging Area** con todas las tablas y su estructura.
2. ✅ **Código ETL implementado** y probado para cada fuente y dimensión.
3. ✅ **Manejo de SCD** implementado y validado con datos reales.
4. ✅ **Tablas de control ETL** (ejecuciones, marcas de agua, cola de errores).
5. ✅ **DAG de orquestación** (Airflow o equivalente) con todas las dependencias.
6. ✅ **Prueba de carga inicial** con datos históricos completos.
7. ✅ **Prueba de carga incremental** con datos del día siguiente.
8. ✅ **Validaciones de consistencia** post-carga automatizadas.

---

## ETL Moderno: ELT y la Transformación con dbt

En las arquitecturas modernas cloud, el patrón está evolucionando de **ETL** a **ELT** (Extract, Load, Transform): los datos se extraen y cargan "crudos" al data warehouse, y las transformaciones se ejecutan dentro del motor de BD usando SQL.

### ¿Por qué ELT?

```
ETL Tradicional:                         ELT Moderno:
──────────────────                       ──────────────────
Fuente → [Servidor ETL] → DWH           Fuente → DWH → [Transformar en DWH]
          ↑                                              ↑
     La transformación                             La transformación
     se ejecuta en un                              se ejecuta dentro
     servidor separado                             del motor cloud
     (costoso, cuello                              (escalable, usa
      de botella)                                   toda la potencia
                                                    del motor columnar)
```

**Ventajas del ELT:**
- Aprovecha la potencia del motor cloud (Snowflake, BigQuery, Redshift) para las transformaciones.
- No requiere un servidor de procesamiento intermedio.
- Las transformaciones quedan definidas en SQL, que es más fácil de auditar y versionar.
- Compatibilidad nativa con herramientas como **dbt** (data build tool).

### dbt: Transformaciones como código

**dbt** es la herramienta estándar de la industria para la "T" del ELT. Define transformaciones como modelos SQL versionados en Git:

```sql
-- models/staging/stg_ventas.sql
-- Modelo de staging: limpieza y tipado de datos crudos
{{ config(materialized='view') }}

SELECT
    factura_id::VARCHAR(30)                    AS numero_factura,
    linea::SMALLINT                            AS linea,
    TO_DATE(fecha, 'DD/MM/YYYY')               AS fecha,
    UPPER(TRIM(cliente_id))                    AS cliente_nk,
    UPPER(TRIM(producto_id))                   AS producto_nk,
    REPLACE(cantidad, ',', '.')::NUMERIC(10,3) AS cantidad,
    REPLACE(precio, ',', '.')::NUMERIC(12,2)   AS precio_unitario,
    COALESCE(REPLACE(descuento, ',', '.')::NUMERIC(5,4), 0) AS descuento_pct
FROM {{ source('erp', 'ventas_raw') }}
WHERE fecha IS NOT NULL
```

```sql
-- models/marts/dm_ventas/fact_ventas.sql
-- Modelo de hechos: unión con dimensiones y cálculo de métricas
{{ config(
    materialized='incremental',
    unique_key=['numero_factura', 'linea'],
    partition_by={'field': 'fecha', 'data_type': 'date', 'granularity': 'month'}
) }}

SELECT
    dt.id_tiempo,
    dc.id_cliente,
    dp.id_producto,
    s.numero_factura,
    s.linea,
    s.cantidad,
    s.precio_unitario,
    s.descuento_pct,
    s.cantidad * s.precio_unitario * (1 - s.descuento_pct) AS total_neto
FROM {{ ref('stg_ventas') }} s
JOIN {{ ref('dim_tiempo') }}   dt ON s.fecha      = dt.fecha
JOIN {{ ref('dim_cliente') }}  dc ON s.cliente_nk  = dc.cliente_nk AND dc.is_current = TRUE
JOIN {{ ref('dim_producto') }} dp ON s.producto_nk = dp.producto_nk AND dp.is_current = TRUE

{% if is_incremental() %}
WHERE s.fecha > (SELECT MAX(dt2.fecha) FROM {{ this }} f JOIN {{ ref('dim_tiempo') }} dt2 ON f.id_tiempo = dt2.id_tiempo)
{% endif %}
```

```yaml
# models/marts/dm_ventas/schema.yml
# Tests de calidad integrados en dbt
version: 2
models:
  - name: fact_ventas
    description: "Tabla de hechos de ventas. Granularidad: línea de factura."
    columns:
      - name: numero_factura
        tests:
          - not_null
      - name: id_cliente
        tests:
          - not_null
          - relationships:
              to: ref('dim_cliente')
              field: id_cliente
      - name: total_neto
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: ">= 0"
```

### Comparación: ETL tradicional vs. ELT con dbt

| Aspecto | ETL tradicional (Python/Airflow) | ELT moderno (dbt + Airflow) |
|---|---|---|
| **Transformaciones** | Python, pandas, PySpark | SQL dentro del DWH |
| **Escalabilidad** | Limitada por el servidor ETL | Escalabilidad del motor cloud |
| **Versionado** | Código en Git (scripts sueltos) | Modelos SQL + tests en Git |
| **Tests de calidad** | Manuales o con scripts propios | Integrados en dbt (declarativos) |
| **Documentación** | Manual | Auto-generada por dbt |
| **Linaje** | Manual | Automático (dbt genera el DAG) |
| **Ideal para** | Transformaciones complejas (ML, APIs) | Transformaciones SQL estándar |

---

## Testing del ETL: Estrategias de Validación

El ETL debe incluir pruebas automatizadas que se ejecutan en cada carga:

### Tests de integridad referencial

```sql
-- Verificar que no hay hechos sin dimensión (FK huérfanas)
SELECT 'fact_ventas → dim_cliente' AS test,
       COUNT(*) AS filas_huerfanas
FROM dm_ventas.fact_ventas f
LEFT JOIN dm_ventas.dim_cliente dc ON f.id_cliente = dc.id_cliente
WHERE dc.id_cliente IS NULL

UNION ALL

SELECT 'fact_ventas → dim_producto',
       COUNT(*)
FROM dm_ventas.fact_ventas f
LEFT JOIN dm_ventas.dim_producto dp ON f.id_producto = dp.id_producto
WHERE dp.id_producto IS NULL

UNION ALL

SELECT 'fact_ventas → dim_tiempo',
       COUNT(*)
FROM dm_ventas.fact_ventas f
LEFT JOIN dm_ventas.dim_tiempo dt ON f.id_tiempo = dt.id_tiempo
WHERE dt.id_tiempo IS NULL;
-- Resultado esperado: 0 en todas las filas
```

### Tests de reconciliación (totales DWH vs. fuente)

```sql
-- Comparar totales del DWH contra el sistema fuente
-- Esto se ejecuta cada noche después de la carga

WITH dwh AS (
    SELECT SUM(total_neto) AS total_dwh,
           COUNT(DISTINCT numero_factura) AS facturas_dwh
    FROM dm_ventas.fact_ventas
    WHERE id_tiempo BETWEEN 20250401 AND 20250430
),
fuente AS (
    SELECT SUM(total_neto) AS total_fuente,
           COUNT(DISTINCT numero_factura) AS facturas_fuente
    FROM erp_replica.ventas
    WHERE fecha BETWEEN '2025-04-01' AND '2025-04-30'
)
SELECT
    dwh.total_dwh,
    fuente.total_fuente,
    ABS(dwh.total_dwh - fuente.total_fuente) AS diferencia_absoluta,
    ROUND(100.0 * ABS(dwh.total_dwh - fuente.total_fuente) / fuente.total_fuente, 4) AS diferencia_pct,
    CASE WHEN ABS(dwh.total_dwh - fuente.total_fuente) < 0.01
         THEN 'OK' ELSE 'ALERTA' END AS estado
FROM dwh, fuente;
```

### Tests de unicidad y completitud

```sql
-- Verificar que no hay duplicados en la fact table
SELECT numero_factura, linea, COUNT(*) AS duplicados
FROM dm_ventas.fact_ventas
GROUP BY numero_factura, linea
HAVING COUNT(*) > 1;
-- Resultado esperado: 0 filas

-- Verificar que no hay huecos en dim_tiempo
SELECT
    COUNT(*) AS dias_existentes,
    (MAX(fecha) - MIN(fecha) + 1) AS dias_esperados,
    CASE WHEN COUNT(*) = (MAX(fecha) - MIN(fecha) + 1)
         THEN 'OK' ELSE 'HUECOS DETECTADOS' END AS estado
FROM dm_ventas.dim_tiempo;
```

---

## Patrones de Carga: Late-Arriving Facts y Dimensions

### Late-Arriving Facts (Hechos tardíos)

Cuando una transacción llega al sistema fuente con fecha anterior a la última carga. Ejemplo: una factura del 15/03 se registra en el ERP el 18/03, pero el ETL ya procesó hasta el 17/03.

**Solución:** El ETL incremental debe mirar un "ventana de seguridad" más amplia que solo el día anterior:

```sql
-- En vez de extraer solo fecha > ultima_carga,
-- extraer con un margen de seguridad de 3 días
WHERE fecha_modificacion > (ultima_carga - INTERVAL '3 days')
```

Combinado con UPSERT, los registros que ya existen se actualizan y los nuevos se insertan.

### Late-Arriving Dimensions (Dimensiones tardías)

Cuando llega un hecho que referencia una dimensión que aún no existe en el DWH. Ejemplo: se registra una venta del cliente "CLI-9999" pero ese cliente aún no se cargó en `dim_cliente`.

**Solución de Kimball:** Insertar un registro "placeholder" en la dimensión con datos mínimos y una marca de "inferido":

```sql
INSERT INTO dm_ventas.dim_cliente (cliente_nk, razon_social, segmento, ciudad, is_current, is_inferred)
VALUES ('CLI-9999', 'PENDIENTE DE CARGA', 'Desconocido', 'Desconocida', TRUE, TRUE);

-- Cuando el ETL cargue los datos reales del cliente, actualiza el placeholder:
UPDATE dm_ventas.dim_cliente
SET razon_social = 'García e Hijos S.A.',
    segmento     = 'Premium',
    ciudad       = 'Córdoba',
    is_inferred  = FALSE
WHERE cliente_nk = 'CLI-9999' AND is_inferred = TRUE;
```

---

## Lecturas recomendadas

- **Kimball, R. & Caserta, J.** — *The Data Warehouse ETL Toolkit*. Wiley. (El libro más completo sobre ETL con la metodología Kimball. Describe los 34 subsistemas en detalle.)
- **Apache Airflow** — Documentación oficial: [airflow.apache.org](https://airflow.apache.org/docs/)
- **dbt (data build tool)** — Para transformaciones ETL modernas con SQL versionado: [docs.getdbt.com](https://docs.getdbt.com)
- **Debezium** — CDC open source: [debezium.io](https://debezium.io/documentation/)
- **Reis, J. & Housley, M.** — *Fundamentals of Data Engineering*. O'Reilly. Capítulos 7-8. (Perspectiva moderna de ingesta y transformación).
- **Maxime Beauchemin** — Creador de Apache Airflow. Blog: [medium.com/@maximebeauchemin](https://medium.com/@maximebeauchemin) (Artículos sobre orquestación y mejores prácticas de ETL).
- **Debezium** — Para CDC (Change Data Capture): [debezium.io](https://debezium.io/documentation/)
