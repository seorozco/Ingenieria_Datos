# Clase de repaso: del dato al análisis
## Cómo diseñar un pipeline confiable

> **Asignatura:** Ingeniería de Datos  
> **Docente:** Ing. Sergio Orozco  
> **Duración sugerida:** 120 minutos  
> **Modalidad:** repaso dialogado, trabajo en grupos y puesta en común

---

## Propósito de la clase

Integrar los contenidos de la materia mediante el diseño de un pipeline que lleva datos desde una fuente operacional hasta un modelo listo para análisis. La clase prioriza el criterio y la comprensión del proceso: no se busca construir una solución compleja ni usar una herramienta nueva.

La pregunta que guía la clase es:

> **¿Cómo sabemos que los datos que llegan a un reporte son útiles, completos y confiables?**

---

## Objetivos de aprendizaje

Al finalizar la clase, el estudiante podrá:

- describir el recorrido de los datos desde una necesidad de negocio hasta su consumo analítico;
- diferenciar extracción, almacenamiento de entrada, transformación, carga y publicación;
- proponer controles básicos de calidad y reconciliación;
- explicar por qué un modelo para análisis puede diferir del modelo del sistema transaccional;
- identificar qué información conviene registrar para entender una ejecución y sus errores.

---

## Contenidos que se integran

- Fuentes y tipos de datos.
- ETL/ELT: extracción, transformación y carga.
- Calidad del dato y reglas de validación.
- Gobierno, responsabilidades, metadatos y trazabilidad.
- Data Warehouse y modelado dimensional.
- Carga incremental, errores, monitoreo y reconciliación.

---

## Materiales

- Pizarra o herramienta para dibujar diagramas.
- La consigna del caso incluida en este documento.
- Opcional: proyector para mostrar el esquema del pipeline.

No se requiere instalar herramientas ni programar durante la clase.

---

## Repaso de conceptos básicos

Este repaso recupera los puntos centrales de las cuatro unidades y los relaciona con un mismo ejemplo: las ventas de una empresa. La intención no es memorizar definiciones, sino entender para qué sirve cada concepto y en qué decisión del pipeline interviene.

**Orientación docente:** dedicar aproximadamente 40 minutos a esta sección, intercalando las preguntas de cada unidad. Reservar el tiempo restante para presentar el caso, diseñar el pipeline y discutir las soluciones. Si la clase dura 90 minutos, seleccionar los conceptos que generen más dudas y dejar el resto como material de consulta.

### Unidad I — Fundamentos e inteligencia de datos

#### Dato, información y conocimiento

Un **dato** es un valor registrado, como una fecha, una cantidad o un precio. Aislado, puede decirnos poco: el valor `12500` no indica qué se midió, en qué moneda ni en qué momento.

La **información** aparece cuando organizamos los datos y les damos contexto: “el importe de esta venta es de 12.500 pesos”. El **conocimiento** permite interpretar esa información: al comparar periodos, podemos reconocer qué productos crecen en ventas. La decisión de negocio requiere además considerar objetivos, costos y otras evidencias; no surge automáticamente de acumular datos.

Los niveles de análisis responden preguntas diferentes: el descriptivo explica **qué pasó**; el diagnóstico busca **por qué pasó**; el predictivo estima **qué podría pasar**; el prescriptivo propone **qué convendría hacer**; y el decisivo, en el enfoque trabajado en la materia, conecta el análisis con decisiones o acciones automatizadas bajo reglas y controles.

#### El rol de la ingeniería de datos y el ciclo de vida

La **ingeniería de datos** diseña y mantiene los procesos que permiten obtener, integrar, almacenar y entregar datos utilizables. No se limita a copiar archivos: debe asegurar que los datos lleguen a tiempo, mantengan su significado y puedan verificarse.

El ciclo de vida incluye la generación o captura, el almacenamiento, el procesamiento, el uso y, cuando corresponde, el archivo o la eliminación. En el caso de ventas, comienza cuando se registra una operación y continúa cuando esa operación alimenta un reporte. Conservar datos indefinidamente no siempre es necesario ni está permitido.

