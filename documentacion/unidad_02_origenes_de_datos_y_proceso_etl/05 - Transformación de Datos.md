# Clase 05 — Transformación de Datos (Transform)

> **Asignatura:** Ingeniería de Datos  
> **Docente:** Ing. Sergio Orozco  
> **Unidad:** II — Orígenes de Datos y Proceso ETL

---

## Objetivos de la Clase

Al finalizar esta clase, el alumno será capaz de:

- Aplicar un **pipeline de limpieza** completo sobre un dataset sucio.
- Normalizar fechas, textos y valores monetarios con formatos heterogéneos.
- Enriquecer un dataset realizando **joins** entre tablas usando pandas.
- Calcular **agregaciones** (GROUP BY) y crear **tablas pivot**.
- Explicar la diferencia entre **ETL y ELT** y cuándo usar cada paradigma.
- Derivar **columnas calculadas** a partir de datos existentes.

---

## 1. ¿Qué es la Transformación?

La transformación es la etapa más **compleja y creativa** del ETL. Su objetivo es convertir los datos crudos extraídos de las fuentes en datos **limpios, consistentes, enriquecidos y listos para el análisis**.

```
┌────────────────────────────────────────────────────────────────────┐
│                     QUÉ HACE LA TRANSFORMACIÓN                     │
│                                                                    │
│  DATOS CRUDOS                          DATOS TRANSFORMADOS         │
│  (del staging)                         (listos para carga)         │
│                                                                    │
│  ❌ Duplicados             ────►   ✅ Sin duplicados               │
│  ❌ Valores nulos                  ✅ Nulos manejados              │
│  ❌ Fechas con 3 formatos          ✅ Fechas en formato ISO        │
│  ❌ "ARS", "ars", "pesos"          ✅ Todo "ARS"                  │
│  ❌ Montos negativos               ✅ Solo montos válidos          │
│  ❌ Sin columna de totales         ✅ total = cantidad × precio    │
│  ❌ Sin info de categoría          ✅ Enriquecido con catálogo     │
└────────────────────────────────────────────────────────────────────┘
```

**Herramienta principal en Python:** `pandas` — la librería de manipulación de datos más usada en el ecosistema de data science e ingeniería de datos.

```bash
pip install pandas numpy openpyxl
```

---

## 2. Limpieza de Datos con pandas

### 2.1 Diagnóstico inicial: conocer el problema antes de operar

El primer paso de cualquier transformación es **entender qué problemas tiene el dataset**. Sin diagnóstico, se transforma a ciegas.

```python
import pandas as pd
import numpy as np

# Dataset con problemas intencionales para practicar
data_cruda = {
    "id_venta":    [1, 2, 2, 3, 4, 5, None],
    "fecha_venta": ["2025-01-15", "15/01/2025", "15/01/2025",
                    "2025-01-16", "2025-99-01", "2025-01-17", "2025-01-18"],
    "cliente":     ["María García", "  JUAN LOPEZ ", "  JUAN LOPEZ ",
                    "Ana Torres", None, "Luis Paz", "Carlos Ruiz"],
    "monto":       [1500.0, 2300.50, 2300.50, -100.0, 850.0, 1200.0, 950.0],
    "moneda":      ["ARS", "ars", "ars", "ARS", "PESOS", "USD", "ARS"],
    "id_producto": [101, 102, 102, 103, 104, 105, 106],
}

df = pd.DataFrame(data_cruda)

# ── Diagnóstico ────────────────────────────────────────────
print("=== DIAGNÓSTICO DEL DATASET ===")
print(f"Dimensiones:     {df.shape[0]} filas × {df.shape[1]} columnas")
print(f"Filas duplicadas:{df.duplicated().sum()}")
print(f"\nValores nulos por columna:")
print(df.isnull().sum())
print(f"\nTipos de dato:")
print(df.dtypes)
print(f"\nMuestra del dataset:")
print(df.to_string())
```

**Salida esperada del diagnóstico:**
```
Dimensiones:     7 filas × 6 columnas
Filas duplicadas: 1
Valores nulos: id_venta=1, cliente=1
Problemas visibles: fechas con formatos distintos, moneda inconsistente,
                    monto negativo, ID y cliente duplicados
```

### 2.2 Pipeline de limpieza completo

