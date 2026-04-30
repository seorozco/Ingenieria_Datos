# Clase 08 — Gobierno del Dato y Gestión de Metadatos

> **Asignatura:** Ingeniería de Datos  
> **Docente:** Ing. Sergio Orozco  
> **Unidad:** III — Calidad del Dato y Gobierno

---

## Objetivos de la Clase

Al finalizar esta clase, el alumno será capaz de:

- Explicar qué es el **Gobierno del Dato** y por qué es necesario en una organización.
- Identificar los **roles** del ecosistema de gobierno: CDO, Data Owner y Data Steward.
- Comprender la diferencia entre un **catálogo de datos** y un **diccionario de datos**.
- Explicar el concepto de **linaje del dato** y su importancia para la trazabilidad.
- Clasificar los datos **PII** y conocer el marco regulatorio básico aplicable en Argentina.
- Implementar técnicas básicas de **enmascaramiento y anonimización** de datos sensibles.

---

## 1. ¿Qué es el Gobierno del Dato?

El **Gobierno del Dato** (Data Governance) es el sistema de toma de decisiones y responsabilidades que define **quién puede hacer qué con cuáles datos** dentro de una organización.

No es una herramienta ni una tecnología. Es un **marco organizacional** que combina:
- **Políticas:** reglas formales sobre cómo se gestionan los datos.
- **Procesos:** procedimientos operativos para acceso, calidad y cambios.
- **Roles:** personas con responsabilidades específicas sobre los datos.
- **Estándares:** definiciones comunes, formatos, nomenclatura.

### ¿Por qué es necesario?

Sin gobierno del dato, las organizaciones enfrentan estos problemas recurrentes:

```
Síntoma                          Causa raíz (sin gobierno)
──────────────────────────────── ──────────────────────────────────────────
"Los números no coinciden entre  No hay una definición única de 'venta'
 el reporte de Ventas y el de    acordada entre ambos departamentos.
 Finanzas"

"Nadie sabe de dónde viene       No existe linaje documentado. El data
 ese campo del dashboard"        engineer que lo creó ya no está.

"Un analista descargó datos de   No hay políticas de acceso ni
 clientes a su laptop personal"  clasificación de datos sensibles.

"Cada equipo tiene su propia     No hay un catálogo centralizado que
 versión del catálogo de         sea la fuente de verdad.
 productos"
```

> **Analogía:** El gobierno del dato es como el reglamento de una biblioteca. Define quién puede sacar libros (acceso), quién puede modificarlos (custodia), cuáles son de consulta restringida (clasificación de datos sensibles) y cómo saber si un libro fue alterado (auditoría y linaje).

### Principios fundamentales

| Principio | Descripción |
|---|---|
| **Responsabilidad definida** | Cada dato tiene un propietario que responde por él |
| **Acceso controlado** | Mínimo privilegio: cada persona accede solo a lo que necesita |
| **Calidad medible** | Las reglas de calidad están formalizadas y monitoreadas |
| **Trazabilidad completa** | Se puede rastrear el origen y transformación de cualquier dato |
| **Cumplimiento regulatorio** | Los procesos respetan las leyes de protección de datos |

---

## 2. Los Roles del Ecosistema de Gobierno

```
┌────────────────────────────────────────────────────────────────────┐
│              JERARQUÍA DE ROLES EN DATA GOVERNANCE                 │
│                                                                    │
│  C-Level        ┌──────────────────────────────┐                  │
│                 │  CDO (Chief Data Officer)      │                  │
│                 │  Estrategia y política global  │                  │
│                 └───────────────┬──────────────┘                  │
│                                 │                                  │
│  Negocio        ┌───────────────▼──────────────┐                  │
│                 │  DATA OWNER                   │                  │
│                 │  (Gerente de área)            │                  │
│                 │  Responsabilidad de negocio   │                  │
│                 └───────────────┬──────────────┘                  │
│                                 │                                  │
│  Operativo      ┌───────────────▼──────────────┐                  │
│                 │  DATA STEWARD                 │                  │
│                 │  (Analista / Especialista)    │                  │
│                 │  Calidad y documentación     │                  │
│                 └───────────────┬──────────────┘                  │
│                                 │                                  │
│  Técnico        ┌───────────────▼──────────────┐                  │
│                 │  DATA ENGINEER                │                  │
│                 │  Implementación y pipelines   │                  │
│                 └──────────────────────────────┘                  │
└────────────────────────────────────────────────────────────────────┘
```

