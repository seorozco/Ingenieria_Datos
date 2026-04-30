# Clase 06 — Carga de Datos (Load) y Orquestación

> **Asignatura:** Ingeniería de Datos  
> **Docente:** Ing. Sergio Orozco  
> **Unidad:** II — Orígenes de Datos y Proceso ETL

---

## Objetivos de la Clase

Al finalizar esta clase, el alumno será capaz de:

- Explicar y aplicar las tres estrategias de carga: **Full Overwrite**, **Append** y **Upsert**.
- Implementar la carga a bases de datos PostgreSQL con `SQLAlchemy` y `pandas`.
- Guardar datos en formatos de Data Lake (Parquet, CSV particionado).
- Entender el concepto de **idempotencia** en pipelines de datos.
- Describir qué es **Apache Airflow**, para qué sirve y cómo se estructura un **DAG**.

---

## 1. ¿Qué es la Carga?

La carga (Load) es la **etapa final del pipeline ETL**: persistir los datos transformados en el sistema destino de forma confiable, eficiente e idempotente.

```
┌────────────────────────────────────────────────────────────────────┐
│                     ETAPA DE CARGA                                 │
│                                                                    │
│  DATOS TRANSFORMADOS               SISTEMA DESTINO                 │
│  (DataFrame pandas)                                                │
│                                                                    │
│  ┌─────────────────┐               ┌──────────────────────────┐   │
│  │                 │  ─────────►   │  PostgreSQL / DWH        │   │
│  │  df_limpio      │               │  Parquet (Data Lake)     │   │
│  │                 │  ─────────►   │  BigQuery / Redshift     │   │
│  └─────────────────┘               │  CSV (staging externo)   │   │
│                                    └──────────────────────────┘   │
│                                                                    │
│  La estrategia de carga elegida determina si los datos            │
│  quedan correctos cuando el pipeline re-ejecuta.                  │
└────────────────────────────────────────────────────────────────────┘
```

### Idempotencia — El principio más importante

Un pipeline es **idempotente** si puede ejecutarse múltiples veces con el mismo resultado final, sin duplicar datos ni generar inconsistencias.

> **¿Por qué importa?** En producción, los pipelines fallan. Pueden caerse a mitad de una carga, necesitar re-ejecutarse por un bug, o correr por accidente dos veces. Un pipeline idempotente sobrevive estos escenarios sin corromper los datos.

```
Pipeline NO idempotente:
  Ejecución 1 → 100 filas en la tabla ✅
  Falla a mitad → 50 filas en la tabla ❌ (incompleto)
  Re-ejecución → 150 filas en la tabla ❌ (duplicados)

Pipeline IDEMPOTENTE:
  Ejecución 1 → 100 filas en la tabla ✅
  Falla a mitad → estado previo restaurado ✅
  Re-ejecución → 100 filas en la tabla ✅ (mismo resultado)
```

---

## 2. Las Tres Estrategias de Carga

### 2.1 Full Overwrite (Reemplazo Total)

Se **borra toda la tabla destino** y se vuelve a insertar completa.

```
Estado anterior:  [fila1, fila2, fila3, fila4]
Operación:         TRUNCATE → INSERT ALL
Estado posterior: [fila1_new, fila2_new, fila3_new, fila4_new, fila5_new]
```

**¿Cuándo usarlo?**
- Tablas pequeñas (dimensiones estáticas, catálogos de referencia).
- Cuando la idempotencia es crítica y el volumen lo permite.
- Cuando es más simple verificar que la tabla completa sea correcta.

**Riesgo:** Si el pipeline falla a mitad del proceso, la tabla queda vacía o incompleta. Se mitiga usando **transacciones** (TRUNCATE + INSERT dentro de un mismo BEGIN/COMMIT).

```sql
-- Implementación SQL segura con transacción
BEGIN;
  TRUNCATE TABLE dw.dim_productos;
  INSERT INTO dw.dim_productos
  SELECT * FROM staging.productos_transformados;
COMMIT;
-- Si falla entre TRUNCATE e INSERT, el ROLLBACK restaura el estado anterior
```

