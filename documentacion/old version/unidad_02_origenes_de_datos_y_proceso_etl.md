# Unidad II — Orígenes de Datos y Proceso ETL

> **Asignatura:** Ingeniería de Datos  
> **Docente:** Ing. Sergio Orozco  
> **Clases:** 3, 4, 5 y 6

---

## Objetivos de la Unidad

Al finalizar esta unidad, el alumno será capaz de:

- Clasificar los distintos tipos de bases de datos según su modelo de datos y su carga de trabajo.
- Seleccionar la base de datos adecuada según el caso de uso y sus patrones de acceso.
- Diferenciar los enfoques OLTP y OLAP y explicar cuándo aplicar cada uno.
- Implementar estrategias de extracción **Full Load** e **Incremental** usando Python.
- Consumir datos desde **APIs REST** y realizar **web scraping** ético con librerías Python.
- Extraer datos desde bases de datos relacionales con **psycopg2** y **SQLAlchemy**.
- Aplicar transformaciones de datos complejas utilizando **pandas**: limpieza, normalización, joins, aggregaciones y pivots.
- Comprender las diferencias entre el paradigma **ETL** y **ELT** y elegir el más adecuado según el contexto.
- Implementar las tres estrategias de carga (Full Overwrite, Append, Upsert) con Python y SQL.
- Describir el rol de **Apache Airflow** como orquestador de pipelines y la estructura de un DAG.

---

## Clase 03 — Tipos de Bases de Datos

### 3.1 ¿Por qué existen tantos tipos de bases de datos?

Durante décadas, las bases de datos relacionales (SQL) fueron la solución casi universal para almacenar datos. Sin embargo, a medida que los sistemas crecieron en escala, diversidad de datos y patrones de acceso, quedó claro que **una sola tecnología no puede ser óptima para todos los casos**.

Un sistema de e-commerce, por ejemplo, necesita:
- Registrar transacciones con consistencia absoluta (SQL).
- Almacenar sesiones de usuario con latencia de milisegundos (clave-valor).
- Guardar el catálogo de productos con campos variables (documental).
- Detectar fraude analizando relaciones entre cuentas (grafo).

Cada necesidad tiene su mejor herramienta. El Data Engineer debe conocerlas todas para elegir sabiamente.

---

### 3.2 Clasificación por Modelo de Datos

#### Bases de Datos Relacionales (SQL)

Son el tipo más maduro y extendido. Organizan los datos en **tablas con filas y columnas** y utilizan **SQL** como lenguaje de consulta estándar. La relación entre tablas se establece mediante **claves foráneas**.

**Propiedades ACID** (garantía de integridad transaccional):
- **Atomicidad:** una transacción se ejecuta completa o no se ejecuta.
- **Consistencia:** los datos siempre pasan de un estado válido a otro.
- **Isolación:** las transacciones concurrentes no se interfieren entre sí.
- **Durabilidad:** los datos confirmados persisten aunque el sistema falle.

**Motores más utilizados:**

| Motor | Uso típico | Característica destacada |
|---|---|---|
| **PostgreSQL** | Analítica, backend, ETL | Open source, extensible, soporte JSON nativo |
| **MySQL / MariaDB** | Aplicaciones web | Velocidad en lectura, amplio soporte |
| **SQL Server** | Entornos corporativos Microsoft | Integración con el stack Microsoft |
| **Oracle DB** | Banca y ERP enterprise | Robustez y soporte comercial |

**Cuándo elegirlas:** cuando la consistencia es crítica (transacciones financieras, inventario, RR.HH.), el esquema es estable y las relaciones entre entidades son importantes.

---

#### Bases de Datos NoSQL Clave-Valor

Almacenan los datos como pares **clave → valor**, sin esquema. La clave es el identificador único y el valor puede ser cualquier cosa: un número, un JSON, una imagen binaria.

**Ejemplos:** Redis, Amazon DynamoDB, Memcached.

**Cuándo elegirlas:**
- Caché de aplicaciones (guardar el resultado de consultas costosas por N segundos).
- Sesiones de usuario en sistemas web.
- Colas de mensajes simples.
- Configuraciones y feature flags en tiempo real.

> **Ejemplo:** Redis almacena la sesión de cada usuario logueado. La clave es el token de sesión, el valor es el JSON con los datos del usuario. La consulta tarda microsegundos porque todo está en memoria.

---

#### Bases de Datos NoSQL Documentales

Almacenan los datos como **documentos** (generalmente JSON o BSON) sin esquema fijo. Cada documento puede tener campos distintos al resto de la colección.

**Ejemplos:** MongoDB, CouchDB, Amazon DocumentDB.

**Cuándo elegirlas:**
- APIs y microservicios donde los objetos tienen estructura variable.
- Catálogos de productos con atributos heterogéneos (un libro tiene autor; un electrónico tiene voltaje).
- Prototipado rápido donde el esquema aún no es estable.

> **Ejemplo:** En un e-commerce, cada producto es un documento. El libro `{título, autor, editorial, ISBN}` y el televisor `{marca, pulgadas, resolución, HDMI}` tienen atributos completamente distintos, pero conviven en la misma colección sin problema.

---

#### Bases de Datos NoSQL Columnares

En lugar de almacenar datos por fila (como SQL), almacenan los datos **por columna**. Esto permite leer solo las columnas necesarias para una consulta analítica, ignorando las demás.

**Ejemplos:** Apache Cassandra, HBase, ScyllaDB.

**Cuándo elegirlas:**
- Escritura masiva y distribuida a escala global.
- Series temporales (métricas, logs, sensores IoT).
- Sistemas donde la disponibilidad importa más que la consistencia estricta.

> **Ejemplo:** Netflix usa Cassandra para almacenar el historial de reproducciones de millones de usuarios simultáneamente. La escritura es extremadamente rápida porque está distribuida en miles de nodos.

---

#### Bases de Datos de Grafos

Almacenan los datos como **nodos** (entidades) y **aristas** (relaciones), con propiedades en ambos. Son extremadamente eficientes cuando las consultas navegan por relaciones complejas.

**Ejemplos:** Neo4j, Amazon Neptune, ArangoDB.

**Cuándo elegirlas:**
- Redes sociales (amigos de amigos, seguidores).
- Detección de fraude (cuentas conectadas a través de IPs, dispositivos o beneficiarios).
- Sistemas de recomendación ("usuarios que compraron X también compraron Y").
- Grafos de conocimiento y ontologías.

> **Ejemplo:** Un banco detecta fraude al notar que 50 cuentas distintas comparten el mismo número de teléfono y han realizado transferencias cruzadas entre sí en las últimas 48 horas. En SQL, esta consulta requirería múltiples JOINs complejos. En Neo4j, es una sola traversal de grafo.