```python
import pandas as pd
import numpy as np

def limpiar_dataset_ventas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pipeline de limpieza completo para el dataset de ventas.
    Cada paso documenta qué problema resuelve y cuántos registros afecta.
    """
    df_limpio = df.copy()
    n_original = len(df_limpio)

    # ── Paso 1: Eliminar filas completamente duplicadas ────────────────
    n_antes = len(df_limpio)
    df_limpio = df_limpio.drop_duplicates()
    print(f"[1] Duplicados eliminados:       {n_antes - len(df_limpio)}")

    # ── Paso 2: Eliminar filas con ID nulo ─────────────────────────────
    n_antes = len(df_limpio)
    df_limpio = df_limpio.dropna(subset=["id_venta"])
    print(f"[2] Filas sin ID eliminadas:     {n_antes - len(df_limpio)}")

    # ── Paso 3: Convertir id_venta a entero ────────────────────────────
    df_limpio["id_venta"] = df_limpio["id_venta"].astype(int)

    # ── Paso 4: Normalizar la columna 'moneda' ─────────────────────────
    # Problema: tenemos "ARS", "ars", "PESOS" — todos deberían ser "ARS"
    mapa_monedas = {"ars": "ARS", "pesos": "ARS", "PESOS": "ARS", "usd": "USD"}
    df_limpio["moneda"] = (
        df_limpio["moneda"]
        .str.strip()
        .str.upper()
    )
    df_limpio["moneda"] = df_limpio["moneda"].replace(mapa_monedas)
    print(f"[4] Valores únicos de 'moneda':  {df_limpio['moneda'].unique().tolist()}")

    # ── Paso 5: Normalizar nombre del cliente ──────────────────────────
    # Problema: "  JUAN LOPEZ " → "Juan Lopez"
    df_limpio["cliente"] = df_limpio["cliente"].str.strip().str.title()

    # ── Paso 6: Parsear fechas con manejo de errores ───────────────────
    # 'coerce' convierte fechas inválidas (como "2025-99-01") a NaT en lugar
    # de lanzar una excepción
    df_limpio["fecha_venta"] = pd.to_datetime(
        df_limpio["fecha_venta"],
        errors="coerce"
    )
    n_antes = len(df_limpio)
    df_limpio = df_limpio.dropna(subset=["fecha_venta"])
    print(f"[6] Fechas inválidas eliminadas: {n_antes - len(df_limpio)}")

    # ── Paso 7: Filtrar montos inválidos ───────────────────────────────
    # Regla de negocio: las ventas no pueden tener monto negativo o cero
    n_antes = len(df_limpio)
    df_limpio = df_limpio[df_limpio["monto"] > 0]
    print(f"[7] Montos negativos/cero elim.: {n_antes - len(df_limpio)}")

    # ── Resumen ────────────────────────────────────────────────────────
    print(f"\n=== RESULTADO ===")
    print(f"Filas originales:  {n_original}")
    print(f"Filas limpias:     {len(df_limpio)}")
    print(f"Filas descartadas: {n_original - len(df_limpio)}")

    return df_limpio.reset_index(drop=True)
```

---

## 3. Normalización y Estandarización

Normalizar significa dar el **mismo formato** a valores equivalentes que vienen de distintas fuentes con distintas convenciones.

### Normalización de fechas con múltiples formatos

```python
import pandas as pd

df = pd.DataFrame({
    "fecha_str": [
        "2025-03-10",      # ISO 8601 (estándar)
        "10/03/2025",      # DD/MM/YYYY (formato argentino)
        "March 10, 2025",  # Formato en inglés
        "10-03-25",        # Formato corto
    ]
})

# pandas intenta múltiples formatos automáticamente
# dayfirst=True: indica que el día va antes que el mes
df["fecha"] = pd.to_datetime(df["fecha_str"], dayfirst=True, errors="coerce")

print(df)
# Resultado: todos convertidos a datetime estándar
```

### Normalización de montos con formato latinoamericano

```python
import pandas as pd

df = pd.DataFrame({
    "precio_str": ["$1.250,50", "1250.50", "1,250.50", "$ 1250"]
    #               ↑ formato   ↑ estándar  ↑ USA       ↑ con espacio
    #               ARG/ES      internacional
})

df["precio"] = (
    df["precio_str"]
    .str.replace(r"[\$\s]", "", regex=True)    # Quitar $ y espacios
    .str.replace(".", "", regex=False)          # Quitar puntos de miles (formato ES/AR)
    .str.replace(",", ".", regex=False)         # Convertir coma decimal a punto
    .astype(float)
)

print(df)
# Resultado: todos como float → 1250.5
```

---

## 4. Joins, Agregaciones y Pivots

### 4.1 JOIN — Enriquecimiento de datos

Un JOIN (unión) combina dos DataFrames basándose en una columna en común. Es el equivalente en pandas del JOIN de SQL.

