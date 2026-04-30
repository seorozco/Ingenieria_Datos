# Clase 01 — Fundamentos de la Inteligencia de Datos

> **Asignatura:** Ingeniería de Datos  
> **Docente:** Ing. Sergio Orozco  
> **Unidad:** I — Fundamentos e Inteligencia de Datos

---

## Objetivos de la Clase

Al finalizar esta clase, el alumno será capaz de:

- Definir qué es la **Inteligencia de Datos** y comprender su alcance dentro de las organizaciones modernas.
- Explicar los **5 niveles de análisis** y diferenciar cuándo aplicar cada uno.
- Comprender el rol de la **Ingeniería de Datos** y su relación con otros roles del ecosistema.
- Reconocer la **Pirámide DIKW** como modelo conceptual que transforma datos crudos en sabiduría.
- Describir la **evolución histórica** del ecosistema de datos.
- Identificar los **4 roles principales** del mundo de los datos y sus responsabilidades.
- Explicar el **ciclo de vida del dato** de extremo a extremo.

---

## 1. ¿Qué es la Inteligencia de Datos?

La **Inteligencia de Datos** (o *Data Intelligence*) es la capacidad de una organización para **recolectar, procesar, analizar y utilizar sus datos** con el fin de tomar decisiones más informadas, eficientes y estratégicas.

No se trata simplemente de acumular datos en servidores. Se trata de convertirlos en un **activo organizacional** que genere valor concreto: reducir costos, detectar oportunidades, anticipar riesgos o mejorar la experiencia del cliente.

> **Analogía:** Tener millones de libros en una biblioteca no te hace más sabio si no sabes leer, buscar o interpretar lo que dicen. Los datos son como esos libros: su valor depende de la capacidad de **extraer significado** de ellos y actuar en consecuencia.

---

## 2. Los 5 Niveles de Análisis

La inteligencia de datos se organiza en **cinco niveles progresivos**, que van desde la descripción simple de hechos hasta la ejecución automatizada de decisiones. Cada nivel agrega más valor que el anterior, pero también exige más complejidad técnica y madurez organizacional.

```
┌─────────────────────────────────────────────────────────────────┐
│                   NIVELES DE ANÁLISIS                           │
├──────────┬─────────────────┬─────────────────────────────────── │
│  Nivel   │  Nombre         │  Pregunta que responde             │
├──────────┼─────────────────┼─────────────────────────────────── │
│    5     │  DECISIVO       │  ¿Cómo ejecutamos la mejor opción? │
│    4     │  PRESCRIPTIVO   │  ¿Qué deberíamos hacer?            │
│    3     │  PREDICTIVO     │  ¿Qué es probable que pase?        │
│    2     │  DIAGNÓSTICO    │  ¿Por qué está pasando?            │
│    1     │  DESCRIPTIVO    │  ¿Qué está pasando?                │
└──────────┴─────────────────┴─────────────────────────────────── │
```

### Nivel 1 — Descriptivo: ¿Qué está pasando?

Es el nivel más básico y el más extendido. Describe el **estado actual o pasado** del negocio usando métricas y reportes.

- **Herramientas típicas:** SQL, Excel, Power BI, Tableau.
- **Producto:** dashboards, reportes, tablas de métricas.
- **Ejemplo:** *"Las ventas de marzo fueron $2.3M, un 8% menos que febrero."*

### Nivel 2 — Diagnóstico: ¿Por qué está pasando?

Va un paso más allá y busca **las causas** detrás de los números. Requiere cruzar datos de distintas fuentes y hacer análisis más profundos.

- **Herramientas típicas:** SQL avanzado, Python, análisis estadístico.
- **Producto:** análisis de causa-raíz, drill-down en reportes.
- **Ejemplo:** *"La caída se debe a quiebres de stock en la categoría electrónica durante la última semana del mes."*

### Nivel 3 — Predictivo: ¿Qué es probable que pase?

Usa datos históricos para **anticipar el futuro**. Requiere modelos estadísticos o de machine learning.

