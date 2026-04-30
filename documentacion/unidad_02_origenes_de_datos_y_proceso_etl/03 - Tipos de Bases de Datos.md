# Clase 03 — Tipos de Bases de Datos

> **Asignatura:** Ingeniería de Datos  
> **Docente:** Ing. Sergio Orozco  
> **Unidad:** II — Orígenes de Datos y Proceso ETL

---

## Objetivos de la Clase

Al finalizar esta clase, el alumno será capaz de:

- Explicar por qué existen múltiples tipos de bases de datos y cuándo usar cada uno.
- Describir las **propiedades ACID** de las bases de datos relacionales.
- Clasificar los cuatro tipos principales de bases de datos **NoSQL** y sus casos de uso.
- Distinguir con precisión **OLTP** y **OLAP** en cuanto a diseño, uso y optimización.
- Diferenciar **Data Warehouse**, **Data Lake** y **Data Lakehouse**.

---

## 1. ¿Por qué Existen Tantos Tipos de Bases de Datos?

Durante décadas, las bases de datos relacionales (SQL) fueron la solución casi universal para almacenar datos. Sin embargo, a medida que los sistemas crecieron en escala, variedad de datos y patrones de acceso, quedó claro que **una sola tecnología no puede ser óptima para todos los casos**.

Pensemos en un sistema de e-commerce:

```
¿Qué necesita un e-commerce?
│
├── Registrar transacciones con consistencia absoluta
│   └─► SQL Relacional (PostgreSQL, MySQL)
│
├── Guardar sesiones de usuario con latencia de microsegundos
│   └─► Clave-Valor (Redis)
│
├── Almacenar catálogo de productos con atributos variables
│   └─► Documental (MongoDB)
│
├── Detectar fraude analizando relaciones entre cuentas
│   └─► Grafo (Neo4j)
│
└── Analizar millones de transacciones históricas para reportes
    └─► Columnar analítico (BigQuery, Redshift, Snowflake)
```

Cada necesidad tiene su mejor herramienta. El Data Engineer debe conocerlas todas para elegir sabiamente.

---

## 2. Bases de Datos Relacionales (SQL)

Son el tipo más maduro y extendido. Organizan los datos en **tablas con filas y columnas** y utilizan **SQL** como lenguaje de consulta estándar. Las relaciones entre tablas se establecen mediante **claves foráneas**.

### 2.1 Propiedades ACID

Las bases de datos relacionales garantizan **integridad transaccional** mediante las propiedades ACID:

```
┌─────────────────────────────────────────────────────────────────────┐
│                     PROPIEDADES ACID                                │
├──────────────────┬─────────────────────────────────────────────────│
│  A — Atomicidad  │  Una transacción se ejecuta COMPLETA o NO       │
│                  │  se ejecuta. No existen medias transacciones.   │
│                  │  Ej: transferencia bancaria = débito + crédito  │
│                  │  (ambos o ninguno)                               │
├──────────────────┼─────────────────────────────────────────────────│
│  C — Consistencia│  Los datos siempre pasan de un estado VÁLIDO   │
│                  │  a otro estado VÁLIDO. Las reglas del esquema    │
│                  │  nunca se violan.                                │
├──────────────────┼─────────────────────────────────────────────────│
│  I — Isolación   │  Las transacciones concurrentes no se          │
│                  │  "ven" entre sí hasta que se confirman          │
│                  │  (commit). Evita lecturas sucias.               │
├──────────────────┼─────────────────────────────────────────────────│
│  D — Durabilidad │  Una vez confirmada (commit), la transacción   │
│                  │  persiste aunque el sistema falle o se reinicie │
└──────────────────┴─────────────────────────────────────────────────│
```

**Ejemplo ACID en la práctica:**

Imaginemos una transferencia bancaria de $1000 de la cuenta A a la cuenta B:

```sql
BEGIN;
  UPDATE cuentas SET saldo = saldo - 1000 WHERE id = 'A';  -- Débito
  UPDATE cuentas SET saldo = saldo + 1000 WHERE id = 'B';  -- Crédito
COMMIT;

-- Si el servidor cae entre los dos UPDATE, la BD hace ROLLBACK automático.
-- La Atomicidad garantiza que nunca habrá un débito sin su crédito.
```

### 2.2 Motores Relacionales Más Usados

| Motor | Licencia | Uso típico | Característica destacada |
|---|---|---|---|
| **PostgreSQL** | Open source | Analítica, backend, ETL | Extensible, soporte JSON nativo, el favorito del ecosistema de datos |
| **MySQL / MariaDB** | Open source | Aplicaciones web | Velocidad en lectura, amplio soporte |
| **SQL Server** | Comercial | Entornos Microsoft | Integración con Power BI, SSIS, Azure |
| **Oracle DB** | Comercial | Banca y ERP enterprise | Robustez y soporte empresarial |
| **SQLite** | Open source | Desarrollo y testing | Embebido, sin servidor, ideal para prototipado |

