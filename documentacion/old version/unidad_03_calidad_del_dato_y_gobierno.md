# Unidad III — Calidad del Dato y Gobierno

> **Asignatura:** Ingeniería de Datos  
> **Docente:** Ing. Sergio Orozco  
> **Clases:** 7 y 8

---

## Objetivos de la Unidad

Al finalizar esta unidad, el alumno será capaz de:

- Identificar y explicar las **6 dimensiones de calidad del dato** y evaluar su impacto en decisiones de negocio.
- Realizar un proceso de **Data Profiling** completo sobre un dataset real usando Python.
- Definir y calcular **métricas y KPIs de calidad** para monitorear la salud de los datos.
- Implementar reglas de validación automatizadas usando **Great Expectations** y **pandas**.
- Construir un **reporte de auditoría de calidad** que identifique y cuantifique problemas.
- Explicar qué es el **Gobierno del Dato**, sus principios y su estructura organizacional.
- Diferenciar los roles de **Data Steward**, **Data Owner** y **Chief Data Officer (CDO)**.
- Comprender qué es un **catálogo de datos** y un **diccionario de datos**, y cómo construirlos.
- Explicar el concepto de **linaje del dato** y por qué es esencial para la trazabilidad.
- Clasificar datos sensibles (**PII**, datos regulados) y aplicar políticas básicas de protección con Python.

---

## Clase 07 — Calidad del Dato: Las 6 Dimensiones y Data Profiling

### 7.1 ¿Por qué importa la calidad del dato?

Antes de aprender a medir la calidad, es fundamental entender el costo de ignorarla.

> **"Garbage in, garbage out"** — si los datos de entrada son incorrectos o incompletos, cualquier análisis, reporte o modelo de machine learning que se construya sobre ellos producirá resultados incorrectos, sin importar cuán sofisticado sea el algoritmo.

**Casos reales de impacto:**

- **Campañas de marketing fallidas:** Una empresa envía emails a 100.000 clientes. El 25% de los emails tiene el campo `email` nulo, el 10% tiene formato inválido (`juan@@empresa`) y el 5% son duplicados. Solo el 60% recibe la campaña. El costo de la campaña fue el mismo, pero el alcance fue un 40% menor.

- **Decisiones gerenciales erróneas:** Un reporte de ventas muestra una caída del 15% en el trimestre. La gerencia decide cortar presupuesto. Semanas después se descubre que el pipeline ETL tenía un bug que omitía transacciones de la región norte. Las ventas reales habían crecido un 5%.

- **Modelos de ML sesgados:** Un modelo de scoring crediticio entrenado con datos donde el 30% de los ingresos reportados son incorrectos (por errores en el formulario) aprueba o rechaza créditos basándose en información falsa. El impacto financiero y legal puede ser enorme.

La calidad del dato no es un problema técnico aislado: es un problema de negocio con consecuencias medibles en dinero, reputación y cumplimiento regulatorio.

---

### 7.2 Las 6 Dimensiones de Calidad del Dato

La organización **DAMA International** (referencia global en gestión de datos) define seis dimensiones fundamentales para evaluar la calidad de un conjunto de datos:

#### 1. Completitud

**Pregunta:** ¿Están todos los datos presentes? ¿Hay valores nulos donde no debería haberlos?

Un campo es incompleto cuando tiene un valor nulo (`NULL`, `NaN`, cadena vacía `""`) en un contexto donde ese valor es obligatorio o necesario para el análisis.

**Métrica:**
$$\text{Completitud}(\%) = \frac{\text{Registros con valor en el campo}}{\text{Total de registros}} \times 100$$

**Ejemplo:** En una tabla de clientes, el campo `email` tiene 850 valores de 1.000 registros → Completitud = 85%.

---

#### 2. Exactitud

**Pregunta:** ¿Los datos representan correctamente la realidad del mundo real?

Un dato puede estar presente (no nulo) pero ser incorrecto. La exactitud es la dimensión más difícil de medir porque requiere comparar contra una fuente de verdad externa.

**Métrica:**
$$\text{Exactitud}(\%) = \frac{\text{Registros que coinciden con la realidad}}{\text{Total de registros validados}} \times 100$$

**Ejemplo:** Una tabla de precios tiene `precio_unitario = 0` para 50 productos. El precio no es nulo, pero es incorrecto (ningún producto se vende a $0 en este catálogo).

---

#### 3. Consistencia

**Pregunta:** ¿Los datos son iguales o coherentes entre distintos sistemas o tablas?

Un dato es inconsistente cuando el mismo concepto tiene valores distintos en sistemas diferentes, o cuando viola una regla de negocio entre columnas del mismo registro.

**Tipos de inconsistencia:**
- **Entre sistemas:** El ERP dice que el cliente tiene 5 pedidos pendientes; el CRM dice que tiene 0.
- **Intra-registro:** El campo `fecha_entrega` es anterior al campo `fecha_pedido` (imposible lógicamente).
- **Entre tablas:** La tabla `ventas` tiene `id_cliente = 9999`, pero ese ID no existe en la tabla `clientes`.

---

#### 4. Unicidad

**Pregunta:** ¿Cada entidad del mundo real aparece una sola vez en el dataset?

Un registro duplicado genera doble conteo en reportes, distorsiona métricas y puede causar errores en joins y aggregaciones.

**Métrica:**
$$\text{Unicidad}(\%) = \frac{\text{Registros únicos}}{\text{Total de registros}} \times 100$$

**Ejemplo:** Una tabla de facturas tiene el mismo `id_factura` en 3 filas distintas → duplicados que inflan las ventas reportadas.

---

#### 5. Vigencia (Temporalidad)

**Pregunta:** ¿Los datos están actualizados en el momento en que se necesitan?

Un dato puede haber sido exacto cuando se registró, pero volverse desactualizado con el tiempo. Su "caducidad" depende del contexto de uso.

**Ejemplos:**
- El domicilio de un cliente fue registrado hace 3 años. Hoy puede ser incorrecto.
- El precio de lista de un producto se actualizó ayer en el ERP pero el pipeline ETL corre diariamente a las 6 AM: los reportes del día tienen precios con 24 horas de retraso.
- Las métricas de stock de un almacén deben actualizarse en tiempo real; un reporte de hace 2 horas puede mostrar disponibilidad de un producto que ya está agotado.

