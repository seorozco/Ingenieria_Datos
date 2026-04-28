---
applyTo: "**/elt_clientes.ipynb"
---

# Instrucciones ELT: Ingesta y Transformación de Clientes

## Contexto

Pipeline ELT en Python/Pandas sobre Jupyter Notebook.

| Elemento | Detalle |
|----------|---------|
| **Fuente** | `datos/input/clientes_crudos.csv` |
| **Bronze** | `datos/output/bronze/clientes_YYYYMMDD.parquet` |
| **Inválidos** | `datos/output/bronze/invalidos_clientes_YYYYMMDD.parquet` |
| **Silver Delta Table** | `datos/silver/clientes_delta/` |

---

## Estilo y Convenciones del Notebook

El notebook debe seguir el estilo pedagógico del proyecto:

- Celda markdown de encabezado con título, tabla de contenidos, asignatura, docente y tecnologías.
- Cada sección tiene una celda markdown explicativa antes del bloque de código.
- Banners de separación internos con `# ── Descripción ─────────────────────`.
- Prints de diagnóstico con `"=== TÍTULO EN MAYÚSCULAS ==="`.
- Confirmaciones de guardado/carga con `✅` / `❌`.
- Constantes en `MAYUSCULAS`, DataFrames con prefijo `df_`, rutas con `pathlib.Path`.
- Trabajar siempre sobre `df.copy()` para preservar el DataFrame original.

## Principios de Legibilidad y Didáctica

El notebook es material de clase. El código y la documentación deben ser comprensibles
para alumnos que están aprendiendo ingeniería de datos. Aplicar siempre:

### Simplicidad del código
- Preferir la solución más simple y directa sobre la más compacta o "pythónica".
- Evitar comprensiones de listas, lambdas o encadenamientos de métodos complejos cuando
  una versión con pasos explícitos sea más fácil de leer.
- Una operación por línea cuando el alumno se beneficia de verla separada.
- No usar librerías adicionales si la funcionalidad ya está disponible en `pandas` o
  en la biblioteca estándar de Python.

### Comentarios en el código
- Cada bloque lógico dentro de una celda debe tener un comentario que explique
  **qué hace** y, cuando no sea obvio, **por qué**.
- Los comentarios deben estar en español y redactados en lenguaje simple, como si se
  le explicara a un compañero de clase.
- Usar el banner `# ── Descripción ─────────────────────` para separar bloques
  dentro de una misma celda.
- Ejemplo de buen comentario:
  ```python
  # Leemos el CSV con dtype=str para que el documento "01234567" no pierda el cero
  # inicial al ser interpretado como número entero.
  df_bronze = pd.read_csv(ARCHIVO_FUENTE, dtype=str, encoding="utf-8")
  ```

### Documentación en celdas markdown
- Antes de cada celda de código incluir una celda markdown que explique:
  1. **Qué** se hace en esa celda (objetivo concreto).
  2. **Por qué** se hace de esa manera (decisión de diseño o buena práctica).
  3. **Qué resultado** se espera ver al ejecutarla.
- Usar listas, tablas o blockquotes (`>`) para destacar conceptos clave.
- Cuando se introduce un concepto nuevo (ej: Bronze layer, Delta Table, upsert),
  agregar una breve definición en la celda markdown correspondiente.

### Docstrings en funciones
- Toda función definida en el notebook debe tener un docstring en español que incluya:
  - Descripción de qué hace la función en una línea.
  - Parámetros con tipo y descripción.
  - Valor de retorno con tipo y descripción.
  - Ejemplo de uso si la función tiene lógica no trivial.
- Ejemplo:
  ```python
  def validar_registro(fila: pd.Series) -> list:
      """
      Evalúa si una fila del DataFrame cumple con las reglas de calidad de datos.

      Parámetros
      ----------
      fila : pd.Series
          Una fila del DataFrame de clientes.

      Retorna
      -------
      list
          Lista de claves de VALIDATION_ERRORS con los errores encontrados.
          Si la lista está vacía, el registro es válido.

      Ejemplo
      -------
      errores = validar_registro(df.iloc[0])
      # ['email_invalido'] si el email no tiene formato correcto
      """
  ```

---

## Sección 1 — Instalación de Dependencias

Instalar las dependencias necesarias en una sola celda:

```python
%pip install pyarrow deltalake
```

---

## Sección 2 — Importación de Librerías y Constantes