---

### 3.3 Clasificación por Carga de Trabajo: OLTP vs. OLAP

Esta distinción es fundamental en arquitectura de datos y determina cómo se diseña y optimiza una base de datos.

#### OLTP — Online Transaction Processing

Optimizadas para **operaciones transaccionales frecuentes y pequeñas**: inserciones, actualizaciones y consultas por registro individual. Son los sistemas operativos del negocio.

| Característica | OLTP |
|---|---|
| Tipo de operaciones | INSERT, UPDATE, DELETE de registros individuales |
| Volumen de datos por consulta | Pequeño (1 a miles de filas) |
| Usuarios concurrentes | Miles (clientes, empleados) |
| Diseño | Normalizado (3NF) para evitar redundancia |
| Prioridad | Velocidad de escritura, consistencia ACID |
| Ejemplos | ERP, CRM, e-commerce, banca online |

#### OLAP — Online Analytical Processing

Optimizadas para **consultas analíticas complejas** que agregan grandes volúmenes de datos históricos. Son los sistemas de soporte a la decisión.

| Característica | OLAP |
|---|---|
| Tipo de operaciones | SELECT con GROUP BY, agregaciones, filtros amplios |
| Volumen de datos por consulta | Masivo (millones a miles de millones de filas) |
| Usuarios concurrentes | Pocos (analistas, gerentes) |
| Diseño | Desnormalizado (esquema estrella) para velocidad de lectura |
| Prioridad | Velocidad de lectura y agregación |
| Ejemplos | Data Warehouse, reportes de BI, dashboards |

> **Regla de oro:** Las bases OLTP generan los datos; las OLAP los analizan. El proceso ETL es el puente entre ambas.

---

### 3.4 Clasificación por Propósito Analítico

| Sistema | Descripción |
|---|---|
| **Data Warehouse** | Repositorio centralizado y estructurado de datos históricos integrados de múltiples fuentes. Esquema fijo, datos curados. |
| **Data Mart** | Subconjunto del Data Warehouse orientado a un área de negocio específica (ventas, finanzas, marketing). |
| **Data Lake** | Repositorio que almacena datos en su formato crudo (sin transformar), sin esquema previo. Alta flexibilidad. |
| **Data Lakehouse** | Arquitectura híbrida que combina la flexibilidad del Data Lake con las capacidades analíticas del Data Warehouse. |

> **Concepto clave:** No existe una base de datos universal. La decisión debe basarse en el **patrón de acceso** (¿se escribe o se lee más?), la **necesidad de consistencia** (¿las transacciones deben ser ACID?) y el **tipo de relaciones** entre los datos (¿son planas o complejas?).

---

## Clase 04 — Extracción de Datos (Extract)

La extracción es el primer paso del pipeline ETL: **traer los datos desde sus fuentes de origen** hacia un área de staging donde serán procesados. La calidad y eficiencia de esta etapa impactan directamente en todo lo que viene después.

### 4.1 Full Load vs. Incremental Extract

#### Full Load (Carga Completa)

Se extraen **todos los registros** de la fuente cada vez que corre el pipeline, independientemente de si cambiaron o no.

**Ventajas:**
- Simple de implementar.
- Garantiza consistencia: el destino siempre refleja el estado completo de la fuente.

**Desventajas:**
- Costoso en tiempo y recursos para tablas grandes.
- No escala bien: una tabla de 100 millones de filas tarda mucho en extraerse diariamente.

**Cuándo usarlo:**
- Tablas pequeñas (tablas de referencia, catálogos, dimensiones estáticas).
- Cuando no hay forma de identificar registros modificados.
- Primera carga histórica (*initial load*).

#### Incremental Extract (Extracción Incremental)

Solo se extraen los registros **nuevos o modificados** desde la última extracción.

**Estrategias para identificar cambios:**

1. **Timestamp de modificación:** la tabla fuente tiene una columna `updated_at`. Se extraen solo los registros donde `updated_at > última_ejecución`.
2. **ID autoincremental:** se extraen solo los registros con `id > último_id_procesado`.
3. **Change Data Capture (CDC):** se leen los logs de transacciones de la base de datos (herramienta: Debezium) para capturar inserciones, actualizaciones y eliminaciones en tiempo real.

**Cuándo usarlo:**
- Tablas grandes con alto volumen de datos históricos.
- Pipelines que corren con frecuencia alta (cada hora, cada 15 minutos).
- Cuando el tiempo de extracción es una restricción crítica.

---

### 4.2 Extracción desde Bases de Datos Relacionales con Python

La librería estándar para conectarse a PostgreSQL desde Python es **psycopg2**. Para una capa de abstracción más cómoda, se usa **SQLAlchemy**.

```
pip install psycopg2-binary sqlalchemy pandas
```

#### Ejemplo 1 — Full Load desde PostgreSQL con psycopg2

```python
import psycopg2
import pandas as pd

# Parámetros de conexión
conexion = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="ventas_db",
    user="data_engineer",
    password="contraseña_segura"
)

# Extracción completa de la tabla de ventas
query = "SELECT * FROM ventas.transacciones;"

df = pd.read_sql_query(query, conexion)
conexion.close()

print(f"Registros extraídos: {len(df)}")
print(df.head())
```

#### Ejemplo 2 — Incremental Load con marca de tiempo

```python
import psycopg2
import pandas as pd
from datetime import datetime

def extraer_ventas_incrementales(ultima_extraccion: datetime) -> pd.DataFrame:
    """
    Extrae solo los registros de ventas modificados o creados
    después de 'ultima_extraccion'.
    """
    conexion = psycopg2.connect(
        host="localhost",
        dbname="ventas_db",
        user="data_engineer",
        password="contraseña_segura"
    )

    query = """
        SELECT
            id_venta,
            fecha_venta,
            id_cliente,
            id_producto,
            cantidad,
            precio_unitario,
            total,
            updated_at
        FROM ventas.transacciones
        WHERE updated_at > %(ultima_extraccion)s
        ORDER BY updated_at ASC;
    """

    # Uso de parámetros nombrados para evitar SQL Injection
    df = pd.read_sql_query(query, conexion, params={"ultima_extraccion": ultima_extraccion})
    conexion.close()

    print(f"Registros nuevos/modificados: {len(df)}")
    return df


# Ejecución
ultima_vez = datetime(2025, 3, 1, 6, 0, 0)  # Última ejecución: 1 de marzo a las 6 AM
df_nuevos = extraer_ventas_incrementales(ultima_vez)
```

> **Nota de seguridad:** Siempre se deben usar **parámetros nombrados** (`%(nombre)s`) en lugar de formatear el SQL con f-strings. El formateo directo expone el sistema a ataques de **SQL Injection**.

