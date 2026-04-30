# Trabajo Práctico — Unidad II
## Pipeline ETL con Python: del Dato Crudo al Dato Confiable

> **Asignatura:** Ingeniería de Datos  
> **Docente:** Ing. Sergio Orozco  
> **Unidad:** II — Orígenes de Datos y Proceso ETL  
> **Modalidad:** Individual o grupal (máx. 2 integrantes)  
> **Fecha de entrega:** A definir por el docente

---

## Descripción General

En este trabajo práctico, el alumno deberá construir un **pipeline ETL (o ELT) completo en Python**, que cubra las tres fases del proceso: **Extracción**, **Transformación** y **Carga**, siguiendo la arquitectura de capas **Bronze → Silver**.

El trabajo integra todos los contenidos de la Unidad II:

| Clase | Tema | Aplicación en el TP |
|---|---|---|
| Clase 03 | Tipos de Bases de Datos | Elección del destino final (SQL, Delta, etc.) |
| Clase 04 | Extracción de Datos | Implementación de la capa Bronze |
| Clase 05 | Transformación de Datos | Limpieza, homologación y validaciones |
| Clase 06 | Carga de Datos y Orquestación | Estrategia de carga y archivo Silver |

---

## Arquitectura del Pipeline

El pipeline que deben implementar sigue el siguiente flujo:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      ARQUITECTURA BRONZE → SILVER                      │
│                                                                         │
│  FUENTE DE DATOS          CAPA BRONZE           CAPA SILVER            │
│  (con errores)                                                          │
│                                                                         │
│  ┌─────────────┐          ┌──────────────┐      ┌──────────────────┐   │
│  │ CSV / XLSX  │          │              │      │                  │   │
│  │ JSON / TXT  │  Extract │  bronze/     │Trans-│  silver/         │   │
│  │ API REST    │ ────────►│  datos_      │form  │  datos_          │   │
│  │ Web Scrap.  │          │  raw.csv     │─────►│  limpios         │   │
│  │ BD SQL      │          │  (sin tocar) │      │  (destino final) │   │
│  └─────────────┘          └──────────────┘      └──────────────────┘   │
│                                                                         │
│                           ← datos originales →  ← datos curados →      │
│                             con todos sus        limpios, validados     │
│                             errores              y homologados          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Requisitos del Trabajo

### Requisito 1 — Fuente de Datos con Errores Reales

El dataset de origen **debe contener errores intencionales** que el pipeline deberá detectar y tratar. Los errores requeridos son (mínimo 5 de los siguientes):

| # | Tipo de Error | Ejemplo |
|---|---|---|
| 1 | **Valores nulos o vacíos** en columnas obligatorias | `nombre = ""` o `NaN` |
| 2 | **Formatos de fecha inconsistentes** | `"15/03/2024"`, `"2024-03-15"`, `"March 15 2024"` |
| 3 | **Valores monetarios mal formateados** | `"$1.500,00"`, `"1500.00"`, `"1,500"` |
| 4 | **Texto con mayúsculas/minúsculas inconsistentes** | `"BUENOS AIRES"`, `"buenos aires"`, `"Buenos Aires"` |
| 5 | **Duplicados** (filas repetidas total o parcialmente) | Mismo ID con distinta fecha |
| 6 | **Outliers** fuera del rango válido de negocio | Edad = -5, precio = 0, monto = 99999999 |
| 7 | **Códigos o categorías no estandarizadas** | `"M"`, `"Masculino"`, `"masc"`, `"male"` para género |
| 8 | **Caracteres especiales o encoding** | `"Gar?a"`, `"São Paulo"` mal codificado |
| 9 | **Tipos de dato incorrectos** | ID numérico guardado como string `"00123"` |
| 10 | **Reglas de negocio violadas** | Fecha de fin anterior a fecha de inicio |