- **Herramientas típicas:** Python (scikit-learn, statsmodels), R, plataformas de ML.
- **Producto:** modelos de predicción, forecasts, scoring de propensión.
- **Ejemplo:** *"Si no se repone stock en los próximos 5 días, se perderán $400K en ventas en abril."*

### Nivel 4 — Prescriptivo: ¿Qué deberíamos hacer?

No solo predice el futuro sino que **recomienda la mejor acción** a tomar. Combina predicciones con restricciones de negocio (costos, capacidad, plazos).

- **Herramientas típicas:** optimización matemática, simulación, sistemas de reglas.
- **Producto:** recomendaciones automatizadas, optimizadores de rutas/precios/inventario.
- **Ejemplo:** *"Hacer un pedido urgente de 500 unidades al proveedor B esta semana para minimizar pérdidas."*

### Nivel 5 — Decisivo: ¿Cómo ejecutamos la mejor opción?

El sistema no solo recomienda: **actúa de forma autónoma**. La decisión se ejecuta sin intervención humana, en tiempo real.

- **Herramientas típicas:** sistemas de reglas, IA, integración con APIs de acción.
- **Producto:** automatizaciones, bots decisores, sistemas de respuesta en tiempo real.
- **Ejemplo:** *"El sistema detecta la necesidad de reposición y activa automáticamente la orden de compra al proveedor B."*

> **Dónde está la industria hoy:** La mayoría de las organizaciones argentinas y de LATAM operan entre el Nivel 1 y el Nivel 2. El Nivel 3 está creciendo aceleradamente con IA. Los Niveles 4 y 5 son todavía el territorio de las empresas tecnológicamente más maduras.

---

## 3. ¿Qué es la Ingeniería de Datos?

La **Ingeniería de Datos** es la disciplina que se ocupa de **construir y mantener la infraestructura** que permite que los datos fluyan desde sus fuentes de origen hasta los sistemas donde serán analizados o utilizados.

Un **Data Engineer** es el profesional que:
- Diseña y construye **pipelines de datos** (los "caños" por donde fluyen los datos).
- Extrae datos de distintas fuentes (bases de datos, APIs, archivos, sensores).
- Los transforma para darles consistencia, calidad y el formato adecuado.
- Los carga en los destinos apropiados (Data Warehouses, Data Lakes).
- Garantiza que todo ese proceso sea **confiable, escalable y automatizado**.

### El proceso ETL: el corazón de la Ingeniería de Datos

**ETL** son las siglas de **Extract** (Extraer), **Transform** (Transformar) y **Load** (Cargar). Es el proceso fundamental que todo Data Engineer debe dominar.

```
┌──────────────┐    ┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ FUENTES DE   │    │  EXTRACCIÓN  │    │  TRANSFORMACIÓN  │    │     DESTINO      │
│    DATOS     │───►│   (Extract)  │───►│    (Transform)   │───►│     (Load)       │
│              │    │              │    │                  │    │                  │
│  ERP / CRM   │    │  Python      │    │  Limpieza        │    │  Data Warehouse  │
│  APIs REST   │    │  Airbyte     │    │  Normalización   │    │  Data Lake       │
│  Archivos    │    │  psycopg2    │    │  Enriquecimiento │    │  Base analítica  │
│  IoT         │    │              │    │  Pandas / dbt    │    │                  │
└──────────────┘    └──────────────┘    └──────────────────┘    └──────────────────┘
```

### Stack tecnológico del Data Engineer

Las herramientas más usadas en el ecosistema actual:

| Herramienta | Para qué sirve |
|---|---|
| **Python** | Lenguaje principal: scripting, procesamiento, automatización |
| **SQL** | Consultar y transformar datos en bases relacionales |
| **Apache Spark** | Procesamiento distribuido de grandes volúmenes |
| **Apache Airflow** | Orquestación y scheduling de pipelines |
| **dbt** | Transformaciones SQL versionadas y testeadas |
| **AWS / GCP / Azure** | Plataformas cloud con servicios gestionados |