#### Ejemplo 3 — Extracción con SQLAlchemy (capa de abstracción)

SQLAlchemy permite cambiar de motor de base de datos (PostgreSQL, MySQL, SQLite) sin cambiar el código de la aplicación, usando una **cadena de conexión** estándar.

```python
from sqlalchemy import create_engine, text
import pandas as pd

# La cadena de conexión define el motor, usuario, contraseña, host y base de datos
engine = create_engine("postgresql+psycopg2://data_engineer:contraseña_segura@localhost:5432/ventas_db")

with engine.connect() as conn:
    df = pd.read_sql(
        text("SELECT * FROM ventas.transacciones WHERE fecha_venta >= '2025-01-01'"),
        conn
    )

print(f"Registros extraídos: {len(df)}")
print(df.dtypes)
```

---

### 4.3 Extracción desde APIs REST con Python

La librería `requests` es el estándar para hacer llamadas HTTP en Python. Permite consumir cualquier API REST con pocas líneas de código.

```
pip install requests
```

#### Ejemplo 4 — Extracción básica desde una API pública

```python
import requests
import pandas as pd

def extraer_datos_api(url: str, api_key: str, params: dict) -> pd.DataFrame:
    """
    Extrae datos desde una API REST y los retorna como DataFrame.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers, params=params, timeout=30)

    # Validar que la respuesta fue exitosa (código 200)
    response.raise_for_status()  # Lanza excepción si el status es 4xx o 5xx

    datos = response.json()
    return pd.DataFrame(datos["resultados"])


# Uso
df_api = extraer_datos_api(
    url="https://apis.datos.gob.ar/series/api/series/",
    api_key="mi_api_key",
    params={"ids": "148.3_INIVELAE_DICI_M_26", "limit": 100}
)
print(df_api.head())
```

#### Ejemplo 5 — API con paginación

Muchas APIs limitan la cantidad de resultados por llamada y requieren iterar sobre páginas para obtener el dataset completo.

```python
import requests
import pandas as pd
import time

def extraer_con_paginacion(url_base: str, api_key: str, registros_por_pagina: int = 100) -> pd.DataFrame:
    """
    Itera sobre todas las páginas de una API paginada y consolida los resultados.
    """
    headers = {"Authorization": f"Bearer {api_key}"}
    todos_los_registros = []
    pagina = 1

    while True:
        params = {"page": pagina, "per_page": registros_por_pagina}
        response = requests.get(url_base, headers=headers, params=params, timeout=30)
        response.raise_for_status()

        datos = response.json()
        registros = datos.get("data", [])

        if not registros:
            # No hay más páginas: salir del loop
            break

        todos_los_registros.extend(registros)
        print(f"Página {pagina} extraída — {len(registros)} registros")

        # Respetar el rate limit de la API: esperar 0.5 segundos entre llamadas
        time.sleep(0.5)
        pagina += 1

    print(f"Total extraído: {len(todos_los_registros)} registros")
    return pd.DataFrame(todos_los_registros)
```

#### Ejemplo 6 — Guardar la extracción en CSV como staging

```python
import requests
import pandas as pd
from pathlib import Path
from datetime import date

def extraer_y_guardar_staging(url: str, api_key: str) -> str:
    """
    Extrae datos de la API y los guarda en un archivo CSV de staging
    con la fecha de ejecución en el nombre del archivo.
    """
    response = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=30)
    response.raise_for_status()

    df = pd.DataFrame(response.json())

    # Crear directorio de staging si no existe
    staging_dir = Path("staging")
    staging_dir.mkdir(exist_ok=True)

    # Nombre con fecha para trazabilidad
    fecha_hoy = date.today().strftime("%Y%m%d")
    ruta_archivo = staging_dir / f"ventas_api_{fecha_hoy}.csv"

    df.to_csv(ruta_archivo, index=False, encoding="utf-8")
    print(f"Datos guardados en: {ruta_archivo} ({len(df)} registros)")

    return str(ruta_archivo)
```

---

### 4.4 Web Scraping Ético con BeautifulSoup

El **web scraping** es la técnica de extraer datos de páginas web mediante código. Es una fuente legítima de datos cuando se respetan los términos de uso del sitio y se hace de forma responsable.

**Consideraciones éticas y legales:**
- Revisar el archivo `robots.txt` del sitio para conocer qué rutas están permitidas.
- No sobrecargar el servidor: agregar pausas entre requests (`time.sleep`).
- No extraer datos personales sin consentimiento.
- Respetar los términos de servicio de cada sitio.

```
pip install requests beautifulsoup4 lxml
```

#### Ejemplo 7 — Scraping de una tabla de datos pública

```python
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrapear_tabla_html(url: str) -> pd.DataFrame:
    """
    Extrae la primera tabla HTML de una página pública y la retorna como DataFrame.
    """
    headers = {
        # Identificarse como un browser real es cortesía; algunos sitios lo requieren
        "User-Agent": "Mozilla/5.0 (compatible; DataEngBot/1.0; +educativo)"
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    # Parsear el HTML con BeautifulSoup
    soup = BeautifulSoup(response.text, "lxml")

    # Encontrar la primera tabla en la página
    tabla = soup.find("table")
    if not tabla:
        raise ValueError("No se encontró ninguna tabla en la página.")

    # Extraer encabezados
    encabezados = [th.get_text(strip=True) for th in tabla.find_all("th")]

    # Extraer filas
    filas = []
    for tr in tabla.find_all("tr")[1:]:  # Saltar la fila de encabezado
        celdas = [td.get_text(strip=True) for td in tr.find_all("td")]
        if celdas:
            filas.append(celdas)

    df = pd.DataFrame(filas, columns=encabezados)
    print(f"Tabla extraída: {len(df)} filas, {len(df.columns)} columnas")
    return df


# Ejemplo: extraer tabla de tipos de cambio de una página del banco central
url_ejemplo = "https://www.bcra.gob.ar/PublicacionesEstadisticas/Tipos_de_cambio_minorista.asp"
# df_tipo_cambio = scrapear_tabla_html(url_ejemplo)  # descomentar para ejecutar

# Pausa de cortesía entre requests al mismo dominio
time.sleep(2)
```

---

## Clase 05 — Transformación de Datos (Transform)

La transformación es la etapa más compleja y creativa del ETL. Su objetivo es convertir los datos crudos extraídos de las fuentes en datos **limpios, consistentes, enriquecidos y listos para el análisis**.

### 5.1 Limpieza de Datos con pandas

La mayoría de los datasets del mundo real contienen problemas: valores nulos, duplicados, tipos de dato incorrectos, formatos inconsistentes. La limpieza los corrige.

