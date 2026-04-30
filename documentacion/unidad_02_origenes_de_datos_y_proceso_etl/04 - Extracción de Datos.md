# Clase 04 — Extracción de Datos (Extract)

> **Asignatura:** Ingeniería de Datos  
> **Docente:** Ing. Sergio Orozco  
> **Unidad:** II — Orígenes de Datos y Proceso ETL

---

## Objetivos de la Clase

Al finalizar esta clase, el alumno será capaz de:

- Distinguir entre **Full Load** e **Incremental Extract** y elegir la estrategia adecuada.
- Extraer datos desde bases de datos **PostgreSQL** usando `psycopg2` y `SQLAlchemy`.
- Consumir datos desde **APIs REST** con autenticación, paginación y manejo de errores.
- Realizar **web scraping** ético de páginas públicas con `BeautifulSoup`.
- Guardar los datos extraídos en un área de **staging** para procesamiento posterior.

---

## 1. ¿Qué es la Extracción?

La extracción (Extract) es el **primer paso del pipeline ETL**: traer los datos desde sus fuentes de origen hacia un área de staging (almacenamiento temporal) donde serán procesados.

```
┌──────────────────────────────────────────────────────────────────────┐
│                       ETAPA DE EXTRACCIÓN                           │
│                                                                      │
│  FUENTES DE ORIGEN              ÁREA DE STAGING                     │
│  ┌─────────────┐               ┌──────────────┐                     │
│  │ PostgreSQL  │──────────────►│              │                     │
│  │ MySQL       │               │  CSV / JSON  │                     │
│  │ API REST    │──────────────►│  Parquet     │  ► Transformación   │
│  │ Archivo CSV │               │  Delta Lake  │                     │
│  │ Web Scraping│──────────────►│              │                     │
│  └─────────────┘               └──────────────┘                     │
│                                                                      │
│  La calidad y eficiencia de esta etapa impacta en TODO lo demás.   │
└──────────────────────────────────────────────────────────────────────┘
```

La calidad y eficiencia de la extracción impactan directamente en todo lo que viene después. Si extraemos datos incompletos, corruptos o con retraso, los problemas se propagan al análisis.

---

## 2. Full Load vs. Incremental Extract

Esta es la primera decisión estratégica de todo pipeline de extracción.

### 2.1 Full Load (Carga Completa)

Se extraen **todos los registros** de la fuente cada vez que corre el pipeline, sin importar si cambiaron o no.

```
Ejecución 1 (lunes):    → Extrae 100.000 registros
Ejecución 2 (martes):   → Extrae 100.005 registros (todos, incluyendo los 5 nuevos)
Ejecución 3 (miércoles):→ Extrae 100.012 registros (todos, otra vez)
```

**Ventajas:**
- Simple de implementar: no requiere lógica adicional.
- Garantiza consistencia: el destino siempre refleja el estado completo de la fuente.
- Idempotente por naturaleza: ejecutarlo dos veces da el mismo resultado.

**Desventajas:**
- Costoso en tiempo y recursos para tablas grandes.
- No escala bien: extraer 100 millones de filas cada hora es inviable.
- Puede generar carga innecesaria en el sistema fuente.

**Cuándo usarlo:**
- Tablas pequeñas (catálogos, dimensiones estáticas).
- Cuando no hay forma de identificar registros modificados.
- Primera carga histórica (*initial load*).

### 2.2 Incremental Extract (Extracción Incremental)

Solo se extraen los registros **nuevos o modificados** desde la última extracción.

```
Ejecución 1 (lunes):    → Extrae 100.000 registros (inicial, full load)
Ejecución 2 (martes):   → Extrae SOLO los 5 registros nuevos/modificados
Ejecución 3 (miércoles):→ Extrae SOLO los 7 nuevos/modificados
```

**Estrategias para identificar cambios:**

```
ESTRATEGIA 1 — Timestamp de modificación:
  La tabla fuente tiene una columna 'updated_at'.
  Se extraen solo los registros donde: updated_at > última_ejecución
  ✅ Simple | ⚠️ No detecta eliminaciones

ESTRATEGIA 2 — ID autoincremental:
  Se extraen solo los registros con: id > último_id_procesado
  ✅ Simple | ⚠️ Solo detecta inserciones nuevas, no modificaciones

ESTRATEGIA 3 — Change Data Capture (CDC):
  Se leen los logs de transacciones de la BD (con Debezium).
  Captura INSERT, UPDATE y DELETE en tiempo real.
  ✅ Completo | ⚠️ Más complejo de implementar
```

---

## 3. Extracción desde Bases de Datos Relacionales con Python

### 3.1 Usando psycopg2 (conexión directa a PostgreSQL)

`psycopg2` es la librería estándar para conectarse a PostgreSQL desde Python. Ofrece control total sobre la conexión y las consultas.

