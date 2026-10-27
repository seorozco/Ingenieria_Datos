# Trabajo Práctico - Unidad III

## Calidad y gobierno del dato: un pipeline de ventas confiable

**Asignatura:** Ingeniería de Datos  
**Unidad:** III - Calidad del Dato y Gobierno  
**Modalidad sugerida:** equipos de hasta 3 integrantes, con defensa individual  
**Dedicación estimada:** 8 a 12 horas por equipo  
**Entorno:** Python/Jupyter local, pandas y SQLite  
**Evaluación:** fundamentación teórica aplicada 20 puntos; implementación práctica 80 puntos

---

## 1. Situación de negocio

Una empresa recibe un lote de ventas para elaborar un reporte por producto y moneda. Antes de utilizarlo, necesita saber si los datos son adecuados, qué registros presentan problemas y quién debe intervenir para resolverlos.

El lote contiene datos faltantes, identificadores repetidos, fechas incorrectas, un producto sin correspondencia en el maestro y otros problemas. Además, incluye un correo de contacto que no es necesario para el reporte solicitado.

**Encargo:** construir una solución local que diagnostique la calidad, aplique reglas documentadas, separe registros problemáticos y decida si se puede publicar el lote. La solución debe registrar lo ocurrido, entregar una salida analítica sin correos y demostrar cómo se detecta y resuelve un incidente.

No se pide que todos los datos terminen aceptados. **Detectar un lote que debe bloquearse también es un resultado correcto.** Se evalúa la coherencia entre las reglas, las decisiones y las evidencias.

## 2. Objetivos de aprendizaje

- Aplicar las dimensiones de calidad al uso concreto de un conjunto de datos.
- Realizar profiling antes de decidir cómo transformar o corregir.
- Definir un contrato con responsables, reglas, acciones y condiciones de publicación.
- Implementar separación de filas aceptadas, rechazadas y hallazgos.
- Verificar una publicación mediante conteos y reconciliación por moneda.
- Documentar significado, procedencia y tratamiento de los datos.
- Aplicar minimización de datos personales y reconocer los límites de una simulación.
- Demostrar monitoreo, bloqueo y recuperación sin ocultar errores ni relajar reglas.

## 3. Entorno, datos y alcance

### 3.1 Herramientas

1. Utilizar Python/Jupyter y pandas, siguiendo los notebooks de la unidad.
2. Para la carga, utilizar `sqlite3` de la biblioteca estándar. Se permite una base en memoria; no se exige persistencia entre sesiones.
3. Para las comprobaciones, utilizar aserciones o `unittest`. No se exige instalar pytest, Great Expectations ni herramientas nuevas.
4. No se requieren SQL Server, Spark, Databricks, servicios cloud, Power BI ni acceso a APIs.
5. Se puede reutilizar código de los notebooks, indicando su procedencia y explicando las adaptaciones. No se acepta entregar únicamente los ejemplos de clase ejecutados sin trabajo propio.

Preparar el entorno según las [instrucciones del laboratorio](../../notebook/unidad_III/README.md). Las versiones y dependencias usadas deben quedar registradas en la entrega.

### 3.2 Datos de partida

Utilizar las ventas ficticias, el maestro de productos y la referencia parcial de importes generados por `crear_datos()` en [gobierno_demo.py](../../notebook/unidad_III/gobierno_demo.py). También se permite incorporar al notebook una copia identificada de esa función para que sea autocontenido.

No es necesario descargar archivos ni obtener datos externos. No modificar el módulo original ni los notebooks del repositorio.

El lote de ventas contiene:

- `fila_fuente`: identificador técnico de cada fila recibida.
- `id_venta`: identificador de negocio de la venta.
- `fecha_venta`: fecha declarada de la operación.
- `id_producto`: referencia al maestro de productos.
- `monto`: importe recibido como texto.
- `moneda`: moneda del importe.
- `email`: correo ficticio de contacto.
- `actualizado_en`: fecha y hora de actualización declarada por la fuente.