### 2.2 Append (Inserción Incremental)

Se insertan **solo los registros nuevos** sin tocar los existentes.

```
Estado anterior:  [fila1, fila2, fila3]
Operación:         INSERT nuevos
Estado posterior: [fila1, fila2, fila3, fila4, fila5]
```

**¿Cuándo usarlo?**
- Tablas de hechos de "solo escritura" (logs, eventos, transacciones que nunca se modifican).
- Cuando los datos son inmutables por naturaleza (registros de auditoría, telemetría de sensores).

**Riesgo:** Si el pipeline corre dos veces, los datos se duplican. Para evitarlo, se deben implementar controles de idempotencia externos (verificar que los IDs no existan antes de insertar).

### 2.3 Upsert (Actualizar o Insertar)

Si el registro **ya existe** en el destino → se actualiza.  
Si el registro **no existe** → se inserta.

```
Estado anterior:  [fila1{v1}, fila2{v1}, fila3{v1}]
Operación:         UPSERT con [fila2{v2}, fila4{nuevo}]
Estado posterior: [fila1{v1}, fila2{v2}, fila3{v1}, fila4{nuevo}]
                               ↑ actualizada        ↑ insertada nueva
```

**¿Cuándo usarlo?** Casi siempre. Es la estrategia más segura y robusta:
- Dimensiones que cambian (clientes que actualizan su dirección).
- Datos que pueden llegar repetidos desde la fuente.
- Pipelines que necesitan ser re-ejecutables sin consecuencias.

---

## 3. Implementación de Carga con Python y SQLAlchemy

```bash
pip install sqlalchemy psycopg2-binary pandas pyarrow
```

### 3.1 Full Overwrite con pandas `to_sql`

```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://data_engineer:contraseña@localhost:5432/dw_ventas"
)

df_dim_productos = pd.DataFrame({
    "id_producto": [101, 102, 103],
    "nombre":      ["Laptop Básica", "Monitor 24\"", "Teclado Mecánico"],
    "categoria":   ["Computación", "Periféricos", "Periféricos"],
    "precio_lista":[85000.0, 32000.0, 8500.0],
})

# if_exists='replace' → DROP + CREATE + INSERT (Full Overwrite)
# ⚠️ No usa transacción automática — combinar con BEGIN/COMMIT para seguridad
df_dim_productos.to_sql(
    name="dim_productos",
    con=engine,
    schema="dw",
    if_exists="replace",  # 'append' para solo agregar
    index=False,
    method="multi",       # Inserta en lotes para mejor rendimiento
    chunksize=1000,
)
print("✅ Dimensión de productos cargada exitosamente.")
```

### 3.2 Append: solo insertar registros nuevos

```python
import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql+psycopg2://data_engineer:contraseña@localhost:5432/dw_ventas"
)

# Nuevas ventas a agregar
df_ventas_nuevas = pd.DataFrame({
    "id_venta":    [1001, 1002, 1003],
    "fecha":       pd.to_datetime(["2025-03-01", "2025-03-02", "2025-03-03"]),
    "total":       [1500.0, 2300.0, 850.0],
    "id_cliente":  [101, 102, 103],
    "id_producto": [201, 202, 203],
})

# Verificar si ya existen los IDs para evitar duplicados (idempotencia manual)
with engine.connect() as conn:
    ids_existentes = pd.read_sql(
        text("SELECT id_venta FROM dw.fact_ventas"),
        conn
    )["id_venta"].tolist()

df_a_insertar = df_ventas_nuevas[~df_ventas_nuevas["id_venta"].isin(ids_existentes)]

if len(df_a_insertar) > 0:
    df_a_insertar.to_sql(
        name="fact_ventas",
        con=engine,
        schema="dw",
        if_exists="append",
        index=False,
        method="multi",
    )
    print(f"✅ {len(df_a_insertar)} ventas nuevas insertadas.")
else:
    print("ℹ️ No hay ventas nuevas para insertar.")
```