> **El dataset puede ser creado manualmente** (un CSV o Excel que el alumno arme) **o puede provenir de una fuente real** (una API pública, web scraping, etc.) a la que se le inyecten errores adicionales.

---

### Requisito 2 — Fuente de Datos (Elegir UNA)

Seleccionar **uno** de los siguientes tipos de origen de datos. La elección condiciona la implementación de la fase de extracción:

| Opción | Origen | Librerías sugeridas |
|---|---|---|
| **A** | Archivo CSV con errores | `pandas` |
| **B** | Archivo Excel (.xlsx) con múltiples hojas | `pandas`, `openpyxl` |
| **C** | Archivo JSON anidado | `json`, `pandas` |
| **D** | Archivo de texto delimitado (.txt o .dat) | `pandas`, `csv` |
| **E** | **API REST pública** (con paginación) | `requests`, `pandas` |
| **F** | **Web Scraping** de un sitio público | `requests`, `BeautifulSoup` |
| **G** | **Base de datos SQL Server o SQLite** existente | `sqlite3` / `pyodbc`, `SQLAlchemy` |

> Se valorará positivamente la elección de las opciones E, F o G por mayor complejidad técnica.

> **Nota:** En caso de usar una base de datos como fuente (opción G), se debe adjuntar el **script SQL de creación** de la base de datos y sus tablas (DDL), junto con el script de inserción de datos de prueba, para que el pipeline pueda ser reproducido por el docente.

---

### Requisito 3 — Capa Bronze: Persistencia del Dato Original

Una vez extraídos los datos, deben guardarse **sin ninguna modificación** en la capa Bronze.

**Regla fundamental de la capa Bronze:** los datos se almacenan tal cual llegan de la fuente, con todos sus errores. Esta capa es la fuente de verdad histórica del dato crudo y permite reproducir cualquier transformación posterior.

**Formato de archivo Bronze aceptado:**

| Formato | Descripción |
|---|---|
| CSV | Formato universal, fácil de auditar |
| JSON | Para datos semi-estructurados |
| Parquet | Formato columnar eficiente (valorado positivamente) |

**Estructura de carpetas sugerida:**

```
mi_pipeline/
├── data/
│   ├── bronze/
│   │   └── datos_raw_YYYYMMDD.csv     ← extracción sin modificar
│   └── silver/
│       └── datos_limpios.db           ← destino final curado
├── src/
│   ├── extraccion.py
│   ├── transformacion.py
│   └── carga.py
├── documentacion/
│   └── transformaciones.md            ← documento obligatorio
└── main.py                            ← script principal del pipeline
```

---

### Requisito 4 — Fase de Transformación: Limpieza y Curación

La capa de transformación debe incluir, como mínimo, las siguientes operaciones. **Cada operación debe estar documentada** (ver Requisito 6):

#### 4.1 Limpieza de Nulos

```python
# Ejemplo mínimo esperado:
# - Identificar columnas con nulos y su porcentaje
# - Decidir estrategia para cada columna: eliminar fila, imputar valor, marcar como 'DESCONOCIDO'
# - Documentar cada decisión
```

#### 4.2 Eliminación de Duplicados

Identificar y eliminar registros duplicados. Definir el criterio de unicidad (¿qué columnas determinan que dos filas son el mismo registro?).

#### 4.3 Homologación de Categorías

Estandarizar los valores de columnas categóricas a un conjunto cerrado de valores válidos.

```python
# Ejemplo:
# "M", "Masculino", "masc", "male" → "M"
# "F", "Femenino", "fem", "female" → "F"
```

#### 4.4 Normalización de Formatos

- **Fechas:** convertir todos los formatos a `YYYY-MM-DD` (ISO 8601).
- **Montos:** eliminar símbolos de moneda, separadores de miles y convertir a `float`.
- **Textos:** eliminar espacios extra, aplicar capitalización consistente (`.strip()`, `.title()`, `.upper()`).
- **Tipos de dato:** convertir IDs a entero, fechas a tipo datetime, montos a float.