```python
import pandas as pd

# Ventas (extraídas del sistema transaccional)
df_ventas = pd.DataFrame({
    "id_venta":    [1, 2, 3, 4, 5],
    "id_producto": [101, 102, 101, 103, 102],
    "cantidad":    [2, 1, 3, 1, 2],
    "precio_unit": [1500.0, 2300.0, 1500.0, 850.0, 2300.0],
})

# Catálogo de productos (dimensión de referencia)
df_productos = pd.DataFrame({
    "id_producto": [101, 102, 103],
    "nombre":      ["Laptop Básica", 'Monitor 24"', "Teclado Mecánico"],
    "categoria":   ["Computación", "Periféricos", "Periféricos"],
    "proveedor":   ["TechCo", "ViewMax", "KeyMaster"],
})

# LEFT JOIN: enriquecer ventas con nombre, categoría y proveedor
# how='left' → mantiene TODOS los registros de ventas aunque no haya producto
df_enriquecido = df_ventas.merge(df_productos, on="id_producto", how="left")

# Columna derivada: calcular el total de cada venta
df_enriquecido["total"] = df_enriquecido["cantidad"] * df_enriquecido["precio_unit"]

print(df_enriquecido[["id_venta", "nombre", "categoria", "cantidad", "total"]])
```

```
Tipos de join en pandas:
  how='inner'  → solo filas con coincidencia en AMBOS DataFrames (como INNER JOIN)
  how='left'   → todas las filas del izquierdo + coincidencias del derecho
  how='right'  → todas las filas del derecho + coincidencias del izquierdo
  how='outer'  → todas las filas de ambos (registros sin coincidencia → NaN)
```

### 4.2 Agregaciones (GROUP BY)

```python
import pandas as pd

df = pd.DataFrame({
    "fecha":     pd.to_datetime(["2025-01-05", "2025-01-12", "2025-02-03",
                                  "2025-02-14", "2025-01-20"]),
    "categoria": ["Computación", "Periféricos", "Computación",
                  "Periféricos", "Computación"],
    "total":     [3000.0, 2300.0, 4500.0, 850.0, 1500.0],
    "cantidad":  [2, 1, 3, 1, 1],
})

# Agregar mes/año
df["anio_mes"] = df["fecha"].dt.to_period("M")

# Múltiples métricas por grupo
resumen = (
    df.groupby(["anio_mes", "categoria"])
    .agg(
        total_vendido     = ("total",    "sum"),
        cantidad_total    = ("cantidad", "sum"),
        num_transacciones = ("total",    "count"),
        ticket_promedio   = ("total",    "mean"),
    )
    .reset_index()
    .sort_values(["anio_mes", "total_vendido"], ascending=[True, False])
)

print(resumen.to_string(index=False))
```

### 4.3 Tabla Pivot

Una tabla pivot **rota** las dimensiones: transforma valores únicos de una columna en nuevas columnas. Es la base de la mayoría de los reportes gerenciales.

```python
import pandas as pd

df = pd.DataFrame({
    "mes":       ["Enero", "Enero", "Febrero", "Febrero", "Marzo", "Marzo"],
    "categoria": ["Computación", "Periféricos", "Computación",
                  "Periféricos", "Computación", "Periféricos"],
    "total":     [7500.0, 3150.0, 4500.0, 850.0, 6000.0, 2200.0],
})

tabla_pivot = df.pivot_table(
    index="mes",
    columns="categoria",
    values="total",
    aggfunc="sum",
    fill_value=0          # rellenar con 0 donde no hay datos
)

print("=== VENTAS POR MES Y CATEGORÍA ===")
print(tabla_pivot)

# Resultado:
# categoria    Computación  Periféricos
# mes
# Enero            7500.0       3150.0
# Febrero          4500.0        850.0
# Marzo            6000.0       2200.0
```

---

## 5. ETL vs. ELT: Dos Paradigmas de Transformación

El orden en que se realizan las etapas del pipeline define el paradigma arquitectónico y tiene implicancias importantes.

### ETL — Extract, Transform, Load

Los datos se **transforman ANTES de llegar al destino**. El destino solo recibe datos curados.

```
[Fuente]  ──►  [Extracción]  ──►  [Transformación]  ──►  [Carga al DWH]
                                  (servidor ETL externo)
                                  Python / Spark
```

**Ventajas:**
- Mayor privacidad: datos sensibles se filtran/anoniman antes de cargar.
- Menor almacenamiento en destino: solo llegan datos curados.
- Compatible con destinos legacy sin poder de transformación.

**Desventajas:**
- Rigidez: si cambian los requerimientos, hay que re-extraer y re-transformar.
- Requiere infraestructura ETL separada.

### ELT — Extract, Load, Transform

Los datos se **cargan CRUDOS** en el destino y se transforman **dentro del mismo**, aprovechando su poder de cómputo.

