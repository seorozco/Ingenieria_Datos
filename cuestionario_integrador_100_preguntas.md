# Cuestionario integrador de Ingeniería de Datos

**Cobertura:** Unidades I a V del programa de la asignatura  
**Total:** 100 preguntas  
**Distribución:** 20 preguntas por unidad; 25 preguntas por tipo de consigna.

## Indicaciones

- Respondé todas las preguntas. En selección simple, marcá una sola opción.
- En verdadero o falso, indicá V o F y justificá las afirmaciones falsas.
- En definición, explicá el concepto con precisión y agregá un ejemplo cuando corresponda.
- En desarrollo, explicitá los supuestos, las decisiones de diseño y sus justificaciones. Podés usar diagramas, tablas o pseudocódigo cuando ayuden a la respuesta.
- El cuestionario fue contrastado con el programa, la presentación `ingenieria_datos_v2.pptx`, la documentación y las notebooks. La Unidad V se apoya especialmente en la presentación y el programa, porque las notebooks disponibles profundizan principalmente las Unidades II, III y IV.

## A. Selección simple

### Unidad I — Fundamentos e Inteligencia de Datos

**1.** Una empresa detecta que las ventas bajaron y busca identificar qué cambió en el comportamiento de sus clientes. ¿Qué nivel de análisis está aplicando principalmente?

A. Descriptivo  
B. Diagnóstico  
C. Predictivo  
D. Decisivo

**2.** En la pirámide DIKW, ¿cuál es el mejor ejemplo de conocimiento construido a partir de información?

A. El valor `200` almacenado en una columna.  
B. El registro de 200 clics en el botón de compra.  
C. La observación de que los clics de compra aumentan los lunes por la tarde.  
D. La decisión de aumentar el inventario para los lunes.

**3.** ¿Cuál es una responsabilidad central del Data Engineer?

A. Definir exclusivamente la estrategia comercial de la empresa.  
B. Construir y mantener pipelines que provean datos confiables para análisis.  
C. Aprobar toda decisión de negocio basada en un reporte.  
D. Diseñar únicamente las visualizaciones finales.

**4.** ¿Cómo se clasifica habitualmente una respuesta de API en formato JSON?

A. Estructurada.  
B. Semi-estructurada.  
C. No estructurada.  
D. Transaccional.

**5.** ¿En cuál de estos casos resulta más apropiado priorizar procesamiento streaming?

A. Cálculo del cierre contable anual.  
B. Generación de un reporte mensual histórico.  
C. Detección de una transacción potencialmente fraudulenta mientras ocurre.  
D. Archivo de respaldos del año anterior.

### Unidad II — Orígenes de Datos y Proceso ETL

**6.** ¿Qué tipo de base de datos es más adecuado para consultar relaciones complejas entre cuentas posiblemente vinculadas con fraude?

A. Clave-valor.  
B. Relacional OLTP.  
C. De grafos.  
D. Documental.

**7.** ¿Qué patrón describe mejor una carga OLTP?

A. Consultas extensas que agregan años de ventas.  
B. Muchas transacciones pequeñas y concurrentes que actualizan registros.  
C. Entrenamiento de modelos sobre datos históricos consolidados.  
D. Lecturas analíticas sobre un esquema dimensional.

**8.** Una tabla fuente incluye una marca de última modificación confiable y solo cambiaron pocos registros desde la ejecución anterior. ¿Qué estrategia de extracción conviene evaluar primero?

A. Full Load en cada ejecución.  
B. Extracción incremental.  
C. Eliminar la tabla fuente.  
D. Scraping de la interfaz de usuario.

**9.** ¿Cuál es la finalidad principal de un `upsert` en una carga?

A. Reemplazar siempre todo el destino, sin importar su contenido.  
B. Insertar filas nuevas y actualizar las existentes según una clave.  
C. Convertir automáticamente un archivo JSON en una API.  
D. Eliminar registros duplicados del sistema de origen.

**10.** ¿Qué característica de Apache Airflow permite expresar que una tarea debe ejecutarse después de otra dentro de un pipeline?

A. La definición de dependencias entre tareas en un DAG.  
B. La serialización de todas las tablas en CSV.  
C. La normalización automática de columnas.  
D. La captura de cambios del motor de base de datos.

### Unidad III — Calidad del Dato y Gobierno

**11.** En una tabla de clientes, una misma persona aparece dos veces con identificadores distintos aunque representa a la misma entidad. ¿Qué dimensión está comprometida principalmente?

A. Vigencia.  
B. Unicidad.  
C. Completitud.  
D. Disponibilidad.

