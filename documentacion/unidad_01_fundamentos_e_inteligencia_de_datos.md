# Unidad I — Fundamentos e Inteligencia de Datos

> **Asignatura:** Ingeniería de Datos  
> **Docente:** Ing. Sergio Orozco  
> **Clases:** 1 y 2

---

## Objetivos de la Unidad

Al finalizar esta unidad, el alumno será capaz de:

- Definir qué es la **Inteligencia de Datos** y comprender su alcance dentro de las organizaciones modernas.
- Explicar los **5 tipos de análisis** (descriptivo, diagnóstico, predictivo, prescriptivo y decisivo) y diferenciar cuándo aplicar cada uno.
- Comprender el rol de la **Ingeniería de Datos** y por qué es la base sobre la que se apoyan analistas y científicos de datos.
- Reconocer la **Pirámide DIKW** como modelo conceptual que transforma datos crudos en sabiduría aplicada.
- Describir la **evolución histórica** del ecosistema de datos: desde los primeros Data Warehouses hasta el Data Mesh.
- Identificar los **roles** del ecosistema de datos y las responsabilidades de cada uno.
- Explicar el **ciclo de vida del dato** desde su captura hasta su archivo.
- Clasificar los datos según su **estructura** (estructurados, semi-estructurados y no estructurados).
- Identificar las principales **fuentes de datos** internas y externas en una organización.
- Comprender las diferencias entre **procesamiento batch y streaming**, y las **4V del Big Data**.

---

## Clase 01 — Fundamentos de la Inteligencia de Datos

### 1.1 ¿Qué es la Inteligencia de Datos?

La **Inteligencia de Datos** (o *Data Intelligence*) es la capacidad de una organización para recolectar, procesar, analizar y utilizar sus datos con el fin de tomar decisiones más informadas, eficientes y estratégicas.

No se trata simplemente de acumular datos, sino de convertirlos en un **activo organizacional** que genere valor concreto: reducir costos, detectar oportunidades, anticipar riesgos o mejorar la experiencia del cliente.

> **Analogía:** Tener millones de libros en una biblioteca no te hace más sabio si no sabes leer, buscar o interpretar lo que dicen. Los datos son como esos libros: su valor depende de la capacidad de extraer significado de ellos.

#### Los 5 Pilares de la Inteligencia de Datos

La inteligencia de datos se organiza en cinco niveles de análisis, que van desde la descripción simple de hechos hasta la ejecución de decisiones automatizadas:

| Nivel | Nombre | Pregunta que responde | Ejemplo |
|---|---|---|---|
| 1 | **Descriptivo** | ¿Qué está pasando? | "Las ventas de marzo fueron $2.3M, un 8% menos que febrero." |
| 2 | **Diagnóstico** | ¿Por qué está pasando? | "La caída se debe a quiebres de stock en la categoría electrónica." |
| 3 | **Predictivo** | ¿Qué es probable que pase? | "Si no se repone stock, se perderán $400K en abril." |
| 4 | **Prescriptivo** | ¿Qué deberíamos hacer? | "Hacer un pedido urgente de 500 unidades al proveedor B esta semana." |
| 5 | **Decisivo** | ¿Cómo ejecutamos la mejor opción? | "El sistema activa automáticamente la orden de compra al proveedor B." |

Cada nivel es más valioso que el anterior, pero también más complejo de implementar. La mayoría de las organizaciones hoy operan entre el nivel descriptivo y diagnóstico. El prescriptivo y decisivo requieren infraestructura de datos madura y equipos capacitados.

---

### 1.2 ¿Qué es la Ingeniería de Datos?

La **Ingeniería de Datos** es la disciplina que se ocupa de construir y mantener la infraestructura que permite que los datos fluyan desde sus fuentes de origen hasta los sistemas donde serán analizados o utilizados.

Un **Data Engineer** es el profesional que diseña, construye y opera los *pipelines* de datos: los procesos automatizados que extraen datos de distintas fuentes, los transforman para darles consistencia y calidad, y los cargan en los destinos apropiados (bases de datos analíticas, Data Warehouses, Data Lakes).

#### El proceso ETL

El corazón de la ingeniería de datos es el proceso **ETL** (Extract, Transform, Load):