### 3.3 Upsert con PostgreSQL INSERT ON CONFLICT

```python
import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql+psycopg2://data_engineer:contraseña@localhost:5432/dw_ventas"
)

df_clientes = pd.DataFrame({
    "id_cliente":  [101, 102, 103],
    "nombre":      ["Ana García", "Juan López", "María Torres"],
    "email":       ["ana@test.com", "juan@test.com", "maria@test.com"],
    "ciudad":      ["Buenos Aires", "Córdoba", "Rosario"],
    "updated_at":  pd.to_datetime(["2025-03-01", "2025-03-02", "2025-03-01"]),
})

# Insertar en tabla temporal y luego hacer UPSERT a la tabla destino
with engine.begin() as conn:
    # Cargar a tabla temporal
    df_clientes.to_sql(
        name="tmp_clientes",
        con=conn,
        schema="staging",
        if_exists="replace",
        index=False,
    )

    # UPSERT: INSERT con ON CONFLICT DO UPDATE
    conn.execute(text("""
        INSERT INTO dw.dim_clientes (id_cliente, nombre, email, ciudad, updated_at)
        SELECT id_cliente, nombre, email, ciudad, updated_at
        FROM staging.tmp_clientes
        ON CONFLICT (id_cliente)
        DO UPDATE SET
            nombre     = EXCLUDED.nombre,
            email      = EXCLUDED.email,
            ciudad     = EXCLUDED.ciudad,
            updated_at = EXCLUDED.updated_at;
    """))

print("✅ Clientes actualizados/insertados con UPSERT.")
```

---

## 4. Carga a Formatos Data Lake

Además de bases de datos, es muy común cargar los datos en formatos de archivo para Data Lakes almacenados en cloud (S3, GCS, Azure Blob).

### 4.1 Guardar en Parquet (el estándar del ecosistema)

```python
import pandas as pd
from pathlib import Path
from datetime import date

df_ventas = pd.DataFrame({
    "id_venta":   [1001, 1002, 1003],
    "fecha":      pd.to_datetime(["2025-03-01", "2025-03-02", "2025-03-03"]),
    "total":      [1500.0, 2300.0, 850.0],
    "id_cliente": [101, 102, 103],
})

# Particionado por fecha: estructura de carpetas estándar en Data Lakes
# La partición permite leer solo los datos del período necesario
anio = "2025"
mes  = "03"
ruta = Path(f"data/silver/ventas/anio={anio}/mes={mes}")
ruta.mkdir(parents=True, exist_ok=True)

ruta_archivo = ruta / f"ventas_{date.today().strftime('%Y%m%d')}.parquet"
df_ventas.to_parquet(ruta_archivo, index=False, compression="snappy")

print(f"✅ Guardado en: {ruta_archivo}")
print(f"   Tamaño: {ruta_archivo.stat().st_size / 1024:.1f} KB")
```

**Estructura resultante en el Data Lake:**
```
data/
└── silver/
    └── ventas/
        ├── anio=2025/
        │   ├── mes=01/
        │   │   └── ventas_20250201.parquet
        │   ├── mes=02/
        │   │   └── ventas_20250301.parquet
        │   └── mes=03/
        │       └── ventas_20250401.parquet
```

---

## 5. Apache Airflow: Orquestación de Pipelines

### 5.1 ¿Para qué sirve un orquestador?

Cuando un pipeline crece más allá de un solo script, aparecen nuevos desafíos:
- Las tareas tienen **dependencias**: la transformación no puede correr hasta que termine la extracción.
- Las tareas deben ejecutarse **en momentos específicos** (cada hora, a las 6 AM, todos los lunes).
- Hay que **monitorear** qué tareas fallaron y cuáles completaron exitosamente.
- Ante un fallo, hay que poder **re-ejecutar solo las tareas fallidas** sin repetir las exitosas.

