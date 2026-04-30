# Clase 02 — Tipos de Datos y Fuentes de Origen

> **Asignatura:** Ingeniería de Datos  
> **Docente:** Ing. Sergio Orozco  
> **Unidad:** I — Fundamentos e Inteligencia de Datos

---

## Objetivos de la Clase

Al finalizar esta clase, el alumno será capaz de:

- Clasificar los datos según su **estructura** (estructurados, semi-estructurados y no estructurados) y elegir las herramientas adecuadas para cada tipo.
- Identificar las principales **fuentes de datos internas y externas** de una organización.
- Entender cómo funcionan las **APIs REST** y cuándo se usan como fuente de datos.
- Conocer los **formatos de archivo** más comunes en el ecosistema de datos.
- Distinguir entre **procesamiento batch y streaming** y elegir el paradigma correcto.
- Comprender las **4 V's del Big Data** y su implicancia arquitectónica.

---

## 1. Clasificación de los Datos según su Estructura

Una de las primeras preguntas que un Data Engineer debe hacerse ante cualquier fuente de datos es: **¿Qué tipo de estructura tienen estos datos?** La respuesta determina qué herramientas son aplicables y qué transformaciones serán necesarias.

```
┌─────────────────────────────────────────────────────────────────────┐
│               TIPOS DE DATOS SEGÚN ESTRUCTURA                       │
├──────────────────────┬────────────────────────┬──────────────────── │
│   ESTRUCTURADO       │  SEMI-ESTRUCTURADO     │  NO ESTRUCTURADO    │
│                      │                        │                     │
│  Tablas SQL          │  JSON / XML / YAML     │  Texto libre        │
│  CSV / Excel         │  Correos electrónicos  │  Imágenes / Video   │
│  ERP / CRM           │  Logs de sistemas      │  Audio              │
│                      │                        │  PDFs               │
│  ▼ Herramientas:     │  ▼ Herramientas:       │  ▼ Herramientas:    │
│  SQL, Pandas         │  Python (json),        │  NLP, OpenCV,       │
│                      │  jsonpath, jq          │  Whisper, OCR       │
└──────────────────────┴────────────────────────┴──────────────────── │
```

---

### 1.1 Datos Estructurados

Son datos organizados en un **formato tabular fijo**: filas y columnas con tipos de dato predefinidos. Son los más fáciles de procesar, consultar y analizar.

**Características principales:**
- Tienen un **esquema predefinido y rígido**: cada columna tiene un nombre y un tipo de dato (número, texto, fecha, booleano).
- Son fácilmente consultables con **SQL estándar**.
- Agregar una nueva columna requiere modificar el esquema (un ALTER TABLE), lo que implica coordinación con todos los consumidores.
- Representan el **20% de los datos** generados en el mundo, pero históricamente el 80% de los datos analizados (son los más fáciles de trabajar).

**Ejemplos reales:**
- Tablas en bases de datos relacionales (PostgreSQL, MySQL, SQL Server, Oracle).
- Archivos CSV o Excel exportados de un ERP o CRM.
- Registros de transacciones bancarias.
- Tablas de un Data Warehouse.

**Ejemplo visual — tabla de ventas:**

```
┌──────────┬─────────────┬────────────┬─────────┬────────┐
│ id_venta │ fecha       │ cliente_id │ monto   │ moneda │
├──────────┼─────────────┼────────────┼─────────┼────────┤
│  1001    │ 2025-03-10  │  C-4521    │ 1250.00 │  ARS   │
│  1002    │ 2025-03-10  │  C-3310    │  890.50 │  USD   │
│  1003    │ 2025-03-11  │  C-4521    │ 3400.00 │  ARS   │
└──────────┴─────────────┴────────────┴─────────┴────────┘
Cada fila tiene exactamente los mismos campos, con el mismo tipo de dato.
```

---

### 1.2 Datos Semi-estructurados

Son datos que **tienen alguna organización interna** (jerarquía, etiquetas, claves) pero **no siguen un esquema tabular rígido**. Su estructura puede variar entre registros del mismo "tipo".