```
[Fuente de datos]  →  [Extracción]  →  [Transformación]  →  [Carga]  →  [Destino analítico]
     ERP, API            Extract           Transform            Load        Data Warehouse
     IoT, CSV            Python            Pandas / dbt         SQL          / Data Lake
     Base de datos       Airbyte           Limpieza             Airflow
```

#### Stack tecnológico de la Ingeniería de Datos

Las herramientas más utilizadas en el ecosistema actual son:

- **Python:** lenguaje principal para scripting, procesamiento y automatización.
- **SQL:** lenguaje universal para consultar y transformar datos en bases relacionales.
- **Apache Spark:** procesamiento distribuido de grandes volúmenes de datos.
- **Apache Airflow:** orquestación y scheduling de pipelines.
- **dbt (data build tool):** transformaciones SQL versionadas y testeadas.
- **Plataformas Cloud:** AWS, Google Cloud, Azure — ofrecen servicios gestionados de almacenamiento, cómputo y orquestación.

> **Concepto clave:** Sin Data Engineers que construyan los pipelines, los analistas y científicos de datos no tienen datos confiables con qué trabajar. El Data Engineer es quien habilita todo el ecosistema analítico de una organización.

---

### 1.3 La Pirámide DIKW

La **Pirámide DIKW** es un modelo conceptual que explica cómo los datos brutos se transforman progresivamente en sabiduría aplicable. Sus siglas corresponden a: **D**ata (Dato), **I**nformation (Información), **K**nowledge (Conocimiento), **W**isdom (Sabiduría).

```
            ╔══════════╗
            ║ SABIDURÍA║   → ¿Cuándo y cómo actuar?
           ╔╩══════════╩╗
           ║CONOCIMIENTO║  → ¿Qué significa esto para nosotros?
          ╔╩════════════╩╗
          ║ INFORMACIÓN  ║  → ¿Qué nos dice este dato en contexto?
         ╔╩══════════════╩╗
         ║     DATOS      ║  → Hechos crudos sin interpretar
         ╚════════════════╝
```

#### Descripción de cada nivel

**Dato:** Es el hecho crudo, sin contexto ni interpretación. Por sí solo no dice nada.
- Ejemplo: `"200"`, `"lunes"`, `"click"`.

**Información:** Es el dato procesado y puesto en contexto. Ya tiene un significado interpretable.
- Ejemplo: "El lunes hubo 200 clicks en el botón de compra entre las 18 y 20 hs."

**Conocimiento:** Es la información analizada y relacionada con otras informaciones. Permite identificar patrones.
- Ejemplo: "Los lunes a la tarde la demanda de compra se dispara. Esto ocurre consistentemente hace 3 meses."

**Sabiduría:** Es el conocimiento aplicado a tomar una decisión concreta con impacto real.
- Ejemplo: "Aumentar el stock disponible y activar una campaña de descuentos los lunes después del mediodía."

> **Ejemplo integrador:** Una tienda registra "200 clicks en comprar" (dato). Procesado: "Alta demanda vespertina los lunes" (información). Analizado: "Patrón de comportamiento de compra semanal" (conocimiento). Aplicado: "Aumentar stock los lunes" (sabiduría).

---

### 1.4 Historia y Evolución del Ecosistema de Datos

El modo en que las organizaciones almacenan, procesan y analizan sus datos ha cambiado radicalmente en los últimos 40 años:

#### Etapa 1 — Data Warehouse On-Premise (1980s–2000s)
Las primeras soluciones analíticas centralizadas fueron los **Data Warehouses** instalados en servidores físicos propios de la empresa. Herramientas como Teradata o Oracle Data Warehouse permitían consolidar datos de distintos sistemas internos para generar reportes. El problema: eran costosos, rígidos y difíciles de escalar.

#### Etapa 2 — Big Data (2005–2015)
Con la explosión de internet y las redes sociales, los volúmenes de datos crecieron exponencialmente. Las soluciones tradicionales no podían manejar terabytes o petabytes de datos. Surgieron tecnologías distribuidas como **Apache Hadoop** (procesamiento en clusters de servidores baratos) y luego **Apache Spark** (más veloz, en memoria). Nació el concepto de **Data Lake**: almacenar datos en su formato crudo sin esquema previo.