**Apache Airflow** resuelve todos estos problemas. Es el orquestador de pipelines más usado en la industria.

### 5.2 Conceptos fundamentales de Airflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                   CONCEPTOS DE AIRFLOW                              │
│                                                                     │
│  DAG (Directed Acyclic Graph)                                       │
│  → Es el "plano" del pipeline. Define las tareas y sus relaciones. │
│  → "Directed" = las tareas tienen dirección (una depende de otra)  │
│  → "Acyclic" = no hay ciclos (A→B→C, nunca C→A)                   │
│                                                                     │
│  TASK (Tarea)                                                       │
│  → Una unidad de trabajo dentro del DAG.                           │
│  → Puede ser: ejecutar un script Python, correr una query SQL,     │
│    copiar un archivo, llamar una API, enviar un email, etc.        │
│                                                                     │
│  OPERATOR (Operador)                                                │
│  → Plantilla para definir un tipo de tarea:                        │
│    PythonOperator → ejecuta una función Python                     │
│    BashOperator   → ejecuta un comando bash                        │
│    PostgresOperator → ejecuta SQL en PostgreSQL                    │
│    HttpOperator   → hace llamadas HTTP                             │
│                                                                     │
│  SCHEDULE (Programación)                                            │
│  → Cuándo debe correr el DAG: "@daily", "@hourly", cron expression │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.3 Ejemplo de DAG para nuestro pipeline ETL

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# ── Funciones del pipeline ──────────────────────────────────────────

def extraer_ventas():
    """Extrae ventas de PostgreSQL y las guarda en staging."""
    import psycopg2
    import pandas as pd
    from pathlib import Path
    from datetime import date

    conn = psycopg2.connect(host="localhost", dbname="ventas_db",
                            user="de", password="pass")
    df = pd.read_sql_query("SELECT * FROM ventas WHERE updated_at > NOW() - INTERVAL '1 day'", conn)
    conn.close()

    staging_path = Path("staging")
    staging_path.mkdir(exist_ok=True)
    df.to_csv(staging_path / f"ventas_{date.today()}.csv", index=False)
    print(f"Extraídos {len(df)} registros.")


def transformar_ventas():
    """Limpia y transforma los datos del staging."""
    import pandas as pd
    from pathlib import Path
    from datetime import date

    df = pd.read_csv(Path("staging") / f"ventas_{date.today()}.csv")

    # Transformaciones básicas
    df = df.drop_duplicates()
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df = df.dropna(subset=["id_venta", "fecha"])
    df["moneda"] = df["moneda"].str.upper().str.strip()

    output_path = Path("output")
    output_path.mkdir(exist_ok=True)
    df.to_parquet(output_path / f"ventas_{date.today()}.parquet", index=False)
    print(f"Transformados {len(df)} registros.")


def cargar_ventas():
    """Carga los datos transformados al Data Warehouse."""
    import pandas as pd
    from sqlalchemy import create_engine
    from pathlib import Path
    from datetime import date

    df = pd.read_parquet(Path("output") / f"ventas_{date.today()}.parquet")
    engine = create_engine("postgresql+psycopg2://de:pass@localhost:5432/dw")
    df.to_sql("fact_ventas", con=engine, schema="dw", if_exists="append",
              index=False, method="multi")
    print(f"Cargados {len(df)} registros al DWH.")


# ── Definición del DAG ───────────────────────────────────────────────

default_args = {
    "owner": "ingenieria_de_datos",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": True,
    "email": ["sergio.orozco@universidad.edu.ar"],
}