```python
import re
import pyarrow as pa
import pandas as pd
from pathlib import Path
from datetime import datetime
from deltalake import DeltaTable, write_deltalake

# ── Rutas ─────────────────────────────────────────────────────────────────────
DIR_BASE   = Path("datos")
DIR_INPUT  = DIR_BASE / "input"
DIR_OUTPUT = DIR_BASE / "output"
DIR_SILVER = DIR_BASE / "silver"

DIR_OUTPUT.mkdir(parents=True, exist_ok=True)
DIR_SILVER.mkdir(parents=True, exist_ok=True)

# ── Parámetros de ejecución ───────────────────────────────────────────────────
FECHA_INGESTA  = datetime.today().strftime("%Y%m%d")
ARCHIVO_FUENTE = DIR_INPUT / "clientes_crudos.csv"
BRONZE_PATH    = DIR_OUTPUT / f"bronze_clientes_{FECHA_INGESTA}.parquet"
INVALIDOS_PATH = DIR_OUTPUT / f"invalidos_clientes_{FECHA_INGESTA}.parquet"
DELTA_PATH     = str(DIR_SILVER / "clientes_delta")

# ── Diccionario de errores de validación ──────────────────────────────────────
VALIDATION_ERRORS = {
    "nombres_invalido"    : "nombres contiene dígitos o está vacío",
    "apellidos_invalido"  : "apellidos contiene dígitos o está vacío",
    "documento_invalido"  : "numero_documento nulo, no numérico o fuera del rango 6-8 dígitos",
    "fecha_alta_invalida" : "fecha_alta es nula o no tiene formato de fecha válido",
    "email_invalido"      : "email presente pero no tiene formato válido",
    "telefono_invalido"   : "nro_telefono presente pero no tiene formato válido",
    "sin_metodo_contacto" : "no tiene email ni teléfono con formato válido",
}

print("=== CONSTANTES INICIALIZADAS ===")
print(f"  Fecha de ingesta : {FECHA_INGESTA}")
print(f"  Fuente           : {ARCHIVO_FUENTE}")
print(f"  Bronze destino   : {BRONZE_PATH}")
print(f"  Inválidos destino: {INVALIDOS_PATH}")
print(f"  Delta Table path : {DELTA_PATH}")
```

---

## Sección 3 — PARTE A: Ingesta Bronze

### Objetivo
Leer el CSV crudo sin transformaciones y persistirlo como Parquet con fecha de ingesta,
simulando la capa Bronze de una arquitectura Medallion.

### Instrucciones de código

1. Leer `ARCHIVO_FUENTE` con `pd.read_csv(..., dtype=str, encoding="utf-8")`.
   - `dtype=str` es **obligatorio** para preservar ceros iniciales en `numero_documento`
     (ej: `"01234567"` no debe convertirse a `1234567`).
2. Reemplazar valores vacíos de tipo string por `None` con `.replace("", None)`.
3. Agregar columna `fecha_ingesta` con valor `FECHA_INGESTA` (string `"YYYYMMDD"`).
4. Guardar en `BRONZE_PATH` con `df.to_parquet(..., engine="pyarrow", index=False)`.
5. Imprimir forma del DataFrame `(filas, columnas)` y confirmar con `✅`.

```python
# ── Lectura del CSV crudo ─────────────────────────────────────────────────────
df_bronze = pd.read_csv(ARCHIVO_FUENTE, dtype=str, encoding="utf-8")
df_bronze = df_bronze.replace("", None)
df_bronze["fecha_ingesta"] = FECHA_INGESTA

print("=== BRONZE — INGESTA ===")
print(f"  Filas x Columnas : {df_bronze.shape}")
print(df_bronze.dtypes)

# ── Guardado Parquet ──────────────────────────────────────────────────────────
df_bronze.to_parquet(BRONZE_PATH, engine="pyarrow", index=False)
print(f"\n✅ Bronze guardado en: {BRONZE_PATH}")
```

---

## Sección 4 — PARTE B: Transformación y Validación

### B1 — Carga desde Bronze

Leer el Parquet bronze y trabajar sobre una copia para no modificar el original.

```python
df_raw    = pd.read_parquet(BRONZE_PATH, engine="pyarrow")
df_trabajo = df_raw.copy()
print(f"=== SILVER — CARGA DESDE BRONZE: {df_trabajo.shape} ===")
```

### B2 — Correcciones silenciosas

Aplicar `pd.to_datetime(..., errors='coerce')` a `fecha_nacimiento` y `fecha_baja`.

- Si el valor no es parseable → queda `NaT`.
- El registro **permanece en válidos** (no es causal de invalidación).
- Guardar estado booleano de si el campo era no nulo antes de parsear, para comparación
  en la regla de email/teléfono de la función de validación.

