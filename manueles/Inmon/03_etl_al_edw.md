# Arquitectura Inmon · Etapa 3 — ETL: Extracción, Transformación y Carga al EDW

> **Arquitectura:** Inmon — Top-Down  
> **Posición en el ciclo:** Tercera etapa. Es el motor que alimenta el EDW con datos de los sistemas fuente.

---

## ¿Qué es el ETL en el contexto Inmon?

El proceso **ETL** (Extract, Transform, Load) es la ingeniería de integración que conecta los **sistemas operativos fuente** con el **Enterprise Data Warehouse**. Es el proceso más complejo y costoso de mantener en la arquitectura Inmon, y suele representar entre el 60% y el 80% del esfuerzo total de construcción del DWH.

En la arquitectura Inmon, el ETL tiene un doble rol:

1. **ETL hacia el EDW:** lleva los datos desde los sistemas fuente hacia el repositorio central 3FN. Este proceso debe resolver la integración, limpiar los datos y gestionar el historial.

2. **ETL desde el EDW hacia los Data Marts:** en la Etapa 4, un segundo proceso ETL toma los datos ya integrados del EDW y los desnormaliza para alimentar los Data Marts con esquemas estrella.

Esta etapa se enfoca en el primero de estos dos procesos.

---

## El flujo completo del ETL Inmon

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  ERP (SAP)   │    │  CRM (SF)    │    │  Planillas   │
│  PostgreSQL  │    │  API REST    │    │  Excel/CSV   │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │ EXTRACCIÓN
                           ▼
              ┌────────────────────────┐
              │     STAGING AREA       │
              │  (copia cruda, sin     │
              │   transformaciones)    │
              └────────────┬───────────┘
                           │ TRANSFORMACIÓN
                           │  • Limpieza
                           │  • Integración de identificadores
                           │  • Resolución de conflictos
                           │  • Aplicación del glosario
                           │  • Gestión del historial
                           ▼
              ┌────────────────────────┐
              │ ENTERPRISE DATA        │
              │ WAREHOUSE (3FN)        │
              │  (datos integrados,    │
              │   históricos, limpios) │
              └────────────────────────┘
```

---

## Etapa 3A — Extracción (*Extract*)

### ¿Qué significa extraer?

Extraer es obtener los datos de cada sistema fuente y copiarlos a la Staging Area, sin modificarlos. El principio fundamental es: **extraer los datos tal como están en la fuente** y hacer todas las decisiones de transformación más adelante, de forma controlada.

### Estrategias de extracción

#### Full Extract (Extracción Completa)

Se copia la totalidad de los datos de la tabla fuente en cada ciclo de carga.

**Cuándo aplicarla:**
- Tablas pequeñas o medianas donde el costo de la extracción completa es aceptable.
- Tablas de referencia (catálogos, listas de valores, tablas maestras) que cambian poco pero cuando cambian lo hacen de forma no rastreable.
- Primera carga histórica (*initial load*) de cualquier tabla.

**Ventaja:** Simplicidad. No requiere marcas ni mecanismos de detección de cambios.  
**Desventaja:** No escala para tablas de millones de registros que se actualizan diariamente.

---

#### Incremental Extract (Extracción Incremental)

Solo se extraen los registros modificados o creados desde la última extracción exitosa.

**Mecanismos para identificar registros modificados:**

**Timestamp de modificación:** la fuente tiene una columna `updated_at` o `fecha_modificacion`. Se extraen solo los registros donde ese timestamp es mayor que el de la última extracción.

```
Ejemplo de consulta de extracción incremental:

SELECT *
FROM erp.ventas.pedido
WHERE fecha_modificacion > '2025-03-14 06:00:00'
  AND fecha_modificacion <= '2025-03-15 06:00:00'