```
pip install pandas openpyxl
```

#### Ejemplo 8 — Dataset sucio: diagnóstico inicial

```python
import pandas as pd
import numpy as np

# Simular un dataset con problemas típicos
data_cruda = {
    "id_venta":       [1, 2, 2, 3, 4, 5, None],
    "fecha_venta":    ["2025-01-15", "15/01/2025", "15/01/2025", "2025-01-16", "2025-99-01", "2025-01-17", "2025-01-18"],
    "cliente":        ["María García", "  JUAN LOPEZ ", "  JUAN LOPEZ ", "Ana Torres", None, "Luis Paz", "Carlos Ruiz"],
    "monto":          [1500.0, 2300.50, 2300.50, -100.0, 850.0, 1200.0, 950.0],
    "moneda":         ["ARS", "ars", "ars", "ARS", "PESOS", "USD", "ARS"],
    "id_producto":    [101, 102, 102, 103, 104, 105, 106],
}

df = pd.DataFrame(data_cruda)
print("=== DATASET CRUDO ===")
print(df)
print("\n=== DIAGNÓSTICO ===")
print(f"Filas totales:     {len(df)}")
print(f"Duplicados:        {df.duplicated().sum()}")
print(f"Nulos por columna:\n{df.isnull().sum()}")
```

#### Ejemplo 9 — Pipeline de limpieza completo

```python
import pandas as pd
import numpy as np

def limpiar_dataset_ventas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica un pipeline de limpieza completo al dataset de ventas.
    Retorna el DataFrame limpio y un reporte de cambios.
    """
    df_limpio = df.copy()
    n_original = len(df_limpio)

    # 1. Eliminar filas completamente duplicadas
    df_limpio = df_limpio.drop_duplicates()
    print(f"[1] Duplicados eliminados: {n_original - len(df_limpio)}")

    # 2. Eliminar filas donde el ID de venta es nulo (no podemos identificar el registro)
    df_limpio = df_limpio.dropna(subset=["id_venta"])
    print(f"[2] Filas sin ID eliminadas: {n_original - len(df_limpio)}")

    # 3. Convertir id_venta a entero
    df_limpio["id_venta"] = df_limpio["id_venta"].astype(int)

    # 4. Normalizar la columna moneda: mayúsculas y mapeo de variantes
    mapa_monedas = {"ars": "ARS", "pesos": "ARS", "PESOS": "ARS", "usd": "USD"}
    df_limpio["moneda"] = df_limpio["moneda"].str.strip().str.upper()
    df_limpio["moneda"] = df_limpio["moneda"].replace(mapa_monedas)

    # 5. Estandarizar nombre de cliente: strip de espacios y title case
    df_limpio["cliente"] = df_limpio["cliente"].str.strip().str.title()

    # 6. Parsear fechas con manejo de errores (coerce convierte inválidos a NaT)
    df_limpio["fecha_venta"] = pd.to_datetime(df_limpio["fecha_venta"], errors="coerce")
    fechas_invalidas = df_limpio["fecha_venta"].isna().sum()
    print(f"[6] Fechas inválidas encontradas: {fechas_invalidas}")
    df_limpio = df_limpio.dropna(subset=["fecha_venta"])

    # 7. Filtrar montos negativos (no deberían existir en ventas)
    montos_negativos = (df_limpio["monto"] < 0).sum()
    df_limpio = df_limpio[df_limpio["monto"] >= 0]
    print(f"[7] Registros con monto negativo eliminados: {montos_negativos}")

    print(f"\n=== RESULTADO ===")
    print(f"Filas originales: {n_original} → Filas limpias: {len(df_limpio)}")
    return df_limpio


# Usar el dataset del Ejemplo 8
data_cruda = {
    "id_venta":    [1, 2, 2, 3, 4, 5, None],
    "fecha_venta": ["2025-01-15", "15/01/2025", "15/01/2025", "2025-01-16", "2025-99-01", "2025-01-17", "2025-01-18"],
    "cliente":     ["María García", "  JUAN LOPEZ ", "  JUAN LOPEZ ", "Ana Torres", None, "Luis Paz", "Carlos Ruiz"],
    "monto":       [1500.0, 2300.50, 2300.50, -100.0, 850.0, 1200.0, 950.0],
    "moneda":      ["ARS", "ars", "ars", "ARS", "PESOS", "USD", "ARS"],
    "id_producto": [101, 102, 102, 103, 104, 105, 106],
}
df_crudo = pd.DataFrame(data_cruda)
df_limpio = limpiar_dataset_ventas(df_crudo)
print(df_limpio)
```

---

### 5.2 Normalización y Estandarización

Normalizar significa dar el mismo formato a valores equivalentes. Es especialmente crítico cuando los datos provienen de múltiples fuentes con distintas convenciones.

#### Ejemplo 10 — Normalización de fechas, montos y textos

```python
import pandas as pd

df = pd.DataFrame({
    "fecha_str": ["2025-03-10", "10/03/2025", "March 10, 2025", "10-03-25"],
    "precio_str": ["$1.250,50", "1250.50", "1,250.50", "$ 1250"],
    "pais": ["argentina", "ARGENTINA", "Argentina ", "ARG"],
})

# Normalizar fechas: pandas prueba múltiples formatos automáticamente
df["fecha"] = pd.to_datetime(df["fecha_str"], dayfirst=True, errors="coerce")

# Normalizar precios: eliminar símbolos, puntos de miles y convertir a float
df["precio"] = (
    df["precio_str"]
    .str.replace(r"[\$\s]", "", regex=True)   # Quitar $ y espacios
    .str.replace(".", "", regex=False)          # Quitar puntos de miles (formato ES)
    .str.replace(",", ".", regex=False)         # Convertir coma decimal a punto
    .astype(float)
)

# Normalizar texto: strip, title case
df["pais_normalizado"] = df["pais"].str.strip().str.title()

print(df[["fecha", "precio", "pais_normalizado"]])
```

---

### 5.3 Joins, Agregaciones y Pivots

#### Ejemplo 11 — Join entre ventas y productos (enriquecimiento)

