# Clase 07 — Calidad del Dato: Las 6 Dimensiones y Data Profiling

> **Asignatura:** Ingeniería de Datos  
> **Docente:** Ing. Sergio Orozco  
> **Unidad:** III — Calidad del Dato y Gobierno

---

## Objetivos de la Clase

Al finalizar esta clase, el alumno será capaz de:

- Explicar por qué la calidad del dato es un **problema de negocio**, no solo técnico.
- Aplicar las **6 dimensiones de calidad** (DAMA) para evaluar cualquier dataset.
- Calcular métricas de calidad usando **pandas** sobre un dataset real.
- Construir un reporte de **Data Profiling** que diagnostique los problemas antes de transformar.
- Detectar **valores atípicos (outliers)** usando el método IQR.
- Implementar un **contrato de calidad** con la librería `great_expectations`.

---

## 1. ¿Por qué Importa la Calidad del Dato?

Antes de medir la calidad, necesitamos entender el costo de ignorarla.

> **"Garbage In, Garbage Out"** — Si los datos de entrada son incorrectos, cualquier análisis, reporte o modelo de machine learning que se construya sobre ellos producirá resultados incorrectos, sin importar cuán sofisticado sea el algoritmo o cuánto tiempo se le dedique.

### Casos reales de impacto

**Caso 1 — Campaña de marketing fallida:**
Una empresa envía emails a 100.000 clientes. Al revisar los datos:
- 25% de los registros tiene el campo `email` nulo.
- 10% tiene formato de email inválido (`juan@@empresa`).
- 5% son duplicados (el mismo cliente recibe el email dos veces).

**Resultado:** solo el 60% de los clientes recibe la campaña. El costo fue el mismo, pero el alcance fue un 40% menor. La empresa no lo sabe porque nadie midió la calidad de los datos antes de enviar.

**Caso 2 — Decisión gerencial errónea:**
Un reporte de ventas muestra una caída del 15% en el trimestre. La gerencia decide reducir presupuesto y despedir vendedores. Semanas después se descubre que el pipeline ETL tenía un bug que omitía transacciones de la región norte. Las ventas reales habían **crecido un 5%**.

**Resultado:** decisiones irreversibles tomadas sobre datos incorrectos.

**Caso 3 — Modelo de ML sesgado:**
Un modelo de scoring crediticio se entrena con datos donde el 30% de los ingresos reportados son incorrectos (por errores en el formulario de registro). El modelo aprueba y rechaza créditos basándose en información falsa, con impacto financiero y potencial impacto legal.

> **Conclusión:** La calidad del dato no es un problema técnico aislado. Es un problema de negocio con consecuencias medibles en dinero, reputación y cumplimiento regulatorio.

---

## 2. Las 6 Dimensiones de Calidad del Dato

La organización **DAMA International** (referencia global en gestión de datos) define seis dimensiones fundamentales para evaluar la calidad de un conjunto de datos. Cada dimensión responde una pregunta diferente:

```
┌──────────────────────────────────────────────────────────────────────┐
│              LAS 6 DIMENSIONES DE CALIDAD (DAMA)                    │
├────────────────────┬──────────────────────────────────────────────── │
│  1. COMPLETITUD    │  ¿Están todos los datos presentes?             │
│  2. EXACTITUD      │  ¿Representan la realidad correctamente?       │
│  3. CONSISTENCIA   │  ¿Son coherentes entre sistemas y tablas?      │
│  4. UNICIDAD       │  ¿Cada entidad aparece solo una vez?           │
│  5. VIGENCIA       │  ¿Los datos están actualizados?                │
│  6. INTEGRIDAD     │  ¿Se mantienen las relaciones entre los datos? │
└────────────────────┴──────────────────────────────────────────────── │
```

---

### Dimensión 1 — Completitud

**Pregunta:** ¿Están todos los datos presentes? ¿Hay valores nulos donde no debería haberlos?

Un campo es incompleto cuando tiene un valor nulo (`NULL`, `NaN`, cadena vacía `""`) en un contexto donde ese valor es **obligatorio** o **necesario para el análisis**.

$$\text{Completitud}(\%) = \frac{\text{Registros con valor en el campo}}{\text{Total de registros}} \times 100$$

**Ejemplo:** En una tabla de 1.000 clientes, el campo `email` tiene 850 valores completos:
$$\text{Completitud(email)} = \frac{850}{1000} \times 100 = 85\%$$