ORDER BY fecha_modificacion ASC;
```

**Columna de versión:** algunos sistemas mantienen un número de versión o secuencia que incrementa con cada modificación. Se extraen los registros con versión mayor a la última procesada.

**Change Data Capture (CDC):** herramientas como **Debezium** leen directamente el log de transacciones de la base de datos (WAL en PostgreSQL, binlog en MySQL, redo log en Oracle) y capturan cada INSERT, UPDATE y DELETE en tiempo casi real. Es el método más potente pero también el más complejo de implementar.

**Flags de procesamiento:** el sistema fuente tiene una columna booleana `ya_procesado` o `pendiente_sync` que el proceso ETL usa para identificar registros nuevos y luego marca como procesados.

---

#### Extracción desde APIs

Muchos sistemas fuente exponen sus datos a través de APIs REST. La extracción desde APIs tiene consideraciones especiales:

- **Paginación:** las APIs suelen limitar la cantidad de registros por llamada. El proceso ETL debe iterar por páginas.
- **Rate limiting:** la API limita la cantidad de llamadas por minuto. El proceso debe respetar esos límites.
- **Autenticación:** las APIs requieren tokens o API Keys que deben almacenarse de forma segura (nunca en el código fuente).
- **Idempotencia:** si la llamada falla a mitad del proceso, debe poder re-ejecutarse sin duplicar datos.

---

#### Extracción de archivos planos

Muchos sistemas legacy o procesos manuales entregan datos en archivos CSV, Excel o TXT. Consideraciones:

- **Detección de llegada:** el proceso ETL debe monitorear una carpeta o bucket de S3 para detectar cuando llega un nuevo archivo.
- **Validación del archivo:** antes de procesar, verificar que el archivo tiene el formato esperado (cantidad de columnas, delimitador, encoding).
- **Archivos parciales:** si el proceso que genera el archivo falla a mitad, puede aparecer un archivo incompleto. Usar archivos de señal (*flag files*) que se generan cuando el archivo principal está completo.
- **Archivado:** una vez procesado, mover el archivo a una carpeta de archivado con timestamp para trazabilidad.

---

## Etapa 3B — Transformación (*Transform*)

La transformación es el corazón del ETL. Es donde los datos crudos de los sistemas fuente se convierten en datos integrados, limpios y conformes con el modelo del EDW.

### Transformaciones de limpieza

**Tratamiento de nulos:** definir para cada campo qué hacer con los valores nulos según el glosario corporativo. Opciones:
- Mantener el nulo (si el campo es opcional).
- Imputar un valor por defecto según la regla de negocio (`'SIN DATOS'`, `0`, `'9999-12-31'`).
- Rechazar el registro si el campo es obligatorio y está nulo (y enviarlo a la cola de errores).

**Estandarización de formatos:**
- Fechas: convertir todos los formatos posibles (`15/03/2025`, `2025-03-15`, `March 15 2025`) a un formato único (`YYYY-MM-DD`).
- Textos: strip de espacios, unificación de mayúsculas/minúsculas según el estándar del glosario.
- Numéricos: resolución del separador decimal (`,` vs `.`) y de miles.

**Validación de dominio:** verificar que los valores pertenecen al conjunto de valores válidos definido en el glosario. Por ejemplo, verificar que el código de moneda está en la lista oficial ISO 4217.

---

### Transformaciones de integración

Esta es la parte más compleja y valiosa del ETL en Inmon: resolver las diferencias entre sistemas fuente para crear una visión unificada.

**Resolución de identificadores (*Entity Resolution*):**

El mismo cliente puede tener identificadores distintos en sistemas distintos:
- En el ERP: `CUST-00004521`
- En el CRM: `C_4521`
- En el sistema de logística: `45210`

Para integrarlos en el EDW como un único cliente, se necesita una **tabla de mapeo de claves** (*crosswalk table*) que relaciona los identificadores de cada sistema:

```
Tabla: edw.mapeo_claves_cliente
─────────────────────────────────────────────────────────────────
id_cliente_edw  │ id_sistema │ clave_origen  │ fecha_mapeo
────────────────│────────────│───────────────│────────────
10001           │ ERP        │ CUST-00004521 │ 2024-01-15
10001           │ CRM        │ C_4521        │ 2024-01-15
10001           │ LOGISTICA  │ 45210         │ 2024-01-15
10002           │ ERP        │ CUST-00003310 │ 2024-01-15
10002           │ CRM        │ C_3310        │ 2024-01-15
```

Esta tabla de mapeo es uno de los activos más valiosos del EDW: representa el conocimiento acumulado sobre cómo se relacionan los datos entre sistemas.

**Resolución de conflictos entre fuentes:**

Cuando el mismo dato existe en dos sistemas y tiene valores distintos, ¿cuál prevalece? Esta decisión debe estar documentada en las **reglas de integración**:

| Atributo | Sistema A (ERP) | Sistema B (CRM) | Regla de resolución |
|---|---|---|---|
| `email_cliente` | `maria@old.com` | `maria@nuevo.com` | Prevalece CRM (más reciente) |
| `razon_social` | `GARCIA MARIA` | `María García` | Prevalece ERP (registro legal) |
| `id_segmento` | Vacío | `Premium` | Prevalece CRM (campo solo existe allí) |

---

### Gestión del historial en el EDW

Cuando un registro cambia en la fuente, el ETL debe preservar el historial en el EDW. El mecanismo es similar al SCD Tipo 2 pero aplicado sistemáticamente a todas las entidades del EDW:

```
Proceso de actualización histórica en el ETL:

1. Extraer el registro modificado de la Staging Area.
2. Buscar el registro vigente en el EDW (is_vigente = TRUE).
3. Si no existe → INSERT como nuevo registro con fecha_efectiva = hoy.
4. Si existe y hay diferencias:
   a. Calcular el hash del registro fuente.
   b. Si el hash difiere del hash del registro EDW → hay cambio.
   c. UPDATE del registro vigente: fecha_vencimiento = hoy-1, is_vigente = FALSE.
   d. INSERT del nuevo registro con los nuevos valores y fecha_efectiva = hoy.
5. Si existe y no hay diferencias → no hacer nada (eficiencia).
```

---

## Etapa 3C — Carga (*Load*)

### Principios de la carga al EDW

**Idempotencia:** el proceso de carga puede ejecutarse múltiples veces con el mismo resultado. Si falla a la mitad y se re-ejecuta, no genera duplicados ni corrompe el historial.

**Atomicidad por lote:** un lote de registros se carga completo o no se carga. Si falla a mitad del lote, se hace rollback y se reintenta desde el principio del lote.

**Orden de carga:** las tablas deben cargarse en el orden correcto respetando las dependencias de claves foráneas:
1. Primero las tablas maestras sin dependencias (PAIS, TIPO_CLIENTE).
2. Luego las tablas que dependen de las anteriores (PROVINCIA → CIUDAD).
3. Finalmente las tablas transaccionales que dependen de todas las anteriores (PEDIDO, VENTA).

**Sin locks prolongados:** la carga debe diseñarse para minimizar el tiempo de bloqueo de tablas, especialmente si el EDW debe estar disponible para los procesos de actualización de Data Marts durante la ventana de carga.

---

### Ventana de Carga

La **ventana de carga** (*load window*) es el período durante el cual el proceso ETL puede ejecutarse sin interferir con los procesos de negocio. En organizaciones con actividad 24/7, definir esta ventana es un desafío crítico.

```
Ejemplo de ventana de carga para un DWH con operaciones en múltiples zonas horarias:

22:00 UTC │ Inicio del proceso de extracción desde fuentes
          │ (horario de menor actividad en todas las zonas)