**12.** ¿Cuál es el objetivo principal del data profiling?

A. Sustituir las reglas de negocio por estimaciones estadísticas.  
B. Examinar estructura, distribución y problemas potenciales de un conjunto de datos.  
C. Crear automáticamente un Data Warehouse.  
D. Eliminar todos los registros que contengan valores atípicos.

**13.** ¿Qué herramienta del stack del curso permite definir y ejecutar expectativas automatizadas como «`id_venta` no nulo», «`id_venta` único» y «moneda dentro de un conjunto permitido»?

A. Apache Airflow.  
B. Great Expectations.  
C. Neo4j.  
D. Apache Kafka.

**14.** ¿Por qué una métrica de calidad debe informar su denominador?

A. Para que todas las métricas puedan sumar más de 100%.  
B. Para interpretar qué población se evaluó y evitar comparaciones engañosas.  
C. Para ocultar las filas que no cumplen las reglas.  
D. Para reemplazar la necesidad de documentar las reglas.

**15.** ¿Qué responsabilidad corresponde principalmente al Data Owner?

A. Aprobar decisiones y excepciones sobre el activo de datos dentro de su ámbito.  
B. Ejecutar todas las consultas SQL de los usuarios.  
C. Crear por sí solo cada transformación técnica.  
D. Administrar el sistema operativo de los servidores.

### Unidad IV — Data Warehouse y Modelado Dimensional

**16.** ¿Cuál es la diferencia general entre los enfoques de Inmon y Kimball?

A. Inmon propone un EDW central normalizado top-down; Kimball prioriza la construcción bottom-up de Data Marts dimensionales integrados.  
B. Inmon se basa en streaming y Kimball exclusivamente en archivos.  
C. Inmon elimina los datos históricos y Kimball conserva solo datos actuales.  
D. Ambos son nombres para el mismo modelo físico.

**17.** En el caso de ventas facturadas de WideWorldImporters, ¿qué grano define el notebook de hechos?

A. Una fila por cliente y año.  
B. Una fila por factura completa.  
C. Una fila por línea de detalle de factura.  
D. Una fila por producto y vendedor sin fecha.

**18.** ¿Qué ventaja aporta una clave sustituta (SK) en una dimensión?

A. Reemplaza la necesidad de conservar cualquier referencia al sistema origen.  
B. Identifica técnicamente una versión de la fila dimensional dentro del DWH.  
C. Garantiza que nunca existan cambios en los atributos descriptivos.  
D. Convierte una tabla de hechos en una tabla transaccional OLTP.

**19.** Una empresa necesita conservar cada versión histórica de la dirección de un cliente. ¿Qué estrategia SCD corresponde?

A. Tipo 1: sobrescribir la dirección.  
B. Tipo 2: insertar una nueva versión con vigencias.  
C. Tipo 3: borrar toda la dimensión.  
D. Append sin claves ni fechas.

**20.** ¿Cuál es un componente típico de una tabla de hechos?

A. Métricas del proceso y claves hacia dimensiones.  
B. Solo descripciones extensas de entidades.  
C. Únicamente reglas de acceso de usuarios.  
D. El código fuente completo del pipeline.

### Unidad V — Arquitecturas Modernas y Proyecto Integrador

**21.** En una arquitectura Medallion, ¿qué capa conserva principalmente la copia cruda del origen?

A. Gold.  
B. Silver.  
C. Bronze.  
D. Semantic.

**22.** ¿Qué capacidad aporta Delta Lake sobre almacenamiento de objetos?

A. Transacciones ACID y consulta de versiones anteriores mediante Time Travel.  
B. La eliminación de toda necesidad de validación.  
C. La conversión obligatoria de cada dato en una tabla relacional normalizada.  
D. La sustitución de las fuentes de datos operacionales.

**23.** ¿Qué resultado se espera normalmente de la capa Gold?

A. Datos sin inspeccionar, idénticos a la fuente.  
B. Datos depurados pero sin propósito de consumo.  
C. Agregados o productos de datos preparados para análisis y consumo.  
D. Archivos temporales de depuración que deben descartarse.

**24.** ¿Qué describe mejor a un Data Lakehouse?

A. Un repositorio de archivos sin metadatos ni controles.  
B. Una arquitectura que busca combinar flexibilidad de Data Lake con capacidades de gestión y análisis propias de un DWH.  
C. Una base de datos exclusivamente orientada a transacciones pequeñas.  
D. Una herramienta que reemplaza toda orquestación.

**25.** ¿Qué combinación se asocia en el programa con ingeniería de datos en tiempo real?