#### Tipos y fuentes de datos

Los datos **estructurados** siguen un esquema definido, como una tabla de ventas. Los **semiestructurados** tienen una organización flexible, como una respuesta JSON de una API. Los **no estructurados**, como imágenes o textos libres, no se presentan directamente como filas y columnas.

Las fuentes pueden ser internas —un sistema de ventas o un ERP— o externas —una API pública o un archivo de un proveedor—. Conocer la fuente ayuda a decidir cómo extraer, interpretar y actualizar los datos. Que un archivo se pueda abrir no significa que comprendamos sus campos.

#### Batch, streaming y Big Data

El procesamiento **batch** trabaja con conjuntos de registros en determinados momentos; por ejemplo, las ventas del día anterior. El **streaming** procesa eventos de forma continua o con baja latencia. No es mejor por definición: si el reporte se consulta una vez por día, una carga diaria puede ser suficiente.

Las **4V** recuerdan que los desafíos no dependen solo de la cantidad de datos: importan el volumen, la velocidad de generación, la variedad de formatos y la veracidad o confiabilidad. La solución debe responder a esas necesidades, no a la herramienta de moda.

> **Para conversar:** si la gerencia revisa un reporte cada mañana, ¿qué justificaría actualizarlo cada segundo?

### Unidad II — Orígenes de datos y proceso ETL

#### Bases de datos, OLTP y OLAP

Una base **relacional** organiza datos en tablas relacionadas y permite definir restricciones. Las bases **NoSQL** incluyen distintos modelos, como documentos, clave-valor o grafos. La elección depende del uso y las necesidades; NoSQL no significa ausencia de estructura o de controles.

**OLTP** se orienta a operaciones cotidianas: registrar una venta, modificar un cliente o actualizar existencias. **OLAP** se orienta al análisis: comparar ventas mensuales, agrupar productos o consultar tendencias históricas. Separar estas necesidades permite diseñar estructuras adecuadas y evitar que consultas analíticas pesadas interfieran con la operación.

#### Pipeline, ETL y ELT

Un **pipeline** es una secuencia organizada de tareas que lleva los datos desde su origen hasta un destino útil. Puede incluir extracción, validación, transformación, carga y publicación.

En **ETL**, se extraen los datos, se transforman y se cargan al destino analítico. En **ELT**, se extraen y cargan primero, y las transformaciones se realizan en la plataforma de destino. La diferencia es dónde y cuándo se transforma, no que un enfoque tenga controles de calidad y el otro no.

#### Extracción completa e incremental

La extracción **completa** obtiene todo el conjunto definido. Es sencilla de entender, pero puede resultar costosa cuando crece el volumen. La **incremental** busca los registros nuevos o modificados desde un punto de control.

Extraer únicamente las ventas de ayer sirve si ese es el alcance acordado, pero no detecta necesariamente una corrección hecha hoy sobre una venta antigua. Por eso hay que conocer cómo informa cambios la fuente. El punto de control debe avanzar solo cuando la carga correspondiente se haya completado correctamente.

#### Transformaciones, formatos y zona de entrada

Transformar puede significar convertir fechas, normalizar nombres, unir ventas con productos, calcular importes o agregar resultados. Una transformación debe tener una regla explicable: reemplazar un importe faltante por cero puede ocultar un problema y modificar los totales.

CSV, JSON y Parquet son formatos, no equivalentes de calidad. CSV es sencillo para intercambiar tablas; JSON representa estructuras flexibles; Parquet es columnar y útil para muchas consultas analíticas. Ningún formato evita por sí solo los duplicados o los valores incorrectos.

La zona **staging** permite recibir y preparar datos antes de cargarlos al modelo analítico. Si se necesita recuperar exactamente lo recibido, debe conservarse una copia de entrada sin sobrescribirla durante la transformación.

#### Estrategias de carga y orquestación

En una carga por **reemplazo**, se sustituye el conjunto de destino definido. **Append** agrega filas, por lo que repetir un lote puede duplicarlas. **Upsert** inserta registros nuevos y actualiza los existentes usando una clave acordada. Su elección depende del significado de los datos y de cómo deben tratarse los cambios.