22:30 UTC │ Finalización de extracciones → Staging Area completa
22:30 UTC │ Inicio de transformaciones
23:30 UTC │ Inicio de carga al EDW
01:00 UTC │ EDW actualizado → inicio de actualización de Data Marts
03:00 UTC │ Data Marts actualizados → informes disponibles para el día
06:00 UTC │ Inicio del día hábil (primer zona horaria)
```

---

## Gestión de errores y reintentos

El ETL debe ser **robusto ante fallos**. Los fallos son inevitables: la red puede caerse, un sistema fuente puede estar inaccesible, un registro puede violar una restricción de integridad. El diseño del ETL debe contemplar:

**Cola de errores (*Error Queue*):** los registros que no pueden procesarse (por error de validación, referencia huérfana, etc.) no deben detener el proceso completo. Se derivan a una tabla de errores con el motivo del rechazo para revisión manual posterior.

```
Tabla: staging.errores_carga
──────────────────────────────────────────────────────────────────────
id_error │ entidad      │ clave_origen │ motivo_error             │ fecha
─────────│──────────────│──────────────│──────────────────────────│──────
1001     │ edw.pedido   │ PED-99812    │ id_cliente no encontrado │ 2025-03-15
1002     │ edw.producto │ SKU-X9991    │ id_categoria nulo        │ 2025-03-15
```

**Registro de auditoría (*Audit Log*):** cada ejecución del ETL debe registrarse con:
- Fecha y hora de inicio y fin.
- Sistema fuente procesado.
- Registros extraídos, transformados y cargados.
- Registros rechazados y enviados a la cola de errores.
- Estado final: éxito o fallo (con mensaje de error).

**Reintentos con backoff:** si un paso falla por un error transitorio (timeout de red, sistema fuente temporalmente no disponible), el proceso debe reintentarlo automáticamente con un tiempo de espera creciente entre intentos.

---

## El Metadato del ETL

Un componente frecuentemente subestimado del ETL es la gestión de sus propios **metadatos de ejecución**: cuándo corrió, qué procesó, qué última fecha fue procesada por cada entidad.

```
Tabla: meta.control_carga
────────────────────────────────────────────────────────────────────────────
entidad_destino  │ sistema_fuente │ ultima_ejecucion_ok │ ultimo_valor_marca
─────────────────│────────────────│─────────────────────│────────────────────
edw.cliente      │ ERP            │ 2025-03-15 01:23:45 │ 2025-03-15 06:00:00
edw.cliente      │ CRM            │ 2025-03-15 01:45:12 │ 2025-03-15 06:00:00
edw.pedido       │ ERP            │ 2025-03-15 02:10:33 │ 2025-03-15 06:00:00
edw.producto     │ ERP            │ 2025-03-15 01:31:08 │ 2025-03-15 06:00:00
```

El campo `ultimo_valor_marca` guarda el "punto de corte" de la última extracción incremental exitosa. Si el proceso falla y se reinicia, sabe desde dónde retomar.

---

## Entregables de la Etapa 3

1. ✅ **Diseño detallado del flujo ETL** por cada entidad y sistema fuente.
2. ✅ **Matriz Fuente-Destino completa** con transformaciones campo a campo.
3. ✅ **Tablas de mapeo de claves** entre sistemas fuente y el EDW.
4. ✅ **Reglas de integración documentadas** (qué prevalece cuando hay conflicto).
5. ✅ **Diseño del esquema de errores y auditoría** del ETL.
6. ✅ **Código ETL** (Python, dbt, Airflow, o herramienta seleccionada).
7. ✅ **Plan de carga inicial** (*initial load*): estrategia para cargar los datos históricos por primera vez.
8. ✅ **Diseño de la ventana de carga** y acuerdo de SLA con el negocio.

---

## Relación con las etapas siguientes

```
ETAPA 3: ETL hacia el EDW
        │
        │ Produce:
        │  • EDW alimentado con datos integrados e históricos
        │  • Metadatos de control y auditoría
        │  • Cola de errores para revisión
        │
        ▼
ETAPA 4: Data Marts (derivación desde el EDW)
        │ Un segundo proceso ETL toma los datos del EDW
        │ y los desnormaliza en esquemas estrella para
        │ cada área de negocio.
        ▼
```

---

## Lecturas recomendadas

- **Kimball, R. & Caserta, J.** — *The Data Warehouse ETL Toolkit: Practical Techniques for Extracting, Cleaning, Conforming, and Delivering Data*. Wiley.
- **Inmon, W.H.** — *Building the Data Warehouse*, 4ta edición. Capítulo 7: "The ETL Process". Wiley.
- **Reis, J. & Housley, M.** — *Fundamentals of Data Engineering*, Capítulo 8. O'Reilly Media.
- **Documentación de Apache Airflow** — [airflow.apache.org](https://airflow.apache.org/docs/) (orquestación de pipelines ETL).
- **Documentación de Debezium** — [debezium.io](https://debezium.io/documentation/) (Change Data Capture).