**¿Es aceptable un 85%?** Depende del contexto. Para una campaña de email marketing, un 15% de emails nulos es un problema crítico. Para un análisis de patrones de compra donde el email no es necesario, puede ser aceptable.

> **Importante:** No todo campo nulo es un problema. Si un cliente no tiene dirección de envío porque solo compra en tienda física, ese nulo es válido. La completitud debe evaluarse según el **uso que se le dará al dato**.

---

### Dimensión 2 — Exactitud

**Pregunta:** ¿Los datos representan correctamente la realidad del mundo real?

Un dato puede estar **presente** (no nulo) pero ser **incorrecto**. La exactitud es la dimensión más difícil de medir porque requiere comparar contra una fuente de verdad externa.

$$\text{Exactitud}(\%) = \frac{\text{Registros que coinciden con la realidad}}{\text{Total de registros validados}} \times 100$$

**Ejemplos de datos presentes pero incorrectos:**
- `precio_unitario = 0` → el producto existe en el catálogo pero tiene precio cero (imposible en este negocio).
- `fecha_nacimiento = 1850-03-15` → la persona tendría 175 años.
- `codigo_postal = 99999` → no corresponde a ningún código postal argentino.
- `email = "noreply@noreply.com"` → el campo está lleno pero con un valor "comodín" inútil.

---

### Dimensión 3 — Consistencia

**Pregunta:** ¿Los datos son coherentes entre distintos sistemas o dentro del mismo registro?

Un dato es inconsistente cuando el mismo concepto tiene **valores distintos en sistemas diferentes**, o cuando viola una regla lógica entre columnas.

**Tipos de inconsistencia:**

| Tipo | Ejemplo |
|---|---|
| **Entre sistemas** | El ERP dice que el cliente tiene 5 pedidos; el CRM dice 0 |
| **Intra-registro** | `fecha_entrega` es anterior a `fecha_pedido` (imposible) |
| **Entre tablas** | La tabla `ventas` tiene `id_cliente = 9999` pero ese ID no existe en `clientes` |
| **De formato** | "Argentina", "ARG", "AR", "argentina" para el mismo país |

---

### Dimensión 4 — Unicidad

**Pregunta:** ¿Cada entidad del mundo real aparece una sola vez en el dataset?

Un registro duplicado genera **doble conteo** en reportes, distorsiona métricas y puede causar errores en JOINs y agregaciones.

$$\text{Unicidad}(\%) = \frac{\text{Registros únicos}}{\text{Total de registros}} \times 100$$

**Tipos de duplicados:**
- **Exacto:** todas las columnas son idénticas.
- **Parcial:** el ID es el mismo pero otros campos difieren (puede ser un error de actualización).
- **Semántico:** el ID es distinto pero representa la misma entidad real (ej: "Ana García" y "ana garcia" son la misma persona).

---

### Dimensión 5 — Vigencia (Temporalidad)

**Pregunta:** ¿Los datos están actualizados en el momento en que se los necesita?

Un dato puede haber sido **exacto cuando se registró**, pero volverse **desactualizado** con el tiempo. Su "caducidad" depende del contexto de uso.

**Ejemplos:**
- El domicilio de un cliente fue registrado hace 3 años → puede ser incorrecto hoy.
- El precio de lista en el catálogo se actualizó ayer, pero el pipeline ETL corre a las 6 AM → los reportes del día tienen precios con hasta 24 horas de retraso.
- Las métricas de stock de un almacén deben actualizarse en tiempo real → un reporte de hace 2 horas puede mostrar disponibilidad de un producto agotado.

---

### Dimensión 6 — Integridad

**Pregunta:** ¿Se mantienen las relaciones entre los datos? ¿Los datos referenciados existen?

La integridad referencial garantiza que las relaciones entre tablas son válidas. Si `ventas.id_cliente = 101`, entonces el cliente con `id = 101` debe existir en la tabla `clientes`.

**Tipos de integridad:**
- **Referencial:** Las claves foráneas apuntan a registros que existen.
- **De dominio:** Los valores pertenecen al conjunto de valores válidos (`moneda` solo puede ser `ARS`, `USD` o `EUR`).
- **De negocio:** Las reglas propias del dominio se cumplen (`descuento` entre 0 y 100, `cantidad` > 0).

---

## 3. Data Profiling: Diagnosticar Antes de Transformar