#### Etapa 3 — Cloud Data Warehouse (2015–2020)
Las plataformas cloud (AWS, GCP, Azure) democratizaron el acceso a infraestructura de gran escala sin inversión inicial. Surgieron **Data Warehouses cloud** como **Snowflake**, **Google BigQuery** y **Amazon Redshift**: elásticos, serverless (sin gestión de servidores) y con pago por uso. Las organizaciones empezaron a migrar sus workloads analíticos a la nube.

#### Etapa 4 — Data Mesh (2020–presente)
El enfoque centralizado generaba cuellos de botella: un único equipo de datos no puede servir a toda la organización. El **Data Mesh** propone descentralizar: cada dominio de negocio (ventas, marketing, logística) es responsable de sus propios datos y los expone como "productos de datos" al resto de la organización. Es un cambio cultural y arquitectónico que está adoptando la industria progresivamente.

---

### 1.5 Roles del Ecosistema de Datos

En una organización moderna de datos, distintos perfiles profesionales colaboran con responsabilidades diferenciadas:

#### Data Analyst — El Intérprete
Se enfoca en **responder preguntas de negocio** a partir de datos ya procesados. Trabaja principalmente con SQL, herramientas de visualización (Power BI, Tableau, Looker) y Excel avanzado. Su producto principal son reportes, dashboards y análisis ad-hoc.

> **Analogía:** El chef que cocina con los ingredientes que otros prepararon.

#### Data Engineer — El Constructor
Diseña y construye la **infraestructura de datos**: pipelines ETL/ELT, integraciones entre sistemas, orquestación de procesos. Trabaja con Python, SQL, Spark, Airflow, Kafka y plataformas cloud. Su producto son pipelines confiables, escalables y automatizados.

> **Analogía:** El que construye la cocina, instala los hornos y trae los ingredientes frescos.

#### Data Scientist — El Investigador
Aplica **modelos estadísticos y de machine learning** para descubrir patrones complejos y hacer predicciones. Trabaja con Python (scikit-learn, TensorFlow, PyTorch), R y SQL. Su producto son modelos predictivos y análisis exploratorio profundo.

> **Analogía:** El investigador nutricional que experimenta con nuevas combinaciones de ingredientes.

#### Data Architect — El Diseñador
Define la **estrategia y arquitectura global** del ecosistema de datos: qué tecnologías usar, cómo organizar el almacenamiento, qué estándares de calidad y seguridad aplicar. No opera sistemas directamente, pero toma las decisiones de diseño de alto nivel.

> **Analogía:** El arquitecto que diseña el plano del edificio antes de construirlo.

---

### 1.6 Ciclo de Vida del Dato

El dato no nace en una base de datos analítica: tiene un ciclo de vida completo desde que se genera hasta que se archiva o elimina. Comprender este ciclo es fundamental para diseñar sistemas de datos robustos.

```
1. Captura       →  El dato se origina: sensor IoT, formulario web, transacción ERP.
2. Procesamiento →  Se limpia, valida y transforma para darle consistencia.
3. Almacenamiento→  Se guarda en el sistema apropiado (BD relacional, Data Lake, DWH).
4. Análisis      →  Se consulta para responder preguntas de negocio.
5. Modelado      →  Se construyen modelos predictivos o dimensionales sobre él.
6. Visualización →  Se presenta en dashboards, reportes o alertas.
7. Activación    →  El insight obtenido acciona un proceso (campaña, alerta, decisión).
8. Archivo       →  El dato que ya no es operativo se archiva o elimina según política.
```

Cada etapa requiere decisiones técnicas específicas: qué herramientas usar, qué formato adoptar, cuánto tiempo retener el dato, quién tiene acceso.

---

## Clase 02 — Tipos de Datos y Fuentes de Origen

### 2.1 Clasificación de los Datos según su Estructura

Uno de los primeros criterios para trabajar con datos es entender su estructura, ya que esto determina qué herramientas y técnicas son aplicables para procesarlos.

#### Datos Estructurados

Son datos organizados en un **formato tabular fijo**: filas y columnas con tipos de dato predefinidos. Son los más fáciles de procesar y consultar con SQL.

**Características:**
- Esquema predefinido y rígido (cada columna tiene un tipo de dato: número, texto, fecha).
- Alta consistencia y fácil consulta con SQL.
- Baja tolerancia a la variabilidad: agregar una columna requiere cambiar el esquema.