**Grano del ejercicio:** una fila aceptada por `id_venta`. No se trata de líneas de factura ni del modelo dimensional de la unidad IV. Los duplicados de negocio no deben confundirse con `fila_fuente`, que identifica cada fila de entrada.

La referencia de exactitud es parcial e independiente dentro del caso ficticio. No permite demostrar la exactitud de todo el lote.

### 3.3 Restricciones

- Usar exclusivamente datos ficticios y correos con dominio `.invalid`. No incorporar información personal real ni credenciales.
- Mantener una copia intacta de la entrada para comparar antes y después.
- Usar como fecha de corte fija `2026-10-06T12:00:00Z`, igual que en los ejemplos. No depender de la fecha del equipo.
- No sustituir importes o fechas inválidos por valores inventados para aprobar los controles.
- No borrar filas antes de medir la calidad ni excluirlas del denominador para mejorar indicadores.
- No se exige Data Warehouse, esquema estrella, SCD ni un orquestador. El foco es calidad y gobierno.

---

## 4. Parte A - Fundamentación teórica aplicada (20 puntos)

Responder en un informe de hasta 3 páginas, sin contar anexos. Cada respuesta debe referirse al caso y a resultados del trabajo.

| Pregunta | Puntos |
|---|---:|
| 1. Explicar las seis dimensiones trabajadas: completitud, exactitud, consistencia, unicidad, vigencia e integridad. Dar ejemplos del lote y distinguir un formato válido de un dato exacto. | 4 |
| 2. Diferenciar profiling, transformación y validación. Explicar por qué detectar un valor atípico no autoriza a eliminarlo y por qué una fila puede generar varios hallazgos. | 4 |
| 3. Distinguir calidad y gobierno. Asignar responsabilidades al Data Owner, Data Steward y custodio técnico, y explicar el papel estratégico del CDO. | 4 |
| 4. Diferenciar diccionario, catálogo y linaje usando los entregables propios. Explicar qué evidencia falta para afirmar la exactitud de todo el lote. | 4 |
| 5. Justificar por qué el correo no debe publicarse para este análisis. Distinguir minimización, enmascaramiento y seudonimización, sin afirmar que equivalen automáticamente a anonimización o cumplimiento legal. | 4 |

## 5. Parte B - Implementación práctica (80 puntos)

### Etapa 1. Profiling y diagnóstico

Antes de transformar:

1. Mostrar cantidad de filas, columnas y tipos recibidos.
2. Medir nulos, cadenas vacías y espacios en los campos relevantes, explicando cómo se consideran.
3. Identificar duplicados de negocio y mostrar las filas involucradas.
4. Relevar monedas, fechas que no pueden interpretarse, importes problemáticos y productos sin correspondencia.
5. Presentar un diagnóstico de al menos cinco problemas, con su impacto en el reporte.

Después de normalizar, comparar al menos tres campos con su versión original y explicar qué cambió. Conservar los valores recibidos para rastrear errores de conversión.

Realizar también una exploración de importes con IQR sobre valores numéricos positivos y separados por moneda. Mostrar el número de observaciones utilizado; si es insuficiente para una interpretación razonable, señalar esa limitación. No eliminar registros ni declararlos incorrectos únicamente por ser atípicos.

**Evidencia:** resumen de profiling, filas de ejemplo y conclusiones. No basta con mostrar `head()` o `describe()`.

### Etapa 2. Contrato y reglas de calidad

Crear un contrato legible en Markdown, diccionario Python o JSON con:

- nombre y finalidad del conjunto;
- versión, fecha de corte y responsables;
- campos esperados, tipos tras normalizar y obligatoriedad;
- clave de negocio y política de duplicados;
- reglas, acción ante incumplimiento y condición de publicación;
- clasificación del correo y criterio de acceso a la salida.

Implementar como mínimo:

1. Identificador de venta presente y convertible a entero positivo.
2. Unicidad de `id_venta`: poner en cuarentena **todas** las filas de cada clave repetida; no elegir una arbitrariamente.
3. Fecha de venta válida y no posterior a la fecha de corte.
4. Importe representable en centavos y mayor que cero.
5. Moneda dentro del dominio `ARS`, `USD` o `EUR`, después de normalizar.
6. Producto existente en el maestro.
7. Actualización válida, no futura y no anterior a la fecha de venta.
8. Formato de correo, como advertencia: no impide publicar una venta para este análisis.
9. Vigencia de la actualización dentro de 48 horas respecto del corte, como advertencia.
10. Comparación de importes con la referencia disponible, como advertencia y únicamente para las ventas evaluables.

Las reglas 1 a 7 generan cuarentena. Una fila puede incumplir más de una. La falta de referencia de exactitud debe informarse como **no evaluable**, no como acierto o error.

Agregar **una regla propia** pertinente y justificar su dimensión, condición y acción. Mostrar al menos un caso de prueba donde se cumpla y otro donde falle. Si modifica la clasificación del lote, explicar la diferencia respecto del ejemplo de clase.

La puerta de publicación permite un máximo de **20% de filas rechazadas**:

```text
tasa de rechazo = filas distintas en cuarentena / filas recibidas × 100
```

La tasa se calcula sobre todo el lote recibido, no solamente sobre las filas publicables. Si supera el umbral o el esquema es incompatible, se bloquea la publicación completa. En este TP, un lote vacío se registra como `SIN_DATOS` y no se publica; no se divide por cero ni se informa cumplimiento del 100%.

**El 20% es una decisión didáctica del caso, no una exigencia de DAMA ni de una norma.**

### Etapa 3. Evaluación, cuarentena y publicación controlada

Implementar un recorrido completo:

```text
Entrada conservada → comprobación de esquema → normalización
→ reglas y hallazgos → aceptadas/cuarentena → puerta de publicación
→ carga SQLite si corresponde → controles y resumen
```

Requisitos:

1. Registrar por hallazgo al menos `fila_fuente`, regla y acción. El valor observado puede conservarse en una salida restringida, evitando exponer correos en el reporte general.
2. Conservar las filas rechazadas y sus motivos, no solo el total.
3. Mostrar que `filas recibidas = filas aceptadas + filas en cuarentena`, sin contar varias veces una fila con múltiples fallos.
4. No cargar ventas de un lote bloqueado. Registrar igualmente su intento y motivo; preservar cualquier publicación anterior válida.
5. Para un lote habilitado, publicar únicamente las filas aceptadas, sin la columna `email`, y conservar claves para trazabilidad.
6. Repetir la carga habilitada sin duplicar ventas ni modificar sus importes. Definir explícitamente qué ocurre si llega el mismo `id_venta` con contenido diferente: bloquear el conflicto, sin sobrescribirlo silenciosamente.
7. Registrar lote, fecha de ejecución, versión del contrato, filas recibidas, aceptadas, rechazadas, publicadas y estado. En una recarga, distinguir registros ya existentes de inserciones nuevas.

Para importes, utilizar centavos enteros o `Decimal` en los cálculos; no basar una igualdad monetaria exacta en números de punto flotante.

**Reconciliación:** para un lote habilitado, comparar cantidades e importes aceptados contra sus registros correspondientes en SQLite, por moneda. No sumar ARS y USD como si fueran una única moneda ni comparar un subconjunto con todo el destino. Un lote bloqueado puede tener filas aceptadas, pero sus filas publicadas deben ser cero.

El lote original sirve para demostrar el diagnóstico y el bloqueo. Para demostrar una publicación habilitada, crear un escenario separado con datos ficticios válidos; no presentar ese escenario como una corrección real del lote original.

### Etapa 4. Gobierno, metadatos y privacidad

Entregar:

1. **Responsabilidades:** quién investiga un rechazo, quién autoriza cambios de contrato y quién ejecuta la corrección. Los roles del ejercicio son simulados.
2. **Diccionario:** todos los campos de la salida analítica, con significado, tipo, obligatoriedad, unidad cuando corresponda y regla asociada.
3. **Ficha de catálogo:** nombre del conjunto, finalidad, ubicación, responsable, frecuencia prevista y clasificación de acceso.
4. **Linaje por campo:** documentar el recorrido de al menos cinco campos, incluyendo el importe, la moneda y la clave. Identificar fuentes, transformaciones y destino.
5. **Minimización:** demostrar con una comprobación ejecutable que `email` no está en la tabla publicada ni en el reporte general.
6. **Matriz de acceso propuesta:** distinguir acceso del analista a la salida y del responsable de calidad a los rechazos. Aclarar que el notebook no implementa autenticación ni una barrera real de acceso.
7. **Conservación:** proponer un plazo para entradas, rechazos y auditoría, con justificación de negocio y sujeto a validación del Owner. No presentarlo como un plazo legal obligatorio.

No es obligatorio implementar HMAC ni cifrado. Si se agrega seudonimización, explicar sus límites y no guardar o imprimir secretos.

### Etapa 5. Monitoreo e incidente

Preparar escenarios separados y reproducibles sobre copias de los datos:

| Escenario | Comportamiento que debe demostrarse |
|---|---|
| Lote original | Diagnóstico completo y decisión de la puerta coherente con la tasa de rechazo. |
| Lote de prueba habilitado | Publicación sin correo, reconciliación y recarga sin duplicados. |
| Degradación del lote habilitado | Introducir suficientes errores para superar el 20%, registrar el bloqueo y mantener intacta la publicación anterior. |
| Recuperación | Restaurar los valores de prueba respaldados antes de la degradación; reevaluar con el mismo contrato y comprobar el resultado sin duplicar registros. |
| Deriva de esquema | Quitar o renombrar una columna requerida; detectar y registrar el problema antes de transformar o cargar. |
| Lote vacío | Registrar `SIN_DATOS` sin publicar ni producir porcentajes engañosos. |

Para el incidente de degradación, registrar: identificador, escenario/lote, problema, impacto, responsable, acción aplicada, evidencia antes y después y estado final.

La recuperación de este escenario no corrige automáticamente las filas defectuosas originales ni resuelve la deriva de esquema. No cerrar incidentes distintos como si fueran uno solo. No cambiar el umbral ni desactivar reglas para obtener una recuperación aparente.

---

## 6. Pruebas mínimas y evidencia

Incluir aserciones o pruebas ejecutables que comprueben:

- Conservación del volumen al separar aceptadas y cuarentena.
- Duplicados de negocio completos en cuarentena.
- Exactitud calculada únicamente sobre registros con referencia, mostrando también su cobertura.
- Bloqueo del lote degradado sin cambios en las ventas publicadas.
- Ausencia de correo en la salida analítica.
- Unicidad en SQLite después de repetir una carga.
- Reconciliación de importes por moneda.
- Detección de deriva antes de cargar.
- Recuperación con la misma versión de contrato y umbral.
- Tratamiento explícito del lote vacío.
- Casos válido e inválido de la regla propia.
- Conflicto de contenido para una clave existente, sin sobrescritura silenciosa ni carga parcial del intento.

Las pruebas se realizan en un entorno propio. Si la base funciona en memoria, documentar que datos, hallazgos y auditoría se pierden al cerrar la conexión. No se exige conservarlos entre ejecuciones del notebook; el recorrido completo debe poder reconstruirse desde cero.

Para cada prueba, mostrar qué se comprueba y el resultado. Una excepción prevista debe verificarse y explicarse; un traceback inesperado no constituye una prueba aprobada.

## 7. Entrega

Cada equipo entregará una carpeta identificada con sus integrantes, que contenga:

- **Informe:** Parte A, diagnóstico, decisiones, responsabilidades, incidente y conclusiones. Los anexos pueden contener contrato y metadatos.
- **Notebook principal:** ejecutable de principio a fin, con salidas de una ejecución completa, escenarios identificados y pruebas.
- **Contrato y documentación:** reglas, diccionario, ficha de catálogo, linaje y matriz de acceso; pueden estar dentro del informe o notebook si son fáciles de localizar.
- **Instrucciones de ejecución:** dependencias utilizadas, orden, fecha de corte, forma de generar los datos y reiniciar el entorno. Incluir cualquier módulo propio necesario.
- **Resumen final:** tres hallazgos sustentados, dos limitaciones y dos mejoras priorizadas.