**¿Cuándo elegir una BD relacional?**
- Cuando la **consistencia es crítica** (transacciones financieras, inventario, RR.HH.).
- Cuando el **esquema es estable** y las relaciones entre entidades son importantes.
- Cuando necesitás hacer **JOINs complejos** entre entidades relacionadas.

---

## 3. Bases de Datos NoSQL

"NoSQL" no significa "sin SQL" sino "Not Only SQL". Son bases de datos diseñadas para casos específicos donde el modelo relacional no es óptimo. Se clasifican en cuatro tipos principales:

### 3.1 Clave-Valor (Key-Value)

Almacenan los datos como pares **clave → valor**. La clave es el identificador único y el valor puede ser cualquier cosa: un número, un string, un JSON, una imagen binaria.

```
clave              │  valor
───────────────────┼─────────────────────────────────────
"sesion:abc123"    │  {"user_id": 4521, "nombre": "Ana", "expires": 1800}
"precio:SKU-101"   │  1500.00
"contador:visitas" │  1842923
"config:max_retry" │  5
```

**Motores:** Redis, Amazon DynamoDB, Memcached.

**Cuándo usarlos:**
- Caché de aplicaciones (guardar el resultado de consultas costosas por N segundos).
- Sesiones de usuario en sistemas web.
- Contadores y rankings en tiempo real.
- Feature flags y configuraciones en caliente.

> **Ejemplo real:** Un sitio de e-commerce usa Redis para guardar el carrito de compras de cada usuario. La clave es el ID de sesión, el valor es el JSON con los productos. Si el usuario cierra el navegador y vuelve, el carrito está intacto. Todo en memoria, latencia de microsegundos.

### 3.2 Documentales (Document Stores)

Almacenan los datos como **documentos** (generalmente JSON o BSON) sin esquema fijo. Cada documento puede tener campos distintos al resto de la colección.

```json
// Colección "productos" — cada documento puede tener campos diferentes:

// Producto tipo LIBRO:
{ "_id": "p-001", "tipo": "libro", "titulo": "Clean Code", "autor": "R. Martin", "isbn": "978-01" }

// Producto tipo ELECTRÓNICO:
{ "_id": "p-002", "tipo": "electronico", "marca": "Samsung", "pulgadas": 27, "resolución": "4K", "puertos_hdmi": 2 }

// Producto tipo ROPA:
{ "_id": "p-003", "tipo": "ropa", "marca": "Adidas", "talle": "M", "color": "azul", "material": "algodón" }
```

**Motores:** MongoDB, CouchDB, Amazon DocumentDB, Firebase Firestore.

**Cuándo usarlos:**
- Catálogos de productos con atributos heterogéneos.
- APIs y microservicios donde los objetos tienen estructura variable.
- Prototipado rápido donde el esquema todavía no está definido.

### 3.3 Columnares (Wide Column Stores)

En lugar de almacenar datos por fila, almacenan los datos **por columna y familia de columnas**. Son extremadamente eficientes para escritura masiva y distribuida a escala global.

> ⚠️ **Cuidado con la confusión:** Las bases de datos columnares de tipo Wide Column (Cassandra, HBase) son diferentes a los formatos columnares analíticos (Parquet, BigQuery). Las primeras son para escritura distribuida masiva; las segundas, para consultas analíticas.

**Motores:** Apache Cassandra, HBase, ScyllaDB.

**Cuándo usarlos:**
- Escritura masiva y distribuida a escala global.
- Series temporales (métricas de sistemas, datos de sensores IoT).
- Cuando la disponibilidad importa más que la consistencia estricta.

> **Ejemplo real:** Netflix usa Apache Cassandra para almacenar el historial de reproducciones de millones de usuarios simultáneamente. La escritura es extremadamente rápida porque está distribuida en miles de nodos en múltiples regiones.

### 3.4 Bases de Datos de Grafos

Almacenan los datos como **nodos** (entidades) y **aristas** (relaciones), con propiedades en ambos. Son extremadamente eficientes cuando las consultas navegan por **relaciones complejas** entre entidades.

```
Modelo RELACIONAL para representar relaciones sociales:
  SELECT u2.nombre
  FROM usuarios u1
  JOIN amistades a1 ON u1.id = a1.user_id
  JOIN amistades a2 ON a1.amigo_id = a2.user_id
  JOIN usuarios u2 ON a2.amigo_id = u2.id
  WHERE u1.nombre = 'Ana'
  -- Esto es "amigos de los amigos de Ana" — ya es complejo

Modelo de GRAFO (Cypher en Neo4j):
  MATCH (ana:Persona {nombre:'Ana'})-[:AMIGO*2]->(persona)
  RETURN persona.nombre
  -- "Personas a 2 saltos de Ana" — simple y eficiente
```

