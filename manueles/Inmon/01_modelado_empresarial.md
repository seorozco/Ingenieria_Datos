# Arquitectura Inmon · Etapa 1 — Modelado Empresarial (*Enterprise Data Modeling*)

> **Arquitectura:** Inmon — Top-Down  
> **Posición en el ciclo:** Primera etapa. Es la base de todo. Sin ella, las etapas siguientes no tienen dirección.

---

## ¿Qué es y por qué es la primera etapa?

La arquitectura Inmon es **top-down**: se empieza por el todo antes de construir las partes. El "todo" en este caso es el **modelo de datos empresarial**: una representación completa y abstracta de cómo la organización ve sus datos, sus entidades de negocio y las relaciones entre ellas.

Bill Inmon sostiene que construir un Data Warehouse sin un modelo empresarial previo es como construir un edificio sin planos: cada equipo levanta su parte de manera independiente y al final los pasillos no conectan, las tuberías no coinciden y las cargas no están balanceadas. En datos, esto se traduce en Data Marts inconsistentes donde "ventas" en el área comercial no coincide con "ventas" en el área financiera.

El modelado empresarial previo garantiza que **todos los sistemas analíticos de la organización hablen el mismo idioma**.

---

## Objetivo de esta etapa

Producir un **Modelo de Datos Empresarial** (*Enterprise Data Model* o EDM) que:

1. Identifique todas las **entidades de negocio** relevantes para la organización (Cliente, Producto, Empleado, Contrato, Pedido, Factura, etc.).
2. Defina las **relaciones** entre esas entidades.
3. Establezca las **definiciones de negocio** de cada entidad y atributo (el glosario corporativo).
4. Sea **independiente de la tecnología**: el EDM describe la realidad del negocio, no cómo se implementará en bases de datos.
5. Sirva como **contrato de datos** entre todas las áreas de la organización.

---

## Los tres niveles del Modelo de Datos Empresarial

Inmon distingue tres niveles de abstracción en el modelado empresarial, que van de lo más general a lo más específico:

### Nivel 1 — Modelo de Alto Nivel (*High-Level Enterprise Data Model*)

Es el mapa conceptual de la organización. Muestra las grandes entidades de negocio y sus relaciones fundamentales, sin entrar en atributos individuales. Es el que se presenta a la dirección ejecutiva y a los sponsors del proyecto.

**Ejemplo para una empresa de distribución:**

```
CLIENTE ──────────────── PEDIDO ──────────────── PRODUCTO
   │                        │                        │
   │                        │                        │
CONTRATO             LÍNEA DE PEDIDO            CATEGORÍA
   │                        │                        │
   │                   FACTURA              PROVEEDOR
SEGMENTO              │
                  PAGO / COBRO
```

En este nivel, el modelo responde: *¿Cuáles son las entidades centrales del negocio y cómo se relacionan entre sí?*

---

### Nivel 2 — Modelo de Mediano Nivel (*Mid-Level Enterprise Data Model*)

Desglosa las entidades del nivel 1 en subtipos y agrega los atributos más importantes de cada entidad. Ya es lo suficientemente detallado como para que los arquitectos de datos y los líderes de negocio lo trabajen juntos.

**Ejemplo: Entidad CLIENTE en el nivel 2**

```
CLIENTE
─────────────────────────────────────────────
id_cliente              (identificador único)
razon_social            (nombre legal)
tipo_cliente            [Persona Física | Empresa | Gobierno]
fecha_alta
estado                  [Activo | Inactivo | Suspendido]
  │
  ├── CLIENTE_PERSONA_FISICA
  │     nro_documento
  │     fecha_nacimiento
  │     genero
  │
  └── CLIENTE_EMPRESA
        nro_cuit
        nro_ingresos_brutos
        id_sector_actividad (FK → SECTOR)

CLIENTE tiene muchos ──── CONTRATO
CLIENTE hace muchos ───── PEDIDO
CLIENTE pertenece a ────── SEGMENTO_CLIENTE
```

---

### Nivel 3 — Modelo de Bajo Nivel (*Low-Level / Physical Enterprise Data Model*)

Es el modelo completamente detallado con todos los atributos, tipos de dato, longitudes, restricciones y relaciones. Es la entrada directa para el diseño de la base de datos del EDW en la siguiente etapa.

**Ejemplo: atributos completos del CLIENTE en nivel 3**