El **Data Profiling** es el proceso de analizar estadística y estructuralmente un dataset para:
1. Entender su contenido, distribución y calidad.
2. Identificar problemas **antes** de que lleguen a producción.
3. Tomar decisiones informadas sobre cómo limpiar y transformar los datos.

> **Analogía médica:** El Data Profiling es como un examen médico completo antes de una cirugía. Antes de operar (transformar), hay que entender exactamente qué está pasando.

### 3.1 Reporte de Profiling Completo con Python

```python
import pandas as pd
import numpy as np

# Dataset con problemas intencionales para practicar el diagnóstico
data = {
    "id_venta":      [1, 2, 2, 3, None, 5, 6, 7, 8, 9],
    "fecha_venta":   ["2025-01-05", "2025-01-06", "2025-01-06", "2025-99-01",
                      "2025-01-08", "2025-01-09", "2025-01-10", "2025-01-11",
                      "2025-01-12", "2025-01-13"],
    "id_cliente":    [101, 102, 102, 103, 104, 105, 9999, 107, 108, 109],
    "monto":         [1500.0, 2300.0, 2300.0, 850.0, 1200.0, -50.0, 950.0,
                      0.0, 1800.0, 150000.0],
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
    sep = "=" * 60

    print(f"\n{sep}")
    print(f"  REPORTE DE DATA PROFILING")
    print(f"  Registros: {n} | Columnas: {len(df.columns)}")
    print(sep)

    # ── 1. Completitud ──────────────────────────────────────────
    print("\n📊 1. COMPLETITUD (valores nulos por columna)")
    nulos = df.isnull().sum()
    pct_nulos = (nulos / n * 100).round(2)
    completitud = pd.DataFrame({
        "Nulos": nulos,
        "% Nulos": pct_nulos,
        "% Completo": (100 - pct_nulos).round(2),
        "Estado": pct_nulos.apply(
            lambda x: "✅ OK" if x == 0
                      else ("⚠️ Revisar" if x < 20
                            else "❌ Crítico")
        )
    })
    print(completitud.to_string())

    # ── 2. Unicidad ──────────────────────────────────────────────
    print(f"\n🔁 2. UNICIDAD (duplicados)")
    total_dup = df.duplicated().sum()
    print(f"  Filas completamente duplicadas: {total_dup} ({total_dup/n*100:.1f}%)")
    for col in df.columns:
        n_dup = df[col].duplicated(keep=False).sum()
        if n_dup > 0:
            print(f"  '{col}': {n_dup} valores duplicados | {df[col].nunique()} únicos de {n}")

    # ── 3. Estadísticas de columnas numéricas ────────────────────
    print(f"\n📈 3. DISTRIBUCIÓN NUMÉRICA")
    numericas = df.select_dtypes(include=[np.number])
    if not numericas.empty:
        stats = numericas.describe().T
        # Calcular outliers con IQR
        def contar_outliers(col):
            q1, q3 = col.quantile(0.25), col.quantile(0.75)
            iqr = q3 - q1
            return ((col < q1 - 1.5*iqr) | (col > q3 + 1.5*iqr)).sum()
        stats["outliers"] = numericas.apply(contar_outliers)
        print(stats[["count", "mean", "min", "50%", "max", "outliers"]].to_string())

    # ── 4. Dominio de valores categóricos ────────────────────────
    print(f"\n🗂️  4. DOMINIO DE VALORES CATEGÓRICOS")
    for col in df.select_dtypes(include=["object"]).columns:
        valores = df[col].value_counts(dropna=False)
        print(f"\n  '{col}' — {df[col].nunique()} únicos:")
        print(f"  {valores.to_dict()}")

    # ── 5. Resumen ejecutivo ─────────────────────────────────────
    print(f"\n{sep}")
    print("  RESUMEN EJECUTIVO DE PROBLEMAS")
    print(sep)
    print(f"  • Registros duplicados:      {total_dup}")
    print(f"  • Columnas con nulos:        {(nulos > 0).sum()}")
    fechas_invalidas = df.select_dtypes(include=["datetime64"]).isnull().sum().sum()
    print(f"  • Fechas inválidas (NaT):    {fechas_invalidas}")
    if "monto" in df.columns:
        print(f"  • Montos negativos:          {(df['monto'] < 0).sum()}")
        print(f"  • Montos cero:               {(df['monto'] == 0).sum()}")


generar_reporte_profiling(df)
```

---

## 4. Métricas y KPIs de Calidad