La **orquestación** coordina el orden, las dependencias y la ejecución de tareas. Un DAG representa tareas y dependencias sin ciclos. Por ejemplo, la carga de hechos puede depender de que las dimensiones estén listas. El orquestador organiza el proceso, pero no garantiza que los importes sean correctos.

> **Para conversar:** si se ejecuta dos veces la carga del mismo día, ¿qué debería ocurrir y qué estrategia ayudaría a conseguirlo?

### Unidad III — Calidad del dato y gobierno

#### Profiling y dimensiones de calidad

El **profiling** es una exploración para conocer los datos antes de decidir cómo tratarlos. Permite revisar tipos, nulos, duplicados, rangos y valores frecuentes. Encontrar una cantidad negativa, por ejemplo, exige averiguar si es un error o una devolución válida.

Las dimensiones trabajadas en la materia permiten evaluar distintos aspectos:

- **Completitud:** están presentes los datos requeridos, como el identificador de venta.
- **Exactitud:** los valores reflejan la realidad; requiere una referencia confiable para comprobarlo.
- **Consistencia:** no existen contradicciones entre campos o sistemas que deberían coincidir.
- **Unicidad:** no hay registros repetidos para la clave y granularidad definidas.
- **Vigencia:** los datos están suficientemente actualizados para el uso previsto.
- **Integridad:** se mantienen las relaciones y restricciones, como la correspondencia entre una venta y un producto.

Que una fecha tenga un formato válido no demuestra que sea la fecha real de la venta. Cada control aporta evidencia sobre un aspecto, no sobre toda la calidad del conjunto.

#### Reglas, contrato de datos y cuarentena

Una **regla de calidad** expresa una condición verificable. Un **contrato de datos** reúne acuerdos sobre el esquema, significado, responsables y condiciones de uso o publicación. También debe quedar claro qué ocurre cuando no se cumplen las condiciones.

La **cuarentena** separa registros problemáticos para investigarlos sin mezclarlos con los publicados. No equivale a eliminarlos ni a corregirlos: debe conservarse evidencia del motivo del rechazo. Si el problema afecta la confiabilidad del lote completo, puede ser necesario bloquear la publicación.

Las métricas deben indicar su denominador. “Se rechazó el 10%” es incompleto si no se aclara el total evaluado. Además, una fila puede incumplir varias reglas: cantidad de hallazgos y cantidad de filas rechazadas no son lo mismo.

#### Gobierno, roles y protección

El **gobierno del dato** establece responsabilidades y criterios para que los datos se administren de forma coherente. El **Data Owner** responde por su uso y decisiones; el **Data Steward** coordina definiciones y calidad; el equipo técnico o custodio implementa y opera los controles.

Los datos personales requieren un tratamiento acorde con su finalidad y las políticas aplicables. Para analizar ventas por producto, tal vez no haga falta publicar el correo del cliente. La minimización consiste en usar solo lo necesario, y los permisos deben limitar el acceso según las responsabilidades.

#### Metadatos, linaje y monitoreo

Los **metadatos** describen los datos: qué significa un campo, qué tipo tiene, quién es responsable y cuándo se actualiza. Un diccionario detalla campos y definiciones; un catálogo facilita encontrar conjuntos de datos y conocer sus características.

El **linaje** explica de dónde proviene un dato y qué transformaciones atravesó. El **monitoreo** observa las ejecuciones y los resultados para detectar problemas, como una reducción inesperada de registros o un cambio de esquema. Resolver un incidente exige comprobar la recuperación, no solamente volver a ejecutar el proceso.

> **Para conversar:** si se publican solo las ventas aceptadas, ¿ya quedó resuelto el problema de las ventas rechazadas?

### Unidad IV — Data Warehouse y modelado dimensional

#### Data Warehouse, Data Mart y Data Lake

Un **Data Warehouse** integra datos orientados al análisis, con contexto histórico y definiciones coherentes. Sus características clásicas son estar orientado a temas, integrado, ser variante en el tiempo y no volátil. Esto último expresa que no se usa como un sistema transaccional cotidiano; no impide realizar correcciones controladas.