---

#### 6. Integridad

**Pregunta:** ¿Se mantienen las relaciones entre los datos? ¿Los datos referenciados existen?

La integridad referencial garantiza que las relaciones entre tablas son válidas: si `ventas.id_cliente = 101`, entonces el cliente con `id = 101` debe existir en la tabla `clientes`.

**Tipos de integridad:**
- **Referencial:** Las claves foráneas apuntan a registros que existen.
- **De dominio:** Los valores pertenecen al conjunto de valores válidos (ej: `moneda` solo puede ser `ARS`, `USD` o `EUR`).
- **De negocio:** Las reglas propias del dominio se cumplen (ej: `fecha_fin >= fecha_inicio`).

---

### 7.3 Data Profiling: Conocer los Datos Antes de Transformarlos

El **Data Profiling** es el proceso de analizar estadística y estructuralmente un dataset para:
1. Entender su contenido, distribución y calidad.
2. Identificar problemas antes de que lleguen a producción.
3. Tomar decisiones informadas sobre cómo limpiar y transformar los datos.

Es el equivalente a un "diagnóstico médico" del dataset: antes de operar, hay que entender qué está pasando.

#### Dimensiones del Data Profiling

| Tipo de análisis | Qué mide |
|---|---|
| **Completitud** | Porcentaje de nulos por columna |
| **Unicidad** | Duplicados y cardinalidad de valores |
| **Distribución** | Min, max, media, mediana, desviación estándar |
| **Formatos** | Tipos de dato, longitudes de cadenas, patrones regex |
| **Outliers** | Valores atípicos que se alejan de la distribución |
| **Integridad referencial** | Claves foráneas huérfanas |

---

### 7.4 Data Profiling con Python y pandas

```
pip install pandas numpy matplotlib seaborn
```

#### Ejemplo 1 — Reporte de profiling básico

```python
import pandas as pd
import numpy as np

# Dataset de ventas con problemas intencionales para el ejercicio
data = {
    "id_venta":      [1, 2, 2, 3, None, 5, 6, 7, 8, 9],
    "fecha_venta":   ["2025-01-05", "2025-01-06", "2025-01-06", "2025-99-01",
                      "2025-01-08", "2025-01-09", "2025-01-10", "2025-01-11",
                      "2025-01-12", "2025-01-13"],
    "id_cliente":    [101, 102, 102, 103, 104, 105, 9999, 107, 108, 109],
    "monto":         [1500.0, 2300.0, 2300.0, 850.0, 1200.0, -50.0, 950.0,
                      0.0, 1800.0, 150000.0],  # -50 y 150000 son outliers
    "moneda":        ["ARS", "ars", "ars", "ARS", "PESOS", "USD", "ARS",
                      "EUR", "ARS", "ARS"],
    "email_cliente": ["a@b.com", "juan@@err.com", "juan@@err.com", None,
                      "ana@test.com", None, "luis@ok.com", "carlos@ok.com",
                      None, "pedro@ok.com"],
}

df = pd.DataFrame(data)
df["fecha_venta"] = pd.to_datetime(df["fecha_venta"], errors="coerce")


def generar_reporte_profiling(df: pd.DataFrame) -> None:
    """Genera un reporte completo de Data Profiling sobre un DataFrame."""
    n = len(df)
    sep = "=" * 55

    print(f"\n{sep}")
    print(f"  REPORTE DE DATA PROFILING")
    print(f"  Registros totales: {n} | Columnas: {len(df.columns)}")
    print(sep)

    # ── 1. Completitud ─────────────────────────────────────
    print("\n📊 1. COMPLETITUD (valores nulos)")
    nulos = df.isnull().sum()
    pct_nulos = (nulos / n * 100).round(2)
    completitud = pd.DataFrame({
        "Nulos": nulos,
        "% Nulos": pct_nulos,
        "% Completo": (100 - pct_nulos).round(2),
        "Estado": pct_nulos.apply(lambda x: "✅ OK" if x == 0 else ("⚠️ Revisar" if x < 20 else "❌ Crítico"))
    })
    print(completitud.to_string())

    # ── 2. Unicidad ────────────────────────────────────────
    print("\n🔁 2. UNICIDAD (duplicados)")
    duplicados_total = df.duplicated().sum()
    print(f"  Filas completamente duplicadas: {duplicados_total} ({duplicados_total/n*100:.1f}%)")

    for col in df.columns:
        dup_col = df[col].duplicated(keep=False).sum()
        if dup_col > 0:
            card = df[col].nunique()
            print(f"  '{col}': {dup_col} valores duplicados | {card} valores únicos de {n}")

    # ── 3. Estadísticas de columnas numéricas ──────────────
    print("\n📈 3. DISTRIBUCIÓN DE COLUMNAS NUMÉRICAS")
    numericas = df.select_dtypes(include=[np.number])
    if not numericas.empty:
        stats = numericas.describe().T
        stats["outliers_iqr"] = numericas.apply(lambda col: (
            ((col < (col.quantile(0.25) - 1.5 * (col.quantile(0.75) - col.quantile(0.25)))) |
             (col > (col.quantile(0.75) + 1.5 * (col.quantile(0.75) - col.quantile(0.25))))).sum()
        ))
        print(stats[["count", "mean", "min", "50%", "max", "outliers_iqr"]].to_string())

    # ── 4. Dominio de valores categóricos ──────────────────
    print("\n🗂️  4. DOMINIO DE VALORES (columnas de texto)")
    texto = df.select_dtypes(include=["object"])
    for col in texto.columns:
        valores = df[col].value_counts(dropna=False)
        print(f"\n  '{col}' — {df[col].nunique()} valores únicos:")
        print(f"  {valores.to_dict()}")

    # ── 5. Resumen de problemas ────────────────────────────
    print(f"\n{sep}")
    print("  RESUMEN DE PROBLEMAS DETECTADOS")
    print(sep)
    print(f"  • Registros duplicados:      {duplicados_total}")
    print(f"  • Columnas con nulos:        {(nulos > 0).sum()}")
    fechas_invalidas = df.select_dtypes(include=["datetime64"]).isnull().sum().sum()
    print(f"  • Fechas inválidas (NaT):    {fechas_invalidas}")
    montos_negativos = (df.get("monto", pd.Series(dtype=float)) < 0).sum()
    print(f"  • Montos negativos:          {montos_negativos}")


generar_reporte_profiling(df)
```