Las métricas de calidad deben monitorearse **a lo largo del tiempo**. Un dataset con 95% de completitud hoy puede caer a 72% mañana si algo rompió en el pipeline.

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

print("=" * 50)
print("  KPIs DE CALIDAD POR DIMENSIÓN")
print("=" * 50)

# Dimensión 1: Completitud
print("\n📊 COMPLETITUD")
print(f"  id_venta:      {df['id_venta'].notna().sum()/n*100:.1f}%")
print(f"  monto:         {df['monto'].notna().sum()/n*100:.1f}%")
print(f"  email_cliente: {df['email_cliente'].notna().sum()/n*100:.1f}%")
print(f"  fecha_venta:   {df['fecha_venta'].notna().sum()/n*100:.1f}%")

# Dimensión 2: Unicidad
duplicados = df.duplicated(subset=["id_venta"]).sum()
print(f"\n🔁 UNICIDAD")
print(f"  Duplicados en id_venta:  {duplicados}")
print(f"  Unicidad id_venta:       {(n - duplicados)/n*100:.1f}%")

# Dimensión 3: Consistencia de dominio
monedas_validas = {"ARS", "USD", "EUR"}
monedas_norm = df["moneda"].str.upper().str.strip()
monedas_invalidas = (~monedas_norm.isin(monedas_validas)).sum()
print(f"\n🔄 CONSISTENCIA")
print(f"  Monedas fuera de dominio: {monedas_invalidas}")
print(f"  Consistencia de moneda:   {(n-monedas_invalidas)/n*100:.1f}%")

# Dimensión 4: Exactitud (reglas de negocio)
montos_invalidos = ((df["monto"] <= 0)).sum()
print(f"\n✅ EXACTITUD")
print(f"  Montos inválidos (<=0):   {montos_invalidos}")
print(f"  Exactitud de monto:       {(n-montos_invalidos)/n*100:.1f}%")

# Dimensión 5: Formato (validación con regex)
patron_email = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
emails_no_nulos = df["email_cliente"].dropna()
emails_validos  = emails_no_nulos.str.match(patron_email).sum()
print(f"\n📧 FORMATO (EMAIL)")
print(f"  Emails inválidos:         {len(emails_no_nulos) - emails_validos}")
print(f"  Exactitud de formato:     {emails_validos/len(emails_no_nulos)*100:.1f}%")

# Score global
scores = [
    df["id_venta"].notna().mean(),
    (n - duplicados)/n,
    df["monto"].notna().mean(),
    df["email_cliente"].notna().mean(),
    (n - monedas_invalidas)/n,
    (n - montos_invalidos)/n,
]
score_global = sum(scores)/len(scores)*100
estado = "✅ Aceptable" if score_global >= 90 else ("⚠️ Revisar" if score_global >= 75 else "❌ Crítico")
print(f"\n{'='*50}")
print(f"  SCORE GLOBAL DE CALIDAD: {score_global:.1f}%  {estado}")
print(f"{'='*50}")
```

---

## 5. Detección de Outliers con el Método IQR

Un **outlier** (valor atípico) es un valor que se aleja significativamente del rango esperado. Pueden ser errores de carga, valores legítimos pero extremos, o señales de fraude.

El método **IQR** (Rango Intercuartílico) es robusto y no asume distribución normal:

$$\text{Límite inferior} = Q_1 - 1.5 \times IQR$$
$$\text{Límite superior} = Q_3 + 1.5 \times IQR$$
$$\text{donde } IQR = Q_3 - Q_1$$

```
Distribución de monto:
 Min    Q1     Mediana    Q3     Max
 │      │         │       │      │
 ├──────┤─────────┤───────┤──────┤
 └──────┴─────────┴───────┴──────┘
 │      │                 │      │
 ◄──────►                 ◄──────►
 Posibles                 Posibles
 outliers                 outliers
 inferiores               superiores