A. Kafka y Flink.  
B. Excel y FTP.  
C. Airflow y PowerPoint.  
D. SQL Server y un proceso anual por lotes.

## B. Verdadero o falso

Indicá V o F. Justificá las afirmaciones falsas.

### Unidad I — Fundamentos e Inteligencia de Datos

**26.** La información se obtiene al contextualizar o procesar datos; el conocimiento incorpora interpretación útil para comprender una situación.

**27.** Un archivo de audio con voz es un ejemplo típico de dato estructurado porque está almacenado como bytes.

**28.** El análisis prescriptivo busca recomendar qué acción conviene tomar, mientras que el decisivo se relaciona con ejecutar o seleccionar la mejor alternativa.

**29.** El ciclo de vida del dato termina necesariamente después de su visualización y no contempla activación ni archivo.

**30.** Volumen, velocidad, variedad y veracidad son las cuatro V del Big Data consideradas en el programa.

### Unidad II — Orígenes de Datos y Proceso ETL

**31.** Una extracción incremental puede reducir el volumen procesado, pero depende de un mecanismo confiable para identificar cambios.

**32.** El web scraping consiste en consultar siempre una API oficial y estructurada.

**33.** Limpiar un dataset puede incluir tratar nulos, duplicados, tipos incorrectos y formatos inconsistentes.

**34.** En ETL se transforman los datos antes de cargarlos al destino; en ELT se cargan primero y se transforman en el entorno de destino.

**35.** Un pipeline idempotente debe producir duplicados nuevos cada vez que se vuelve a ejecutar con la misma entrada.

### Unidad III — Calidad del Dato y Gobierno

**36.** Si una fila incumple varias reglas, el número de hallazgos puede ser superior al número de filas rechazadas.

**37.** La tasa de rechazo y la tasa de cumplimiento de exactitud siempre usan el mismo denominador.

**38.** En la práctica de ETL gobernado, superar el umbral de rechazo puede bloquear el lote completo aunque algunas filas sean válidas.

**39.** Un catálogo de datos, un diccionario de datos y un glosario de negocio describen exactamente lo mismo y pueden usarse como sinónimos sin pérdida.

**40.** Una huella SHA-256 demuestra por sí sola quién generó los datos y que su contenido es exacto.

### Unidad IV — Data Warehouse y Modelado Dimensional

**41.** El Data Warehouse complementa los sistemas operacionales y está orientado a consultas analíticas e históricas.

**42.** En un esquema estrella, las dimensiones suelen contener atributos descriptivos que permiten filtrar y agrupar las métricas de hechos.

**43.** Si cambia un atributo bajo SCD Tipo 1, se conserva siempre una fila distinta por cada versión histórica.

**44.** En una carga de hechos, resolver las claves naturales de origen a claves sustitutas de dimensiones ayuda a mantener las relaciones del modelo dimensional.

**45.** La granularidad puede definirse después de construir la tabla de hechos, porque no afecta qué representa cada fila.

### Unidad V — Arquitecturas Modernas y Proyecto Integrador

**46.** En el patrón Medallion, Bronze suele preservar datos cercanos al origen, Silver aplica limpieza y Gold prepara productos para consumo.

**47.** El concepto de data swamp describe un Data Lake tradicional que carece de organización, metadatos o controles suficientes.

**48.** Time Travel permite consultar versiones anteriores de datos cuando la tecnología y la retención configurada lo permiten.

**49.** La adopción de un formato Lakehouse vuelve innecesarios el gobierno, el control de calidad y la documentación del linaje.

**50.** Un proyecto integrador del programa debe articular fuente, extracción, transformación, calidad, modelado analítico y orquestación.

## C. Definición de conceptos

Definí cada término con precisión. Incluí un ejemplo breve cuando la consigna lo solicite.

### Unidad I — Fundamentos e Inteligencia de Datos

**51.** Definí Inteligencia de Datos e Ingeniería de Datos, diferenciando sus objetivos y explicando qué papel cumple ETL en la segunda.

**52.** Definí la pirámide DIKW y describí la diferencia entre dato, información, conocimiento y sabiduría.

**53.** Definí análisis descriptivo y análisis predictivo; diferenciá la pregunta que responde cada uno.

**54.** Definí dato estructurado, semi-estructurado y no estructurado. Incluí un ejemplo de cada tipo.

**55.** Definí Data Mesh y explicá cómo se relacionan en este paradigma los dominios de negocio, los datos como productos y la gobernanza federada.

### Unidad II — Orígenes de Datos y Proceso ETL