**Características principales:**
- Son **auto-descriptivos**: el dato lleva consigo su propia estructura (las "etiquetas" forman parte del dato).
- Son **flexibles**: distintos registros pueden tener distintos campos.
- Requieren **parsing** (interpretación del formato) para procesarlos.
- Son el formato nativo de la mayoría de las **APIs modernas**.

**Formatos más comunes:**

| Formato | Nombre completo | Uso típico |
|---|---|---|
| **JSON** | JavaScript Object Notation | APIs REST, configuraciones, microservicios |
| **XML** | eXtensible Markup Language | Integraciones legacy, EDI, SOAP |
| **YAML** | YAML Ain't Markup Language | Configuraciones de herramientas (Airflow, Docker, K8s) |
| **Avro** | Apache Avro | Streaming con Kafka, serialización eficiente |

**Ejemplo visual — respuesta de API en JSON:**

```json
{
  "id_pedido": "P-9921",
  "fecha": "2025-03-15T14:32:00Z",
  "cliente": {
    "nombre": "María González",
    "email": "maria@ejemplo.com",
    "ciudad": "Córdoba"
  },
  "items": [
    { "producto": "Laptop",  "cantidad": 1, "precio": 85000 },
    { "producto": "Mouse",   "cantidad": 2, "precio": 3500  },
    { "producto": "Mochila", "cantidad": 1, "precio": 4200  }
  ],
  "total": 96200,
  "moneda": "ARS"
}
```

> **¿Ven el desafío?** El campo `items` contiene una lista de longitud **variable**: un pedido puede tener 1 ítem o 100. Esto sería imposible de representar directamente en una sola fila de una tabla SQL. Para "aplanar" este JSON a formato tabular, necesitaríamos transformarlo (explode, unnest, etc.).

---

### 1.3 Datos No Estructurados

Son datos que **no tienen un formato ni esquema definido**. Constituyen aproximadamente el **80-90% de los datos generados** en el mundo y son los más difíciles de procesar con técnicas tradicionales.

**Características principales:**
- Sin esquema fijo: cada archivo o registro puede tener forma completamente distinta.
- Requieren técnicas especializadas para extraer información de ellos.
- Contienen **enorme riqueza de información**, pero con alta complejidad de extracción.

**Ejemplos reales:**

| Tipo | Ejemplos | Técnica de procesamiento |
|---|---|---|
| **Texto libre** | Emails, reseñas, chats, noticias | NLP (Natural Language Processing) |
| **Imágenes** | Fotos de productos, capturas de facturas | Visión por computadora (OpenCV, YOLO) |
| **Video** | Grabaciones de cámaras, tutoriales | Análisis de frames, detección de objetos |
| **Audio** | Llamadas de call center, podcasts | Speech-to-text (Whisper, Google STT) |
| **Documentos** | PDFs, contratos, informes escaneados | OCR (Tesseract, Azure Document Intelligence) |

**Ejemplo práctico — ¿qué información hay en un email de reclamo?**

```
Asunto: Mi pedido llegó roto

Hola, les escribo porque recibí el pedido #P-9921 el día de ayer
y la pantalla del notebook estaba quebrada. Necesito que me 
expliquen el proceso de devolución. Estoy muy disconforme con el
servicio. Ya es la segunda vez que me pasa esto.

Gracias,
María González
```

Con técnicas de NLP se puede extraer automáticamente:
- **Sentimiento:** negativo (disconforme, segunda vez).
- **Entidad:** N° de pedido P-9921, producto "notebook".
- **Intención:** solicitar proceso de devolución.
- **Urgencia:** media-alta.

---

### Resumen comparativo