with DAG(
    dag_id="pipeline_ventas_diario",
    description="Pipeline ETL diario de ventas",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval="0 6 * * *",   # Todos los días a las 6:00 AM (cron)
    catchup=False,                   # No re-ejecutar fechas pasadas
    tags=["ventas", "etl", "diario"],
) as dag:

    # Definir las tareas
    tarea_extraccion    = PythonOperator(task_id="extraer_ventas",    python_callable=extraer_ventas)
    tarea_transformacion= PythonOperator(task_id="transformar_ventas",python_callable=transformar_ventas)
    tarea_carga         = PythonOperator(task_id="cargar_ventas",     python_callable=cargar_ventas)

    # Definir las dependencias (orden de ejecución)
    tarea_extraccion >> tarea_transformacion >> tarea_carga
    # Airflow solo ejecuta la siguiente tarea si la anterior completó exitosamente
```

**Diagrama del DAG:**

```
Todos los días a las 6:00 AM:

  [extraer_ventas]  ──►  [transformar_ventas]  ──►  [cargar_ventas]
       ✅                        ✅                        ✅
  (si falla aquí,         (si falla, Airflow       (si falla, reintenta
   las siguientes          reintenta 2 veces)        2 veces y notifica)
   no se ejecutan)
```

### 5.4 Sintaxis de programación con cron

El schedule de Airflow usa expresiones **cron** para definir la frecuencia de ejecución:

```
┌────────────────── minutos (0-59)
│  ┌─────────────── horas (0-23)
│  │  ┌──────────── día del mes (1-31)
│  │  │  ┌───────── mes (1-12)
│  │  │  │  ┌────── día de la semana (0=domingo, 6=sábado)
│  │  │  │  │
*  *  *  *  *

Ejemplos:
  "0 6 * * *"    → Todos los días a las 6:00 AM
  "0 */4 * * *"  → Cada 4 horas
  "0 8 * * 1"    → Lunes a las 8:00 AM
  "30 22 * * 5"  → Viernes a las 22:30
  "0 0 1 * *"    → El primer día de cada mes a la medianoche
  "@daily"       → Equivalente a "0 0 * * *"
  "@hourly"      → Equivalente a "0 * * * *"
```

---

## 6. Resumen del Pipeline ETL Completo

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PIPELINE ETL DE PRINCIPIO A FIN                      │
│                                                                          │
│                        AIRFLOW (orquestador)                             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                                                                   │   │
│  │  EXTRACT               TRANSFORM              LOAD               │   │
│  │  ─────────────         ──────────────         ─────────────────  │   │
│  │  psycopg2         ──►  pandas pipeline   ──►  to_sql (Upsert)   │   │
│  │  requests              limpieza               Parquet (Lake)     │   │
│  │  BeautifulSoup         joins                  BigQuery           │   │
│  │  SQLAlchemy            agregaciones           Snowflake          │   │
│  │                        normalización                             │   │
│  │                        derivaciones                              │   │
│  │                                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ESTRATEGIAS DE CARGA:                                                  │
│  Full Overwrite → catálogos y dimensiones estáticas                     │
│  Append         → eventos y logs inmutables                             │
│  Upsert         → datos que pueden cambiar (clientes, productos)        │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Resumen de la Clase

| Concepto | Definición en una frase |
|---|---|
| **Idempotencia** | Un pipeline que se puede re-ejecutar N veces con el mismo resultado |
| **Full Overwrite** | Borrar y recargar completo; ideal para tablas pequeñas o estáticas |
| **Append** | Agregar solo registros nuevos; ideal para eventos inmutables |
| **Upsert** | Actualizar si existe, insertar si no; la estrategia más robusta |
| **Apache Airflow** | Orquestador de pipelines: scheduling, dependencias, monitoreo |
| **DAG** | El "plano" del pipeline: define tareas y su orden de ejecución |
| **Parquet particionado** | Formato columnar organizado por fecha para Data Lakes eficientes |

---

> 💡 **Para la próxima unidad:** Ahora sabemos construir pipelines ETL de principio a fin. En la **Unidad III** vamos a profundizar en un tema crítico: ¿qué pasa cuando los datos que extrajimos son incorrectos, incompletos o inconsistentes? Vamos a aprender a medir, monitorear y garantizar la **calidad del dato**.