**56.** Definí las bases relacionales y los modelos NoSQL clave-valor, documental, columnar y de grafos. Para cada modelo, indicá un uso apropiado y un ejemplo de tecnología.

**57.** Definí Change Data Capture (CDC) y explicá qué tipo de cambios permite capturar.

**58.** Definí idempotencia aplicada a una carga de datos.

**59.** Definí ETL y ELT, indicando el orden de extracción, transformación y carga de cada enfoque.

**60.** Definí DAG en el contexto de Apache Airflow y explicá qué representan sus nodos y dependencias.

### Unidad III — Calidad del Dato y Gobierno

**61.** Definí completitud y exactitud, y distinguí qué pregunta responde cada dimensión.

**62.** Definí data profiling e indicá qué tipos de hallazgos puede revelar sobre un dataset.

**63.** Definí contrato de datos y mencioná dos ejemplos de reglas verificables que podría incluir.

**64.** Definí linaje del dato y explicá qué información conecta desde el origen hasta el destino.

**65.** Definí Data Owner y Data Steward, diferenciando sus responsabilidades generales.

### Unidad IV — Data Warehouse y Modelado Dimensional

**66.** Definí Data Warehouse e indicá sus características de orientación temática, integración, no volatilidad y variación temporal.

**67.** Definí granularidad de una tabla de hechos y explicá por qué se decide antes de diseñar sus medidas y dimensiones.

**68.** Definí dimensión conformada y explicá cómo ayuda a integrar distintos procesos de negocio.

**69.** Definí clave natural (NK) y clave sustituta (SK), señalando dónde suele originarse cada una.

**70.** Definí SCD Tipo 1, Tipo 2 y Tipo 3, indicando cómo trata cada estrategia los cambios históricos.

### Unidad V — Arquitecturas Modernas y Proyecto Integrador

**71.** Definí Data Lake y describí el propósito de las zonas Raw, Staged y Curated.

**72.** Definí Data Lakehouse y explicá qué necesidades busca cubrir frente a un Data Lake tradicional.

**73.** Definí Delta Lake y mencioná el papel de ACID y Time Travel.

**74.** Definí la arquitectura Medallion y describí la finalidad de Bronze, Silver y Gold.

**75.** Definí DataOps y explicá cómo contribuye al desarrollo o la operación de pipelines de datos.

## D. Desarrollo

Respondé con argumentos y decisiones justificadas. Cuando corresponda, incluí un esquema, tabla, pseudocódigo o reglas de validación.

### Unidad I — Fundamentos e Inteligencia de Datos

**76.** Una empresa integra ventas de su ERP, datos de clima desde una API pública, mediciones de sensores IoT y publicaciones de redes sociales. Clasificá cada fuente por origen y estructura; proponé cuáles procesarías en batch y cuáles en streaming, justificando por valor temporal y volumen.

**77.** A partir del dato «200 clics en comprar», construí una secuencia DIKW completa que termine en una decisión empresarial. Explicá qué evidencia adicional necesitarías antes de ejecutar esa decisión.

**78.** Para un caso de detección de abandono de clientes, formulá una pregunta descriptiva, una diagnóstica, una predictiva, una prescriptiva y una decisiva. Indicá qué salida se espera de cada nivel.

**79.** Diseñá un mapa de responsabilidades para Data Engineer, Data Analyst, Data Scientist y Data Architect en un proyecto que integra datos de ventas y atención al cliente. Explicá cómo se coordinan.

**80.** Describí la evolución desde el Data Warehouse on-premise hacia Big Data, el Data Warehouse cloud y Data Mesh. Compará cómo cambian la arquitectura, la escalabilidad y la responsabilidad por los datos en cada etapa.

### Unidad II — Orígenes de Datos y Proceso ETL

**81.** Una organización necesita integrar ventas desde SQL Server, cotizaciones desde una API pública y precios publicados en una web. Diseñá la estrategia de extracción para cada fuente, contemplando conectores, autenticación, scraping ético, frecuencia, carga completa o incremental y manejo de fallos.

**82.** Proponé un flujo de transformación para un archivo de clientes que contiene nulos, duplicados, fechas en formatos distintos y monedas mezcladas. Indicá el orden de las operaciones, cómo validarías los resultados y qué decisiones no deberías tomar sin una regla de negocio.

**83.** Compará ETL y ELT para un escenario en el que los datos contienen información personal y el destino es un entorno cloud escalable. Recomendá un enfoque o una combinación y justificá la decisión en términos de privacidad, flexibilidad, costo y capacidad de transformación.