> **Concepto clave:** Sin Data Engineers que construyan los pipelines, los analistas y científicos de datos **no tienen datos confiables** con qué trabajar. El Data Engineer es quien habilita todo el ecosistema analítico de una organización. Es la base de la pirámide.

---

## 4. La Pirámide DIKW

La **Pirámide DIKW** es uno de los modelos conceptuales más importantes en el mundo de los datos. Explica cómo los **datos brutos** se transforman progresivamente en **sabiduría aplicable**.

Sus siglas corresponden a:  
**D**ata → **I**nformation → **K**nowledge → **W**isdom  
(Dato → Información → Conocimiento → Sabiduría)

```
                    ╔══════════════════╗
                    ║    SABIDURÍA     ║  ← ¿Cuándo y cómo actuar?
                   ╔╩══════════════════╩╗
                   ║   CONOCIMIENTO    ║  ← ¿Qué significa esto para nosotros?
                  ╔╩════════════════════╩╗
                  ║    INFORMACIÓN     ║  ← ¿Qué nos dice este dato en contexto?
                 ╔╩══════════════════════╩╗
                 ║        DATOS          ║  ← Hechos crudos sin interpretar
                 ╚════════════════════════╝
                    (más abundante, menos valioso)
```

### Descripción de cada nivel

#### 📊 Dato — El hecho crudo
El dato es el hecho puro, sin contexto ni interpretación. Por sí solo no dice nada, no genera acción.

- Ejemplos: `200`, `lunes`, `click`, `37.5°C`, `$1250`
- Son la materia prima. Baratos de generar, pero sin valor por sí solos.

#### ℹ️ Información — El dato en contexto
La información es el **dato procesado y puesto en contexto**. Ya tiene un significado interpretable por un humano.

- Ejemplo: *"El lunes hubo 200 clicks en el botón de compra entre las 18 y 20 hs."*
- El dato `200` y `lunes` ahora tienen un marco que los hace comprensibles.

#### 🧠 Conocimiento — Los patrones identificados
El conocimiento es la **información analizada** y relacionada con otras informaciones, que permite identificar patrones y relaciones.

- Ejemplo: *"Los lunes a la tarde la demanda de compra se dispara. Este patrón se repite hace 3 meses."*
- Ahora ya no es un hecho aislado: es un patrón recurrente que podemos usar para predecir.

#### 💡 Sabiduría — La decisión aplicada
La sabiduría es el **conocimiento aplicado a tomar una decisión concreta** con impacto real en el mundo.

- Ejemplo: *"Aumentar el stock disponible y activar una campaña de descuentos los lunes después del mediodía."*
- Es el nivel más escaso y más valioso. Es el objetivo final de todo el ecosistema de datos.

### Ejemplo integrador completo

| Nivel | Contenido |
|---|---|
| **Dato** | `200`, `lunes`, `18hs`, `click` |
| **Información** | "El lunes a las 18hs se registraron 200 clicks en 'Comprar'" |
| **Conocimiento** | "Hay un pico de intención de compra los lunes al atardecer, con el doble de conversión respecto a otros horarios" |
| **Sabiduría** | "Programar stock de reposición para los lunes a las 16hs y activar ofertas en ese horario" |

---

## 5. Historia y Evolución del Ecosistema de Datos

El modo en que las organizaciones gestionan sus datos ha cambiado radicalmente en los últimos 40 años. Entender esta evolución ayuda a comprender por qué las herramientas actuales existen y qué problema vinieron a resolver.

```
1980s──────────1990s──────────2005──────────2015──────────2020──────────HOY
  │                │              │              │              │
  ▼                ▼              ▼              ▼              ▼
Reportes      Data Warehouse   Big Data      Cloud DWH     Data Mesh /
del ERP       On-Premise       + Hadoop      Snowflake     Lakehouse
(Excel)       (Teradata)       (Spark)       BigQuery      Delta Lake
```

### Etapa 1 — Reportes del ERP (1970s–1990s)
Los primeros sistemas digitales eran puramente transaccionales. Los reportes eran módulos adicionales del propio ERP que corrían directamente contra la base de datos operativa. Eran lentos, bloqueaban el sistema productivo y no permitían análisis complejos. Los analistas exportaban todo a Excel para cualquier trabajo más sofisticado.