**Ejemplos:**
- Tablas en bases de datos relacionales (PostgreSQL, MySQL, SQL Server).
- Archivos CSV o Excel exportados de un ERP.
- Registros de transacciones bancarias.

```
id_venta | fecha       | cliente_id | monto   | moneda
---------|-------------|------------|---------|-------
1001     | 2025-03-10  | C-4521     | 1250.00 | ARS
1002     | 2025-03-10  | C-3310     | 890.50  | USD
```

#### Datos Semi-estructurados

Son datos que **tienen alguna organización interna** (jerarquía, etiquetas, claves) pero no siguen un esquema tabular rígido. Su estructura puede variar entre registros.

**Características:**
- Formato auto-descriptivo: el dato lleva consigo su propia estructura.
- Flexible: distintos registros pueden tener distintos campos.
- Requiere parsing (interpretación del formato) para procesarlos.

**Ejemplos:**
- **JSON** (JavaScript Object Notation): usado en APIs REST, configuraciones y microservicios.
- **XML** (eXtensible Markup Language): usado en integraciones legacy y EDI.
- **YAML**: usado en configuraciones de herramientas (Airflow, Docker, Kubernetes).

```json
{
  "id_pedido": "P-9921",
  "cliente": {
    "nombre": "María González",
    "email": "maria@ejemplo.com"
  },
  "items": [
    { "producto": "Laptop", "cantidad": 1, "precio": 85000 },
    { "producto": "Mouse",  "cantidad": 2, "precio": 3500  }
  ],
  "total": 92000,
  "moneda": "ARS"
}
```

> Nótese que el campo `items` contiene una lista de longitud variable. Esto sería imposible de representar directamente en una sola fila de una tabla.

#### Datos No Estructurados

Son datos que **no tienen un formato ni esquema definido**. Constituyen la mayor parte de los datos generados en el mundo (~80-90%) y son los más difíciles de procesar con técnicas tradicionales.

**Características:**
- Sin esquema fijo: cada registro puede tener forma completamente distinta.
- Requieren técnicas especializadas: NLP, visión por computadora, análisis de audio.
- Gran riqueza de información, pero alta complejidad de extracción.

**Ejemplos:**
- Texto libre: emails, comentarios en redes sociales, reseñas, chats de soporte.
- Imágenes y videos: fotos de productos, grabaciones de cámaras de seguridad.
- Audio: llamadas grabadas de call centers, podcasts.
- Documentos: PDFs, contratos escaneados, informes en Word.

> **Ejemplo comparativo:**
> - Un email es **no estructurado** (texto libre sin campos fijos).
> - Una factura en SAP es **estructurada** (campos predefinidos: número, fecha, proveedor, monto).
> - La respuesta de una API de clima es **JSON semi-estructurado**.
> - Cada tipo requiere herramientas distintas para ser procesado.

---

### 2.2 Fuentes de Datos: Internas vs. Externas

Las organizaciones consumen datos que provienen de dos grandes categorías de fuentes:

#### Fuentes Internas

Son los sistemas y procesos propios de la organización que generan datos como subproducto de sus operaciones cotidianas.

| Sistema | Descripción | Tipo de datos |
|---|---|---|
| **ERP** (SAP, Oracle) | Planificación de recursos empresariales: compras, inventario, finanzas, RR.HH. | Estructurado |
| **CRM** (Salesforce, HubSpot) | Gestión de clientes y pipeline comercial: contactos, oportunidades, interacciones. | Estructurado |
| **Plataformas e-commerce** | Pedidos, carritos abandonados, historial de navegación. | Estructurado / Semi-estructurado |
| **Logs de aplicaciones** | Registros de eventos de sistemas: errores, accesos, tiempos de respuesta. | Semi-estructurado / No estructurado |
| **Bases de datos operativas** | Cualquier BBDD que soporte las operaciones del negocio. | Estructurado |

#### Fuentes Externas

Son datos que provienen de fuera de la organización, generalmente obtenidos a través de APIs, compras de datos o scraping.