#### 4.5 Validaciones de Negocio

Definir y aplicar al menos **3 reglas de negocio** propias del dominio elegido. Ejemplos:

| Dominio | Reglas posibles |
|---|---|
| Ventas | Monto > 0, fecha_venta <= fecha_actual, cliente_id no nulo |
| RR.HH. | Edad entre 18 y 70, sueldo > salario mínimo, fecha_ingreso <= fecha_actual |
| Inventario | Stock >= 0, precio_costo < precio_venta, código SKU único |
| Estudiantes | Nota entre 0 y 10, DNI sin letras, carrera en lista de carreras válidas |

Los registros que violen las reglas de negocio deben:
- Ser **registrados en un log de rechazos** (archivo separado o tabla en la BD).
- **No pasar a la capa Silver**.

---

### Requisito 5 — Capa Silver: Estrategia de Carga (Elegir UNA)

Los datos transformados y validados deben cargarse en el destino final usando **una** de las siguientes estrategias:

| Estrategia | Descripción | Cuándo usarla |
|---|---|---|
| **Full Load** | Reemplaza completamente la tabla destino | El dataset es pequeño y siempre se procesa completo |
| **Append** | Agrega los registros nuevos sin modificar los existentes | Logs, eventos, registros históricos que nunca cambian |
| **Upsert** | Inserta si no existe, actualiza si ya existe | Registros que pueden modificarse (clientes, productos) |
| **Delta / Incremental** | Solo carga los registros nuevos o modificados desde el último proceso | Tablas grandes con muchas actualizaciones |

**Destino final Silver aceptado (Elegir UNO):**

| Opción | Descripción | Librerías |
|---|---|---|
| **SQLite** | BD relacional embebida, sin servidor | `sqlite3`, `SQLAlchemy` |
| **CSV / Parquet** | Archivo en disco | `pandas` |
| **Delta Table** | Formato transaccional open-source (avanzado) | `deltalake` |
| **Apache Iceberg** | Formato de tabla analítica open-source (avanzado) | `pyiceberg` |

---

### Requisito 6 — Documento de Transformaciones (OBLIGATORIO)

Deben entregar un documento `transformaciones.md` (o `transformaciones.docx`) que incluya:

1. **Descripción del dataset:** origen, dominio, cantidad de registros, columnas y sus tipos.
2. **Inventario de errores encontrados:** tabla con cada error detectado, su columna, frecuencia y ejemplo.
3. **Decisiones de transformación:** para cada error, la decisión tomada y su justificación.
4. **Reglas de negocio aplicadas:** descripción de cada regla, columna que valida y acción ante violación.
5. **Resultados del proceso:** cuántos registros entraron, cuántos pasaron a Silver, cuántos fueron rechazados.

**Plantilla sugerida para el documento:**

```markdown
## Inventario de Errores

| # | Columna | Tipo de Error | Frecuencia | Ejemplo | Decisión | Justificación |
|---|---------|--------------|------------|---------|----------|---------------|
| 1 | email   | Nulo         | 12 (8%)    | NaN     | Eliminar fila | Email es identificador obligatorio |
| 2 | fecha   | Formato mixto| 45 (30%)   | "15/03/24" | Parsear con dateutil | ... |

## Reglas de Negocio

| # | Regla | Columnas | Condición | Acción |
|---|-------|----------|-----------|--------|
| 1 | Monto positivo | monto | monto > 0 | Rechazar y loguear |

## Resultados del Proceso

| Etapa | Registros |
|---|---|
| Extraídos (Bronze) | 150 |
| Rechazados por nulos | 12 |
| Rechazados por reglas de negocio | 5 |
| Cargados en Silver | 133 |
```

---

## Criterios de Evaluación