#### Ejemplo 2 — Cálculo de métricas de calidad por dimensión

```python
import pandas as pd
import numpy as np
import re

df = pd.DataFrame({
    "id_venta":      [1, 2, 2, 3, None, 5, 6, 7, 8, 9],
    "monto":         [1500.0, 2300.0, 2300.0, 850.0, 1200.0, -50.0, 950.0, 0.0, 1800.0, 150000.0],
    "moneda":        ["ARS", "ars", "ars", "ARS", "PESOS", "USD", "ARS", "EUR", "ARS", "ARS"],
    "email_cliente": ["a@b.com", "juan@@err.com", "juan@@err.com", None,
                      "ana@test.com", None, "luis@ok.com", "carlos@ok.com", None, "pedro@ok.com"],
    "fecha_venta":   pd.to_datetime(["2025-01-05", "2025-01-06", "2025-01-06", None,
                                     "2025-01-08", "2025-01-09", "2025-01-10", "2025-01-11",
                                     "2025-01-12", "2025-01-13"], errors="coerce"),
})

n = len(df)

# ── Dimensión 1: Completitud ───────────────────────────────
completitud_id     = df["id_venta"].notna().sum() / n * 100
completitud_monto  = df["monto"].notna().sum() / n * 100
completitud_email  = df["email_cliente"].notna().sum() / n * 100
completitud_fecha  = df["fecha_venta"].notna().sum() / n * 100

print("=== COMPLETITUD ===")
print(f"  id_venta:      {completitud_id:.1f}%")
print(f"  monto:         {completitud_monto:.1f}%")
print(f"  email_cliente: {completitud_email:.1f}%")
print(f"  fecha_venta:   {completitud_fecha:.1f}%")

# ── Dimensión 2: Unicidad ──────────────────────────────────
duplicados = df.duplicated(subset=["id_venta"]).sum()
unicidad_id = (n - duplicados) / n * 100
print(f"\n=== UNICIDAD ===")
print(f"  Duplicados en id_venta: {duplicados}")
print(f"  Unicidad id_venta: {unicidad_id:.1f}%")

# ── Dimensión 3: Consistencia de dominio ──────────────────
monedas_validas = {"ARS", "USD", "EUR"}
monedas_normalizadas = df["moneda"].str.upper().str.strip()
consistencia_moneda = monedas_normalizadas.isin(monedas_validas).sum() / n * 100
print(f"\n=== CONSISTENCIA ===")
print(f"  Monedas fuera del dominio válido: {(~monedas_normalizadas.isin(monedas_validas)).sum()}")
print(f"  Consistencia de moneda: {consistencia_moneda:.1f}%")

# ── Dimensión 4: Exactitud (reglas de negocio) ─────────────
montos_invalidos = ((df["monto"] < 0) | (df["monto"] == 0)).sum()
exactitud_monto = (n - montos_invalidos) / n * 100
print(f"\n=== EXACTITUD ===")
print(f"  Montos inválidos (<=0): {montos_invalidos}")
print(f"  Exactitud de monto: {exactitud_monto:.1f}%")

# ── Dimensión 5: Formato de email ─────────────────────────
patron_email = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
emails_no_nulos = df["email_cliente"].dropna()
emails_validos  = emails_no_nulos.str.match(patron_email).sum()
exactitud_email = emails_validos / len(emails_no_nulos) * 100
print(f"\n=== FORMATO (EMAIL) ===")
print(f"  Emails con formato inválido: {len(emails_no_nulos) - emails_validos}")
print(f"  Exactitud de formato email: {exactitud_email:.1f}%")

# ── Resumen de KPIs ────────────────────────────────────────
print("\n=== KPI GLOBAL DE CALIDAD ===")
kpi_global = (completitud_id + completitud_monto + completitud_email +
              unicidad_id + consistencia_moneda + exactitud_monto) / 6
print(f"  Score de calidad promedio: {kpi_global:.1f}%")
estado = "✅ Aceptable" if kpi_global >= 90 else ("⚠️ Revisar" if kpi_global >= 75 else "❌ Crítico")
print(f"  Estado: {estado}")
```

#### Ejemplo 3 — Detección de outliers con IQR

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "monto": [1500.0, 2300.0, 850.0, 1200.0, 950.0, 1800.0,
              -50.0,    # outlier negativo
              150000.0, # outlier positivo extremo
              1600.0, 1100.0],
})

def detectar_outliers_iqr(serie: pd.Series) -> pd.DataFrame:
    """
    Detecta outliers usando el método IQR (Rango Intercuartílico).
    Un valor es outlier si está por debajo de Q1 - 1.5*IQR
    o por encima de Q3 + 1.5*IQR.
    """
    Q1  = serie.quantile(0.25)
    Q3  = serie.quantile(0.75)
    IQR = Q3 - Q1

    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR

    print(f"  Q1={Q1:.2f} | Q3={Q3:.2f} | IQR={IQR:.2f}")
    print(f"  Límite inferior: {limite_inferior:.2f}")
    print(f"  Límite superior: {limite_superior:.2f}")

    es_outlier = (serie < limite_inferior) | (serie > limite_superior)

    return pd.DataFrame({
        "valor":      serie,
        "es_outlier": es_outlier,
        "motivo":     np.where(serie < limite_inferior, "Por debajo del límite",
                      np.where(serie > limite_superior, "Por encima del límite", "OK")),
    })


print("=== DETECCIÓN DE OUTLIERS EN 'monto' ===")
resultado = detectar_outliers_iqr(df["monto"])
print(resultado[resultado["es_outlier"]])
print(f"\nTotal outliers detectados: {resultado['es_outlier'].sum()} de {len(df)}")
```

---

### 7.5 Validación Automatizada con Great Expectations

**Great Expectations** (GE) es la librería Python líder para validación automatizada de datos. Permite definir **expectativas** (reglas de calidad) sobre los datos y generar reportes HTML automáticos cuando se violan.

El concepto central es el **"contrato de datos"**: un conjunto de reglas que los datos deben cumplir para ser considerados aptos para el análisis. Si las reglas no se cumplen, el pipeline debe detenerse o alertar.

```
pip install great-expectations
```

#### Ejemplo 4 — Definición de expectativas básicas

```python
import great_expectations as ge
import pandas as pd