Un **Data Mart** se enfoca en un área o proceso, como ventas. Un **Data Lake** permite almacenar datos de distintos formatos y niveles de preparación. Un **Lakehouse** combina almacenamiento de tipo lake con capacidades de gestión de tablas y análisis. Estas alternativas requieren gobierno: guardar muchos archivos no produce automáticamente información confiable.

#### Inmon y Kimball

El enfoque **Inmon** parte de un modelo empresarial integrado, habitualmente normalizado, del que se derivan estructuras de consumo. El enfoque **Kimball** construye modelos dimensionales por procesos de negocio y los integra mediante dimensiones conformadas, es decir, compartidas con definiciones compatibles.

Ambos buscan coherencia analítica. La decisión no consiste en elegir un nombre, sino en considerar necesidades, alcance y posibilidades del proyecto. En el caso de la clase, un Data Mart dimensional de ventas permite trabajar con un alcance concreto.

#### Granularidad, hechos y dimensiones

La **granularidad** establece qué representa exactamente una fila. Para evitar ambigüedades, podemos definirla como **una fila por línea de factura**, identificada por la factura y su número de línea. Un mismo producto podría aparecer en más de una línea de la misma factura.

La tabla de **hechos** contiene las claves del contexto y medidas, como cantidad e importe de esa línea. Las **dimensiones** describen fecha, cliente y producto. El **esquema estrella** relaciona directamente los hechos con las dimensiones; el copo de nieve divide algunas dimensiones en tablas relacionadas.

No todas las medidas se suman de la misma manera. El importe de líneas puede agregarse si se mantiene la misma moneda y definición; un porcentaje de margen no debe sumarse. Tampoco contar líneas equivale a contar facturas: para estas últimas hay que identificar facturas distintas.

#### Claves e historia: SCD

Una **clave natural** identifica una entidad en el negocio o sistema origen, como el código de cliente. Una **clave sustituta** identifica una fila de dimensión en el modelo analítico. Permite, entre otras cosas, representar varias versiones históricas de un mismo cliente.

Las **Slowly Changing Dimensions (SCD)** resuelven cómo tratar cambios en atributos:

- **Tipo 1:** sobrescribe el valor y no conserva su historia en ese atributo.
- **Tipo 2:** agrega una nueva versión con su periodo de vigencia.
- **Tipo 3:** conserva el valor actual y un valor anterior en columnas específicas.

Si un cliente cambia de categoría, debemos decidir si una venta antigua se analiza con su categoría histórica o con la actual. Con SCD tipo 2, la carga debe asociar el hecho con la versión que corresponda a la fecha de la venta.

#### Reconciliación y publicación para BI

La **reconciliación** compara origen y destino con el mismo alcance y las mismas definiciones. No basta con comparar dos totales si uno incluye impuestos y el otro no, o si corresponden a periodos distintos.

En un lote sin duplicados de entrada, si cada línea se acepta o se rechaza una sola vez, debe cumplirse: **líneas recibidas = líneas aceptadas + líneas rechazadas**. Los importes se comparan sobre conjuntos equivalentes; los rechazos y otras diferencias deben quedar explicados.

Finalmente, un KPI necesita una definición compartida. Por ejemplo, el ticket promedio puede calcularse como importe total dividido por cantidad de facturas distintas, no por cantidad de líneas. Publicar datos para BI significa entregar resultados que puedan interpretarse y verificarse, no solo una tabla disponible.

> **Para conversar:** una factura tiene tres líneas. ¿Cuántas filas aporta a la tabla de hechos y cuántas facturas aporta al cálculo del ticket promedio?

### Conexión entre las unidades

La Unidad I ayuda a comprender **para qué y con qué datos trabajamos**. La Unidad II explica **cómo los movemos y preparamos**. La Unidad III establece **cómo los controlamos y quién responde por ellos**. La Unidad IV organiza **cómo conservarlos y consultarlos para analizar el negocio**.