| Criterio | Peso | Descripción |
|---|---|---|
| **Extracción funcional** | 15% | El script de extracción corre sin errores y guarda correctamente la capa Bronze |
| **Calidad de transformaciones** | 30% | Todas las transformaciones están implementadas y son correctas |
| **Estrategia de carga** | 15% | La carga Silver usa la estrategia elegida correctamente (Full/Append/Upsert/Delta) |
| **Documento de transformaciones** | 25% | Completo, claro y con todas las secciones requeridas |
| **Calidad del código** | 10% | Código legible, con funciones, sin repetición innecesaria |
| **Bonus: complejidad** | +5% | Uso de API, web scraping, Delta Table o Parquet como destino |

---

## Entregables

El alumno debe entregar un **repositorio comprimido (.zip)** o un **enlace a GitHub** con la siguiente estructura:

```
apellido_nombre_tp_unidad2/
├── data/
│   ├── fuente/                ← dataset original con errores
│   ├── bronze/                ← datos extraídos sin modificar
│   └── silver/                ← datos finales curados
├── src/
│   ├── extraccion.py          ← OBLIGATORIO
│   ├── transformacion.py      ← OBLIGATORIO
│   └── carga.py               ← OBLIGATORIO
├── documentacion/
│   └── transformaciones.md   ← OBLIGATORIO
├── main.py                    ← script principal que ejecuta todo el pipeline
└── requirements.txt           ← dependencias del proyecto
```

> **El pipeline debe poder ejecutarse** corriendo `python main.py` desde la raíz del proyecto, sin modificaciones.

---

## Ejemplos de Datasets con Errores

Si el alumno no tiene una fuente propia, puede usar uno de los siguientes datasets de ejemplo (disponibles en la carpeta `notebook/unidad_II/datos/input/` del repositorio de la materia):

| Archivo | Dominio | Errores incluidos |
|---|---|---|
| `clientes_crudos.csv` | Clientes de comercio | Nulos en email, fechas inconsistentes, categorías mixtas |
| `ventas_crudas.csv` | Transacciones de ventas | Montos mal formateados, duplicados, outliers |

También se puede usar cualquier dataset público de:
- [Kaggle](https://www.kaggle.com/datasets) — buscar datasets con la etiqueta "dirty data" o "data cleaning"
- [datos.gob.ar](https://datos.gob.ar) — datos abiertos del gobierno argentino
- Cualquier API pública (OpenWeatherMap, CoinGecko, JSONPlaceholder, etc.)

---

## Preguntas Frecuentes

**¿Puedo usar Jupyter Notebook en lugar de scripts `.py`?**  
Sí, pero el notebook debe estar organizado con celdas claras para cada fase (extracción, transformación, carga) y los archivos de datos deben generarse igual.

**¿Cuántos registros debe tener el dataset?**  
Mínimo 100 registros. Se recomienda entre 200 y 1000 para que las transformaciones sean representativas.

**¿El documento de transformaciones puede ser el mismo notebook?**  
Sí, en ese caso el notebook debe incluir celdas Markdown explicativas para cada decisión de transformación además del código. No alcanza con comentarios en el código.

**¿Puedo usar otras librerías además de pandas?**  
Sí. Librerías como `great_expectations`, `pydantic`, `cerberus` o `pandera` para validaciones son bienvenidas y suman al criterio de calidad del código.

---

## Recursos de Consulta

- [Clase 04 — Extracción de Datos](./04%20-%20Extracción%20de%20Datos.md)
- [Clase 05 — Transformación de Datos](./05%20-%20Transformación%20de%20Datos.md)
- [Clase 06 — Carga de Datos y Orquestación](./06%20-%20Carga%20de%20Datos%20y%20Orquestación.md)
- Documentación oficial de pandas: https://pandas.pydata.org/docs/
- Documentación de SQLAlchemy: https://docs.sqlalchemy.org/
- Documentación de Delta Lake (Python): https://delta-io.github.io/delta-rs/