| Fuente | Descripción | Ejemplo de uso |
|---|---|---|
| **APIs públicas** | Servicios que exponen datos de acceso libre o por suscripción. | Clima, tipo de cambio, datos del gobierno, geolocalización. |
| **Redes sociales** | Comentarios, menciones, métricas de engagement. | Análisis de sentimiento de marca. |
| **Sensores IoT** | Dispositivos físicos que reportan lecturas en tiempo real. | Temperatura de almacén, nivel de tanque, velocidad de flota. |
| **Proveedores de datos** | Empresas que venden datasets especializados. | Datos demográficos, scores crediticios, comportamiento de mercado. |
| **Web scraping** | Extracción automatizada de información pública de sitios web. | Precios de competidores, disponibilidad de vuelos. |

---

### 2.3 APIs REST y GraphQL como Fuentes de Datos

Las APIs (*Application Programming Interfaces*) son una de las fuentes de datos más importantes en la ingeniería de datos moderna. Permiten a los sistemas comunicarse entre sí de manera estandarizada.

#### API REST

Es el estilo de API más extendido. Funciona sobre HTTP y organiza los datos en **recursos** accesibles mediante URLs. Cada endpoint devuelve tipicamente un JSON.

```python
import requests

# Extrayendo datos del clima desde una API pública
response = requests.get(
    "https://api.openweathermap.org/data/2.5/weather",
    params={"q": "Buenos Aires", "appid": "TU_API_KEY", "lang": "es"}
)

data = response.json()
print(f"Temperatura: {data['main']['temp']} K")
print(f"Condición:   {data['weather'][0]['description']}")
```

**Características clave de las APIs REST:**
- **Autenticación:** las APIs generalmente requieren una API Key o token OAuth para autenticar las solicitudes.
- **Rate limiting:** limitan la cantidad de llamadas por minuto/hora para evitar abuso.
- **Paginación:** cuando hay muchos resultados, se devuelven en páginas.

#### API GraphQL

Es una alternativa más flexible a REST. En lugar de tener múltiples endpoints, tiene **un único endpoint** donde el cliente especifica exactamente qué datos necesita. Esto evita el problema del *over-fetching* (recibir más datos de los necesarios) y *under-fetching* (tener que hacer múltiples llamadas).

---

### 2.4 Archivos Planos y Logs

Además de las APIs y bases de datos, muchas fuentes de datos son simplemente **archivos**:

- **CSV (Comma-Separated Values):** el formato más universal para intercambio de datos tabulares. Simple pero frágil si hay comas o saltos de línea en los valores.
- **Excel (.xlsx):** muy común en entornos corporativos. Problemático para pipelines automatizados por su complejidad y dependencias.
- **Parquet:** formato columnar binario, altamente eficiente para grandes volúmenes de datos analíticos. El estándar en Data Lakes modernos.
- **JSON Lines (.jsonl):** un JSON por línea. Ideal para logs y streaming.

Los **logs de sistemas** son archivos de texto generados automáticamente por aplicaciones, servidores y dispositivos de red. Registran eventos con timestamp, nivel de severidad y mensaje. Son fundamentales para monitoreo, auditoría y detección de anomalías.

---

### 2.5 Batch vs. Streaming: Dos Paradigmas de Procesamiento

Una de las decisiones arquitectónicas más importantes en ingeniería de datos es elegir entre **procesamiento por lotes (batch)** o **procesamiento en tiempo real (streaming)**.

#### Procesamiento Batch

Los datos se **acumulan durante un período** (horas, días) y se procesan todos juntos en un momento determinado.

**Características:**
- Alta eficiencia: procesar en bulk es más económico computacionalmente.
- Latencia alta: los resultados no están disponibles hasta que el lote se procesa.
- Fácil de implementar y depurar.
- Ideal cuando el "frescor" del dato no es crítico.

**Ejemplos de uso:**
- Facturación mensual.
- Carga nocturna al Data Warehouse.
- Entrenamiento de modelos de machine learning.
- Reportes de ventas diarios generados a las 6 AM.

#### Procesamiento Streaming

Los datos se procesan **en el momento en que son generados**, evento por evento o en micro-lotes de segundos.

**Características:**
- Latencia muy baja (milisegundos a segundos).
- Mayor complejidad de implementación.
- Requiere infraestructura especializada (Apache Kafka, Apache Flink, Spark Streaming).
- Costoso si el volumen es alto.

**Ejemplos de uso:**
- Detección de fraude en transacciones bancarias en tiempo real.
- Alertas de temperatura en sensores industriales.
- Precios de acciones en bolsa.
- Notificaciones push de aplicaciones móviles.