### 2.1 Chief Data Officer (CDO)

Es el **máximo responsable de la estrategia de datos** de la organización. Define la visión, prioridades y políticas de alto nivel. Reporta a la dirección ejecutiva.

**Responsabilidades:**
- Definir la estrategia global de datos de la empresa.
- Garantizar el cumplimiento con regulaciones de datos.
- Promover la cultura *data-driven* en toda la organización.
- Gestionar el presupuesto del área de datos.
- Arbitrar disputas sobre propiedad y uso de datos entre áreas.

### 2.2 Data Owner (Propietario del Dato)

Es el **responsable de negocio** de un conjunto de datos específico. Generalmente es un gerente o director del área que genera o usa esos datos.

**Ejemplos:**
- El Gerente de Ventas es el Data Owner de los datos de transacciones y clientes.
- El Gerente de Finanzas es el Data Owner de los datos contables y presupuestarios.
- El Gerente de RR.HH. es el Data Owner de los datos de empleados.

**Responsabilidades:**
- Aprobar (o denegar) el acceso a sus datos.
- Definir los requisitos de calidad para sus datos.
- Resolver disputas sobre el significado o reglas de negocio.
- Asegurar que los datos de su dominio cumplan con las políticas organizacionales.

> **Sin Data Owners, la gobernanza no funciona.** Si nadie tiene la autoridad de decir "este campo debe ser obligatorio" o "este tipo de cambio solo puede ser positivo", las reglas de calidad son solo sugerencias que nadie cumple.

### 2.3 Data Steward (Custodio del Dato)

Es el **responsable operativo** de la calidad y gestión diaria de un conjunto de datos. Trabaja en coordinación con el Data Owner y el equipo de ingeniería.

**Responsabilidades:**
- Documentar los datos (diccionario de datos, glosario de términos).
- Monitorear las métricas de calidad y reportar anomalías.
- Definir y mantener las reglas de validación.
- Gestionar solicitudes de acceso a los datos.
- Coordinar la resolución de problemas de calidad entre sistemas.

### Resumen comparativo de roles

| Rol | Perfil | Responsabilidad | Ejemplo concreto |
|---|---|---|---|
| **CDO** | Director ejecutivo | Estrategia y política global | "Los datos de clientes son un activo estratégico de la empresa" |
| **Data Owner** | Gerente de área | Responsabilidad de negocio | "El campo 'email' es obligatorio para clientes activos" |
| **Data Steward** | Analista senior | Calidad y documentación | Actualiza el diccionario y monitorea el % de emails nulos |
| **Data Engineer** | Técnico | Implementación | Implementa la regla de validación en el pipeline |

---

## 3. Catálogo de Datos y Diccionario de Datos

### 3.1 Catálogo de Datos

Es un **inventario centralizado y buscable** de todos los activos de datos de la organización. Responde la pregunta: *"¿Qué datos existen en nuestra organización y dónde están?"*

**Funciones principales:**
- **Descubrimiento:** los analistas encuentran el dataset que necesitan sin preguntar a 5 personas.
- **Contexto:** cada activo tiene descripción, responsable, calidad y linaje.
- **Colaboración:** los equipos pueden comentar y enriquecer la documentación.
- **Cumplimiento:** facilita identificar dónde están los datos sensibles (PII).

**Herramientas del mercado:**

| Herramienta | Tipo | Descripción |
|---|---|---|
| **DataHub** (LinkedIn) | Open source | Muy adoptado en la industria, integración con Airflow, dbt |
| **Apache Atlas** | Open source | Ecosistema Hadoop, linaje nativo |
| **OpenMetadata** | Open source | Moderno, API-first, muy completo |
| **Collibra** | Comercial | Referencia del mercado enterprise |
| **Alation** | Comercial | Foco en descubrimiento colaborativo |

### 3.2 Diccionario de Datos