# Cargar el dataset como un GE DataFrame (wrapper sobre pandas)
df_crudo = pd.DataFrame({
    "id_venta":       [1, 2, 2, 3, None, 5],
    "precio_unitario":[1500.0, 2300.0, 2300.0, -50.0, 850.0, 75000.0],
    "moneda":         ["ARS", "ars", "ARS", "ARS", "USD", "BTC"],  # BTC inválido
    "email":          ["a@b.com", "juan@@err", "juan@@err", None, "ok@test.com", "otro@ok.com"],
    "cantidad":       [1, 2, 2, 3, 0, 1],
})

df = ge.from_pandas(df_crudo)

# ── Expectativas de Completitud ────────────────────────────
df.expect_column_values_to_not_be_null("id_venta")
df.expect_column_values_to_not_be_null("precio_unitario")

# ── Expectativas de Unicidad ──────────────────────────────
df.expect_column_values_to_be_unique("id_venta")

# ── Expectativas de Rango (Exactitud) ─────────────────────
df.expect_column_values_to_be_between(
    "precio_unitario",
    min_value=0.01,
    max_value=50000.0
)
df.expect_column_values_to_be_between(
    "cantidad",
    min_value=1,
    max_value=9999
)

# ── Expectativas de Dominio (Consistencia) ────────────────
df.expect_column_values_to_be_in_set(
    "moneda",
    value_set=["ARS", "USD", "EUR"]
)

# ── Expectativas de Formato (regex) ───────────────────────
df.expect_column_values_to_match_regex(
    "email",
    regex=r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$",
    mostly=0.9  # Al menos el 90% debe cumplirlo (tolera algunos nulos)
)

# ── Validar y mostrar resultado ───────────────────────────
resultado = df.validate()

total     = resultado["statistics"]["evaluated_expectations"]
exitosos  = resultado["statistics"]["successful_expectations"]
fallidos  = resultado["statistics"]["unsuccessful_expectations"]
pct_ok    = resultado["statistics"]["success_percent"]

print(f"{'='*45}")
print(f"  RESULTADO DE VALIDACIÓN")
print(f"{'='*45}")
print(f"  Expectativas evaluadas: {total}")
print(f"  ✅ Exitosas:            {exitosos}")
print(f"  ❌ Fallidas:            {fallidos}")
print(f"  Score de calidad:       {pct_ok:.1f}%")
print(f"  Estado global:          {'APROBADO ✅' if resultado['success'] else 'RECHAZADO ❌'}")

# Mostrar detalle de las expectativas fallidas
print(f"\n{'='*45}")
print("  DETALLE DE FALLAS")
print(f"{'='*45}")
for expectativa in resultado["results"]:
    if not expectativa["success"]:
        col   = expectativa["expectation_config"]["kwargs"].get("column", "N/A")
        tipo  = expectativa["expectation_config"]["expectation_type"]
        stats = expectativa.get("result", {})
        print(f"  ❌ [{col}] {tipo}")
        if "unexpected_count" in stats:
            print(f"     Registros inválidos: {stats['unexpected_count']}")
        if "unexpected_values" in stats:
            print(f"     Valores problemáticos: {stats['unexpected_values'][:5]}")
```

#### Ejemplo 5 — Integrar la validación dentro de un pipeline ETL

```python
import great_expectations as ge
import pandas as pd
import logging

log = logging.getLogger(__name__)

def validar_datos_o_fallar(df: pd.DataFrame, umbral_calidad: float = 0.95) -> pd.DataFrame:
    """
    Valida el DataFrame contra las reglas de calidad definidas.
    Si el score de calidad es menor al umbral, lanza una excepción
    deteniendo el pipeline antes de cargar datos defectuosos.

    Args:
        df: DataFrame a validar.
        umbral_calidad: Porcentaje mínimo de expectativas que deben cumplirse (0-1).

    Returns:
        El mismo DataFrame si pasa la validación.

    Raises:
        ValueError: Si la calidad del dato no alcanza el umbral.
    """
    df_ge = ge.from_pandas(df)

    # Definir contrato de calidad
    df_ge.expect_column_values_to_not_be_null("id_venta")
    df_ge.expect_column_values_to_be_unique("id_venta")
    df_ge.expect_column_values_to_be_between("monto", min_value=0.01, max_value=100000.0)
    df_ge.expect_column_values_to_be_in_set("moneda", value_set=["ARS", "USD", "EUR"])
    df_ge.expect_column_values_to_not_be_null("id_cliente")

    resultado = df_ge.validate()
    score = resultado["statistics"]["success_percent"] / 100

    log.info(f"Score de calidad: {score*100:.1f}% (umbral: {umbral_calidad*100:.1f}%)")

    if score < umbral_calidad:
        fallidos = resultado["statistics"]["unsuccessful_expectations"]
        raise ValueError(
            f"Validación de calidad FALLIDA: {score*100:.1f}% < {umbral_calidad*100:.1f}% requerido. "
            f"{fallidos} expectativas no cumplidas. Pipeline detenido."
        )

    log.info("✅ Validación de calidad APROBADA. Continuando con la carga.")
    return df


# Uso dentro del pipeline ETL
def pipeline_con_validacion(df_raw: pd.DataFrame) -> None:
    try:
        df_validado = validar_datos_o_fallar(df_raw, umbral_calidad=0.90)
        # ... continuar con transformación y carga
        print("Pipeline completado exitosamente.")
    except ValueError as e:
        print(f"PIPELINE DETENIDO: {e}")
        # Aquí se podría: enviar alerta, guardar los datos defectuosos, notificar al equipo
```

---

### 7.6 Construcción de un Dashboard de Calidad con pandas

Un **Data Quality Dashboard** es un reporte periódico que muestra la evolución de las métricas de calidad a lo largo del tiempo. Permite detectar regresiones: si la completitud del campo `email` era 95% la semana pasada y hoy es 72%, algo rompió en el pipeline.

#### Ejemplo 6 — Reporte de calidad histórico

```python
import pandas as pd
from datetime import date, timedelta
import random