```python
# ── Corrección silenciosa de fechas opcionales ────────────────────────────────
df_trabajo["fecha_nacimiento"] = pd.to_datetime(
    df_trabajo["fecha_nacimiento"], errors="coerce"
)
df_trabajo["fecha_baja"] = pd.to_datetime(
    df_trabajo["fecha_baja"], errors="coerce"
)
print("=== CORRECCIONES SILENCIOSAS APLICADAS ===")
print(f"  fecha_nacimiento NaT: {df_trabajo['fecha_nacimiento'].isna().sum()}")
print(f"  fecha_baja       NaT: {df_trabajo['fecha_baja'].isna().sum()}")
```

### B3 — Función de validación

Definir `validar_registro(fila: pd.Series) -> list[str]` que retorna una lista de
claves de `VALIDATION_ERRORS` que aplican a esa fila.

**Tabla de reglas:**

| # | Campo | Regla | Clave de error |
|---|-------|-------|----------------|
| 1 | `nombres` | No contiene dígitos (`re.search(r'\d', valor)`). No es nulo ni vacío tras `.strip()`. | `"nombres_invalido"` |
| 2 | `apellidos` | Misma regla que nombres. | `"apellidos_invalido"` |
| 3 | `numero_documento` | No nulo. Solo dígitos y longitud 6–8 (`re.fullmatch(r'\d{6,8}', valor)`). | `"documento_invalido"` |
| 4 | `fecha_alta` | No nulo. Parseable como fecha (`pd.to_datetime(..., errors='coerce')` no es `NaT`). | `"fecha_alta_invalida"` |
| 5 | `email` | Si no es nulo/vacío: validar con `re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", valor)`. | `"email_invalido"` |
| 6 | `nro_telefono` | Si no es nulo/vacío: validar con `re.fullmatch(r"\+?\d{7,15}", valor)`. | `"telefono_invalido"` |
| 7 | Contacto | Si email **y** teléfono son ambos nulos/vacíos **o** ambos fallaron sus validaciones. | `"sin_metodo_contacto"` |

> **Nota regla 7:** Un campo de contacto se considera disponible si existe (no nulo) y
> pasó la validación de su respectiva regla (5 ó 6). Si ninguno de los dos está
> disponible, agregar `"sin_metodo_contacto"`.

```python
def validar_registro(fila: pd.Series) -> list:
    """
    Recibe una fila del DataFrame y retorna una lista con las claves
    de VALIDATION_ERRORS que corresponden a los errores encontrados.
    """
    errores = []

    # ── Regla 1: nombres ──────────────────────────────────────────────────────
    nombres = str(fila.get("nombres") or "").strip()
    if not nombres or bool(re.search(r"\d", nombres)):
        errores.append("nombres_invalido")

    # ── Regla 2: apellidos ────────────────────────────────────────────────────
    apellidos = str(fila.get("apellidos") or "").strip()
    if not apellidos or bool(re.search(r"\d", apellidos)):
        errores.append("apellidos_invalido")

    # ── Regla 3: numero_documento ─────────────────────────────────────────────
    doc = str(fila.get("numero_documento") or "").strip()
    if not doc or not re.fullmatch(r"\d{6,8}", doc):
        errores.append("documento_invalido")

    # ── Regla 4: fecha_alta ───────────────────────────────────────────────────
    fecha_alta_raw = fila.get("fecha_alta")
    if pd.isna(fecha_alta_raw) or pd.to_datetime(fecha_alta_raw, errors="coerce") is pd.NaT:
        errores.append("fecha_alta_invalida")

    # ── Reglas 5 y 6: email y teléfono ───────────────────────────────────────
    email_raw = str(fila.get("email") or "").strip()
    tel_raw   = str(fila.get("nro_telefono") or "").strip()

    email_valido = False
    tel_valido   = False

    if email_raw:
        if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email_raw):
            email_valido = True
        else:
            errores.append("email_invalido")

    if tel_raw:
        if re.fullmatch(r"\+?\d{7,15}", tel_raw):
            tel_valido = True
        else:
            errores.append("telefono_invalido")

    # ── Regla 7: al menos un método de contacto ───────────────────────────────
    if not email_valido and not tel_valido:
        errores.append("sin_metodo_contacto")

    return errores
```

### B4 — Aplicar validación y separar DataFrames