Es la **documentación técnica detallada** de cada tabla y columna: qué es cada campo, su tipo de dato, valores válidos, origen, responsable y reglas de validación.

**Ejemplo práctico — Construcción de un diccionario con Python:**

```python
import pandas as pd
import json
from datetime import date

# Definición del diccionario de datos de la tabla de ventas
diccionario = [
    {
        "tabla":          "dw.fact_ventas",
        "columna":        "id_venta",
        "tipo_dato":      "INTEGER",
        "nullable":       False,
        "unico":          True,
        "descripcion":    "Identificador único de la transacción de venta. "
                          "Generado por el ERP SAP, campo BELNR.",
        "origen":         "ERP SAP — tabla BSEG, campo BELNR",
        "valores_validos":"Enteros positivos > 0. No puede ser nulo.",
        "reglas_calidad": "Unicidad 100%. Completitud 100%.",
        "data_owner":     "Gerencia Comercial",
        "data_steward":   "Ana González",
        "ultima_revision": str(date.today()),
    },
    {
        "tabla":          "dw.fact_ventas",
        "columna":        "fecha_venta",
        "tipo_dato":      "DATE",
        "nullable":       False,
        "unico":          False,
        "descripcion":    "Fecha en que se registró la venta en el sistema transaccional "
                          "(fecha contable, no fecha de entrega).",
        "origen":         "ERP SAP — tabla BKPF, campo BUDAT",
        "valores_validos":"Fechas entre 2020-01-01 y la fecha actual. No puede ser futura.",
        "reglas_calidad": "Completitud 100%. fecha_venta <= fecha_actual.",
        "data_owner":     "Gerencia Comercial",
        "data_steward":   "Ana González",
        "ultima_revision": str(date.today()),
    },
    {
        "tabla":          "dw.fact_ventas",
        "columna":        "monto",
        "tipo_dato":      "NUMERIC(15,2)",
        "nullable":       False,
        "unico":          False,
        "descripcion":    "Monto bruto de la venta en la moneda de la transacción, "
                          "sin impuestos. Corresponde al precio de lista.",
        "origen":         "ERP SAP — tabla BSEG, campo WRBTR",
        "valores_validos":"Valores > 0. Máximo esperado en operación normal: $500.000.",
        "reglas_calidad": "Completitud 100%. monto > 0. Outliers IQR: revisar > $200.000.",
        "data_owner":     "Gerencia Comercial",
        "data_steward":   "Ana González",
        "ultima_revision": str(date.today()),
    },
    {
        "tabla":          "dw.fact_ventas",
        "columna":        "moneda",
        "tipo_dato":      "VARCHAR(3)",
        "nullable":       False,
        "unico":          False,
        "descripcion":    "Código ISO 4217 de la moneda de la transacción.",
        "origen":         "ERP SAP — tabla BSEG, campo WAERS",
        "valores_validos":"ARS | USD | EUR (lista cerrada)",
        "reglas_calidad": "Consistencia 100% contra lista de monedas válidas.",
        "data_owner":     "Gerencia Comercial",
        "data_steward":   "Ana González",
        "ultima_revision": str(date.today()),
    },
]

df_dict = pd.DataFrame(diccionario)

# Exportar para compartir
df_dict.to_csv("diccionario_fact_ventas.csv", index=False, encoding="utf-8")

print("=== DICCIONARIO DE DATOS — dw.fact_ventas ===\n")
print(df_dict[["columna", "tipo_dato", "nullable", "descripcion", "data_owner"]].to_string(index=False))
```

---

## 4. Linaje del Dato (Data Lineage)

El **linaje del dato** es la capacidad de rastrear el **origen, transformaciones y destino** de un dato a lo largo de todo su ciclo de vida.

**Responde la pregunta:** *"¿De dónde viene el número $2.3M de ventas que aparece en el dashboard de gerencia del lunes pasado?"*

### ¿Por qué es esencial?