```python
import pandas as pd

# Tabla de ventas (extraída del sistema transaccional)
df_ventas = pd.DataFrame({
    "id_venta":    [1, 2, 3, 4, 5],
    "id_producto": [101, 102, 101, 103, 102],
    "cantidad":    [2, 1, 3, 1, 2],
    "precio_unit": [1500.0, 2300.0, 1500.0, 850.0, 2300.0],
})

# Tabla de referencia de productos (dimensión)
df_productos = pd.DataFrame({
    "id_producto": [101, 102, 103],
    "nombre":      ["Laptop Básica", "Monitor 24\"", "Teclado Mecánico"],
    "categoria":   ["Computación", "Periféricos", "Periféricos"],
    "proveedor":   ["TechCo", "ViewMax", "KeyMaster"],
})

# LEFT JOIN: enriquecer ventas con datos del catálogo de productos
df_enriquecido = df_ventas.merge(df_productos, on="id_producto", how="left")

# Calcular total por venta (columna derivada)
df_enriquecido["total"] = df_enriquecido["cantidad"] * df_enriquecido["precio_unit"]

print("=== VENTAS ENRIQUECIDAS ===")
print(df_enriquecido)
```

#### Ejemplo 12 — Agregaciones: ventas por categoría y mes

```python
import pandas as pd

# Dataset enriquecido con fechas
df = pd.DataFrame({
    "fecha":      pd.to_datetime(["2025-01-05", "2025-01-12", "2025-02-03", "2025-02-14", "2025-01-20"]),
    "categoria":  ["Computación", "Periféricos", "Computación", "Periféricos", "Computación"],
    "total":      [3000.0, 2300.0, 4500.0, 850.0, 1500.0],
    "cantidad":   [2, 1, 3, 1, 1],
})

# Agregar mes/año para el agrupamiento
df["anio_mes"] = df["fecha"].dt.to_period("M")

# Agrupamiento: ventas totales y cantidad de transacciones por mes y categoría
resumen = (
    df.groupby(["anio_mes", "categoria"])
    .agg(
        total_vendido=("total", "sum"),
        cantidad_total=("cantidad", "sum"),
        num_transacciones=("total", "count"),
        ticket_promedio=("total", "mean"),
    )
    .reset_index()
    .sort_values(["anio_mes", "total_vendido"], ascending=[True, False])
)

print(resumen.to_string(index=False))
```

#### Ejemplo 13 — Pivot Table: ventas mensuales por categoría

```python
import pandas as pd

df = pd.DataFrame({
    "mes":       ["Enero", "Enero", "Febrero", "Febrero", "Marzo", "Marzo"],
    "categoria": ["Computación", "Periféricos", "Computación", "Periféricos", "Computación", "Periféricos"],
    "total":     [7500.0, 3150.0, 4500.0, 850.0, 6000.0, 2200.0],
})

# Pivot: filas = mes, columnas = categoría, valores = suma de total
tabla_pivot = df.pivot_table(
    index="mes",
    columns="categoria",
    values="total",
    aggfunc="sum",
    fill_value=0
)

print("=== VENTAS POR MES Y CATEGORÍA ===")
print(tabla_pivot)
```

---

### 5.4 ETL vs. ELT: Dos Paradigmas de Transformación

El orden en que se realizan las etapas del pipeline define el paradigma:

#### ETL — Extract, Transform, Load

Los datos se **transforman antes de llegar al destino**. El destino solo recibe datos limpios y estructurados.

```
[Fuente]  →  [Extracción]  →  [Transformación fuera del destino]  →  [Carga al DWH]
                                  (Python, Spark, servidor ETL)
```

**Ventajas:**
- Mayor privacidad: los datos sensibles se filtran/anoniman antes de cargarse.
- Menor almacenamiento en destino: solo llegan datos curados.
- Compatible con destinos legacy que no tienen capacidad de transformación.

**Desventajas:**
- Rigidez: si cambian los requerimientos, hay que re-extraer y re-transformar.
- Requiere infraestructura ETL separada.

#### ELT — Extract, Load, Transform

Los datos se cargan crudos en el destino y **se transforman dentro del mismo**, aprovechando su poder de cómputo.

```
[Fuente]  →  [Extracción]  →  [Carga Raw al DWH/Lake]  →  [Transformación en destino]
                                                               (SQL, dbt, Spark SQL)
```

**Ventajas:**
- Más rápido de implementar: se carga primero, se decide qué transformar después.
- Flexibilidad: los datos crudos están siempre disponibles para re-procesar.
- Escalable: los motores cloud (BigQuery, Snowflake, Redshift) son muy eficientes para SQL analítico.

**Desventajas:**
- Los datos sensibles llegan crudos al destino → requiere controles de acceso estrictos.
- Mayor costo de almacenamiento.

> **Tendencia actual:** el paradigma **ELT** predomina en arquitecturas cloud modernas, donde el poder de cómputo del Data Warehouse es barato y elástico. **dbt** es la herramienta central de este paradigma.

---

### 5.5 Derivación de Nuevas Columnas y Enriquecimiento

#### Ejemplo 14 — Derivar columnas calculadas

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "fecha_venta":    pd.to_datetime(["2025-01-05", "2025-01-12", "2025-02-14", "2025-03-08"]),
    "fecha_entrega":  pd.to_datetime(["2025-01-08", "2025-01-18", "2025-02-15", "2025-03-20"]),
    "precio_unit":    [1500.0, 2300.0, 850.0, 1200.0],
    "cantidad":       [2, 1, 3, 2],
    "descuento_pct":  [0.10, 0.0, 0.05, 0.15],
})

# Columnas derivadas
df["total_bruto"]    = df["precio_unit"] * df["cantidad"]
df["descuento_monto"]= df["total_bruto"] * df["descuento_pct"]
df["total_neto"]     = df["total_bruto"] - df["descuento_monto"]
df["dias_entrega"]   = (df["fecha_entrega"] - df["fecha_venta"]).dt.days
df["dia_semana"]     = df["fecha_venta"].dt.day_name()
df["trimestre"]      = df["fecha_venta"].dt.quarter

# Clasificar por monto de venta
condiciones = [
    df["total_neto"] < 1000,
    (df["total_neto"] >= 1000) & (df["total_neto"] < 3000),
    df["total_neto"] >= 3000,
]
categorias = ["Pequeña", "Mediana", "Grande"]
df["segmento_venta"] = np.select(condiciones, categorias, default="Sin clasificar")