```bash
pip install psycopg2-binary pandas
```

#### Ejemplo 1 — Full Load desde PostgreSQL

```python
import psycopg2
import pandas as pd

# Configuración de la conexión
# ⚠️ NUNCA guardar credenciales en el código. Usar variables de entorno.
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
print(df.dtypes)
```

#### Ejemplo 2 — Incremental Load con marca de tiempo

```python
import psycopg2
import pandas as pd
from datetime import datetime

def extraer_ventas_incrementales(ultima_extraccion: datetime) -> pd.DataFrame:
    """
    Extrae solo los registros nuevos o modificados después de 'ultima_extraccion'.
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

    # ✅ Uso de parámetros nombrados para PREVENIR SQL INJECTION
    # ❌ NUNCA hacer: f"WHERE updated_at > '{ultima_extraccion}'" 
    df = pd.read_sql_query(
        query,
        conexion,
        params={"ultima_extraccion": ultima_extraccion}
    )
    conexion.close()

    print(f"Registros nuevos/modificados: {len(df)}")
    return df


# Ejecución — extraer desde la última vez que corrió el pipeline
ultima_vez = datetime(2025, 3, 1, 6, 0, 0)
df_nuevos = extraer_ventas_incrementales(ultima_vez)
```

> **⚠️ Seguridad crítica — SQL Injection:** Siempre usar parámetros (`%(nombre)s` o `%s`) en lugar de formatear el SQL con f-strings o `.format()`. El formateo directo permite que un atacante inyecte código SQL malicioso en la consulta.

### 3.2 Usando SQLAlchemy (capa de abstracción)

`SQLAlchemy` permite cambiar de motor de base de datos (PostgreSQL, MySQL, SQLite, Oracle) **sin cambiar el código de la aplicación**, usando una cadena de conexión estándar.

```bash
pip install sqlalchemy psycopg2-binary
```

```python
from sqlalchemy import create_engine, text
import pandas as pd

# Cadena de conexión: dialecto+driver://usuario:contraseña@host:puerto/base
engine = create_engine(
    "postgresql+psycopg2://data_engineer:contraseña@localhost:5432/ventas_db"
)

# Uso de context manager para garantizar el cierre de la conexión
with engine.connect() as conn:
    df = pd.read_sql(
        text("""
            SELECT *
            FROM ventas.transacciones
            WHERE fecha_venta >= '2025-01-01'
              AND estado = 'confirmada'
        """),
        conn
    )

print(f"Registros: {len(df)}")
print(df.head())
```

---

## 4. Extracción desde APIs REST con Python

La librería `requests` es el estándar para hacer llamadas HTTP en Python.

```bash
pip install requests
```

### 4.1 Extracción básica desde una API pública

```python
import requests
import pandas as pd

def extraer_tipo_cambio_bcra(variable_id: int, desde: str, hasta: str) -> pd.DataFrame:
    """
    Extrae series estadísticas del BCRA (Banco Central de Argentina).
    variable_id 4 = Tipo de cambio de referencia (vendedor).
    """
    url = f"https://api.bcra.gob.ar/estadisticas/v2.0/datosvariable/{variable_id}/{desde}/{hasta}"

    response = requests.get(url, timeout=30)

    # raise_for_status() lanza una excepción si el status es 4xx o 5xx
    response.raise_for_status()

    datos = response.json()
    df = pd.DataFrame(datos["results"])

    print(f"Registros obtenidos: {len(df)}")
    return df


# Extracción del tipo de cambio de enero a marzo 2025
df_cambio = extraer_tipo_cambio_bcra(
    variable_id=4,
    desde="2025-01-01",
    hasta="2025-03-31"
)
print(df_cambio.head())
```

### 4.2 API con autenticación y paginación

Muchas APIs privadas requieren autenticación y limitan la cantidad de resultados por llamada.

```python
import requests
import pandas as pd
import time

def extraer_con_paginacion(
    url_base: str,
    api_key: str,
    registros_por_pagina: int = 100
) -> pd.DataFrame:
    """
    Itera sobre todas las páginas de una API paginada y consolida los resultados.
    Incluye:
      - Autenticación por header
      - Manejo de rate limiting (pausa entre llamadas)
      - Detección del final de la paginación
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    todos_los_registros = []
    pagina = 1

    while True:
        params = {
            "page": pagina,
            "per_page": registros_por_pagina
        }

        response = requests.get(
            url_base,
            headers=headers,
            params=params,
            timeout=30
        )
        response.raise_for_status()

        datos = response.json()
        registros = datos.get("data", [])

        if not registros:
            # No hay más páginas: terminamos
            print(f"Paginación completa en página {pagina}")
            break

        todos_los_registros.extend(registros)
        print(f"Página {pagina} → {len(registros)} registros (acumulado: {len(todos_los_registros)})")

        # Respetar el rate limit: esperar entre llamadas
        time.sleep(0.5)
        pagina += 1

    return pd.DataFrame(todos_los_registros)
```