| Situación | Sin linaje | Con linaje |
|---|---|---|
| El número del reporte es incorrecto | Horas o días buscando el bug | Trazabilidad inmediata: en qué paso ocurrió el error |
| Auditoría regulatoria | Imposible demostrar el origen | Documentación completa del proceso |
| Cambio en tabla fuente | No se sabe qué reportes se afectarán | Análisis de impacto automatizado |
| Eliminación de datos PII | No se sabe en qué sistemas está | Se puede eliminar de todos los puntos |

```
Ejemplo de linaje de un indicador de ventas:

ERP SAP          staging          dw               BI
tabla BSEG  ──►  ventas_raw  ──►  fact_ventas  ──►  dashboard_ventas
campo WRBTR      (CSV/Parquet)    columna monto     tarjeta "Ventas Q1"

Transformaciones intermedias:
  ├── DROP duplicados (DEDUP)
  ├── FILTER nulos (id_venta IS NOT NULL)
  ├── NORMALIZE moneda (UPPER + TRIM)
  ├── FILTER montos inválidos (monto > 0)
  └── SUM(monto) GROUP BY trimestre
```

### Implementación: documentar linaje en el pipeline

```python
import pandas as pd
from datetime import datetime

def pipeline_con_linaje(df_fuente: pd.DataFrame) -> tuple:
    """
    Ejecuta el pipeline y registra automáticamente el linaje de cada paso.
    """
    registro_linaje = []

    def registrar_paso(nombre: str, descripcion: str,
                       df_antes: pd.DataFrame, df_despues: pd.DataFrame,
                       sql_equivalente: str = "") -> None:
        registro_linaje.append({
            "paso":               nombre,
            "descripcion":        descripcion,
            "timestamp":          datetime.now().isoformat(),
            "registros_entrada":  len(df_antes),
            "registros_salida":   len(df_despues),
            "registros_perdidos": len(df_antes) - len(df_despues),
            "columnas_nuevas":    list(set(df_despues.columns) - set(df_antes.columns)),
            "sql_equivalente":    sql_equivalente,
        })

    # ── Paso 0: Origen ─────────────────────────────────────────────
    registrar_paso(
        "FUENTE", "ERP SAP → tabla BSEG → columnas: id_venta, fecha, monto, moneda",
        df_fuente, df_fuente, "SELECT * FROM erp.bseg WHERE budat > :fecha_corte"
    )

    # ── Paso 1: Deduplicación ──────────────────────────────────────
    df1 = df_fuente.drop_duplicates(subset=["id_venta"])
    registrar_paso(
        "DEDUP", "Eliminación de registros con id_venta duplicado, se conserva el último",
        df_fuente, df1,
        "SELECT DISTINCT ON (id_venta) * FROM staging ORDER BY id_venta, updated_at DESC"
    )

    # ── Paso 2: Filtrar nulos obligatorios ─────────────────────────
    df2 = df1.dropna(subset=["id_venta", "monto"])
    registrar_paso(
        "FILTER_NULOS", "Eliminación de filas con id_venta o monto nulos",
        df1, df2,
        "SELECT * FROM dedup WHERE id_venta IS NOT NULL AND monto IS NOT NULL"
    )

    # ── Paso 3: Normalizar moneda ──────────────────────────────────
    df3 = df2.copy()
    df3["moneda"] = df3["moneda"].str.upper().str.strip()
    registrar_paso(
        "NORMALIZE_MONEDA", "Estandarización de código de moneda: UPPER + TRIM",
        df2, df3,
        "SELECT *, UPPER(TRIM(moneda)) AS moneda FROM filter_nulos"
    )

    # ── Paso 4: Filtrar montos inválidos ───────────────────────────
    df4 = df3[df3["monto"] > 0]
    registrar_paso(
        "FILTER_MONTO", "Eliminar registros con monto <= 0 (regla de negocio)",
        df3, df4,
        "SELECT * FROM normalize_moneda WHERE monto > 0"
    )

    return df4, registro_linaje


# Datos de prueba
df_origen = pd.DataFrame({
    "id_venta": [1, 2, 2, 3, None, 5],
    "monto":    [1500.0, 2300.0, 2300.0, -50.0, 1200.0, 950.0],
    "moneda":   ["ARS", "ars", "ars", "ARS", "USD", "eur"],
})

df_resultado, linaje = pipeline_con_linaje(df_origen)

print("=== REGISTRO DE LINAJE DEL PIPELINE ===\n")
for paso in linaje:
    print(f"📍 [{paso['paso']}] {paso['descripcion']}")
    print(f"   Entrada: {paso['registros_entrada']} → Salida: {paso['registros_salida']}"
          f" (perdidos: {paso['registros_perdidos']})")
    if paso["columnas_nuevas"]:
        print(f"   Columnas agregadas: {paso['columnas_nuevas']}")
    print()
```