```
┌────────────────────┬──────────────┬──────────────────┬──────────────────┐
│ Criterio           │ Estructurado │ Semi-estructurado│ No estructurado  │
├────────────────────┼──────────────┼──────────────────┼──────────────────┤
│ Esquema            │ Fijo         │ Flexible         │ Sin esquema      │
│ Fácil de procesar  │ ✅ Sí        │ ⚠️ Moderado      │ ❌ Difícil       │
│ Herramienta        │ SQL, Pandas  │ Python, jq       │ NLP, CV, OCR     │
│ % en el mundo      │ ~20%         │ ~10%             │ ~70%             │
│ Ejemplo            │ CSV, tabla   │ JSON, XML        │ Email, imagen    │
└────────────────────┴──────────────┴──────────────────┴──────────────────┘
```

---

## 2. Fuentes de Datos: Internas vs. Externas

Las organizaciones consumen datos que provienen de dos grandes categorías de fuentes. El Data Engineer debe conocer ambas para diseñar las estrategias de extracción adecuadas.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FUENTES DE DATOS                                 │
├────────────────────────────┬────────────────────────────────────── │
│      INTERNAS              │           EXTERNAS                    │
│                            │                                       │
│  ERP (SAP, Oracle)         │  APIs públicas (clima, BCRA)          │
│  CRM (Salesforce)          │  Redes sociales                       │
│  E-commerce                │  Sensores IoT                         │
│  Logs de sistemas          │  Proveedores de datos                 │
│  Bases de datos operativas │  Web scraping                         │
│                            │                                       │
│  ✅ Controladas            │  ⚠️ Variable calidad y disponibilidad │
│  ✅ Confiables             │  💡 Alta riqueza informativa          │
└────────────────────────────┴────────────────────────────────────── │
```

### 2.1 Fuentes Internas

Son los sistemas y procesos propios de la organización que generan datos como **subproducto de sus operaciones cotidianas**.

| Sistema | ¿Qué genera? | Tipo de datos |
|---|---|---|
| **ERP** (SAP, Oracle) | Compras, inventario, finanzas, RR.HH. | Estructurado |
| **CRM** (Salesforce, HubSpot) | Contactos, oportunidades comerciales, interacciones | Estructurado |
| **Plataformas e-commerce** | Pedidos, carritos, historial de navegación | Estructurado / Semi-estructurado |
| **Logs de aplicaciones** | Errores, accesos, tiempos de respuesta | Semi-estructurado |
| **Bases de datos operativas** | Cualquier BBDD que soporte las operaciones | Estructurado |

### 2.2 Fuentes Externas

Son datos que provienen de **fuera de la organización**.

| Fuente | Descripción | Ejemplo de uso |
|---|---|---|
| **APIs públicas** | Servicios que exponen datos libres o por suscripción | Tipo de cambio del BCRA, datos del INDEC |
| **Redes sociales** | Comentarios, menciones, métricas de engagement | Análisis de sentimiento de marca |
| **Sensores IoT** | Dispositivos físicos con lecturas en tiempo real | Temperatura de almacén, GPS de flota |
| **Proveedores de datos** | Empresas que venden datasets especializados | Scores crediticios, datos demográficos |
| **Web scraping** | Extracción automática de información pública | Precios de competidores, disponibilidad |

---

## 3. APIs REST y GraphQL como Fuentes de Datos

Las APIs (*Application Programming Interfaces*) son una de las fuentes de datos **más importantes en la ingeniería de datos moderna**. Permiten a los sistemas comunicarse entre sí de manera estandarizada y son la forma estándar de exponer datos en internet.

### 3.1 ¿Cómo funciona una API REST?

**REST** (Representational State Transfer) es el estilo de API más extendido. Funciona sobre **HTTP** y organiza los datos en "recursos" accesibles mediante URLs.

```
CLIENTE (nuestro script Python)          SERVIDOR (API externa)
        │                                        │
        │  GET /api/dolares HTTP/1.1             │
        │  Host: api.bcra.gov.ar                 │
        │  Authorization: Bearer mi_token        │
        │──────────────────────────────────────►│
        │                                        │
        │  HTTP/1.1 200 OK                       │
        │  Content-Type: application/json        │
        │  {"fecha":"2025-04-30","valor":1250.5} │
        │◄──────────────────────────────────────│