### Etapa 2 — Data Warehouse On-Premise (1990s–2005)
**Bill Inmon** (1992) y **Ralph Kimball** (1996) formalizaron el concepto de Data Warehouse: un sistema separado, diseñado exclusivamente para el análisis, al que se le mueven los datos de los sistemas operativos. Plataformas como **Teradata**, **Oracle DWH** e **IBM DB2** dominaron esta era. Eran potentes pero extremadamente caros (proyectos de millones de dólares) y rígidos.

### Etapa 3 — Big Data (2005–2015)
La explosión de internet y las redes sociales generó volúmenes de datos que los DWH tradicionales no podían manejar. Google publicó papers fundamentales que inspiraron **Apache Hadoop** (2006) y luego **Apache Spark** (2014). Surgió el concepto de **Data Lake**: almacenar todos los datos en formato crudo sin esquema previo, procesarlos más tarde según la necesidad.

### Etapa 4 — Cloud Data Warehouse (2015–presente)
Las plataformas cloud democratizaron el acceso a infraestructura de gran escala. Surgieron **Snowflake** (separación de cómputo y almacenamiento), **Google BigQuery** (serverless, pago por bytes) y **Amazon Redshift**. Hoy cualquier empresa puede tener un DWH de nivel enterprise sin inversión de capital.

### Etapa 5 — Data Mesh y Lakehouse (2020–presente)
El **Data Mesh** propone descentralizar la responsabilidad de los datos: cada dominio de negocio (ventas, marketing, logística) es dueño de sus datos y los expone como "productos" al resto de la organización. El **Lakehouse** (Delta Lake, Apache Iceberg) combina la flexibilidad del Data Lake con las garantías ACID del Data Warehouse.

---

## 6. Los 4 Roles del Ecosistema de Datos

En una organización moderna de datos, distintos perfiles profesionales colaboran con responsabilidades claramente diferenciadas. Conocerlos te ayudará a entender dónde te posicionás vos como futuro Data Engineer.

```
┌──────────────────────────────────────────────────────────────────────┐
│                    ECOSISTEMA DE ROLES                               │
│                                                                      │
│  DATA ARCHITECT ────── Define la estrategia y arquitectura global   │
│       │                                                              │
│       ▼                                                              │
│  DATA ENGINEER ─────── Construye pipelines, infraestructura, ETL   │
│       │                                                              │
│       ├──────────────────────────────────────────────┐              │
│       ▼                                              ▼              │
│  DATA ANALYST ──────── Reportes y dashboards    DATA SCIENTIST ──── │
│  (responde qué pasó)   para el negocio          (modelos predictivos)│
└──────────────────────────────────────────────────────────────────────┘
```

### 🔨 Data Engineer — El Constructor
**Es el protagonista de esta carrera.**

Diseña y construye la **infraestructura de datos**: pipelines ETL/ELT, integraciones entre sistemas, orquestación de procesos. Trabaja con Python, SQL, Spark, Airflow, Kafka y plataformas cloud.

- **Su producto:** pipelines confiables, escalables y automatizados.
- **Pregunta que responde:** *"¿Cómo hago que los datos lleguen, limpios y a tiempo, a donde los necesitan?"*
- **Analogía:** El que construye la cocina, instala los hornos y trae los ingredientes frescos cada mañana.

### 📊 Data Analyst — El Intérprete
Se enfoca en **responder preguntas de negocio** a partir de datos ya procesados. Trabaja principalmente con SQL, herramientas de visualización (Power BI, Tableau, Looker) y Excel avanzado.

- **Su producto:** reportes, dashboards, análisis ad-hoc.
- **Pregunta que responde:** *"¿Qué pasó? ¿Por qué?"*
- **Analogía:** El chef que cocina con los ingredientes que el Data Engineer preparó.