random.seed(42)

# Simular métricas de calidad recolectadas diariamente durante 2 semanas
fechas = [date(2025, 3, 1) + timedelta(days=i) for i in range(14)]

metricas = []
for i, fecha in enumerate(fechas):
    # Simular deterioro de calidad a partir del día 8
    degradacion = 0.10 if i >= 8 else 0.0
    metricas.append({
        "fecha":                   fecha,
        "completitud_id_venta":    round(random.uniform(0.99, 1.00), 4),
        "completitud_email":       round(random.uniform(0.78, 0.85) - degradacion, 4),
        "unicidad_id_venta":       round(random.uniform(0.98, 1.00), 4),
        "consistencia_moneda":     round(random.uniform(0.95, 0.99) - degradacion, 4),
        "exactitud_monto":         round(random.uniform(0.97, 1.00), 4),
        "registros_procesados":    random.randint(4500, 5500),
    })

df_metricas = pd.DataFrame(metricas)
df_metricas["score_global"] = df_metricas[[
    "completitud_id_venta", "completitud_email",
    "unicidad_id_venta", "consistencia_moneda", "exactitud_monto"
]].mean(axis=1).round(4)

# Identificar días donde el score global cayó por debajo del umbral
UMBRAL = 0.90
df_metricas["alerta"] = df_metricas["score_global"] < UMBRAL

print("=== DASHBOARD DE CALIDAD — ÚLTIMAS 2 SEMANAS ===\n")
print(df_metricas[["fecha", "completitud_email", "consistencia_moneda",
                    "score_global", "alerta"]].to_string(index=False))

alertas = df_metricas[df_metricas["alerta"]]
if not alertas.empty:
    print(f"\n⚠️ ALERTAS: {len(alertas)} día(s) con score global < {UMBRAL*100:.0f}%")
    print(alertas[["fecha", "score_global"]].to_string(index=False))
```

---

## Clase 08 — Gobierno del Dato y Gestión de Metadatos

### 8.1 ¿Qué es el Gobierno del Dato?

El **Gobierno del Dato** (Data Governance) es el sistema de toma de decisiones y responsabilidades que define **quién puede hacer qué con cuáles datos** dentro de una organización.

No es una herramienta ni una tecnología: es un **marco organizacional** que combina políticas, procesos, roles y estándares para garantizar que los datos sean:
- **Confiables:** tienen calidad suficiente para tomar decisiones.
- **Seguros:** solo las personas autorizadas acceden a ellos.
- **Conformes:** cumplen con regulaciones (GDPR, PDPA, Ley 25.326 en Argentina).
- **Trazables:** se puede conocer su origen, transformaciones y uso.

> **Analogía:** El gobierno del dato es como el reglamento de una biblioteca. Define quién puede sacar libros (acceso), quién los puede modificar (custodia), qué libros son de consulta restringida (clasificación) y cómo saber si un libro fue alterado (auditoría).

#### Principios del Gobierno del Dato

1. **Responsabilidad definida:** cada dato tiene un propietario responsable.
2. **Acceso controlado:** mínimo privilegio necesario para cada rol.
3. **Calidad medible:** las reglas de calidad deben estar formalizadas y monitoreadas.
4. **Trazabilidad completa:** se puede rastrear el origen y transformación de cualquier dato.
5. **Cumplimiento regulatorio:** los procesos de datos respetan las leyes aplicables.

---

### 8.2 Roles del Ecosistema de Gobierno

#### Chief Data Officer (CDO)

Es el **máximo responsable de la estrategia de datos** de la organización. Define la visión, prioridades y políticas de alto nivel. Reporta a la dirección ejecutiva.

**Responsabilidades:**
- Definir la estrategia de datos de la empresa.
- Garantizar el cumplimiento regulatorio.
- Promover la cultura data-driven en toda la organización.
- Gestionar el presupuesto del área de datos.

#### Data Owner (Propietario del Dato)

Es el **responsable de negocio** de un conjunto de datos específico. Generalmente es un gerente o director del área que genera o usa esos datos (ej: el Gerente de Ventas es el Data Owner de los datos de ventas).

**Responsabilidades:**
- Aprobar el acceso a sus datos.
- Definir los requisitos de calidad para sus datos.
- Resolver disputas sobre el significado o reglas de negocio.
- Asegurar que los datos de su dominio cumplan con las políticas organizacionales.

#### Data Steward (Custodio del Dato)

Es el **responsable operativo** de la calidad y gestión diaria de un conjunto de datos. Trabaja en coordinación con el Data Owner y el equipo de ingeniería.

**Responsabilidades:**
- Documentar los datos (diccionario de datos, glosario).
- Monitorear las métricas de calidad y reportar anomalías.
- Definir y mantener las reglas de validación.
- Gestionar solicitudes de acceso a los datos.
- Coordinar la resolución de problemas de calidad entre sistemas.

#### Resumen de roles

| Rol | Perfil típico | Responsabilidad principal |
|---|---|---|
| **CDO** | Director ejecutivo | Estrategia y política global de datos |
| **Data Owner** | Gerente de área | Responsabilidad de negocio del activo |
| **Data Steward** | Analista / Ingeniero | Calidad, documentación y acceso operativo |
| **Data Engineer** | Técnico | Construcción y mantenimiento de pipelines |
| **Data Consumer** | Analista / Científico | Uso responsable de los datos |

> **Concepto clave:** Sin Data Owners claramente asignados, las reglas de calidad no se cumplen porque nadie tiene la autoridad ni la responsabilidad de hacerlas cumplir. La gobernanza sin propietarios es solo burocracia en papel.

---

### 8.3 Catálogo de Datos y Diccionario de Datos

#### Catálogo de Datos

Es un **inventario centralizado y buscable** de todos los activos de datos de la organización: qué datos existen, dónde están, quién es responsable, qué calidad tienen y cómo se relacionan entre sí.

**Funciones principales:**
- Descubrimiento de datos: los analistas pueden encontrar el dataset que necesitan.
- Colaboración: los equipos pueden dejar notas y comentarios sobre los datos.
- Control de calidad: muestra las métricas de calidad de cada activo.
- Linaje visual: muestra de dónde vienen los datos y adónde van.

**Herramientas del mercado:** Collibra, Alation, OpenMetadata, Apache Atlas, DataHub (LinkedIn), Amundsen (Lyft).

#### Diccionario de Datos

Es la **documentación técnica detallada** de cada tabla y columna: nombre, tipo de dato, descripción, valores válidos, origen, responsable, reglas de validación.

#### Ejemplo 7 — Construcción de un diccionario de datos con Python

```python
import pandas as pd
import json
from datetime import date