```

**Verbos HTTP más comunes en APIs:**

| Verbo | Acción | Ejemplo |
|---|---|---|
| `GET` | Obtener datos (leer) | `GET /api/productos/101` |
| `POST` | Crear un nuevo recurso | `POST /api/pedidos` |
| `PUT` | Actualizar un recurso completo | `PUT /api/clientes/4521` |
| `DELETE` | Eliminar un recurso | `DELETE /api/sesion/abc123` |

**Conceptos clave al trabajar con APIs:**

- **Autenticación:** las APIs generalmente requieren una **API Key** o token **OAuth** para identificar quién hace la solicitud y controlar el acceso.
- **Rate limiting:** limitan la cantidad de llamadas permitidas por minuto/hora para prevenir abuso.
- **Paginación:** cuando hay muchos resultados, se devuelven en "páginas" y hay que iterar para obtenerlos todos.
- **Timeout:** si la API no responde en un tiempo límite, el cliente debe manejar el error.

**Ejemplo de extracción con Python:**

```python
import requests

# Extrayendo tipo de cambio desde la API del BCRA
response = requests.get(
    "https://api.bcra.gob.ar/estadisticas/v2.0/datosvariable/4/2025-01-01/2025-03-31",
    timeout=30
)

# Validar que la respuesta fue exitosa
if response.status_code == 200:
    datos = response.json()
    print(f"Registros obtenidos: {len(datos['results'])}")
    for registro in datos['results'][:3]:
        print(f"  Fecha: {registro['fecha']} | Valor: {registro['valor']}")
else:
    print(f"Error en la API: {response.status_code}")
```

### 3.2 API GraphQL — Una alternativa flexible

**GraphQL** es una alternativa más moderna a REST. En lugar de múltiples endpoints (uno por recurso), tiene **un único endpoint** donde el cliente especifica exactamente qué datos necesita.

Esto resuelve dos problemas comunes de REST:
- **Over-fetching:** recibir más datos de los necesarios (el servidor devuelve 50 campos pero solo necesitás 3).
- **Under-fetching:** tener que hacer múltiples llamadas para obtener datos relacionados.

```
REST (múltiples llamadas):
  GET /api/clientes/101          → datos del cliente
  GET /api/clientes/101/pedidos  → pedidos del cliente
  GET /api/pedidos/P-9921/items  → ítems del pedido

GraphQL (una sola consulta):
  query {
    cliente(id: "101") {
      nombre
      pedidos(limit: 5) {
        id_pedido
        total
        items { producto cantidad }
      }
    }
  }
```

---

## 4. Archivos Planos y Formatos de Datos

Además de las APIs y bases de datos, muchas fuentes de datos son simplemente **archivos**. Conocer sus características ayuda a elegir el mejor para cada situación.

```
┌───────────┬───────────┬──────────┬──────────┬─────────────┐
│ Formato   │ Tipo      │ Legible  │ Eficiente│ Uso típico  │
│           │           │ por hum. │ (grande) │             │
├───────────┼───────────┼──────────┼──────────┼─────────────┤
│ CSV       │ Texto     │  ✅ Sí   │  ❌ No   │ Intercambio │
│ Excel     │ Binario   │  ✅ Sí   │  ❌ No   │ Corporativo │
│ JSON      │ Texto     │  ✅ Sí   │  ❌ No   │ APIs, config│
│ Parquet   │ Columnar  │  ❌ No   │  ✅ Sí   │ Data Lakes  │
│ Avro      │ Binario   │  ❌ No   │  ✅ Sí   │ Streaming   │
│ JSON Lines│ Texto     │  ✅ Sí   │  ⚠️ Med  │ Logs, stream│
└───────────┴───────────┴──────────┴──────────┴─────────────┘
```

### CSV — El más universal
El formato **CSV** (Comma-Separated Values) es el más simple y extendido para intercambiar datos tabulares. Una fila por registro, valores separados por comas (o punto y coma en español).

**Fortalezas:** Simple, legible, compatible con todo.  
**Debilidades:** Frágil si los datos contienen comas o saltos de línea. Sin tipos de dato (todo es texto). Ineficiente para grandes volúmenes.

### Parquet — El estándar de los Data Lakes
**Apache Parquet** es un formato **columnar binario** desarrollado específicamente para analítica de grandes volúmenes. En lugar de almacenar los datos por fila (como CSV), los almacena por columna.

```
Almacenamiento por FILA (CSV):
  [id=1, nombre="Ana", monto=1500, fecha="2025-01-05"]
  [id=2, nombre="Juan", monto=2300, fecha="2025-01-06"]