```
CLIENTE
─────────────────────────────────────────────────────────────────
id_cliente            BIGINT         NOT NULL  PK  AUTO_INCREMENT
tipo_cliente          CHAR(1)        NOT NULL  ['F','E','G']
razon_social          VARCHAR(200)   NOT NULL
nombre_fantasia       VARCHAR(200)
nro_documento         VARCHAR(20)
tipo_documento        CHAR(4)        ['DNI','CUIT','CUIL','PASP']
nro_ingresos_brutos   VARCHAR(20)
id_pais               SMALLINT       NOT NULL  FK → PAIS
id_estado_cliente     TINYINT        NOT NULL  FK → ESTADO_CLIENTE
id_segmento           SMALLINT       FK → SEGMENTO_CLIENTE
canal_adquisicion     VARCHAR(50)
fecha_alta            DATE           NOT NULL
fecha_baja            DATE
fecha_ultima_compra   DATE
observaciones         TEXT
fecha_creacion        TIMESTAMP      NOT NULL  DEFAULT NOW()
fecha_modificacion    TIMESTAMP
usuario_creacion      VARCHAR(50)    NOT NULL
usuario_modificacion  VARCHAR(50)
```

---

## Las Áreas Temáticas (*Subject Areas*)

Una parte central del modelado empresarial Inmon es la identificación de las **áreas temáticas**: agrupaciones lógicas de entidades relacionadas que representan un dominio de negocio coherente.

Estas áreas temáticas serán la base para organizar el EDW en la Etapa 2 y eventualmente darán origen a los Data Marts en la Etapa 4.

**Ejemplo de áreas temáticas para una empresa de distribución:**

| Área Temática | Entidades que contiene |
|---|---|
| **Clientes** | Cliente, Segmento, Contrato, Contacto, Dirección |
| **Productos** | Producto, Categoría, Subcategoría, Marca, Proveedor, Precio |
| **Pedidos y Ventas** | Pedido, Línea de Pedido, Factura, Devolución |
| **Logística** | Entrega, Ruta, Vehículo, Depósito, Stock |
| **Finanzas** | Cobro, Pago, Cuenta Corriente, Nota de Crédito |
| **Personas** | Empleado, Vendedor, Cargo, Departamento |
| **Tiempo** | Fecha, Período, Año Fiscal |

---

## El Glosario Corporativo: definir antes de modelar

Un problema habitual en organizaciones sin un modelo empresarial formal es que los distintos departamentos usan los mismos términos con significados distintos, o términos distintos para el mismo concepto:

- El área comercial llama "cliente" a quien hizo alguna vez una consulta.
- El área de facturación llama "cliente" solo a quien tiene al menos una factura emitida.
- El área de logística llama "cliente" al punto de entrega (que puede ser distinto a quien paga).

Si el EDW no resuelve esto antes de construirse, los reportes serán inconsistentes: habrá tres números distintos de "clientes" dependiendo de qué área los produzca.

El **glosario corporativo** (o *business glossary*) es un documento formal que establece la definición oficial y acordada de cada término de negocio:

**Ejemplo de entradas del Glosario Corporativo:**

| Término | Definición oficial | Área responsable | Criterio de inclusión |
|---|---|---|---|
| **Cliente activo** | Persona o empresa que realizó al menos una compra en los últimos 12 meses calendar. | Gerencia Comercial | `fecha_ultima_compra >= SYSDATE - 365` |
| **Venta neta** | Monto facturado menos descuentos aplicados y devoluciones aceptadas, en moneda de origen. | Gerencia Financiera | `monto_factura - descuentos - nc_aceptadas` |
| **Margen bruto** | Diferencia entre venta neta y costo de mercadería vendida (CMV). No incluye gastos operativos. | Gerencia Financiera | `venta_neta - costo_mercaderia` |
| **Período fiscal** | Año fiscal de la empresa: va del 1 de julio al 30 de junio del año siguiente. | Gerencia Financiera | `FY2025 = 2024-07-01 a 2025-06-30` |

---

## Quiénes participan en esta etapa

Esta etapa no es exclusivamente técnica. Es fundamentalmente una actividad de **colaboración entre negocio y tecnología**:

- **Arquitecto de Datos:** lidera el proceso de modelado, propone la estructura y mantiene la consistencia técnica.
- **Data Stewards de cada área:** representantes de negocio que validan que el modelo refleje correctamente la realidad de su dominio.
- **Data Owner / Gerentes de área:** aprueban las definiciones del glosario y los criterios de inclusión.
- **DBA / Ingenieros de Datos senior:** aportan perspectiva técnica sobre viabilidad de implementación.

---

## Entregables de la Etapa 1