### 4.3 Guardar la extracción en staging con nombre por fecha

Una práctica importante en producción es guardar los datos extraídos con la **fecha de extracción en el nombre del archivo**, para tener trazabilidad histórica.

```python
import requests
import pandas as pd
from pathlib import Path
from datetime import date

def extraer_y_guardar_staging(url: str, api_key: str, nombre: str) -> str:
    """
    Extrae datos y los guarda en el área de staging con fecha en el nombre.
    Retorna la ruta del archivo guardado.
    """
    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=30
    )
    response.raise_for_status()

    df = pd.DataFrame(response.json())

    # Crear carpeta staging si no existe
    staging_dir = Path("staging") / nombre
    staging_dir.mkdir(parents=True, exist_ok=True)

    # Nombre del archivo con fecha de ejecución
    fecha_hoy = date.today().strftime("%Y%m%d")
    ruta_archivo = staging_dir / f"{nombre}_{fecha_hoy}.parquet"

    # Guardar en Parquet (más eficiente que CSV para grandes volúmenes)
    df.to_parquet(ruta_archivo, index=False)
    print(f"[STAGING] {len(df)} registros guardados en: {ruta_archivo}")

    return str(ruta_archivo)
```

---

## 5. Web Scraping Ético con BeautifulSoup

El **web scraping** es la técnica de extraer datos de páginas web mediante código. Es una fuente legítima de datos cuando se respetan ciertas reglas.

### 5.1 Consideraciones éticas y legales

Antes de hacer scraping de cualquier sitio, se deben verificar tres cosas:

1. **`robots.txt`:** El archivo `/robots.txt` de cualquier sitio define qué rutas están permitidas o prohibidas para bots. Respetarlo es obligatorio en términos legales y éticos.
2. **Términos de servicio:** Algunos sitios prohíben explícitamente el scraping en sus ToS.
3. **Carga al servidor:** Hacer miles de requests por segundo puede tumbar un servidor pequeño. Agregar pausas entre requests es una cortesía esencial.

```bash
pip install requests beautifulsoup4 lxml
```

### 5.2 Scraping de una tabla HTML pública

```python
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrapear_tabla_html(url: str) -> pd.DataFrame:
    """
    Extrae la primera tabla HTML de una página pública.
    """
    headers = {
        # Identificarse con un User-Agent descriptivo es buena práctica
        "User-Agent": "Mozilla/5.0 (compatible; DataEngBot/1.0; educativo)"
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    # Parsear el HTML
    soup = BeautifulSoup(response.text, "lxml")

    # Buscar la primera tabla
    tabla = soup.find("table")
    if not tabla:
        raise ValueError(f"No se encontró ninguna tabla en {url}")

    # Extraer encabezados
    encabezados = [th.get_text(strip=True) for th in tabla.find_all("th")]

    # Extraer filas
    filas = []
    for tr in tabla.find_all("tr")[1:]:  # Saltar la fila de encabezado
        celdas = [td.get_text(strip=True) for td in tr.find_all("td")]
        if celdas:
            filas.append(celdas)

    df = pd.DataFrame(filas, columns=encabezados if encabezados else None)
    print(f"Tabla extraída: {len(df)} filas × {len(df.columns)} columnas")
    return df


# Pausa obligatoria entre requests al mismo dominio
time.sleep(2)
```

---

## Resumen de la Clase

```
┌──────────────────────────────────────────────────────────────────────┐
│              ESTRATEGIAS DE EXTRACCIÓN                              │
├─────────────────────────┬────────────────────────────────────────── │
│  Full Load              │  Incremental                              │
│  ─────────              │  ───────────                              │
│  + Simple               │  + Eficiente para tablas grandes          │
│  + Idempotente          │  + Menor carga en el sistema fuente       │
│  - Lento para tablas    │  - Requiere columna de fecha/ID           │
│    grandes              │  - Más lógica a implementar               │
├─────────────────────────┴────────────────────────────────────────── │
│              HERRAMIENTAS DE EXTRACCIÓN                             │
├──────────────────────────────────────────────────────────────────── │
│  psycopg2       → Extracción directa desde PostgreSQL               │
│  SQLAlchemy     → Abstracción multi-motor (PostgreSQL, MySQL, etc.) │
│  requests       → Consumir APIs REST con autenticación              │
│  BeautifulSoup  → Scraping de páginas HTML públicas                 │
└──────────────────────────────────────────────────────────────────── │
```

---

> 💡 **Para la próxima clase:** Tenemos los datos en el área de staging. Ahora viene la etapa más desafiante y creativa del ETL: la **Transformación**. Vamos a limpiar, normalizar, enriquecer y estructurar esos datos crudos para que sean analíticamente útiles.