Almacenamiento por COLUMNA (Parquet):
  [id: 1, 2, 3, ...]
  [nombre: "Ana", "Juan", "María", ...]
  [monto: 1500, 2300, 850, ...]
  [fecha: "2025-01-05", "2025-01-06", ...]
```

**¿Por qué esto importa?** Si una consulta analítica solo necesita `SUM(monto)`, con Parquet se leen solo los bytes de la columna `monto`. Con CSV, hay que leer toda la fila (todos los campos) para llegar al monto. En un archivo de 1 millón de filas con 50 columnas, la diferencia es enorme.

**Parquet es el estándar de facto para Data Lakes y pipelines de Big Data.**

---

## 5. Batch vs. Streaming: Dos Paradigmas de Procesamiento

Esta es una de las **decisiones arquitectónicas más importantes** que enfrentará un Data Engineer. Elige mal y el sistema será demasiado costoso, demasiado lento, o ambos.

```
BATCH                                     STREAMING
  │                                          │
  │  Los datos se acumulan                   │  Los datos se procesan
  │  durante un período                      │  en el momento que llegan
  │  y se procesan juntos                    │  evento por evento
  │                                          │
  │  ────────────────────                    │  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
  │  ↑              ↑                        │  ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑
  │  t=0           t=24hs                   │  instante a instante
  │                                          │
  ▼                                          ▼
Carga nocturna al DWH                   Detección de fraude
Reportes de ventas diarios              Alertas en tiempo real
Entrenamiento de modelos ML             Precios de bolsa
```

### 5.1 Procesamiento Batch (por lotes)

Los datos se **acumulan durante un período** (minutos, horas, días) y se procesan todos juntos en un momento determinado.

**Características:**
- Alta eficiencia: procesar en bulk es más económico computacionalmente.
- Latencia alta: los resultados no están disponibles hasta que el lote se procesa.
- Fácil de implementar, depurar y re-ejecutar.
- El paradigma clásico de los Data Warehouses y pipelines ETL.

**Cuándo usar batch:**
- Facturación mensual o reportes diarios.
- Carga nocturna al Data Warehouse.
- Entrenamiento de modelos de machine learning.
- Procesamiento de archivos enviados por proveedores.

### 5.2 Procesamiento Streaming (en tiempo real)

Los datos se procesan **en el momento en que son generados**, evento por evento o en micro-lotes de segundos.

**Características:**
- Latencia muy baja: milisegundos a segundos desde que el evento ocurre hasta que se procesa.
- Mayor complejidad de implementación y operación.
- Requiere infraestructura especializada: **Apache Kafka**, **Apache Flink**, **Spark Streaming**.
- Más costoso: la infraestructura debe estar activa las 24 horas.

**Cuándo usar streaming:**
- Detección de fraude en transacciones bancarias.
- Alertas de temperatura en sensores industriales.
- Precios de acciones o criptomonedas.
- Notificaciones push en aplicaciones móviles.
- Monitoreo de logs en tiempo real.

### 5.3 La regla de decisión

> **¿Vale la pena la complejidad del streaming?**
>
> Usá **streaming** cuando el **valor del dato decae rápidamente con el tiempo**: detectar un fraude 5 minutos después es inútil; detectarlo en segundos puede evitar el daño.
>
> Usá **batch** cuando la **latencia no es crítica**: un reporte de ventas del día anterior sigue siendo válido si se genera a las 6 AM.
>
> El streaming no es "mejor" que el batch. Es más complejo, más costoso y solo se justifica cuando la inmediatez es un requerimiento real de negocio.

---

## 6. Las 4V del Big Data

El término **Big Data** no describe simplemente datos "grandes". Define cuatro **dimensiones** que hacen que los datos de la era digital sean cualitativamente distintos a los datos tradicionales, y que exigen nuevas arquitecturas para manejarlos.

```
                    ┌─────────────┐
                    │   BIG DATA  │
                    └──────┬──────┘
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
     VOLUMEN           VELOCIDAD           VARIEDAD
   (¿cuánto?)         (¿qué tan rápido?)   (¿qué formas?)
          │                 │                 │
          └─────────────────┼─────────────────┘
                            ▼
                        VERACIDAD
                      (¿qué tan confiable?)