```
[Fuente]  ──►  [Extracción]  ──►  [Carga Raw al DWH]  ──►  [Transformación en el DWH]
                                   (datos crudos)             SQL / dbt
```

**Ventajas:**
- Más rápido de implementar: se carga primero, se decide qué transformar después.
- Los datos crudos están **siempre disponibles** para re-procesar si cambian los requerimientos.
- Los motores cloud (BigQuery, Snowflake, Redshift) son muy eficientes para SQL analítico.

**Desventajas:**
- Los datos sensibles llegan crudos al destino → requiere controles de acceso estrictos.
- Mayor costo de almacenamiento.

```
┌─────────────────────────────────────────────────────────────────────┐
│              ¿CUÁNDO USAR CADA PARADIGMA?                           │
├──────────────────────────┬──────────────────────────────────────── │
│  ETL                     │  ELT                                    │
├──────────────────────────┼──────────────────────────────────────── │
│  Datos muy sensibles      │  Cloud DWH moderno (BigQuery, Snowflake)│
│  (PII, datos médicos)    │  Datos semi-estructurados o raw          │
│  Sistemas legacy         │  Equipos que prefieren SQL/dbt           │
│  Transformaciones compl. │  Necesidad de re-procesar frecuentemente │
│  antes de cargar         │  Almacenamiento barato en la nube        │
└──────────────────────────┴──────────────────────────────────────── │
```

> **Tendencia actual:** el paradigma **ELT** predomina en arquitecturas cloud modernas. **dbt (data build tool)** es la herramienta central de este paradigma: permite escribir las transformaciones en SQL versionado y testeado.

---

## 6. Derivación de Nuevas Columnas

Una de las transformaciones más comunes es crear columnas calculadas a partir de datos existentes.

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "fecha_venta":    pd.to_datetime(["2025-01-05", "2025-01-12",
                                      "2025-02-14", "2025-03-08"]),
    "fecha_entrega":  pd.to_datetime(["2025-01-08", "2025-01-18",
                                      "2025-02-15", "2025-03-20"]),
    "precio_unit":    [1500.0, 2300.0, 850.0, 1200.0],
    "cantidad":       [2, 1, 3, 2],
    "descuento_pct":  [0.10, 0.0, 0.05, 0.15],
})

# ── Columnas calculadas ────────────────────────────────────────────
df["total_bruto"]     = df["precio_unit"] * df["cantidad"]
df["descuento_monto"] = df["total_bruto"] * df["descuento_pct"]
df["total_neto"]      = df["total_bruto"] - df["descuento_monto"]
df["dias_entrega"]    = (df["fecha_entrega"] - df["fecha_venta"]).dt.days
df["dia_semana"]      = df["fecha_venta"].dt.day_name()
df["trimestre"]       = df["fecha_venta"].dt.quarter
df["anio"]            = df["fecha_venta"].dt.year

# ── Clasificación por monto (usando np.select para múltiples condiciones)
condiciones = [
    df["total_neto"] < 1000,
    (df["total_neto"] >= 1000) & (df["total_neto"] < 3000),
    df["total_neto"] >= 3000,
]
etiquetas = ["Venta pequeña", "Venta mediana", "Venta grande"]
df["segmento_venta"] = np.select(condiciones, etiquetas, default="Sin clasificar")

print(df[["total_neto", "dias_entrega", "dia_semana", "trimestre", "segmento_venta"]])
```

---

## Resumen de la Clase

| Operación | Función pandas | ¿Qué problema resuelve? |
|---|---|---|
| Eliminar duplicados | `drop_duplicates()` | Registros duplicados que distorsionan métricas |
| Eliminar nulos | `dropna(subset=[...])` | Registros incompletos en campos obligatorios |
| Normalizar texto | `.str.strip().str.title()` | Inconsistencias en mayúsculas/espacios |
| Parsear fechas | `pd.to_datetime(..., errors='coerce')` | Múltiples formatos de fecha |
| Reemplazar valores | `.replace(mapa)` | Variantes del mismo valor ("ARS", "ars", "pesos") |
| Join/enriquecimiento | `.merge(otro_df, on=..., how=...)` | Agregar contexto de tablas de referencia |
| Agregación | `.groupby().agg()` | Calcular métricas por grupo |
| Pivot table | `.pivot_table()` | Reportes cruzados (filas × columnas) |
| Columnas derivadas | `df["nueva"] = ...` | Crear métricas calculadas |

---

> 💡 **Para la próxima clase:** Los datos ya están limpios y transformados. En la **Clase 06** vamos a aprender las estrategias para **cargarlos de forma confiable** en el destino final, y a orquestar todo el pipeline con **Apache Airflow**.