> **Regla práctica:** Usar **streaming** cuando el valor del dato decae rápidamente con el tiempo (fraude, alertas, precios de bolsa). Usar **batch** cuando la latencia no es crítica (reportes mensuales, entrenamientos de modelos). El streaming no siempre es mejor; es más complejo y costoso.

---

### 2.6 Las 4V del Big Data

El término **Big Data** no describe solo el tamaño de los datos, sino cuatro dimensiones que los diferencian de los datos "tradicionales":

#### Volumen
La **cantidad** de datos generados. Estamos hablando de terabytes, petabytes o exabytes. Una sola plataforma como Facebook o YouTube genera más datos por día de lo que cualquier organización generaba en toda su historia hace 20 años.

> **Implicancia:** Los sistemas tradicionales (una sola base de datos en un servidor) no pueden manejar este volumen. Se necesitan sistemas distribuidos (Hadoop, Spark) o almacenamiento cloud elástico.

#### Velocidad
La **rapidez** con que los datos son generados y deben ser procesados. Hoy los datos llegan en tiempo real desde sensores, transacciones, logs y redes sociales. El procesamiento debe estar a la altura.

> **Implicancia:** Requiere arquitecturas de streaming (Apache Kafka, Kinesis) en lugar de pipelines batch que corren una vez al día.

#### Variedad
La **diversidad de tipos y formatos** de datos: estructurados, semi-estructurados, no estructurados. Imágenes, texto, video, JSON, CSV, audio, sensores: todos conviven en el mismo ecosistema.

> **Implicancia:** No se puede usar una sola herramienta para todo. Los Data Lakes permiten almacenar datos en múltiples formatos para luego procesarlos con la herramienta adecuada.

#### Veracidad
La **confiabilidad y calidad** de los datos. A mayor volumen y variedad, mayor probabilidad de que los datos tengan errores, inconsistencias o sesgos. No todos los datos que se recopilan son verdaderos o útiles.

> **Implicancia:** La calidad del dato no es opcional. Un pipeline que genera datos incorrectos o sesgados puede tomar decisiones peores que no tener datos. De aquí la importancia de la Unidad III de esta asignatura.

```
      VOLUMEN          VELOCIDAD         VARIEDAD         VERACIDAD
  ┌───────────┐     ┌────────────┐    ┌───────────┐    ┌───────────┐
  │  Petabytes│     │ Tiempo     │    │ SQL, JSON,│    │ ¿Puedo    │
  │  de datos │     │ real /     │    │ CSV, img, │    │ confiar   │
  │  diarios  │     │ streaming  │    │ audio...  │    │ en estos  │
  │           │     │            │    │           │    │ datos?    │
  └───────────┘     └────────────┘    └───────────┘    └───────────┘
```

---

## Resumen de la Unidad

| Concepto | Definición resumida |
|---|---|
| Inteligencia de Datos | Capacidad de convertir datos en decisiones de valor. |
| 5 pilares del análisis | Descriptivo → Diagnóstico → Predictivo → Prescriptivo → Decisivo. |
| Ingeniería de Datos | Construcción de pipelines que mueven y transforman datos de extremo a extremo. |
| ETL | Extract (extraer) → Transform (transformar) → Load (cargar). |
| Pirámide DIKW | Dato → Información → Conocimiento → Sabiduría. |
| Datos estructurados | Formato tabular fijo (CSV, SQL). |
| Datos semi-estructurados | Jerarquía flexible (JSON, XML). |
| Datos no estructurados | Sin esquema (texto, imagen, audio). |
| Batch | Procesamiento en lotes diferidos. |
| Streaming | Procesamiento en tiempo real, evento a evento. |
| 4V del Big Data | Volumen, Velocidad, Variedad, Veracidad. |

---

## Bibliografía de la Unidad

- **Davenport, T. H.** — *Competing on Analytics: The New Science of Winning*. Harvard Business Review Press.
- **Kimball, R. & Ross, M.** — *The Data Warehouse Toolkit* (Introducción). Wiley.
- **Kleppmann, M.** — *Designing Data-Intensive Applications*, Capítulo 1. O'Reilly Media.
- **Documentación oficial de Apache Kafka** — [kafka.apache.org](https://kafka.apache.org/documentation/).
- **Reis, J. & Housley, M.** — *Fundamentals of Data Engineering*. O'Reilly Media.