```python
# ── Aplicar validación fila por fila ─────────────────────────────────────────
df_trabajo["motivo_invalido"] = df_trabajo.apply(
    lambda fila: "; ".join(validar_registro(fila)), axis=1
)

# ── Separar en válidos e inválidos ────────────────────────────────────────────
df_invalidos = df_trabajo[df_trabajo["motivo_invalido"] != ""].copy()
df_validos   = (
    df_trabajo[df_trabajo["motivo_invalido"] == ""]
    .drop(columns=["motivo_invalido"])
    .copy()
)

print("=== RESULTADO DE VALIDACIÓN ===")
print(f"  ✅ Registros válidos  : {len(df_validos)}")
print(f"  ❌ Registros inválidos: {len(df_invalidos)}")
```

### B5 — Guardado de inválidos

```python
df_invalidos.to_parquet(INVALIDOS_PATH, engine="pyarrow", index=False)
print(f"\n✅ Inválidos guardados en: {INVALIDOS_PATH}")
print("\n=== DETALLE DE INVÁLIDOS ===")
print(df_invalidos[["id_cliente", "nombres", "apellidos", "numero_documento", "motivo_invalido"]])
```

---

## Sección 5 — PARTE C: Carga a Delta Table

### Objetivo
Upsert de `df_validos` en la Delta Table Silver usando `numero_documento` como PK.
Se usa la librería `deltalake` (delta-rs), **sin PySpark**.

### Instrucciones de código

1. Convertir `df_validos` a `pyarrow.Table` con `pa.Table.from_pandas(df_validos)`.
2. Verificar existencia con `DeltaTable.is_deltatable(DELTA_PATH)`.
3. **Si NO existe** → crear con `write_deltalake(..., mode="overwrite")`.
4. **Si existe** → MERGE/UPSERT con predicado por `numero_documento`.
5. Mostrar conteo final de registros en la tabla.

```python
# ── Conversión a PyArrow Table ────────────────────────────────────────────────
pa_table = pa.Table.from_pandas(df_validos, preserve_index=False)

# ── Verificar existencia de la Delta Table ────────────────────────────────────
if not DeltaTable.is_deltatable(DELTA_PATH):
    print("=== DELTA TABLE NO EXISTE — CREANDO ===")
    write_deltalake(DELTA_PATH, pa_table, mode="overwrite")
    print(f"✅ Delta Table creada en: {DELTA_PATH}")
else:
    print("=== DELTA TABLE EXISTE — EJECUTANDO MERGE ===")
    dt = DeltaTable(DELTA_PATH)
    (
        dt.merge(
            source=pa_table,
            predicate="source.numero_documento = target.numero_documento",
            source_alias="source",
            target_alias="target",
        )
        .when_matched_update_all()
        .when_not_matched_insert_all()
        .execute()
    )
    print(f"✅ Merge ejecutado en: {DELTA_PATH}")

# ── Conteo final ──────────────────────────────────────────────────────────────
total_delta = DeltaTable(DELTA_PATH).to_pandas().shape[0]
print(f"\n=== DELTA TABLE — ESTADO FINAL ===")
print(f"  Total registros en Silver: {total_delta}")
print(f"  Delta log en             : {DELTA_PATH}/_delta_log")
```

---

## Sección 6 — Resumen Final

Agregar celda markdown de resumen al final del notebook:

| Capa | Formato | Descripción | Ruta |
|------|---------|-------------|------|
| Bronze | Parquet | Todos los registros crudos con fecha de ingesta | `datos/output/bronze_clientes_YYYYMMDD.parquet` |
| Inválidos | Parquet | Registros que no pasaron validación + motivo | `datos/output/invalidos_clientes_YYYYMMDD.parquet` |
| Silver | Delta Table | Registros válidos con upsert por `numero_documento` | `datos/silver/clientes_delta/` |

---

## Dependencias requeridas

```
pyarrow>=14.0
deltalake>=0.17
pandas>=2.0
```

---

## Casos de prueba esperados

Al ejecutar el notebook con `clientes_crudos.csv` los siguientes registros deben
quedar en `df_invalidos`:

| `id_cliente` | Motivo esperado |
|-------------|----------------|
| 15 | `documento_invalido` |
| 16 | `email_invalido` |
| 17 | `telefono_invalido` |
| 34 | `email_invalido` |
| 35 | `telefono_invalido` |
| 36 | `nombres_invalido` |
| 37 | `apellidos_invalido` |
| 38 | `sin_metodo_contacto` |

Los registros 13 (sin fecha_nacimiento), 33 (sin teléfono pero con email válido) y
14 (con fecha_baja) deben quedar en `df_validos`.