No se aceptan solamente capturas, salidas sin código o una copia sin adaptación de los notebooks. No entregar entornos virtuales, secretos ni datos personales reales.

**Aporte propio obligatorio:** regla adicional, escenarios controlados con evidencia, documentación de gobierno aplicada y conclusiones. Cada integrante debe poder explicar una regla, su denominador, una decisión de publicación y una limitación del trabajo.

## 8. Rúbrica de evaluación

| Componente | Puntos | Evidencia para obtener el puntaje completo |
|---|---:|---|
| Fundamentación teórica aplicada | 20 | Respuestas relacionadas con el caso y las evidencias, conforme a la Parte A. |
| Profiling y diagnóstico | 12 | Entrada conservada, mediciones interpretadas, problemas identificados e IQR con sus límites. |
| Contrato y reglas | 18 | Reglas implementadas, acciones coherentes, regla propia probada, denominadores y no evaluables explícitos. |
| Cuarentena, publicación y reconciliación | 20 | Puerta correcta, rechazos trazables, publicación sin duplicados, conflictos controlados y comparación monetaria por moneda. |
| Gobierno, metadatos y privacidad | 14 | Roles, diccionario, catálogo, linaje, minimización comprobada y límites de acceso/conservación explicados. |
| Monitoreo y recuperación | 10 | Escenarios reproducibles, bloqueo sin alterar la publicación e incidente recuperado sin relajar controles. |
| Reproducibilidad y conclusiones | 6 | Ejecución completa desde cero, pruebas, instrucciones y conclusiones sustentadas. |
| **Total** | **100** | **20 teóricos + 80 prácticos.** |

Se asigna puntaje completo cuando se presentan todas las evidencias del componente, parcial cuando hay omisiones identificadas y cero cuando no se entrega o no puede demostrarse.

**Condiciones mínimas de logro práctico:** evaluación real de datos, cuarentena con motivos, puerta de publicación verificable, salida sin correo, reconciliación y al menos un bloqueo con recuperación comprobada. El umbral numérico de aprobación se rige por la normativa de la asignatura.

## 9. Material de referencia

- [Objetivos de la Unidad III](../../documentacion/unidad_03_calidad_del_dato_y_gobierno/00%20-%20Objetivos%20de%20la%20Unidad.md).
- [Calidad del dato: dimensiones y profiling](../../documentacion/unidad_03_calidad_del_dato_y_gobierno/07%20-%20Calidad%20del%20Dato%20-%20Las%206%20Dimensiones%20y%20Data%20Profiling.md).
- [Gobierno y gestión de metadatos](../../documentacion/unidad_03_calidad_del_dato_y_gobierno/08%20-%20Gobierno%20del%20Dato%20y%20Gesti%C3%B3n%20de%20Metadatos.md).
- [Manual de gobierno, calidad y DAMA](../../manueles/gobierno_del_dato/01_manual_gobierno_calidad_y_DAMA.md).
- [Guía del laboratorio y alcance de los ejemplos](../../notebook/unidad_III/README.md).
- Notebooks de clase: [profiling](../../notebook/unidad_III/01_profiling_y_dimensiones_clase.ipynb), [contrato](../../notebook/unidad_III/02_contrato_y_reglas_calidad_clase.ipynb), [ETL y cuarentena](../../notebook/unidad_III/03_etl_gobernado_y_cuarentena_clase.ipynb), [metadatos y privacidad](../../notebook/unidad_III/04_metadatos_linaje_y_privacidad_clase.ipynb) y [monitoreo e incidentes](../../notebook/unidad_III/05_monitoreo_e_incidentes_clase.ipynb).
- [Clase de repaso: pipeline confiable](../../documentacion/Clase%20de%20repaso%20-%20Pipeline%20confiable.md).

**Recorrido esperado:** finalidad → profiling → contrato → validaciones → cuarentena → decisión de publicación → reconciliación → metadatos y protección → monitoreo y recuperación.