```

### 🔢 Volumen — La cantidad masiva

La **cantidad** de datos generados. Estamos hablando de terabytes, petabytes o incluso exabytes.

- Facebook genera ~4 petabytes de datos por día.
- YouTube recibe 500 horas de video por minuto.
- Un auto Tesla con modo autopilot genera ~25 GB de datos por hora.

**Implicancia para el Data Engineer:** los sistemas tradicionales (un servidor con PostgreSQL) no pueden manejar este volumen. Se necesitan sistemas **distribuidos** (Hadoop, Spark) o almacenamiento cloud elástico (S3, GCS, Azure Blob).

### ⚡ Velocidad — La rapidez de generación

La **rapidez** con que los datos son generados y deben ser procesados. Hoy los datos llegan en tiempo real desde sensores, transacciones, logs y redes sociales.

**Implicancia:** se necesitan arquitecturas de streaming (**Apache Kafka**, **AWS Kinesis**) en lugar de pipelines batch que corren una vez al día.

### 🎨 Variedad — La diversidad de formatos

La **diversidad de tipos y formatos**: estructurados, semi-estructurados, no estructurados. Imágenes, texto, video, JSON, CSV, audio, sensores — todos conviven en el mismo ecosistema.

**Implicancia:** no se puede usar una sola herramienta para todo. Los **Data Lakes** permiten almacenar datos de múltiples formatos para luego procesarlos con la herramienta adecuada.

### ✅ Veracidad — La confiabilidad de los datos

La **calidad y confiabilidad** de los datos. A mayor volumen y variedad, mayor probabilidad de que los datos tengan errores, inconsistencias, ruido o sesgos.

**Implicancia:** el trabajo de calidad del dato (que veremos en la Unidad III) se vuelve crítico. "Más datos" no significa "mejores decisiones" si esos datos son incorrectos.

> **La 5ta V (no oficial): Valor** — El objetivo final de gestionar las 4V es generar **valor** para la organización. Sin valor de negocio, el Big Data es solo ruido costoso.

---

## Resumen de la Clase

| Concepto | Definición en una frase |
|---|---|
| **Estructurado** | Tablas con esquema fijo; fácil de procesar con SQL |
| **Semi-estructurado** | JSON/XML con estructura flexible; requiere parsing |
| **No estructurado** | Texto, imágenes, audio; requiere técnicas especializadas |
| **Fuentes internas** | ERP, CRM, bases operativas — datos propios de la organización |
| **Fuentes externas** | APIs, redes sociales, IoT, scraping — datos del mundo exterior |
| **API REST** | Interfaz HTTP para consumir datos de servicios externos |
| **Parquet** | Formato columnar binario, estándar para Data Lakes |
| **Batch** | Procesamiento por lotes en intervalos regulares |
| **Streaming** | Procesamiento en tiempo real, evento por evento |
| **4V del Big Data** | Volumen, Velocidad, Variedad, Veracidad |

---

> 💡 **Para la próxima unidad:** Ahora que conocemos de dónde vienen los datos y cómo se clasifican, en la **Unidad II** vamos a aprender a **extraerlos, transformarlos y cargarlos** usando Python, SQL y las herramientas del stack moderno de Ingeniería de Datos.