**Motores:** Neo4j, Amazon Neptune, ArangoDB.

**Cuándo usarlos:**
- Redes sociales (amigos de amigos, seguidores, comunidades).
- Detección de fraude (cuentas conectadas por IPs, dispositivos, beneficiarios).
- Sistemas de recomendación ("usuarios que compraron X también compraron Y").
- Grafos de conocimiento y ontologías.

---

## 4. OLTP vs. OLAP: El Contraste Fundamental

Esta es una distinción **absolutamente crítica** en arquitectura de datos. Determina cómo se diseña una base de datos, qué tecnología se usa y cómo se optimiza.

```
┌─────────────────────────────────────────────────────────────────────┐
│              OLTP                    │           OLAP               │
│   (Online Transaction Processing)   │  (Online Analytical Process) │
├──────────────────────────────────────┼─────────────────────────────│
│  Propósito: operar el negocio        │  Propósito: analizar datos   │
│  ¿Quién lo usa? Cajeras, empleados   │  ¿Quién lo usa? Analistas    │
│  Operaciones: INSERT/UPDATE/DELETE   │  Operaciones: SELECT + GROUP │
│  Filas por consulta: 1 a miles       │  Filas por consulta: millones│
│  Diseño: Normalizado (3NF)           │  Diseño: Desnormalizado      │
│  Prioridad: Escritura rápida + ACID  │  Prioridad: Lectura rápida   │
│  Datos: Solo estado actual           │  Datos: Histórico completo   │
└──────────────────────────────────────┴─────────────────────────────│
```

> **Regla de oro:** Las bases OLTP **generan** los datos. Las OLAP los **analizan**. El proceso ETL es el puente que conecta ambos mundos.

**Ejemplo visual — ¿cuál uso para qué?**

| Pregunta | Sistema correcto |
|---|---|
| "Registrar la venta del cliente Juan" | OLTP (INSERT en base transaccional) |
| "¿Cuáles fueron los 10 productos más vendidos este año?" | OLAP (SELECT en DWH) |
| "Actualizar el stock después de una compra" | OLTP (UPDATE inmediato) |
| "¿Cuál fue la evolución del margen por trimestre en los últimos 3 años?" | OLAP (análisis histórico) |

---

## 5. Sistemas Analíticos: DWH, Data Lake y Lakehouse

En el destino de nuestros pipelines existen distintos tipos de sistemas analíticos, cada uno con sus características:

```
┌─────────────────┬────────────────────────────┬─────────────────────────────┐
│  Sistema        │  Analogía                  │  Características            │
├─────────────────┼────────────────────────────┼─────────────────────────────┤
│ DATA WAREHOUSE  │  Biblioteca organizada:     │  Datos estructurados,       │
│                 │  libros catalogados,        │  curados y modelados.       │
│                 │  indexados y curados.       │  Esquema fijo.              │
│                 │                            │  Alta performance SQL.       │
├─────────────────┼────────────────────────────┼─────────────────────────────┤
│ DATA LAKE       │  Depósito: se guarda todo  │  Datos en formato crudo.    │
│                 │  sin procesar. Flexible     │  Sin esquema previo.        │
│                 │  pero difícil de encontrar  │  Bajo costo de storage.     │
│                 │  algo específico.           │  Requiere processing layer. │
├─────────────────┼────────────────────────────┼─────────────────────────────┤
│ DATA LAKEHOUSE  │  Biblioteca moderna: tiene  │  Combina la flexibilidad    │
│                 │  la amplitud del depósito   │  del Lake con las garantías │
│                 │  con la organización de     │  ACID del DWH.              │
│                 │  la biblioteca.             │  Delta Lake, Iceberg, Hudi. │
└─────────────────┴────────────────────────────┴─────────────────────────────┘
```

---

## Resumen de la Clase

| Tipo de BD | Modelo | Cuándo usarla |
|---|---|---|
| **Relacional (SQL)** | Tablas + esquema fijo | Transacciones, consistencia crítica, relaciones estructuradas |
| **Clave-Valor** | Pares key→value | Caché, sesiones, contadores, latencia crítica |
| **Documental** | Documentos JSON | Objetos con estructura variable, APIs, catálogos |
| **Columnar (Wide)** | Familias de columnas | Escritura masiva distribuida, IoT, series temporales |
| **Grafo** | Nodos y aristas | Redes sociales, fraude, recomendaciones |
| **OLTP** | Normalizado, transaccional | Operaciones del negocio en tiempo real |
| **OLAP / DWH** | Desnormalizado, analítico | Análisis histórico, reportes, BI |

---

> 💡 **Para la próxima clase:** Ahora que conocemos las distintas bases de datos disponibles, en la **Clase 04** vamos a aprender las técnicas concretas para **extraer datos** de ellas usando Python.