Al finalizar esta etapa, la organización debe contar con:

1. ✅ **Modelo de Datos Empresarial** en sus tres niveles (conceptual, lógico, físico parcial).
2. ✅ **Diagrama de Áreas Temáticas** con las entidades agrupadas por dominio de negocio.
3. ✅ **Glosario Corporativo** con definiciones acordadas y firmadas por los Data Owners.
4. ✅ **Matriz de Fuentes** (*Source-to-Target Mapping* preliminar): qué sistema fuente provee cada entidad del modelo.
5. ✅ **Inventario de sistemas fuente** relevantes: ERP, CRM, SCM, hojas de cálculo, etc.

---

## Duración típica y esfuerzo

| Factor | Referencia |
|---|---|
| **Organización pequeña/mediana** | 4 a 8 semanas |
| **Organización grande o compleja** | 3 a 6 meses |
| **Principal desafío** | Conseguir consenso entre áreas sobre definiciones de negocio. El modelado técnico es la parte fácil. |
| **Principal riesgo** | Intentar modelar la organización completa de una vez → análisis paralítico. Preferir modelado iterativo por áreas temáticas. |

---

## Relación con las etapas siguientes

```
ETAPA 1: Modelado Empresarial
        │
        │ Produce:
        │  • Entidades y relaciones validadas
        │  • Glosario corporativo acordado
        │  • Áreas temáticas definidas
        │
        ▼
ETAPA 2: Diseño del EDW Normalizado
        │ Usa el modelo para crear el esquema 3NF del repositorio central.
        │ Las áreas temáticas se convierten en los sujetos del EDW.
        ▼
...
```

Sin un modelo empresarial sólido, el EDW de la Etapa 2 se convierte en una base de datos más del ERP, sin la visión integrada que lo hace valioso.

---

## Técnicas de Relevamiento para la Construcción del EDM

El modelo empresarial no se construye en un escritorio aislado: requiere un proceso riguroso de relevamiento que combine múltiples técnicas para capturar la realidad del negocio.

### Workshops de Modelado Empresarial

Los workshops son sesiones facilitadas donde arquitectos de datos y expertos de negocio trabajan juntos para identificar entidades, relaciones y definiciones. Son la técnica más efectiva para construir el modelo de alto nivel.

**Estructura recomendada de un workshop:**

| Fase | Duración | Actividad | Participantes |
|---|---|---|---|
| **Apertura** | 15 min | Presentar objetivos, alcance y reglas de juego | Todos |
| **Inventario de entidades** | 60 min | Cada área lista las entidades que maneja y las pone en post-its | Todos |
| **Agrupamiento y deduplicación** | 30 min | Agrupar entidades similares, identificar sinónimos | Facilitador + todos |
| **Definición de relaciones** | 60 min | Conectar entidades y definir cardinalidades | Arquitecto + negocio |
| **Definiciones preliminares** | 45 min | Redactar una definición de una línea para cada entidad | Data Stewards |
| **Cierre y próximos pasos** | 15 min | Validar el mapa conceptual, asignar responsables | Todos |

**Errores frecuentes en workshops:**
- Invitar solo a técnicos → el modelo no refleja la realidad del negocio.
- No tener facilitador → las discusiones se desvían hacia problemas operativos.
- Intentar llegar al nivel 3 en un solo workshop → fatiga y pérdida de foco.

---

### Entrevistas Estructuradas

Las entrevistas uno-a-uno con Data Owners y expertos de dominio son esenciales para:
- Capturar reglas de negocio que no se mencionan en grupo.
- Descubrir excepciones y casos borde.
- Identificar conflictos de definición entre áreas antes de que emerjan en un workshop grupal.

**Guía de preguntas para entrevistas:**

1. *¿Cuáles son las entidades más importantes de su área?*
2. *¿Qué reportes o análisis genera con mayor frecuencia?*
3. *¿Qué datos necesita de otras áreas para hacer su trabajo?*
4. *¿Cuándo dos registros representan la "misma cosa"? ¿Cuál es el criterio de unicidad?*
5. *¿Qué datos cambian con frecuencia? ¿Necesita ver cómo eran antes del cambio?*
6. *¿Hay datos que hoy no tiene y le gustaría tener?*
7. *¿Cuál es su definición de [término clave]? ¿Coincide con la de [otra área]?*

---

### Análisis de Sistemas Fuente (*Reverse Engineering*)

Cuando la organización no tiene documentación actualizada de sus sistemas, el equipo de datos debe hacer ingeniería reversa: analizar los esquemas de las bases de datos existentes para entender qué datos existen y cómo están estructurados.