# Definición del diccionario de datos de la tabla de ventas
diccionario = [
    {
        "tabla":          "dw.ventas",
        "columna":        "id_venta",
        "tipo_dato":      "INTEGER",
        "nullable":       False,
        "unico":          True,
        "descripcion":    "Identificador único de la transacción de venta. Generado por el ERP.",
        "origen":         "ERP SAP — tabla BSEG",
        "valores_validos":"Enteros positivos > 0",
        "data_owner":     "Gerencia Comercial",
        "data_steward":   "Ana González",
        "ultima_revision": str(date.today()),
    },
    {
        "tabla":          "dw.ventas",
        "columna":        "fecha_venta",
        "tipo_dato":      "DATE",
        "nullable":       False,
        "unico":          False,
        "descripcion":    "Fecha en que se registró la venta en el sistema transaccional.",
        "origen":         "ERP SAP — tabla BKPF",
        "valores_validos":"Fechas entre 2020-01-01 y la fecha actual",
        "data_owner":     "Gerencia Comercial",
        "data_steward":   "Ana González",
        "ultima_revision": str(date.today()),
    },
    {
        "tabla":          "dw.ventas",
        "columna":        "monto",
        "tipo_dato":      "NUMERIC(15,2)",
        "nullable":       False,
        "unico":          False,
        "descripcion":    "Monto bruto de la venta en la moneda indicada, sin impuestos.",
        "origen":         "ERP SAP — tabla BSEG campo WRBTR",
        "valores_validos":"Valores > 0. Máximo esperado: 500,000.",
        "data_owner":     "Gerencia Comercial",
        "data_steward":   "Ana González",
        "ultima_revision": str(date.today()),
    },
    {
        "tabla":          "dw.ventas",
        "columna":        "moneda",
        "tipo_dato":      "VARCHAR(3)",
        "nullable":       False,
        "unico":          False,
        "descripcion":    "Código ISO 4217 de la moneda de la transacción.",
        "origen":         "ERP SAP — tabla BSEG campo WAERS",
        "valores_validos":"ARS | USD | EUR",
        "data_owner":     "Gerencia Comercial",
        "data_steward":   "Ana González",
        "ultima_revision": str(date.today()),
    },
]

df_diccionario = pd.DataFrame(diccionario)

# Exportar a CSV para compartir con el equipo
df_diccionario.to_csv("diccionario_datos_ventas.csv", index=False, encoding="utf-8")

# Exportar a JSON para ingestarlo en una herramienta de catálogo
with open("diccionario_datos_ventas.json", "w", encoding="utf-8") as f:
    json.dump(diccionario, f, ensure_ascii=False, indent=2)

print("=== DICCIONARIO DE DATOS — dw.ventas ===\n")
print(df_diccionario[["columna", "tipo_dato", "nullable", "descripcion"]].to_string(index=False))
```

---

### 8.4 Linaje del Dato (Data Lineage)

El **linaje del dato** es la capacidad de rastrear el **origen, transformaciones y destino** de un dato a lo largo de todo su ciclo de vida. Responde la pregunta: *¿de dónde vino este número en el dashboard?*

**¿Por qué es esencial?**
- **Auditoría y regulación:** poder demostrar cómo se calculó un indicador financiero o de riesgo.
- **Debugging de pipelines:** cuando un número en un reporte es incorrecto, el linaje permite rastrear en qué paso ocurrió el error.
- **Análisis de impacto:** si se modifica una tabla fuente, saber qué reportes y modelos se verán afectados.
- **Cumplimiento de datos personales:** poder demostrar que un dato de un cliente fue eliminado de todos los sistemas donde existía.

#### Ejemplo 8 — Documentar linaje de transformaciones en un pipeline

```python
import pandas as pd
from datetime import datetime