Un pipeline confiable reúne esas cuatro miradas: propósito, procesamiento, controles y consumo.

### Preguntas para activar conocimientos previos

1. ¿Qué diferencia hay entre el sistema que registra una venta y el que la analiza?
2. ¿Qué significa ETL? ¿En qué se diferencia de ELT?
3. ¿Qué problemas de calidad podrían impedir usar una venta en un reporte?
4. ¿Qué representa una fila de la tabla de hechos del caso?
5. ¿Cómo podríamos saber si la carga diaria quedó completa?

No es necesario resolver todas las preguntas en profundidad en esta etapa. Se retoman durante el diseño del pipeline.

---

## Caso práctico: ventas diarias

Una empresa quiere analizar sus ventas por fecha, cliente y producto. Los datos se originan en su sistema de ventas. Cada día necesita incorporar las ventas nuevas, controlar registros problemáticos y dejar disponible información confiable para los reportes.

Para este ejercicio, considerar que:

- una venta puede contener varios productos;
- cada registro de detalle representa un producto vendido dentro de una venta;
- puede haber registros con datos faltantes, fechas inválidas o referencias a productos inexistentes;
- el reporte requiere consultar ventas por periodo, cliente y producto.

### Pregunta para los grupos

> Diseñen el recorrido de los datos desde el sistema de ventas hasta el reporte. Incluyan qué se valida, qué ocurre ante errores y cómo se comprueba que la carga es correcta.

---

## El recorrido de un pipeline confiable

```text
Necesidad de negocio
        ↓
Fuente de datos
        ↓
Extracción
        ↓
Staging / datos recibidos
        ↓
Transformación y controles de calidad
        ↓
Carga al modelo analítico
        ↓
Reconciliación y publicación
        ↓
Reportes y seguimiento
```

### 1. Definir la necesidad y el nivel de detalle

Antes de construir el pipeline, aclarar qué preguntas de negocio se quieren responder y qué representa cada fila.

En este caso, la granularidad de la tabla de hechos es **una fila por línea de factura**, identificada por la factura y su número de línea. Si la granularidad no queda clara, pueden mezclarse cantidades, importes y conteos que no representan lo mismo.

### 2. Identificar la fuente y entender los datos

Determinar qué sistema entrega la información, qué campos contiene, con qué frecuencia cambian y quién puede explicar su significado. Revisar ejemplos y detectar dependencias con otras entidades, como clientes y productos.

### 3. Extraer los datos

Obtener los registros necesarios desde la fuente, ya sea mediante una carga completa o una carga incremental. La estrategia depende del volumen, la frecuencia y las capacidades del sistema origen.

La extracción debe permitir responder: **qué periodo o conjunto de datos se solicitó y qué cantidad de registros se recibió**.

### 4. Conservar los datos recibidos

Guardar los datos de entrada en una zona de staging antes de modificarlos. Esto permite revisar qué llegó y separar los problemas de origen de los errores introducidos por las transformaciones.

### 5. Transformar y aplicar controles

Estandarizar tipos y formatos, preparar las claves y aplicar reglas de calidad. Para el caso, algunas reglas podrían ser:

- la fecha de venta debe ser válida;
- la cantidad debe ser mayor que cero;
- el identificador de producto debe corresponder a un producto conocido;
- los campos necesarios para identificar la línea de venta no deben estar vacíos.

Una regla debe tener una acción definida: aceptar, advertir, poner en cuarentena o bloquear la publicación. No todos los errores requieren detener el lote completo.

### 6. Cargar el modelo analítico

Preparar los datos para las consultas de análisis. Una opción es una tabla de hechos de ventas relacionada con dimensiones de fecha, cliente y producto.

La estructura analítica facilita responder preguntas de negocio, aunque no sea idéntica a la estructura utilizada para registrar una venta en el sistema operacional.

### 7. Reconciliar y publicar

Antes de habilitar los datos para reportes, comprobar que el resultado tenga sentido. Por ejemplo:

- comparar la cantidad de líneas recibidas, aceptadas y rechazadas;
- comparar los importes de origen y destino para el mismo periodo;
- verificar que no haya claves de dimensión sin correspondencia;
- comprobar que la carga no haya agregado registros duplicados.