---

## 5. Datos PII y Protección de Datos Personales

### 5.1 ¿Qué son los datos PII?

**PII** (*Personally Identifiable Information* — Información de Identificación Personal) son todos los datos que permiten identificar, contactar o ubicar a una persona física, directa o indirectamente.

```
┌──────────────────────────────────────────────────────────────────────┐
│                     CLASIFICACIÓN DE DATOS PII                      │
├─────────────────────────────┬──────────────────────────────────────  │
│  PII DIRECTA                │  PII INDIRECTA (combinación)          │
│  (identifica sola)          │  (identifica en combinación)          │
├─────────────────────────────┼──────────────────────────────────────  │
│  ✉️  Email                  │  🏘️  Código postal + edad + género    │
│  📛 Nombre completo         │  📅 Fecha de nacimiento               │
│  🪪  DNI / CUIL             │  🌍 Dirección IP                     │
│  📞 Teléfono                │  🍪 Cookie ID / Device ID            │
│  🏠 Domicilio               │  📊 Historial de compras              │
│  🏥 Datos de salud          │  📍 Coordenadas GPS                  │
│  💳 Datos bancarios         │                                       │
└─────────────────────────────┴──────────────────────────────────────  │
```

### 5.2 Marco regulatorio

| Regulación | Ámbito | Obligaciones clave |
|---|---|---|
| **Ley 25.326** (Argentina) | Datos personales argentinos | Consentimiento informado, derecho de acceso, rectificación y supresión |
| **GDPR** (UE) | Datos de ciudadanos europeos | Consentimiento explícito, portabilidad, derecho al olvido. Multa hasta 4% de facturación global |
| **LGPD** (Brasil) | Datos de ciudadanos brasileños | Similar a GDPR. Aplica a operaciones en Brasil o que traten datos de brasileños |
| **HIPAA** (EE.UU.) | Datos de salud | Protección estricta de registros médicos |

> **Importante para el Data Engineer:** Si tu pipeline extrae, transforma o carga datos PII, tenés **responsabilidad legal**. Debés implementar controles de acceso, enmascaramiento o anonimización según corresponda.

### 5.3 Técnicas de protección de datos PII

```python
import pandas as pd
import hashlib
import re

df = pd.DataFrame({
    "id_cliente":   [101, 102, 103, 104],
    "nombre":       ["María García", "Juan López", "Ana Torres", "Luis Paz"],
    "email":        ["maria@ejemplo.com", "juan@test.com", "ana@demo.com", "luis@ok.com"],
    "dni":          ["28456789", "32111222", "40987654", "25333444"],
    "monto_compra": [1500.0, 2300.0, 850.0, 1200.0],
})


# ── Técnica 1: Enmascaramiento (Masking) ────────────────────────────
# Oculta parte del valor pero conserva el formato para identificación visual

def enmascarar_email(email: str) -> str:
    """ma***@ejemplo.com — oculta el usuario, conserva el dominio"""
    if not email or "@" not in email:
        return email
    usuario, dominio = email.split("@", 1)
    visible = usuario[:2] if len(usuario) > 2 else usuario[0]
    return f"{visible}***@{dominio}"

def enmascarar_nombre(nombre: str) -> str:
    """María G. — conserva nombre, oculta apellido"""
    partes = nombre.strip().split()
    if len(partes) == 1:
        return partes[0]
    return f"{partes[0]} {partes[-1][0]}."

def enmascarar_dni(dni: str) -> str:
    """****6789 — oculta primeros dígitos, conserva los últimos 4"""
    if not dni:
        return dni
    return f"{'*' * (len(dni) - 4)}{dni[-4:]}"


# ── Técnica 2: Pseudonimización (Hashing) ────────────────────────────
# Reemplaza el identificador real por un hash determinístico.
# Permite hacer JOINs sin exponer el dato real.

def pseudonimizar(valor: str, sal: str = "mi_sal_secreta_2025") -> str:
    """Genera un hash SHA-256 determinístico del valor."""
    texto = f"{valor}{sal}".encode("utf-8")
    return hashlib.sha256(texto).hexdigest()[:16]  # primeros 16 chars


# Aplicar transformaciones
df_enmascarado = df.copy()
df_enmascarado["email"]  = df_enmascarado["email"].apply(enmascarar_email)
df_enmascarado["nombre"] = df_enmascarado["nombre"].apply(enmascarar_nombre)
df_enmascarado["dni"]    = df_enmascarado["dni"].apply(enmascarar_dni)

# Pseudonimizar el email para análisis (permite JOINs sin exponer el email real)
df_enmascarado["email_hash"] = df["email"].apply(pseudonimizar)

print("=== DATASET ORIGINAL (solo para ver el contraste) ===")
print(df[["id_cliente", "nombre", "email", "dni"]].to_string(index=False))

print("\n=== DATASET ENMASCARADO (seguro para análisis) ===")
print(df_enmascarado[["id_cliente", "nombre", "email", "dni", "email_hash"]].to_string(index=False))

print("\nNota: el campo 'monto_compra' no es PII y no requiere enmascaramiento.")
```

