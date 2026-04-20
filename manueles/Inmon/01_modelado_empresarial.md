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

## Lecturas recomendadas

- **Inmon, W.H.** — *Building the Data Warehouse*, 4ta edición. Capítulo 3: "The Corporate Information Factory". Wiley.
- **Inmon, W.H.** — *Data Architecture: A Primer for the Data Scientist*. Morgan Kaufmann.
- **DAMA International** — *DAMA-DMBOK: Data Management Body of Knowledge*, Capítulo 8: "Data Modeling and Design".