print(df[["total_neto", "dias_entrega", "dia_semana", "trimestre", "segmento_venta"]])
```

---

## Clase 06 — Carga de Datos (Load) y Orquestación

La carga es la etapa final del pipeline ETL: **persistir los datos transformados en el sistema destino** (Data Warehouse, Data Lake, base de datos operativa). La estrategia de carga elegida impacta directamente en la integridad, el rendimiento y la idempotencia del pipeline.

### 6.1 Estrategias de Carga

#### Full Overwrite (Reemplazo Total)

Se borra toda la tabla destino y se vuelve a insertar completa.

```sql
-- En SQL puro
TRUNCATE TABLE dw.ventas_diarias;
INSERT INTO dw.ventas_diarias SELECT * FROM staging.ventas_diarias;
```

**Cuándo usarlo:** tablas pequeñas, dimensiones estáticas, cuando la idempotencia es crítica y el volumen lo permite.

**Riesgo:** si el pipeline falla a mitad del proceso, la tabla queda vacía.

#### Append (Inserción Incremental)

Se insertan solo los registros nuevos **sin tocar los existentes**.

**Cuándo usarlo:** tablas de hechos de solo escritura (logs, eventos, transacciones que nunca se modifican).

**Riesgo:** si el pipeline corre dos veces, los datos se duplican. Requiere idempotencia externa.

#### Upsert (Actualizar o Insertar)

Si el registro **ya existe** en el destino, se actualiza. Si **no existe**, se inserta. Es la estrategia más robusta y segura.

```sql
-- En PostgreSQL (INSERT ON CONFLICT)
INSERT INTO dw.clientes (id_cliente, nombre, email, updated_at)
VALUES (%(id)s, %(nombre)s, %(email)s, %(updated_at)s)
ON CONFLICT (id_cliente)
DO UPDATE SET
    nombre     = EXCLUDED.nombre,
    email      = EXCLUDED.email,
    updated_at = EXCLUDED.updated_at;
```

**Cuándo usarlo:** casi siempre. Es la estrategia más segura porque el pipeline puede ejecutarse múltiples veces sin duplicar datos (idempotencia).

---

### 6.2 Carga a PostgreSQL con SQLAlchemy y pandas

```
pip install sqlalchemy psycopg2-binary pandas
```

#### Ejemplo 15 — Full Overwrite con pandas `to_sql`

```python
import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine("postgresql+psycopg2://data_engineer:contraseña@localhost:5432/dw_ventas")

df_transformado = pd.DataFrame({
    "id_venta":    [1, 2, 3],
    "fecha":       pd.to_datetime(["2025-03-01", "2025-03-02", "2025-03-03"]),
    "total":       [1500.0, 2300.0, 850.0],
    "id_cliente":  [101, 102, 103],
})

# if_exists='replace' → DROP + CREATE + INSERT (Full Overwrite)
df_transformado.to_sql(
    name="ventas_diarias",
    con=engine,
    schema="dw",
    if_exists="replace",   # 'append' para solo insertar, 'replace' para reemplazar
    index=False,
    method="multi",        # Inserta en lotes para mejor rendimiento
    chunksize=1000,
)

print("Carga completa exitosa.")
```

#### Ejemplo 16 — Append: insertar solo registros nuevos

```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg2://data_engineer:contraseña@localhost:5432/dw_ventas")

df_nuevos = pd.DataFrame({
    "id_venta":   [4, 5, 6],
    "fecha":      pd.to_datetime(["2025-03-04", "2025-03-05", "2025-03-06"]),
    "total":      [1200.0, 950.0, 3100.0],
    "id_cliente": [104, 105, 106],
})

# if_exists='append' → solo inserta sin tocar los existentes
df_nuevos.to_sql(
    name="ventas_diarias",
    con=engine,
    schema="dw",
    if_exists="append",
    index=False,
    method="multi",
)

print(f"{len(df_nuevos)} registros nuevos cargados.")
```

#### Ejemplo 17 — Upsert con psycopg2 (estrategia recomendada)

```python
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

def upsert_ventas(df: pd.DataFrame, conexion_str: dict) -> None:
    """
    Realiza un UPSERT de ventas en la tabla destino.
    Si el id_venta ya existe, actualiza total y fecha.
    Si no existe, lo inserta.
    """
    conn = psycopg2.connect(**conexion_str)
    cursor = conn.cursor()

    sql_upsert = """
        INSERT INTO dw.ventas (id_venta, fecha, total, id_cliente)
        VALUES %s
        ON CONFLICT (id_venta)
        DO UPDATE SET
            fecha      = EXCLUDED.fecha,
            total      = EXCLUDED.total,
            id_cliente = EXCLUDED.id_cliente,
            updated_at = NOW();
    """

    # Convertir DataFrame a lista de tuplas para execute_values
    registros = [
        (row.id_venta, row.fecha, row.total, row.id_cliente)
        for row in df.itertuples(index=False)
    ]

    # execute_values inserta en bulk de forma eficiente
    execute_values(cursor, sql_upsert, registros, page_size=500)
    conn.commit()

    print(f"Upsert completado: {len(registros)} registros procesados.")
    cursor.close()
    conn.close()


# Datos de ejemplo
df_upsert = pd.DataFrame({
    "id_venta":   [1, 2, 7],  # 1 y 2 ya existen → UPDATE; 7 es nuevo → INSERT
    "fecha":      pd.to_datetime(["2025-03-01", "2025-03-02", "2025-03-07"]),
    "total":      [1600.0, 2300.0, 4200.0],  # id_venta=1 cambió de 1500 a 1600
    "id_cliente": [101, 102, 107],
})

conexion = {
    "host": "localhost",
    "dbname": "dw_ventas",
    "user": "data_engineer",
    "password": "contraseña"
}

upsert_ventas(df_upsert, conexion)
```

---

### 6.3 Idempotencia: el Principio Más Importante de los Pipelines

Un pipeline es **idempotente** si puede ejecutarse múltiples veces con el mismo resultado. Es decir: si corre una vez o cien veces, el estado final de los datos es el mismo.

La idempotencia es crítica porque:
- Los pipelines **fallan** y se re-ejecutan (errores de red, timeouts, recursos).
- Los orquestadores como Airflow pueden **re-intentar** tareas automáticamente.
- Alguien puede correr manualmente el pipeline para corregir un error.

**Sin idempotencia:** cada re-ejecución duplica o corrompe datos.  
**Con idempotencia:** re-ejecutar es siempre seguro.

#### Ejemplo 18 — Pipeline idempotente completo

```python
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from datetime import date

