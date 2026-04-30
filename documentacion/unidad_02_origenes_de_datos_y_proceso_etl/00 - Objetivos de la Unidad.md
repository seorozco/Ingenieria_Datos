# Unidad II — Orígenes de Datos y Proceso ETL
## Objetivos de la Unidad

> **Asignatura:** Ingeniería de Datos  
> **Docente:** Ing. Sergio Orozco  
> **Clases que componen esta unidad:** Clase 03, 04, 05 y 06

---

## ¿De qué trata esta unidad?

Esta unidad es el **núcleo técnico del primer módulo**. Aquí pasamos de los conceptos a la práctica: vamos a aprender a **extraer datos de distintas fuentes** (bases de datos, APIs, archivos, sitios web), a **transformarlos** para darles consistencia y calidad, y a **cargarlos** en el destino final de manera confiable y eficiente.

Es decir: vamos a construir el proceso **ETL** (Extract, Transform, Load) de principio a fin con Python y SQL.

> Si la Unidad I fue el mapa del territorio, la Unidad II es donde empezamos a caminar ese territorio con herramientas reales en la mano.

---

## Objetivos de Aprendizaje

Al finalizar esta unidad, el alumno será capaz de:

- ✅ Clasificar los distintos **tipos de bases de datos** (SQL, NoSQL, columnares, de grafos) y seleccionar la adecuada para cada caso de uso.
- ✅ Diferenciar los enfoques **OLTP y OLAP** y explicar cuándo aplicar cada uno.
- ✅ Implementar estrategias de extracción **Full Load** e **Incremental** usando Python.
- ✅ Consumir datos desde **APIs REST** y realizar **web scraping** ético con librerías Python.
- ✅ Extraer datos desde bases de datos relacionales con **psycopg2** y **SQLAlchemy**.
- ✅ Aplicar transformaciones de datos complejas con **pandas**: limpieza, normalización, joins, agregaciones y pivots.
- ✅ Comprender las diferencias entre **ETL** y **ELT** y elegir el paradigma adecuado según el contexto.
- ✅ Implementar las tres estrategias de carga (**Full Overwrite**, **Append**, **Upsert**) con Python y SQL.
- ✅ Describir el rol de **Apache Airflow** como orquestador de pipelines y entender la estructura de un DAG.

---

## Estructura de la Unidad

```
Unidad II
├── Clase 03 — Tipos de Bases de Datos
│   ├── ¿Por qué existen tantos tipos?
│   ├── Relacionales (SQL) — propiedades ACID
│   ├── NoSQL: Clave-Valor, Documentales, Columnares, Grafos
│   ├── OLTP vs. OLAP: el contraste fundamental
│   └── Data Warehouse, Data Lake, Data Lakehouse
│
├── Clase 04 — Extracción de Datos (Extract)
│   ├── Full Load vs. Incremental Extract
│   ├── Extracción desde PostgreSQL (psycopg2, SQLAlchemy)
│   ├── APIs REST con paginación y autenticación
│   └── Web Scraping con BeautifulSoup
│
├── Clase 05 — Transformación de Datos (Transform)
│   ├── Limpieza de datos con pandas
│   ├── Normalización y estandarización
│   ├── Joins, agregaciones y pivots
│   ├── ETL vs. ELT
│   └── Derivación de nuevas columnas
│
└── Clase 06 — Carga de Datos y Orquestación
    ├── Full Overwrite, Append y Upsert
    ├── Carga a PostgreSQL con SQLAlchemy
    ├── Carga a formatos Data Lake (CSV, Parquet)
    └── Apache Airflow y los DAGs
```

---

## Aspectos Relevantes de la Unidad

### 🔑 Conceptos Clave

| Concepto | Por qué importa |
|---|---|
| **OLTP vs. OLAP** | Determina si se usa una BD transaccional o analítica como destino |
| **Full Load vs. Incremental** | Impacta directamente en la performance y costos del pipeline |
| **Upsert** | La estrategia de carga más robusta y usada en producción |
| **ETL vs. ELT** | Define la arquitectura del pipeline: transforma antes o después de cargar |
| **Airflow DAG** | Cómo se orquestan y monitorean los pipelines en producción |

### ⚠️ Puntos que suelen generar confusión

1. **"Siempre uso Full Load para simplificar"** — En tablas grandes esto puede tardar horas. La extracción incremental es esencial para pipelines productivos.
2. **"Primero codifico, después pienso la estrategia de carga"** — Al revés. La estrategia de carga (Overwrite/Append/Upsert) debe definirse antes de escribir una sola línea.
3. **"pandas es suficiente para todo"** — Para volúmenes grandes (millones de filas), pandas en memoria no alcanza. Hay que escalar a Spark o usar SQL directamente en el DWH.
4. **"ETL y ELT hacen lo mismo"** — Tienen implicancias arquitectónicas muy distintas en cuanto a privacidad de datos, flexibilidad y costos.

### 📚 Relación con las unidades siguientes

- En la **Unidad III** vamos a profundizar en **calidad del dato**: qué pasa cuando los datos que extrajimos aquí son incorrectos, cómo detectarlo y cómo medirlo.
- En la **Unidad IV** vamos a ver el **destino final más importante** de los pipelines: el Data Warehouse y su modelo dimensional, donde los datos transformados aquí van a "aterrizar".

---

## Diagrama General del Proceso ETL

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PROCESO ETL COMPLETO                             │
│                                                                          │
│  ┌─────────────┐   EXTRACT   ┌──────────┐   TRANSFORM  ┌────────────┐  │
│  │   FUENTES   │────────────►│ STAGING  │─────────────►│   DATOS    │  │
│  │             │             │  (área   │              │  LIMPIOS   │  │
│  │ · PostgreSQL│             │  cruda)  │              │  Y LISTOS  │  │
│  │ · REST APIs │             │          │              │            │  │
│  │ · Archivos  │             │ CSV/JSON │              │ DataFrame  │  │
│  │ · Web       │             │ sin proc.│              │ pandas     │  │
│  └─────────────┘             └──────────┘              └─────┬──────┘  │
│                                                               │         │
│                                                          LOAD │         │
│                                                               ▼         │
│                                              ┌────────────────────────┐ │
│                                              │      DESTINO FINAL     │ │
│                                              │                        │ │
│                                              │  · Data Warehouse      │ │
│                                              │  · Data Lake (Parquet) │ │
│                                              │  · Base analítica      │ │
│                                              └────────────────────────┘ │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  ORQUESTACIÓN: Apache Airflow programa y monitorea todo el flujo│   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

> 💡 **Consejo para los alumnos:** En esta unidad van a escribir código real. La mejor forma de aprender es **ejecutar cada ejemplo**, romperlo intencionalmente y entender por qué falla. Los errores son los mejores maestros en Ingeniería de Datos.