def pipeline_con_linaje(df_fuente: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    """
    Ejecuta el pipeline de transformación y registra el linaje de cada paso.
    Retorna el DataFrame transformado y el registro de linaje.
    """
    registro_linaje = []
    timestamp_inicio = datetime.now().isoformat()

    def registrar_paso(nombre: str, descripcion: str, df_entrada: pd.DataFrame,
                       df_salida: pd.DataFrame, transformacion: str) -> None:
        registro_linaje.append({
            "paso":            nombre,
            "descripcion":     descripcion,
            "timestamp":       datetime.now().isoformat(),
            "registros_entrada": len(df_entrada),
            "registros_salida":  len(df_salida),
            "registros_eliminados": len(df_entrada) - len(df_salida),
            "columnas_agregadas": list(set(df_salida.columns) - set(df_entrada.columns)),
            "transformacion_sql_equivalente": transformacion,
        })

    # Paso 1: Fuente
    registrar_paso(
        "EXTRACT",
        "Lectura de tabla ventas.transacciones desde ERP PostgreSQL",
        df_fuente, df_fuente,
        "SELECT * FROM erp.ventas.transacciones WHERE updated_at > '2025-03-01'"
    )

    # Paso 2: Eliminar duplicados
    df_sin_dup = df_fuente.drop_duplicates(subset=["id_venta"])
    registrar_paso(
        "DEDUP",
        "Eliminación de registros duplicados por id_venta",
        df_fuente, df_sin_dup,
        "SELECT DISTINCT ON (id_venta) * FROM staging.ventas ORDER BY id_venta, updated_at DESC"
    )

    # Paso 3: Filtrar nulos
    df_sin_nulos = df_sin_dup.dropna(subset=["id_venta", "monto"])
    registrar_paso(
        "FILTER_NULLS",
        "Eliminación de filas con id_venta o monto nulos",
        df_sin_dup, df_sin_nulos,
        "SELECT * FROM dedup WHERE id_venta IS NOT NULL AND monto IS NOT NULL"
    )

    # Paso 4: Normalizar moneda
    df_norm = df_sin_nulos.copy()
    df_norm["moneda"] = df_norm["moneda"].str.upper().str.strip()
    registrar_paso(
        "NORMALIZE_CURRENCY",
        "Normalización de código de moneda a mayúsculas sin espacios",
        df_sin_nulos, df_norm,
        "SELECT *, UPPER(TRIM(moneda)) AS moneda FROM filter_nulls"
    )

    # Paso 5: Calcular columna derivada
    df_final = df_norm.copy()
    df_final["total_con_iva"] = (df_final["monto"] * 1.21).round(2)
    registrar_paso(
        "DERIVE_IVA",
        "Cálculo del total con IVA 21% sobre el monto bruto",
        df_norm, df_final,
        "SELECT *, ROUND(monto * 1.21, 2) AS total_con_iva FROM normalize_currency"
    )

    return df_final, registro_linaje


# Datos de prueba
df_origen = pd.DataFrame({
    "id_venta": [1, 2, 2, 3, None, 5],
    "monto":    [1500.0, 2300.0, 2300.0, 850.0, 1200.0, 950.0],
    "moneda":   ["ARS", "ars", "ars", "ARS", "USD", "eur"],
})

df_resultado, linaje = pipeline_con_linaje(df_origen)

print("=== REGISTRO DE LINAJE ===\n")
for paso in linaje:
    print(f"📍 [{paso['paso']}] {paso['descripcion']}")
    print(f"   Entrada: {paso['registros_entrada']} → Salida: {paso['registros_salida']} "
          f"(eliminados: {paso['registros_eliminados']})")
    if paso["columnas_agregadas"]:
        print(f"   Columnas nuevas: {paso['columnas_agregadas']}")
    print()

print("\n=== DATASET FINAL ===")
print(df_resultado)
```

---

### 8.5 Clasificación de Datos Sensibles: PII y Regulaciones

#### ¿Qué son los datos PII?

**PII** (*Personally Identifiable Information* — Información de Identificación Personal) son todos los datos que permiten identificar, contactar o ubicar a una persona física, directa o indirectamente.

**Ejemplos de PII:**
- Nombre y apellido
- DNI / CUIL / CUIT
- Dirección de email
- Número de teléfono
- Domicilio
- Dirección IP
- Cookies y tokens de sesión
- Datos biométricos (huella dactilar, reconocimiento facial)
- Historial de salud, bancario o judicial

#### Marco regulatorio en Argentina y el mundo

| Regulación | Ámbito | Obligaciones principales |
|---|---|---|
| **Ley 25.326** (Argentina) | Datos personales | Consentimiento informado, derecho de acceso, rectificación y supresión |
| **GDPR** (Unión Europea) | Datos personales | Consentimiento explícito, portabilidad, derecho al olvido, multas de hasta el 4% de la facturación global |
| **LGPD** (Brasil) | Datos personales | Similar a GDPR, aplica a organizaciones que procesen datos de ciudadanos brasileños |
| **HIPAA** (EE.UU.) | Datos de salud | Protección específica de registros médicos |

#### Ejemplo 9 — Detección y enmascaramiento de PII con Python

```python
import pandas as pd
import re
import hashlib

df = pd.DataFrame({
    "id_cliente":  [101, 102, 103, 104],
    "nombre":      ["María García", "Juan López", "Ana Torres", "Luis Paz"],
    "email":       ["maria@ejemplo.com", "juan@test.com", "ana@demo.com", "luis@ok.com"],
    "dni":         ["28456789", "32111222", "40987654", "25333444"],
    "telefono":    ["+54 11 1234-5678", "+54 9 351 987-6543", None, "+54 11 4444-5555"],
    "monto_compra":[1500.0, 2300.0, 850.0, 1200.0],
})


def enmascarar_email(email: str) -> str:
    """Conserva el dominio pero oculta el usuario: ma***@ejemplo.com"""
    if not email or "@" not in email:
        return email
    usuario, dominio = email.split("@", 1)
    return f"{usuario[:2]}***@{dominio}"


def tokenizar_campo(valor: str) -> str:
    """
    Reemplaza el valor original por un hash SHA-256 reproducible.
    El mismo valor siempre produce el mismo token (útil para joins),
    pero el token no puede revertirse al valor original.
    """
    if pd.isna(valor):
        return None
    return hashlib.sha256(str(valor).encode()).hexdigest()[:16]


def anonimizar_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica técnicas de anonimización/pseudoanonimización a datos PII.
    """
    df_anon = df.copy()

    # Pseudoanonimización: reemplazar identificadores directos por tokens
    # (el join original sigue siendo posible si se guarda la tabla de mapeo)
    df_anon["email_token"]    = df_anon["email"].apply(tokenizar_campo)
    df_anon["dni_token"]      = df_anon["dni"].apply(tokenizar_campo)

    # Enmascaramiento: ocultar parcialmente valores sensibles
    df_anon["email_masked"]   = df_anon["email"].apply(
        lambda x: enmascarar_email(x) if pd.notna(x) else None
    )
    df_anon["telefono_masked"]= df_anon["telefono"].apply(
        lambda x: x[:6] + "****" if pd.notna(x) else None
    )

    # Eliminar columnas PII originales del dataset de salida
    columnas_pii = ["nombre", "email", "dni", "telefono"]
    df_anon = df_anon.drop(columns=columnas_pii)

    return df_anon


df_anonimizado = anonimizar_dataset(df)

print("=== DATASET ORIGINAL (contiene PII) ===")
print(df[["nombre", "email", "dni", "monto_compra"]])

print("\n=== DATASET ANONIMIZADO (seguro para análisis) ===")
print(df_anonimizado)
```

#### Ejemplo 10 — Escaneo automático de columnas con posible PII

```python
import pandas as pd
import re

# Patrones regex para detectar posible PII en los valores de las columnas
PATRONES_PII = {
    "email":    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$",
    "telefono": r"^\+?[\d\s\-\(\)]{8,15}$",
    "dni_arg":  r"^\d{7,8}$",
    "cuil":     r"^\d{2}-\d{8}-\d$",
    "tarjeta":  r"^\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}$",
}

# Palabras clave en el nombre de la columna que sugieren PII
KEYWORDS_PII = [
    "nombre", "apellido", "email", "mail", "telefono", "tel", "celular",
    "dni", "documento", "cuil", "cuit", "direccion", "domicilio",
    "password", "contraseña", "clave", "tarjeta", "cuenta",
]


def escanear_pii(df: pd.DataFrame) -> pd.DataFrame:
    """
    Escanea un DataFrame en busca de columnas que posiblemente contengan PII,
    basándose en el nombre de la columna y en los patrones de sus valores.
    """
    resultados = []

    for columna in df.columns:
        col_lower = columna.lower()

        # Verificar por nombre de columna
        por_nombre = any(kw in col_lower for kw in KEYWORDS_PII)

        # Verificar por patrón de valores (solo columnas de texto)
        por_patron = False
        tipo_detectado = None
        if df[columna].dtype == object:
            muestra = df[columna].dropna().head(20).astype(str)
            for tipo, patron in PATRONES_PII.items():
                coincidencias = muestra.str.match(patron).sum()
                if coincidencias / max(len(muestra), 1) >= 0.5:  # 50% o más coinciden
                    por_patron = True
                    tipo_detectado = tipo
                    break

        es_pii = por_nombre or por_patron
        resultados.append({
            "columna":       columna,
            "tipo_dato":     str(df[columna].dtype),
            "posible_pii":   es_pii,
            "detectado_por": ("nombre y patrón" if por_nombre and por_patron else
                              "nombre de columna" if por_nombre else
                              f"patrón de valores ({tipo_detectado})" if por_patron else
                              "No detectado"),
            "accion_sugerida": "Enmascarar o tokenizar" if es_pii else "Sin acción requerida",
        })

    return pd.DataFrame(resultados)


# Dataset de prueba con datos mixtos
df_test = pd.DataFrame({
    "id_cliente":  [101, 102, 103],
    "nombre":      ["María García", "Juan López", "Ana Torres"],
    "email":       ["maria@ejemplo.com", "juan@test.com", "ana@demo.com"],
    "dni":         ["28456789", "32111222", "40987654"],
    "segmento":    ["Premium", "Estándar", "Premium"],
    "monto_total": [15000.0, 8500.0, 22000.0],
})

reporte_pii = escanear_pii(df_test)
print("=== ESCANEO DE PII ===\n")
print(reporte_pii.to_string(index=False))

columnas_pii = reporte_pii[reporte_pii["posible_pii"]]["columna"].tolist()
print(f"\n⚠️ Columnas con posible PII detectadas: {columnas_pii}")
print("→ Aplicar enmascaramiento o tokenización antes de compartir este dataset.")
```

---

## Resumen de la Unidad

| Concepto | Definición resumida |
|---|---|
| **Calidad del dato** | Conjunto de características que determinan si un dato es apto para su uso previsto. |
| **Completitud** | % de valores presentes donde deberían existir. |
| **Exactitud** | Los valores representan correctamente la realidad. |
| **Consistencia** | Los datos son coherentes entre sistemas y dentro del mismo registro. |
| **Unicidad** | Cada entidad aparece una sola vez sin duplicados. |
| **Vigencia** | Los datos están actualizados en el momento en que se necesitan. |
| **Integridad** | Las relaciones entre datos y sus dominios de valores son válidos. |
| **Data Profiling** | Análisis estadístico y estructural de un dataset para diagnosticar su calidad. |
| **Great Expectations** | Librería Python para definir y ejecutar contratos de calidad automatizados. |
| **Data Governance** | Marco organizacional que define responsabilidades, políticas y procesos sobre los datos. |
| **CDO** | Máximo responsable de la estrategia de datos en la organización. |
| **Data Owner** | Responsable de negocio de un activo de datos específico. |
| **Data Steward** | Responsable operativo de la calidad y documentación de un activo. |
| **Catálogo de datos** | Inventario centralizado y buscable de todos los activos de datos. |
| **Diccionario de datos** | Documentación técnica de tablas y columnas: tipo, descripción, reglas. |
| **Linaje del dato** | Trazabilidad del origen, transformaciones y destino de un dato. |
| **PII** | Datos que permiten identificar a una persona: nombre, email, DNI, etc. |
| **Anonimización** | Eliminación irreversible de la posibilidad de identificar a una persona. |
| **Pseudoanonimización** | Reemplazo del dato original por un token reversible (con clave). |

---

## Librerías Python Utilizadas en esta Unidad

| Librería | Instalación | Uso |
|---|---|---|
| `pandas` | `pip install pandas` | Profiling, métricas, transformaciones y reportes |
| `numpy` | `pip install numpy` | Operaciones numéricas, detección de outliers |
| `great-expectations` | `pip install great-expectations` | Validación automatizada con contratos de calidad |
| `re` | Incluida en Python | Expresiones regulares para validación de formatos |
| `hashlib` | Incluida en Python | Tokenización y pseudoanonimización con SHA-256 |
| `json` | Incluida en Python | Exportación del diccionario de datos |
| `matplotlib` | `pip install matplotlib` | Visualización de distribuciones y outliers |
| `seaborn` | `pip install seaborn` | Gráficos estadísticos para Data Profiling |

---

## Bibliografía de la Unidad

- **DAMA International** — *DAMA-DMBOK: Data Management Body of Knowledge*, Capítulos 3, 7 y 13. Technics Publications.
- **Ladley, J.** — *Data Governance: How Organizations Value and Use Information as an Asset*. Morgan Kaufmann.
- **Documentación oficial de Great Expectations** — [docs.greatexpectations.io](https://docs.greatexpectations.io/).
- **Documentación de OpenMetadata** — [docs.open-metadata.org](https://docs.open-metadata.org/).
- **Ley 25.326 de Protección de Datos Personales** — Agencia de Acceso a la Información Pública (AAIP), Argentina.
- **Reglamento General de Protección de Datos (GDPR)** — Unión Europea, 2016/679.
- **Reis, J. & Housley, M.** — *Fundamentals of Data Engineering*, Capítulo 9. O'Reilly Media.