**Proceso de reverse engineering:**

```
1. Obtener el esquema DDL de cada base de datos fuente:
   → pg_dump --schema-only para PostgreSQL
   → mysqldump --no-data para MySQL
   → sp_help para SQL Server

2. Generar diagramas ER automáticos (herramientas: DBeaver, DataGrip, SchemaSpy).

3. Analizar volúmenes (COUNT(*), MAX(date), MIN(date)) para entender
   qué tablas son activas y cuántos datos históricos hay.

4. Analizar la calidad de los datos fuente:
   → Porcentaje de nulos por columna
   → Distribución de valores (¿hay columnas con un solo valor?)
   → Detección de duplicados

5. Documentar hallazgos y contrastar con lo relevado en workshops.
```

---

## Anti-patrones Comunes del Modelado Empresarial

La experiencia acumulada en proyectos de Data Warehouse ha identificado errores recurrentes que deben evitarse:

### Anti-patrón 1: Modelo orientado al ERP

Copiar la estructura del ERP como modelo empresarial. El ERP está diseñado para operaciones transaccionales, no para análisis. Un modelo empresarial que refleja exactamente las tablas del ERP heredará todas sus limitaciones: falta de historial, datos desnormalizados por conveniencia operativa, campos multiuso.

**Síntoma:** el modelo tiene tablas como `MATERIAL_MASTER_DATA` o `BSEG` (nombres de SAP).  
**Solución:** el modelo empresarial debe reflejar la realidad del negocio, no la implementación de un sistema particular.

### Anti-patrón 2: Modelo sin dueño

Construir el modelo pero no asignar responsables de su mantenimiento. En 6 meses, el modelo estará desactualizado y nadie confiará en él.

**Síntoma:** el modelo de datos no se actualiza cuando el negocio cambia.  
**Solución:** cada área temática debe tener un Data Steward responsable de mantener su porción del modelo actualizada.

### Anti-patrón 3: Análisis paralítico

Intentar modelar toda la organización antes de empezar a construir. El perfeccionismo lleva a que el modelo nunca esté "terminado" y el proyecto se paralice.

**Síntoma:** llevamos 8 meses modelando y no tenemos una sola tabla creada en el EDW.  
**Solución:** modelado iterativo por áreas temáticas. Empezar con 2-3 áreas temáticas prioritarias y expandir incrementalmente.

### Anti-patrón 4: Confundir modelo lógico con modelo físico

Tomar decisiones de implementación física (tipos de datos, índices, particiones) durante el modelado conceptual/lógico. Esto contamina el modelo con restricciones tecnológicas que limitan su validez a largo plazo.

**Síntoma:** el modelo de alto nivel ya tiene columnas como `VARCHAR(50)` o discusiones sobre particionamiento.  
**Solución:** respetar la separación de niveles. El modelo conceptual y lógico deben ser independientes de la tecnología.

---

## El Modelo Empresarial en el Contexto Moderno

Si bien el concepto de Inmon nació en los años 90, los principios del modelado empresarial siguen vigentes en las arquitecturas modernas de datos:

### Data Contracts

Los **contratos de datos** (*data contracts*) son la evolución moderna del glosario corporativo y el modelo empresarial. Definen de forma programática y versionable:

- La estructura de los datos (esquema).
- Las reglas de calidad (validaciones).
- El SLA de entrega (frecuencia, latencia).
- El responsable del dato (data owner).

```yaml
# Ejemplo de Data Contract moderno (formato YAML)
dataContract:
  name: "cliente"
  version: "2.1.0"
  owner: "equipo-crm"
  description: "Entidad de cliente unificada según glosario corporativo"
  sla:
    freshness: "daily"
    availability: "99.9%"
  schema:
    - name: id_cliente
      type: bigint
      required: true
      description: "Identificador único del cliente en el EDW"
    - name: razon_social
      type: string
      required: true
      maxLength: 200
    - name: tipo_cliente
      type: enum
      values: ["persona_fisica", "empresa", "gobierno"]
      required: true
    - name: fecha_alta
      type: date
      required: true
  quality:
    - rule: "no_nulls"
      columns: [id_cliente, razon_social, tipo_cliente]
    - rule: "unique"
      columns: [id_cliente]
    - rule: "referential_integrity"
      column: id_segmento
      references: segmento.id_segmento
```

### Data Mesh y el Modelado Empresarial