def pipeline_ventas_diarias(fecha_proceso: date, conexion_str: dict) -> None:
    """
    Pipeline idempotente: puede ejecutarse N veces para la misma fecha
    y el resultado siempre será el mismo.
    """
    print(f"=== Iniciando pipeline para fecha: {fecha_proceso} ===")

    # PASO 1: Extraer solo los datos del día a procesar
    conn = psycopg2.connect(**conexion_str)
    df = pd.read_sql(
        "SELECT * FROM fuente.ventas WHERE DATE(created_at) = %(fecha)s",
        conn,
        params={"fecha": fecha_proceso}
    )
    print(f"[Extract] {len(df)} registros extraídos")

    # PASO 2: Transformar
    df["total"] = df["cantidad"] * df["precio_unit"] * (1 - df["descuento"])
    df["fecha_proceso"] = fecha_proceso
    print(f"[Transform] Columnas calculadas correctamente")

    # PASO 3: Carga idempotente
    # Primero eliminar los datos de esa fecha (si existen de una ejecución anterior)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM dw.ventas_procesadas WHERE fecha_proceso = %(fecha)s",
        {"fecha": fecha_proceso}
    )
    print(f"[Load] Datos anteriores de {fecha_proceso} eliminados (si existían)")

    # Luego insertar los datos frescos
    registros = list(df[["id_venta", "total", "fecha_proceso"]].itertuples(index=False, name=None))
    if registros:
        execute_values(
            cursor,
            "INSERT INTO dw.ventas_procesadas (id_venta, total, fecha_proceso) VALUES %s",
            registros
        )

    conn.commit()
    cursor.close()
    conn.close()
    print(f"[Load] {len(registros)} registros cargados exitosamente")
    print(f"=== Pipeline finalizado ===")
```

---

### 6.4 Orquestación con Apache Airflow

**Apache Airflow** es el orquestador de pipelines más utilizado en la industria. Permite:

- **Definir pipelines como código Python** (DAGs: Directed Acyclic Graphs).
- **Programar ejecuciones** automáticas (cada día, cada hora, cada lunes a las 6 AM).
- **Gestionar dependencias** entre tareas: la tarea B solo corre si la tarea A tuvo éxito.
- **Reintentar tareas fallidas** automáticamente, con espera exponencial.
- **Monitorear** el estado de cada ejecución desde una interfaz web.

#### Conceptos fundamentales

| Concepto | Descripción |
|---|---|
| **DAG** | Directed Acyclic Graph. Define el pipeline completo: tareas y sus dependencias. |
| **Task** | Una unidad de trabajo dentro del DAG (extracción, transformación, carga). |
| **Operator** | Tipo de tarea: `PythonOperator` (corre una función Python), `BashOperator`, `PostgresOperator`, etc. |
| **Schedule** | Expresión cron que define cuándo corre el DAG: `"0 6 * * *"` = todos los días a las 6 AM. |
| **DAG Run** | Una instancia de ejecución del DAG para una fecha/hora específica. |
| **XCom** | Mecanismo para pasar datos entre tareas dentro del mismo DAG. |

#### Ejemplo 19 — DAG de Airflow: pipeline ETL completo

```python
# archivo: dags/pipeline_ventas_diarias.py
# Instalar: pip install apache-airflow

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import pandas as pd
import requests
import psycopg2
from psycopg2.extras import execute_values


# ─────────────────────────────────────────────
# Funciones del pipeline
# ─────────────────────────────────────────────

def extraer_ventas(**context) -> str:
    """Extrae ventas de la API y las guarda en staging."""
    fecha = context["ds"]  # Fecha de ejecución del DAG (YYYY-MM-DD)

    response = requests.get(
        "https://api.interna.empresa.com/ventas",
        headers={"Authorization": "Bearer TOKEN_SECRETO"},
        params={"fecha": fecha},
        timeout=60
    )
    response.raise_for_status()

    df = pd.DataFrame(response.json()["ventas"])
    ruta = f"/tmp/ventas_staging_{fecha}.csv"
    df.to_csv(ruta, index=False)

    print(f"Extraídos {len(df)} registros para {fecha}")
    return ruta  # Se pasa a la siguiente tarea via XCom


def transformar_ventas(**context) -> str:
    """Lee el staging, aplica transformaciones y guarda resultado limpio."""
    # Obtener la ruta del archivo generado en la tarea anterior (XCom)
    ti = context["ti"]
    ruta_staging = ti.xcom_pull(task_ids="extraer")

    df = pd.read_csv(ruta_staging, parse_dates=["fecha_venta"])

    # Transformaciones
    df = df.drop_duplicates(subset=["id_venta"])
    df = df.dropna(subset=["id_venta", "monto"])
    df = df[df["monto"] > 0]
    df["total_con_iva"] = df["monto"] * 1.21
    df["moneda"] = df["moneda"].str.upper().str.strip()

    ruta_transformada = ruta_staging.replace("staging", "transformado")
    df.to_csv(ruta_transformada, index=False)

    print(f"Transformación completa: {len(df)} registros listos")
    return ruta_transformada


def cargar_ventas(**context) -> None:
    """Carga los datos transformados en el Data Warehouse con upsert."""
    ti = context["ti"]
    ruta = ti.xcom_pull(task_ids="transformar")
    fecha = context["ds"]

    df = pd.read_csv(ruta, parse_dates=["fecha_venta"])

    conn = psycopg2.connect(
        host="localhost", dbname="dw_ventas",
        user="data_engineer", password="contraseña"
    )
    cursor = conn.cursor()

    # Idempotencia: eliminar datos previos de esta fecha
    cursor.execute("DELETE FROM dw.ventas WHERE DATE(fecha_venta) = %s", (fecha,))

    registros = [
        (row.id_venta, row.fecha_venta, row.monto, row.total_con_iva, row.moneda)
        for row in df.itertuples(index=False)
    ]

    execute_values(
        cursor,
        "INSERT INTO dw.ventas (id_venta, fecha_venta, monto, total_con_iva, moneda) VALUES %s",
        registros
    )

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Cargados {len(registros)} registros en dw.ventas para {fecha}")


# ─────────────────────────────────────────────
# Definición del DAG
# ─────────────────────────────────────────────

with DAG(
    dag_id="pipeline_ventas_diarias",
    description="ETL diario de ventas: API → staging → transformación → DWH",
    schedule_interval="0 6 * * *",          # Todos los días a las 6:00 AM
    start_date=datetime(2025, 1, 1),
    catchup=False,                           # No ejecutar fechas pasadas al activar
    max_active_runs=1,                       # Solo una ejecución a la vez
    default_args={
        "owner": "data_engineering",
        "retries": 2,                        # Reintentar hasta 2 veces si falla
        "retry_delay": timedelta(minutes=5), # Esperar 5 min entre reintentos
        "email_on_failure": True,
        "email": ["alertas@empresa.com"],
    },
) as dag:

    tarea_extraccion = PythonOperator(
        task_id="extraer",
        python_callable=extraer_ventas,
    )

    tarea_transformacion = PythonOperator(
        task_id="transformar",
        python_callable=transformar_ventas,
    )

    tarea_carga = PythonOperator(
        task_id="cargar",
        python_callable=cargar_ventas,
    )

    # Definir orden de ejecución: extraer → transformar → cargar
    tarea_extraccion >> tarea_transformacion >> tarea_carga