### 🔬 Data Scientist — El Investigador
Aplica **modelos estadísticos y de machine learning** para descubrir patrones complejos y hacer predicciones. Trabaja con Python (scikit-learn, TensorFlow), R y SQL.

- **Su producto:** modelos predictivos, análisis exploratorio profundo.
- **Pregunta que responde:** *"¿Qué va a pasar? ¿Por qué ocurre esto?"*
- **Analogía:** El investigador nutricional que experimenta con nuevas combinaciones de ingredientes.

### 🏛️ Data Architect — El Diseñador
Define la **estrategia y arquitectura global** del ecosistema de datos: qué tecnologías usar, cómo organizar el almacenamiento, qué estándares aplicar. No opera sistemas directamente, toma decisiones de alto nivel.

- **Su producto:** planos de arquitectura, estándares tecnológicos, roadmaps.
- **Pregunta que responde:** *"¿Cómo debe estar diseñado todo el sistema para que funcione en 5 años?"*
- **Analogía:** El arquitecto que diseña el plano del edificio antes de que alguien ponga el primer ladrillo.

---

## 7. El Ciclo de Vida del Dato

El dato no nace en una base de datos analítica: tiene un **ciclo de vida completo** desde que se genera hasta que se archiva o elimina. Como Data Engineers, debemos tener visibilidad de todo el ciclo porque nuestros pipelines lo atraviesan de punta a punta.

```
┌──────────────────────────────────────────────────────────────────────┐
│                   CICLO DE VIDA DEL DATO                            │
│                                                                      │
│  1. CAPTURA ────► El dato nace: sensor IoT, formulario web, ERP     │
│       │                                                              │
│  2. INGESTA ────► Llega al sistema de datos: staging area, raw zone │
│       │                                                              │
│  3. PROCESAMIENTO ► Se limpia, valida y transforma                  │
│       │                                                              │
│  4. ALMACENAMIENTO ► Se guarda en el sistema apropiado (DWH, Lake)  │
│       │                                                              │
│  5. ANÁLISIS ───► Se consulta para responder preguntas de negocio   │
│       │                                                              │
│  6. VISUALIZACIÓN ► Se presenta en dashboards y reportes            │
│       │                                                              │
│  7. ACTIVACIÓN ─► El insight genera una acción: campaña, alerta     │
│       │                                                              │
│  8. ARCHIVO ────► El dato vencido se archiva o elimina              │
└──────────────────────────────────────────────────────────────────────┘
```

### Responsabilidades del Data Engineer en el ciclo

| Etapa | Responsabilidad del DE |
|---|---|
| Captura | Definir conectores y adaptadores para cada fuente |
| Ingesta | Diseñar el área de staging, decidir formato y frecuencia |
| Procesamiento | Construir las transformaciones (ETL/ELT) |
| Almacenamiento | Diseñar el esquema destino, particionado, compresión |
| Análisis | Garantizar que los datos estén disponibles con la calidad necesaria |
| Archivo | Implementar políticas de retención y eliminación |

---

## Resumen de la Clase

| Concepto | Definición en una frase |
|---|---|
| **Inteligencia de Datos** | Capacidad de convertir datos en decisiones que generan valor |
| **5 niveles de análisis** | De descriptivo (qué pasó) a decisivo (acción automática) |
| **Ingeniería de Datos** | Disciplina que construye la infraestructura para que los datos fluyan |
| **ETL** | Extract-Transform-Load: el proceso central del Data Engineer |
| **Pirámide DIKW** | Los datos se transforman en información, conocimiento y sabiduría |
| **Evolución del ecosistema** | De los DWH on-premise a la nube, de centralizado al Data Mesh |
| **4 roles** | Architect, Engineer, Analyst, Scientist — cada uno con su función específica |
| **Ciclo de vida del dato** | De la captura al archivo, el DE gestiona todo el recorrido |

---

> 💡 **Para la próxima clase:** En la Clase 02 vamos a profundizar en los tipos de datos (estructurados, semi-estructurados, no estructurados) y las fuentes desde donde se originan. Es el paso natural después de entender *para qué* los necesitamos.