```

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "monto": [1500.0, 2300.0, 850.0, 1200.0, 950.0, 1800.0,
              -50.0,    # outlier negativo
              150000.0, # outlier extremo positivo
              1600.0, 1100.0],
})

def detectar_outliers_iqr(serie: pd.Series) -> pd.DataFrame:
    Q1  = serie.quantile(0.25)
    Q3  = serie.quantile(0.75)
    IQR = Q3 - Q1
    lim_inf = Q1 - 1.5 * IQR
    lim_sup = Q3 + 1.5 * IQR

    print(f"  Q1={Q1:.1f} | Q3={Q3:.1f} | IQR={IQR:.1f}")
    print(f"  Rango válido: [{lim_inf:.1f}, {lim_sup:.1f}]")

    es_outlier = (serie < lim_inf) | (serie > lim_sup)
    return pd.DataFrame({
        "valor":      serie,
        "es_outlier": es_outlier,
        "motivo":     np.where(serie < lim_inf, "Demasiado bajo",
                      np.where(serie > lim_sup, "Demasiado alto", "Normal")),
    })

print("=== DETECCIÓN DE OUTLIERS EN COLUMNA 'monto' ===")
resultado = detectar_outliers_iqr(df["monto"])
print("\nOutliers detectados:")
print(resultado[resultado["es_outlier"]].to_string())
print(f"\nTotal: {resultado['es_outlier'].sum()} outliers en {len(df)} registros")
```

---

## 6. Validación Automatizada con Great Expectations

**Great Expectations** (GE) es la librería Python líder para definir **contratos de calidad** sobre los datos. Un contrato de calidad es un conjunto de reglas que los datos *deben* cumplir para ser considerados aptos para el análisis. Si las reglas se violan, el pipeline se detiene.

```bash
pip install great-expectations
```

```python
import great_expectations as ge
import pandas as pd

df_crudo = pd.DataFrame({
    "id_venta":        [1, 2, 2, 3, None, 5],
    "precio_unitario": [1500.0, 2300.0, 2300.0, -50.0, 850.0, 75000.0],
    "moneda":          ["ARS", "ars", "ARS", "ARS", "USD", "BTC"],
    "email":           ["a@b.com", "juan@@err", "juan@@err", None, "ok@test.com", "otro@ok.com"],
    "cantidad":        [1, 2, 2, 3, 0, 1],
})

df = ge.from_pandas(df_crudo)

# ── Definir el contrato de calidad ─────────────────────────────────
# Completitud
df.expect_column_values_to_not_be_null("id_venta")
df.expect_column_values_to_not_be_null("precio_unitario")

# Unicidad
df.expect_column_values_to_be_unique("id_venta")

# Rango válido (exactitud)
df.expect_column_values_to_be_between("precio_unitario", min_value=0.01, max_value=50000.0)
df.expect_column_values_to_be_between("cantidad", min_value=1, max_value=9999)

# Dominio (consistencia)
df.expect_column_values_to_be_in_set("moneda", value_set=["ARS", "USD", "EUR"])

# Formato (regex)
df.expect_column_values_to_match_regex(
    "email",
    regex=r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$",
    mostly=0.9  # tolera hasta 10% de excepciones (ej: nulos)
)

# ── Validar y mostrar resultado ─────────────────────────────────────
resultado = df.validate()
stats = resultado["statistics"]

print("=" * 50)
print("  RESULTADO DEL CONTRATO DE CALIDAD")
print("=" * 50)
print(f"  Evaluadas:  {stats['evaluated_expectations']}")
print(f"  ✅ Exitosas: {stats['successful_expectations']}")
print(f"  ❌ Fallidas: {stats['unsuccessful_expectations']}")
print(f"  Score:      {stats['success_percent']:.1f}%")
print(f"  Estado:     {'APROBADO ✅' if resultado['success'] else 'RECHAZADO ❌'}")

# Detalle de fallas
print("\nDetalle de expectativas fallidas:")
for exp in resultado["results"]:
    if not exp["success"]:
        col  = exp["expectation_config"]["kwargs"].get("column", "N/A")
        tipo = exp["expectation_config"]["expectation_type"]
        print(f"  ❌ [{col}] {tipo}")
```

---

## Resumen de la Clase

| Dimensión | Pregunta | Métrica |
|---|---|---|
| **Completitud** | ¿Hay nulos? | % de registros con valor |
| **Exactitud** | ¿Son correctos? | % que cumple reglas de negocio |
| **Consistencia** | ¿Son coherentes? | % dentro del dominio válido |
| **Unicidad** | ¿Hay duplicados? | % de registros únicos |
| **Vigencia** | ¿Están actualizados? | Tiempo desde la última actualización |
| **Integridad** | ¿Las relaciones son válidas? | % de FK que tienen referencia |

---

> 💡 **Para la próxima clase:** Sabemos **cómo medir** la calidad. Ahora necesitamos saber **quién es responsable** de mantenerla. La **Clase 08** introduce el Gobierno del Dato: el marco organizacional que da sustentabilidad a todo lo que construimos aquí.