```

El operador `>>` define las dependencias: `transformar` solo se ejecuta si `extraer` fue exitosa; `cargar` solo corre si `transformar` fue exitosa. Si alguna tarea falla, Airflow la reintenta según la configuración y envía una alerta por email.

---

### 6.5 Pipeline ETL Completo de Extremo a Extremo (sin Airflow)

Para entornos más simples o para entender el flujo antes de orquestarlo, se puede correr el pipeline completo en un único script Python:

#### Ejemplo 20 — Pipeline ETL autónomo con logging y manejo de errores

```python
import pandas as pd
import requests
import psycopg2
from psycopg2.extras import execute_values
from datetime import date
import logging

# Configurar logging para trazabilidad
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger(__name__)


def extraer(fecha: date) -> pd.DataFrame:
    log.info(f"[EXTRACT] Iniciando extracción para {fecha}")
    response = requests.get(
        "https://api.ejemplo.com/ventas",
        params={"fecha": str(fecha)},
        timeout=30
    )
    response.raise_for_status()
    df = pd.DataFrame(response.json())
    log.info(f"[EXTRACT] {len(df)} registros extraídos")
    return df


def transformar(df: pd.DataFrame) -> pd.DataFrame:
    log.info("[TRANSFORM] Iniciando transformaciones")
    df = df.drop_duplicates(subset=["id_venta"])
    df = df.dropna(subset=["id_venta", "monto"])
    df = df[df["monto"] > 0]
    df["total_con_iva"] = df["monto"] * 1.21
    df["moneda"] = df["moneda"].str.upper().str.strip()
    log.info(f"[TRANSFORM] {len(df)} registros después de limpieza")
    return df


def cargar(df: pd.DataFrame, fecha: date, conexion_str: dict) -> None:
    log.info(f"[LOAD] Iniciando carga de {len(df)} registros")
    conn = psycopg2.connect(**conexion_str)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM dw.ventas WHERE fecha_proceso = %s", (fecha,))
    log.info(f"[LOAD] Registros anteriores de {fecha} eliminados")

    registros = list(df[["id_venta", "monto", "total_con_iva", "moneda"]].itertuples(index=False, name=None))
    execute_values(
        cursor,
        "INSERT INTO dw.ventas (id_venta, monto, total_con_iva, moneda) VALUES %s",
        registros
    )

    conn.commit()
    cursor.close()
    conn.close()
    log.info(f"[LOAD] Carga completada exitosamente")


def ejecutar_pipeline(fecha: date) -> None:
    """Orquesta el pipeline ETL completo."""
    log.info(f"{'='*50}")
    log.info(f"PIPELINE ETL — Fecha: {fecha}")
    log.info(f"{'='*50}")

    conexion = {
        "host": "localhost", "dbname": "dw_ventas",
        "user": "data_engineer", "password": "contraseña"
    }

    try:
        df_raw = extraer(fecha)
        df_clean = transformar(df_raw)
        cargar(df_clean, fecha, conexion)
        log.info("PIPELINE COMPLETADO EXITOSAMENTE")
    except requests.RequestException as e:
        log.error(f"Error en extracción: {e}")
        raise
    except psycopg2.Error as e:
        log.error(f"Error en base de datos: {e}")
        raise
    except Exception as e:
        log.error(f"Error inesperado: {e}")
        raise


if __name__ == "__main__":
    ejecutar_pipeline(fecha=date.today())
```

---

## Resumen de la Unidad

| Concepto | Definición resumida |
|---|---|
| Bases de datos relacionales | Tablas + SQL + ACID. Máxima consistencia. |
| NoSQL Clave-Valor | Pares clave→valor en memoria. Ultra-rápido. Ej: Redis. |
| NoSQL Documental | Documentos JSON sin esquema fijo. Ej: MongoDB. |
| NoSQL Columnar | Almacenamiento por columna para escritura masiva distribuida. Ej: Cassandra. |
| Grafos | Nodos y aristas. Ideal para relaciones complejas. Ej: Neo4j. |
| OLTP | Transacciones frecuentes y pequeñas. Sistema operativo del negocio. |
| OLAP | Consultas analíticas complejas sobre grandes volúmenes históricos. |
| Full Load | Extraer todo cada vez. Simple pero costoso en escala. |
| Incremental Extract | Extraer solo lo nuevo/modificado. Eficiente en escala. |
| ETL | Transformar antes de cargar. Mayor privacidad y control. |
| ELT | Cargar crudo y transformar en destino. Flexible y escalable en cloud. |
| Full Overwrite | Borrar y reemplazar toda la tabla destino. |
| Append | Agregar registros sin tocar los existentes. |
| Upsert | Actualizar si existe, insertar si no existe. La más segura. |
| Idempotencia | El pipeline puede correr N veces con el mismo resultado. |
| Apache Airflow | Orquestador de pipelines: define DAGs, schedules y dependencias en Python. |

---

## Librerías Python Utilizadas en esta Unidad

| Librería | Instalación | Uso |
|---|---|---|
| `pandas` | `pip install pandas` | Manipulación y transformación de datos tabulares |
| `requests` | `pip install requests` | Consumo de APIs REST |
| `psycopg2` | `pip install psycopg2-binary` | Conexión y operaciones sobre PostgreSQL |
| `sqlalchemy` | `pip install sqlalchemy` | Capa de abstracción ORM para múltiples motores SQL |
| `beautifulsoup4` | `pip install beautifulsoup4` | Parsing de HTML para web scraping |
| `lxml` | `pip install lxml` | Parser HTML/XML rápido (backend para BeautifulSoup) |
| `apache-airflow` | `pip install apache-airflow` | Orquestación de pipelines con DAGs |
| `numpy` | `pip install numpy` | Operaciones numéricas y manejo de valores nulos |
| `openpyxl` | `pip install openpyxl` | Lectura y escritura de archivos Excel (.xlsx) |

---

## Bibliografía de la Unidad

- **Reis, J. & Housley, M.** — *Fundamentals of Data Engineering*, Capítulos 5 y 6. O'Reilly Media.
- **McKinney, W.** — *Python for Data Analysis*, 3ra edición. O'Reilly Media.
- **Harenslak, B. & de Ruiter, J.** — *Data Pipelines with Apache Airflow*. Manning Publications.
- **Documentación oficial de Apache Airflow** — [airflow.apache.org](https://airflow.apache.org/docs/).
- **Documentación oficial de pandas** — [pandas.pydata.org](https://pandas.pydata.org/docs/).
- **Documentación oficial de SQLAlchemy** — [docs.sqlalchemy.org](https://docs.sqlalchemy.org/).
- **Tutorial oficial de requests** — [docs.python-requests.org](https://docs.python-requests.org/).
- **Documentación de Airbyte** — [docs.airbyte.com](https://docs.airbyte.com/).