**Resultado del enmascaramiento:**

```
Original:
  id_cliente   nombre            email                dni
  101          María García      maria@ejemplo.com    28456789

Enmascarado:
  id_cliente   nombre            email                dni        email_hash
  101          María G.          ma***@ejemplo.com    ****6789   a3f7c2b1d4e8...
```

---

## 6. Implementando una Política de Clasificación de Datos

Una política de clasificación define **niveles de sensibilidad** y los controles asociados a cada uno:

```
NIVEL 1 — PÚBLICO
  Puede ser accedido por cualquiera, incluso externo.
  Ejemplo: precios de lista, información del sitio web.
  Control: ninguno especial.

NIVEL 2 — INTERNO
  Solo para empleados de la organización.
  Ejemplo: reportes de ventas por producto, métricas internas.
  Control: acceso autenticado, sin PII.

NIVEL 3 — CONFIDENCIAL
  Solo para empleados autorizados del área.
  Ejemplo: datos de clientes (sin PII directa), estrategias comerciales.
  Control: acceso por rol (RBAC), log de accesos.

NIVEL 4 — RESTRINGIDO (PII / Datos Sensibles)
  Solo para quienes tienen necesidad estricta de negocio.
  Ejemplo: DNI, datos de salud, información bancaria, datos biométricos.
  Control: acceso mínimo, enmascaramiento, cifrado, auditoría completa.
```

---

## Resumen de la Clase

| Concepto | Definición en una frase |
|---|---|
| **Gobierno del Dato** | Marco organizacional de responsabilidades, políticas y procesos sobre los datos |
| **CDO** | Director ejecutivo responsable de la estrategia de datos |
| **Data Owner** | Gerente de área responsable de negocio de un dominio de datos |
| **Data Steward** | Responsable operativo de calidad, documentación y acceso |
| **Catálogo de Datos** | Inventario centralizado y buscable de todos los activos de datos |
| **Diccionario de Datos** | Documentación técnica detallada de tablas y columnas |
| **Linaje del Dato** | Trazabilidad completa del origen, transformaciones y destino de un dato |
| **PII** | Datos que permiten identificar a una persona física (email, DNI, nombre) |
| **Enmascaramiento** | Ocultar parte del dato preservando el formato (ma***@dominio.com) |
| **Pseudonimización** | Reemplazar el dato real por un identificador reversible (hash) |

---

> 💡 **Para la próxima unidad:** Con los fundamentos de calidad y gobierno establecidos, en la **Unidad IV** construimos el destino final de todos nuestros pipelines: el **Data Warehouse**. Vamos a diseñar modelos dimensionales, entender el esquema estrella y aprender a manejar datos que cambian con el tiempo (SCD).