**84.** Diseñá la estrategia de carga para un destino analítico que recibe registros nuevos y correcciones de registros existentes. Explicá cuándo usarías overwrite, append o upsert y cómo probarías que la ejecución es idempotente.

**85.** Representá como DAG un pipeline diario de extracción, transformación, validación y carga. Explicá sus dependencias, programación, reintentos, logs, alertas al responsable y acciones ante un fallo de validación o una interrupción técnica.

### Unidad III — Calidad del Dato y Gobierno

**86.** Un conjunto de ventas contiene identificadores nulos y duplicados, precios negativos, monedas fuera del dominio permitido y fechas desactualizadas. Clasificá los problemas por dimensión de calidad y proponé una regla verificable para cada uno.

**87.** Diseñá un contrato de datos para una tabla de ventas que incluya restricciones sobre identificador, precio, moneda y fecha. Explicá cómo un proceso de profiling previo puede ayudar a definir reglas realistas y cómo reportarías su cumplimiento.

**88.** En un lote de 12 filas, 8 son rechazadas y se permite como máximo un 20% de rechazo. Describí qué debería hacer una puerta de publicación, qué evidencia conservarías y por qué no sería correcto publicar automáticamente las 4 filas válidas como si el lote original hubiera sido reparado.

**89.** Diseñá los metadatos mínimos de catálogo y linaje para seguir una métrica de ventas desde su fuente hasta un reporte. Incluí significado de campos, Owner, Steward, clasificación de privacidad, finalidad, transformaciones y limitaciones de una huella criptográfica.

**90.** Proponé un procedimiento de monitoreo e incidentes para un pipeline sujeto a cambios de esquema y rechazos de datos. Definí una métrica con denominador explícito, distinguí SLI, SLO y SLA, asigná responsabilidades y describí qué evidencia dejarías para un reintento o una excepción.

### Unidad IV — Data Warehouse y Modelado Dimensional

**91.** Para el proceso de ventas facturadas de WideWorldImporters, formulá preguntas de negocio, definí una granularidad precisa y construí una Bus Matrix inicial que relacione procesos con dimensiones conformadas. Justificá el alcance de un primer Data Mart.

**92.** Diseñá un esquema estrella de ventas con tabla de hechos, dimensiones y medidas. Explicá qué atributos ubicarías en cada dimensión, qué representa cada fila de la fact y cómo una consulta podría analizar ventas por tiempo, cliente, producto y ciudad.

**93.** Un cliente cambia de ciudad y un producto cambia de categoría. Para cada cambio, elegí entre SCD Tipo 1, 2 o 3 según distintos requisitos analíticos. Describí cómo registrarías vigencias y cómo resolverías NK a SK al cargar hechos históricos.

**94.** Compará las arquitecturas de Inmon y Kimball para una empresa que necesita integrar varias áreas, obtener resultados graduales y mantener definiciones analíticas consistentes. Presentá ventajas, costos o riesgos y una recomendación justificada.

**95.** Describí el flujo ETL para cargar `fact_ventas` desde un sistema transaccional: extracción de líneas de factura, carga de dimensiones, resolución de claves, tratamiento de filas sin SK válida, carga incremental y verificaciones de calidad, integridad y reconciliación.

### Unidad V — Arquitecturas Modernas y Proyecto Integrador

**96.** Diseñá una arquitectura Medallion para datos de ventas que llegan desde una API y un sistema transaccional. Indicá qué conservarías en Bronze, qué transformaciones y validaciones aplicarías en Silver, y qué productos generarías en Gold.

**97.** Un equipo detecta que una transformación publicada alteró datos históricos. Explicá cómo Delta Lake y Time Travel podrían ayudar en la investigación o recuperación, qué condiciones deben cumplirse y qué controles adicionales conservarías.

**98.** Una organización acumuló archivos heterogéneos en un Data Lake y los usuarios no saben qué significan ni si son confiables. Diagnosticá cómo se llegó a un data swamp y proponé controles de organización, metadatos, calidad, propiedad y acceso para prevenirlo.

**99.** Especificá el proyecto integrador de punta a punta para una fuente real: extracción, transformaciones, reglas de calidad, modelo dimensional en un DWH cloud, orquestación, observabilidad y presentación de resultados. Identificá entregables y criterios para demostrar que el pipeline es reproducible y confiable.

**100.** Diseñá una solución para un caso que combine reportes diarios y alertas de fraude en tiempo real. Explicá qué partes resolverías con batch y cuáles con Kafka/Flink, cómo integrarías DataOps o MLOps y qué pruebas aplicarías antes de poner el flujo en producción.