Las tolerancias y reglas deben ser acordes al caso y acordadas con los responsables del dato.

### 8. Registrar y monitorear la ejecución

Guardar información suficiente para entender qué pasó. Como mínimo:

- proceso y fecha de ejecución;
- periodo o lote procesado;
- cantidad de filas recibidas, cargadas y rechazadas;
- estado final;
- errores relevantes y ubicación de los registros en cuarentena.

La orquestación permite coordinar pasos y dependencias; no reemplaza las validaciones ni garantiza por sí sola que los datos sean correctos.

---

## Actividad grupal

**Duración:** 25 minutos  
**Organización:** grupos de 3 o 4 estudiantes

Cada grupo dibuja el pipeline del caso y responde:

1. ¿Qué necesita saber del negocio antes de empezar?
2. ¿Cuál es la granularidad de los datos que cargaría?
3. ¿Qué información conservaría en staging?
4. ¿Qué tres controles de calidad aplicaría?
5. ¿Qué haría con una fila inválida? ¿Y si el problema afecta a todo el lote?
6. ¿Cómo comprobaría que no faltaron registros ni se duplicaron ventas?
7. ¿Qué dimensiones y hechos necesita el reporte?
8. ¿Qué dejaría registrado para investigar una ejecución fallida?

Cada grupo prepara una explicación de hasta tres minutos. Se evalúa la justificación de las decisiones, no la cantidad de herramientas nombradas.

---

## Puesta en común: situaciones para discutir

Presentar una situación a la vez y pedir que los grupos indiquen qué parte del pipeline debería detectarla y qué acción proponen.

### Situación A: faltan identificadores de producto

- ¿Se puede cargar la venta sin asociarla a un producto?
- ¿La fila se rechaza, se pone en cuarentena o se asigna a una categoría desconocida?
- ¿Qué evidencia se conserva para resolver el problema?

### Situación B: el proceso terminó, pero cargó menos ventas que las recibidas

- ¿Alcanza con que el programa haya terminado sin errores?
- ¿Qué conteos o totales compararían?
- ¿Se publica el lote mientras se investiga la diferencia?

### Situación C: el mismo lote se procesa otra vez

- ¿Qué riesgo existe de duplicar información?
- ¿Cómo se puede detectar o evitar el duplicado?
- ¿Qué conviene registrar para identificar el lote?

---

## Síntesis: lista de revisión

Un pipeline está razonablemente bien planteado si:

- [ ] parte de una necesidad de negocio clara;
- [ ] define qué representa cada registro;
- [ ] identifica la fuente, su responsable y su frecuencia de actualización;
- [ ] conserva evidencia de los datos recibidos;
- [ ] transforma los datos de manera consistente;
- [ ] aplica reglas de calidad con acciones definidas;
- [ ] separa y registra los registros rechazados;
- [ ] verifica cantidades, claves y resultados antes de publicar;
- [ ] permite entender qué ocurrió durante cada ejecución;
- [ ] entrega un modelo adecuado para las consultas analíticas.

---

## Evaluación de salida

Antes de terminar, pedir a cada estudiante que responda individualmente:

1. ¿Qué validación considerarías indispensable para el caso de ventas y por qué?
2. ¿Qué diferencia hay entre que un pipeline termine correctamente y que sus datos sean confiables?
3. ¿Qué comprobación harías antes de publicar los datos para los reportes?

### Criterio de logro

Se considera alcanzado el objetivo si el estudiante puede describir el flujo completo y justificar al menos un control de calidad y una comprobación de reconciliación.

---

## Cierre docente

La idea central para cerrar la clase es:

> **Un pipeline no es confiable solo porque termina sin errores. Es confiable cuando entrega datos adecuados para el propósito, permite verificar sus resultados y hace visibles los problemas.**

La ingeniería de datos conecta las fuentes con el uso analítico. Para hacerlo bien, no alcanza con mover datos: hay que comprender qué significan, definir cómo se controlan y dejar evidencia de lo que ocurrió.