La arquitectura **Data Mesh** (Zhamak Dehghani, 2019) propone que cada dominio de negocio sea responsable de sus propios datos como producto. Esto puede parecer contradictorio con el modelo empresarial centralizado de Inmon, pero en realidad **el modelo empresarial es necesario aun en Data Mesh** para:

- Definir las **interfaces** entre dominios (qué datos comparte cada dominio y en qué formato).
- Garantizar la **interoperabilidad** entre productos de datos de diferentes dominios.
- Mantener un **glosario corporativo compartido** que evite las inconsistencias.

La diferencia es que en Data Mesh la **responsabilidad** del modelado se distribuye entre los dominios, pero el **estándar** sigue siendo centralizado. El modelo empresarial de Inmon puede evolucionar hacia una **federación de modelos de dominio** coordinados por una gobernanza central.

---

## Herramientas para el Modelado Empresarial

| Herramienta | Tipo | Uso principal | Licencia |
|---|---|---|---|
| **erwin Data Modeler** | Profesional | Modelado ER completo en los 3 niveles | Comercial |
| **PowerDesigner (SAP)** | Profesional | Modelado conceptual, lógico y físico con generación de DDL | Comercial |
| **ER/Studio (Idera)** | Profesional | Modelado con repositorio central y versionado | Comercial |
| **dbdiagram.io** | Web/gratuito | Diagramas ER rápidos con sintaxis DSL | Freemium |
| **draw.io / diagrams.net** | Web/gratuito | Diagramas genéricos (útil para nivel 1 y 2) | Gratuito |
| **DBeaver** | Open source | Reverse engineering de bases existentes + diagramas ER | Gratuito / Comercial |
| **DataGrip (JetBrains)** | Profesional | IDE de base de datos con visualización de esquemas | Comercial |
| **dbt** | Open source | Definición de modelos como código (lógico → físico) | Gratuito / Cloud |

---

## Ejercicio Práctico: Mini-Modelo Empresarial

**Contexto:** Una universidad necesita un Data Warehouse para analizar la gestión académica. Construir el modelo de alto nivel (nivel 1) y un modelo de mediano nivel (nivel 2) para la entidad ALUMNO.

**Nivel 1 — Modelo conceptual:**

```
ALUMNO ─────── INSCRIPCIÓN ─────── MATERIA
   │                │                  │
   │                │                  │
CARRERA        CUATRIMESTRE         CÁTEDRA
   │                                   │
   │                              DOCENTE
FACULTAD
```

**Nivel 2 — Entidad ALUMNO expandida:**

```
ALUMNO
───────────────────────────────────────────
id_alumno                (identificador único)
legajo                   (código alfanumérico)
nombre_completo          (nombre + apellido)
tipo_documento           [DNI | Pasaporte | ...]
nro_documento
fecha_nacimiento
genero                   [M | F | X]
email_institucional
email_personal
fecha_ingreso
id_carrera (FK)          → CARRERA
estado                   [Regular | Libre | Graduado | Baja]
  │
  ├── HISTORIAL_ACADEMICO
  │     id_inscripcion, id_materia, nota_final, estado_cursada
  │
  └── BECAS_ALUMNO
        id_beca, tipo_beca, monto, fecha_otorgamiento
```

**Ejercicio para el estudiante:**
1. Agregar las entidades DOCENTE, MATERIA y CARRERA con sus atributos principales (nivel 2).
2. Identificar al menos 4 áreas temáticas del dominio universitario.
3. Redactar 3 entradas del glosario corporativo (ej: ¿qué es un "alumno regular"? ¿qué es una "materia aprobada"?).

---

## Lecturas recomendadas

- **Inmon, W.H.** — *Building the Data Warehouse*, 4ta edición. Capítulo 3: "The Corporate Information Factory". Wiley.
- **Inmon, W.H.** — *Data Architecture: A Primer for the Data Scientist*. Morgan Kaufmann.
- **DAMA International** — *DAMA-DMBOK: Data Management Body of Knowledge*, Capítulo 8: "Data Modeling and Design".
- **Dehghani, Z.** — *Data Mesh: Delivering Data-Driven Value at Scale*. O'Reilly Media. (Para la perspectiva moderna de modelado distribuido).
- **Sadalage, P. & Fowler, M.** — *NoSQL Distilled: A Brief Guide to the Emerging World of Polyglot Persistence*. (Para contrastar con modelado relacional).
- **Hay, D.C.** — *Data Model Patterns: A Metadata Map*. Morgan Kaufmann. (Patrones reutilizables de modelado empresarial).
