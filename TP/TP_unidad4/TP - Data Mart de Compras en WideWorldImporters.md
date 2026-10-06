# Trabajo Practico - Unidad IV

## Data Mart a eleccion sobre WideWorldImporters

**Asignatura:** Ingenieria de Datos  
**Base de origen:** SQL Server - `WideWorldImporters` (OLTP)  
**Destino sugerido:** `WideWorldImportersDW2`, esquema `dw`  
**Modalidad sugerida:** equipos de hasta 3 integrantes, con defensa individual  
**Dedicacion estimada:** 12 a 16 horas por equipo  
**Evaluacion:** teoria aplicada 20 puntos; implementacion practica 80 puntos

---

## 1. Situacion de negocio

Wide World Importers ya dispone de un Data Mart de ventas. La empresa solicita ampliar el Data Warehouse para analizar otro proceso de negocio que cada equipo debera seleccionar y justificar.

Actualmente, las consultas requieren combinar transacciones y maestros del sistema operativo. Se necesita un modelo dimensional que responda preguntas concretas del area elegida y permita analizar indicadores con trazabilidad hacia el origen.

**Encargo:** elegir un proceso disponible en `WideWorldImporters`, disenar, crear y poblar una nueva tabla de hechos `dw.fact_<proceso>` y todas las dimensiones necesarias. Cada equipo puede elegir la fact que prefiera, siempre que los datos de origen permitan sostener su grano y sus indicadores. No se acepta renombrar `fact_ventas` ni entregar solamente consultas sobre la base OLTP.

**Ejemplo de referencia:** se conserva el caso `dw.fact_compras`, desarrollado en la seccion 5B, para mostrar el nivel de detalle esperado. Se puede elegir Compras u otro proceso; no es obligatorio usar ese nombre, esas dimensiones, esas medidas ni sus pruebas especificas. Los requisitos comunes de la seccion 5A y la rubrica se aplican a todas las elecciones.

La fuente de datos es exclusivamente la base restaurada `WideWorldImporters`. **No se entregan ni se requieren CSV, Excel ni otros archivos de entrada.** Los casos de prueba se construyen a partir de registros reales extraidos de esa base, dentro de un staging aislado.

## 2. Objetivos de aprendizaje

- Aplicar los cuatro pasos del modelado dimensional de Kimball.
- Definir una granularidad consistente y medidas con significado de negocio.
- Construir dimensiones con NK, SK, atributos descriptivos y reglas SCD.
- Integrar el proceso elegido y Ventas mediante dimensiones conformadas cuando corresponda.
- Implementar un ETL reproducible con inserciones, actualizaciones y trazabilidad.
- Validar integridad, idempotencia y reconciliacion contra el origen.
- Convertir los datos cargados en indicadores y conclusiones de negocio.

## 3. Entorno, alcance y restricciones

1. Trabajar con SQL Server y Python/Jupyter, siguiendo los patrones de `pandas`, `sqlalchemy` y `pyodbc` utilizados en clase. El DDL y las consultas deben ser T-SQL.
2. Usar el origen con permisos de lectura. **No modificar tablas ni datos de `WideWorldImporters`.** Las pruebas se realizan en staging o en una base de pruebas propia.
3. Utilizar un destino propio por equipo o uno asignado por el docente. No borrar ni reemplazar dimensiones compartidas o `dw.fact_ventas`.
4. Parametrizar servidor, bases, periodo y fecha efectiva de prueba. No entregar contrasenas ni credenciales en archivos o salidas del notebook.
5. Relevar el rango real de la fecha del proceso elegido; no asumir que la base contiene datos del anio actual. Para procesos con historia, seleccionar al menos 12 meses consecutivos con datos, o todo el periodo disponible si es menor. Si solo existe un estado actual, documentar la fecha de corte y no inventar historia.
6. Registrar version de SQL Server, variante de WWI, volumen fuente y periodo utilizado. Verificar tablas, columnas, tipos y relaciones con `sys.tables`, `sys.columns` y `sys.foreign_keys` antes de programar.
7. No usar la base de ejemplo `WideWorldImportersDW` como origen ni copiar sus tablas de hechos ya construidas.

Cada equipo debe delimitar que eventos o estados representa su fact y que queda fuera del alcance. La eleccion debe sustentarse en tablas, relaciones y fechas verificadas en su instalacion de WWI; no se requieren fuentes externas.

---

## 4. Parte A - Fundamentacion teorica aplicada (20 puntos)

Responder en un informe de hasta 3 paginas, con ejemplos del modelo construido. No se evaluan definiciones copiadas sin relacion con el caso.

| Pregunta | Puntos |
| --- | ---: |
| 1. Explicar por que el proceso elegido necesita un Data Mart separado del OLTP. Relacionar el caso con las cuatro caracteristicas de Inmon y distinguir no volatilidad de las actualizaciones controladas de un snapshot acumulado. | 4 |
| 2. Justificar una topologia Bus Kimball frente a un EDW normalizado de Inmon. Incorporar una Bus Matrix con Ventas y el proceso elegido, distinguiendo dimensiones compartidas de las especificas. | 4 |
| 3. Comparar fact transaccional, snapshot periodico y snapshot acumulado. Justificar el tipo elegido para este encargo y explicar que analisis no permite. | 4 |
| 4. Explicar NK, SK, dimensiones conformadas y dimensiones con multiples roles de fecha. Justificar estrella frente a copo de nieve en este caso. | 4 |
| 5. Comparar SCD1, SCD2 y SCD3 con ejemplos del proceso elegido. Clasificar las medidas del TP y explicar por que no se deben sumar precios ni promediar porcentajes sin considerar su denominador. | 4 |

## 5A. Parte B - Requisitos comunes de implementacion (80 puntos)

### Eleccion del proceso

Las siguientes opciones son orientativas; se permite cualquier otro proceso viable en WWI:

| Opcion | Fact posible | Fuentes a investigar | Aspecto a justificar |
| --- | --- | --- | --- |
| Compras y recepciones | `dw.fact_compras` | `Purchasing.PurchaseOrders`, `Purchasing.PurchaseOrderLines` | Estado acumulado por linea; caso desarrollado en la seccion 5B. |
| Pedidos de clientes | `dw.fact_pedidos` | `Sales.Orders`, `Sales.OrderLines` | Linea de pedido y medidas de demanda; no confundir pedido con venta facturada. |
| Movimientos de inventario | `dw.fact_movimientos_stock` | `Warehouse.StockItemTransactions` | Un movimiento por fila; analizar signos y tipos antes de sumar cantidades. |
| Transacciones de clientes | `dw.fact_transacciones_clientes` | `Sales.CustomerTransactions` | Una transaccion por fila; distinguir cargos, pagos y saldo pendiente. |
| Transacciones de proveedores | `dw.fact_transacciones_proveedores` | `Purchasing.SupplierTransactions` | Una transaccion por fila; definir signos y evitar mezclar compras, facturas y pagos. |
| Estado de inventario | `dw.fact_inventario` | `Warehouse.StockItemHoldings`, `Warehouse.StockItems` | Snapshot por producto y fecha de corte. El estado actual no permite reconstruir por si solo el inventario historico. |

Presentar una ficha de propuesta antes de implementar: proceso y usuario destinatario, nombre de fact, frase de grano, tipo de fact, fuentes verificadas, dimensiones, medidas, fecha de referencia, periodo o corte disponible y limitaciones. La eleccion es libre dentro de estos requisitos; no debe reproducir sin cambios el caso de ventas de los notebooks.

### Entregables tecnicos comunes

1. **Requerimientos:** alcance, priorizacion MoSCoW y al menos 8 preguntas de negocio propias, respondibles con los datos disponibles. Identificar para cada una dimensiones, medidas y limitaciones.
2. **Modelo:** diagrama estrella, Bus Matrix con Ventas, diccionario y matriz origen-destino con joins, transformaciones, nulabilidad, unidades y reglas de calidad. Definir grano, clave de negocio estable y tipo de fact antes del DDL.
3. **Dimensiones:** seleccionar y justificar todas las necesarias, incluyendo tiempo. Reutilizar las conformadas cuando sean compatibles y construir las faltantes. Demostrar al menos una regla SCD1 y una SCD2 sobre atributos del proceso con significado de negocio; los nombres y cantidades de dimensiones no estan fijados por el ejemplo.
4. **Diseno fisico:** crear fact y dimensiones con PK, FK fisicas, unicidad del grano, tipos adecuados y al menos dos indices justificados. Conservar NK para trazabilidad y usar SK para las relaciones dimensionales. Usar `DECIMAL` para importes y documentar precision y redondeo.
5. **ETL:** extraer, validar, cargar dimensiones, resolver NK a SK y cargar la fact. Incluir auditoria por lote, rechazos identificables e idempotencia. No vaciar ni reemplazar tablas en cada corrida.
6. **Temporalidad:** resolver dimensiones SCD2 segun la fecha de referencia del hecho, sin superposiciones ni fallback silencioso. Documentar la convencion de vigencia y cualquier supuesto de inicializacion; no presentar maestros actuales como historia reconstruida.
7. **Calidad:** controles ejecutables de grano, volumen, integridad, reglas numericas propias, vigencias SCD2 y reconciliacion de al menos dos medidas contra el origen al mismo grano o agregacion. Comparar igual poblacion, fecha de corte, unidades y formulas; explicar rechazos y diferencias.
8. **Analitica:** ejecutar las 8 consultas propias sobre el DW, contrastar al menos dos con el OLTP y producir 3 visualizaciones pertinentes. Publicar definiciones de KPI, 3 hallazgos, 2 limitaciones y una mejora.

Si se elige inventario u otro proceso sin importes, reconciliar cantidades u otras medidas existentes: no es obligatorio inventar una medida monetaria. Clasificar la aditividad de cada medida; un saldo o stock no se suma entre cortes para obtener un total historico.

### Estrategia de carga segun el tipo de fact

| Tipo elegido | Comportamiento esperado | Prueba especifica |
| --- | --- | --- |
| Transaccional | Insertar eventos nuevos por una clave estable. Si el origen admite correcciones, definir una politica explicita para tratarlas. | Cargar un evento real reservado en staging para una segunda corrida y demostrar una sola insercion; repetirlo sin duplicados. |
| Snapshot periodico | Una fila por entidad y corte, con unicidad sobre ambas claves. No inventar cortes anteriores sin evidencia fuente. | Crear un segundo corte controlado en staging a partir de datos reales, conservar el primero y repetir el nuevo corte sin duplicarlo. Identificar el corte simulado como prueba, no como historia real. |
| Snapshot acumulado | Insertar el proceso o linea inicial y actualizar la misma fila conforme avanza, conservando identidad y fecha de carga original. | Modificar un estado o medida en staging, demostrar actualizacion sin otra fila y repetir el lote sin cambios adicionales. |

Para un snapshot periodico de estado actual, la carga real inicial puede tener un solo corte. La prueba del segundo corte demuestra la estrategia de carga, no la disponibilidad de un historial de 12 meses.

### Experimentos comunes obligatorios

Realizar las pruebas con copias de registros reales en staging y destino de pruebas aislados, sin modificar WWI ni contaminar la reconciliacion final:

- **SCD1:** cambiar un atributo apropiado de una dimension; demostrar actualizacion con la misma SK y sin otra fila para la NK.
- **SCD2:** cambiar un atributo historizable en una fecha efectiva explicita; demostrar cierre de version, nueva SK, una sola version actual y resolucion temporal antes/despues. Si no hay hechos reales a ambos lados, usar fechas de referencia controladas para probar la busqueda de SK y rotularlas como pruebas.
- **Carga de la fact:** ejecutar la prueba correspondiente al tipo de fact de la tabla anterior, seguida de una recarga sin cambios.
- **Rechazo:** introducir una NK inexistente o un dato invalido en una copia y demostrar cuarentena o miembro desconocido auditado, sin perdida silenciosa.

Documentar claves seleccionadas, parametros, valores antes/despues y resultados. El registro por lote debe distinguir filas nuevas, actualizadas cuando corresponda, sin cambios y rechazadas.

## 5B. Ejemplo de referencia - Compras y recepcion

**Esta seccion desarrolla una posible eleccion, no impone Compras al resto de los equipos.** Los nombres de tablas, fuentes, dimensiones, medidas, preguntas y pruebas siguientes corresponden exclusivamente a quien elija este caso. Para otro proceso, sustituirlos por los propios y cumplir los requisitos comunes de la seccion 5A con igual nivel de detalle.

En este ejemplo el alcance comprende **ordenes de compra**, no facturas de proveedores ni pagos. Los importes son estimaciones de la orden: no representan gasto contable efectivamente facturado. No se exige reconstruir cada recepcion parcial ni un historial diario de pendientes.

### Etapa 1. Requerimientos y relevamiento

Para el caso de Compras, el informe debe contener el alcance, usuarios destinatarios, al menos 8 preguntas de negocio y una priorizacion MoSCoW. Las preguntas propuestas para este ejemplo son:

1. Importe estimado ordenado por mes de emision y proveedor.
2. Top 10 productos por importe estimado ordenado.
3. Cantidad pendiente por proveedor, producto y empaque.
4. Porcentaje de recepcion por producto y empaque.
5. Ordenes distintas e importe promedio por orden y comprador.
6. Importe ordenado por categoria y pais del proveedor.
7. Lineas finalizadas que aun presentan cantidades pendientes.
8. Lineas cuya ultima recepcion registrada supera la fecha esperada.

Para cada pregunta, identificar dimensiones, medidas y limitaciones del dato. El punto 8 es un indicador de **ultima recepcion posterior a lo esperado**, no una medicion exacta de entrega completa a tiempo.

### Etapa 2. Definir y documentar el modelo

**Grano del ejemplo:** una fila representa una linea de orden de compra de `Purchasing.PurchaseOrderLines`, identificada de manera estable por `PurchaseOrderLineID`, asociada a su `PurchaseOrderID`.

La tabla conserva el estado acumulado mas reciente de esa linea: cantidades ordenadas y recibidas, fechas disponibles y finalizacion. Por ello, para este caso se implementara como **snapshot acumulado**. Una recepcion adicional actualiza la fila existente; no crea otro evento ni agrega otra fila para la misma linea.

No generar el identificador de linea con `ROW_NUMBER`, `cumcount` o la posicion del registro. No agrupar por orden antes de cargar. Conservar el numero de orden como dimension degenerada; una orden con varias lineas sigue siendo una sola orden al calcular indicadores.

Entregar un diagrama estrella (Mermaid o herramienta equivalente), un diccionario de datos y una matriz origen-destino con columnas, joins, transformaciones, nulabilidad y reglas de calidad. El siguiente relevamiento orienta la busqueda; deben verificarlo contra su instalacion.

#### Fuentes transaccionales a investigar

| Tabla WWI | Campos principales y funcion |
| --- | --- |
| `Purchasing.PurchaseOrders` | `PurchaseOrderID`, `SupplierID`, `OrderDate`, `ExpectedDeliveryDate`, `ContactPersonID`, `DeliveryMethodID`, `IsOrderFinalized`, `LastEditedWhen`. Cabecera de la orden. |
| `Purchasing.PurchaseOrderLines` | `PurchaseOrderLineID`, `PurchaseOrderID`, `StockItemID`, `OrderedOuters`, `ReceivedOuters`, `PackageTypeID`, `ExpectedUnitPricePerOuter`, `LastReceiptDate`, `IsOrderLineFinalized`, `LastEditedWhen`. Grano y medidas. |
| `Purchasing.Suppliers` | `SupplierID`, `SupplierName`, `SupplierCategoryID`, `DeliveryCityID`, `PaymentDays`. Maestro del proveedor contratado. |
| `Purchasing.SupplierCategories` | `SupplierCategoryID`, `SupplierCategoryName`. Categoria del proveedor. |
| `Warehouse.StockItems` | `StockItemID`, `StockItemName`, `Brand`, `ColorID`, `UnitPackageID`, `OuterPackageID`. Maestro de productos. |
| `Warehouse.Colors` | `ColorID`, `ColorName`. Atributo descriptivo del producto. |
| `Warehouse.PackageTypes` | `PackageTypeID`, `PackageTypeName`. Empaque de la linea y descripciones de empaques del producto. |
| `Application.People` | `PersonID`, `FullName`, `PreferredName`, `IsEmployee`. Persona responsable indicada en la orden. |
| `Application.DeliveryMethods` | `DeliveryMethodID`, `DeliveryMethodName`. Metodo pactado en la orden. |
| `Application.Cities`, `Application.StateProvinces`, `Application.Countries` | IDs y nombres para aplanar ciudad, provincia y pais del proveedor. |

**Advertencias de modelado:** el proveedor de la compra se obtiene de `PurchaseOrders.SupplierID`, no del proveedor actual o preferido de `StockItems`. El empaque de la compra se obtiene de `PurchaseOrderLines.PackageTypeID`, no se infiere del maestro de producto. El comprador se obtiene de `PurchaseOrders.ContactPersonID`; no filtrar `People` por `IsSalesperson = 1`. En el diccionario aclarar que "comprador" es el rol didactico asignado a la persona de contacto de la orden, no un cargo verificado.

#### Dimensiones necesarias para el ejemplo de Compras

| Dimension | Contenido minimo | Regla solicitada |
| --- | --- | --- |
| `dw.dim_tiempo` | Fecha, dia, mes, nombre de mes, trimestre, anio y fin de semana. | Generada, sin SCD. Reutilizarla si existe. Cubrir fechas de orden, entrega esperada y ultima recepcion; la misma tabla cumple tres roles. |
| `dw.dim_producto` | NK del producto, nombre, marca, color y descripciones de empaques de unidad y externo. | Reutilizar la dimension de clase si es compatible, conservando su SCD2. Si se construye desde cero, implementar SCD1 y documentar la limitacion historica. |
| `dw.dim_proveedor` | NK, nombre, categoria, dias de pago, ciudad, provincia y pais aplanados. | Crear; SCD2 para categoria y dias de pago. Declarar la politica de los demas atributos. |
| `dw.dim_comprador` | NK de persona, nombre completo, nombre preferido y bandera de empleado. | Crear; SCD1. Incluir todas las personas referenciadas por las ordenes del alcance. |
| `dw.dim_metodo_entrega` | NK y nombre del metodo. | Crear; SCD1. |
| `dw.dim_empaque` | NK y nombre del tipo de empaque utilizado por la linea. | Crear; SCD1. |

Cada dimension, excepto el calendario con clave `YYYYMMDD`, tendra una SK entera independiente de la NK. Preservar las NK para trazabilidad. Definir PK, unicidad de NK en SCD1 y unicidad de la version actual por NK en SCD2. No imponer unicidad global de NK a una dimension historizada.

La geografia del proveedor debe quedar aplanada en `dim_proveedor`; no se solicita una dimension geografica adicional. Tampoco se solicita `dim_cliente` o `dim_vendedor` para este proceso.

La conformidad con Ventas debe comprobarse en claves, significado y atributos, no solamente en el nombre de la tabla. Si no estan disponibles las dimensiones de clase, construir las necesarias y explicar como se integrarian con Ventas.

#### Estructura minima de `dw.fact_compras`

| Grupo | Campos requeridos |
| --- | --- |
| Identidad | `id_fact_compra_sk` como PK tecnica; `id_orden_compra_nk` y `id_linea_compra_nk` para trazabilidad. Restriccion unica sobre `id_linea_compra_nk`. |
| Fechas | `id_tiempo_orden`, `id_tiempo_entrega_esperada`, `id_tiempo_ultima_recepcion`, todas referidas a `dim_tiempo`. La ultima admite NULL si no hubo recepcion registrada. |
| Contexto | `id_proveedor_sk`, `id_producto_sk`, `id_comprador_sk`, `id_metodo_entrega_sk`, `id_empaque_sk`. |
| Medidas | `cantidad_ordenada_outer`, `cantidad_recibida_outer`, `cantidad_pendiente_outer`, `precio_estimado_por_outer`, `importe_estimado_ordenado`, `importe_estimado_recibido`. |
| Estado | `es_linea_finalizada`, `es_orden_finalizada`. Son indicadores de estado, no importes. |
| Auditoria | `fecha_carga`, `fecha_actualizacion`, `id_lote` y marcas de modificacion fuente de cabecera y linea. |

No se entrega el DDL resuelto: cada equipo debe elegir tipos, precision, escala, constraints e indices y justificar sus decisiones. Usar `DECIMAL` para precios e importes; no `FLOAT`. Implementar FK fisicas para las dimensiones y al menos dos indices acordes con consultas concretas.

#### Definicion de medidas y unidades

| Medida | Definicion |
| --- | --- |
| Cantidad ordenada | `OrderedOuters`: cantidad de empaques externos ordenados. |
| Cantidad recibida | `ReceivedOuters`: cantidad acumulada de empaques externos recibidos. |
| Cantidad pendiente | `MAX(OrderedOuters - ReceivedOuters, 0)` como regla del TP. Registrar aparte los casos de sobrerrecepcion; no alterar las cantidades originales. |
| Precio estimado por outer | `ExpectedUnitPricePerOuter`. No reemplazarlo por el precio de venta actual del producto. |
| Importe estimado ordenado | Cantidad ordenada por precio estimado por outer, redondeado a 2 decimales por linea. |
| Importe estimado recibido | Cantidad recibida por el mismo precio estimado, redondeado a 2 decimales por linea. No es el importe de una factura real. |

Las cantidades no son unidades individuales. No convertirlas a unidades sin una equivalencia verificada. Presentar indicadores de cantidades y recepcion agrupados por producto y empaque para evitar comparar empaques de capacidades diferentes. No sumar precios; el precio medio ponderado se calcula como suma de cantidad por precio dividida por suma de cantidad, dentro de grupos comparables.

El porcentaje de recepcion se calcula como `100 * SUM(cantidad_recibida_outer) / NULLIF(SUM(cantidad_ordenada_outer), 0)`. Puede superar 100 si hay sobrerrecepcion; no ocultarlo. El importe promedio de orden se calcula como suma del importe ordenado dividida por ordenes distintas, no por numero de lineas.

Estos pendientes representan el **ultimo estado disponible** de las ordenes, incluso al agrupar por mes de emision. No permiten saber cuanto estaba pendiente al cierre de cada mes historico: eso requeriria otro grano y un snapshot periodico.

### Etapa 3. Construccion del ETL

Implementar un pipeline ejecutable de principio a fin:

1. Comprobar conexiones, objetos fuente, periodo y parametros.
2. Extraer cabeceras, lineas y maestros hacia staging del destino o estructuras de staging en memoria; conservar una identificacion del lote.
3. Medir volumen y unicidad antes y despues de los joins. Enriquecer sin multiplicar ni perder silenciosamente lineas.
4. Normalizar atributos, validar datos y separar rechazos con clave fuente, motivo y lote.
5. Cargar primero calendario y dimensiones; luego resolver NK a SK.
6. Insertar lineas nuevas y actualizar solamente las lineas existentes cuyos valores o estados hayan cambiado. Conservar su PK tecnica y `fecha_carga` original.
7. Ejecutar controles y registrar filas leidas, nuevas, actualizadas, sin cambios y rechazadas, ademas de estado y duracion del lote.

La recarga de una fuente sin cambios no debe generar filas, versiones SCD ni modificaciones de contenido o `fecha_actualizacion` innecesarias. No se acepta `if_exists='replace'`, vaciar todas las tablas ni reconstruir el DW en cada corrida.

Para el volumen didactico se permite releer todo el periodo y comparar por clave y contenido. Como alternativa, usar marcas de agua sobre `LastEditedWhen`, contemplando **cabecera y detalle**: una cabecera modificada puede requerir reprocesar todas sus lineas aunque estas no hayan cambiado. Explicar empates en timestamps, ventana de solapamiento y avance de la marca solamente tras una carga exitosa.

#### Tratamiento temporal obligatorio

- Resolver SCD2 por NK y **fecha de la orden**, con exactamente una version aplicable. No elegir arbitrariamente una SK si hay superposiciones.
- Establecer una convencion unica de intervalos: preferentemente inicio inclusivo y fin exclusivo, con fin NULL para la version actual. Documentar como adaptar una dimension de clase con fin inclusivo.
- No utilizar la fecha actual de ejecucion como si fuera la fecha efectiva de un cambio pasado.
- Para la carga inicial, si solo se extraen maestros actuales, se permite una version base desde la primera orden del alcance, identificada y documentada como **supuesto de inicializacion**, no como historia real reconstruida. Conservar un indicador o registro de auditoria de ese supuesto.
- Si se dispone de tablas temporales de WWI, su uso para reconstruccion historica es opcional y requiere verificar su existencia y cobertura.
- No aplicar un fallback silencioso a `es_actual = 1`. Ante una NK o vigencia no resoluble, rechazar con motivo o usar un miembro desconocido explicitamente identificado y contabilizado.
- Los atributos cambiantes se procesan en una transaccion que cierre e inserte versiones de forma atomica. Una nueva recepcion de una orden anterior no debe reasignar su proveedor a una version posterior a la fecha de esa orden.
- La ausencia de una ultima fecha de recepcion no es un error si no existe recepcion registrada. No inventar una fecha ni sustituirla por la fecha de carga. Investigar los casos inconsistentes.

### Etapa 4. Pruebas y reconciliacion

Entregar consultas o aserciones ejecutables, resultados y una conclusion para cada control. Las capturas sin consultas o codigo reproducible no son suficientes.

| Control | Evidencia y criterio esperado |
| --- | --- |
| Grano | Cero duplicados por `id_linea_compra_nk`; ningun join aumenta el numero de lineas sin justificacion. |
| Volumen | En la carga inicial: lineas del alcance = lineas cargadas + lineas rechazadas. En recargas, separar nuevas, actualizadas y sin cambios; no sumar actualizaciones como filas nuevas. |
| Integridad | Cero FK huerfanas. NULL solo en campos autorizados, como fecha de ultima recepcion. Contar miembros desconocidos si se utilizan. |
| Numericas | Ordenada mayor que cero; recibida y precio no negativos; importes coherentes con formula y escala. Sobrerrecepciones visibles, no eliminadas automaticamente. |
| SCD2 | Una version actual por NK, sin rangos superpuestos ni intervalos vacios, y resolucion temporal unica por hecho. |
| Reconciliacion | Comparar conteos e importes estimados por mes de orden y proveedor. Usar igual periodo, formulas, redondeo por linea y poblacion en ambas fuentes. |
| Unidades | Comparar cantidades por producto y empaque. No mezclar cantidades de unidades individuales con outers. |
| Idempotencia | Dos ejecuciones consecutivas sin cambios dejan igual contenido, conteos e importes; segunda corrida sin nuevas filas ni nuevas versiones. |

Los importes deben coincidir a 2 decimales cuando se aplica la misma formula por linea. Explicar cualquier diferencia; no elegir una tolerancia amplia para ocultarla. Si hay rechazos, presentar tanto el total bruto fuente como el total aceptado y los importes excluidos. Si no existen casos de una anomalia, mostrar que el control se ejecuto y encontro cero casos.

#### Experimentos obligatorios en staging aislado

No se entregan datos sinteticos externos ni se modifican tablas fuente. Seleccionar registros reales, copiarlos a un staging de pruebas y conservar su estado inicial. Parametrizar el ETL para leer ese staging durante los experimentos. Usar un destino de pruebas separado para que estos cambios no alteren la reconciliacion final.

1. **SCD1:** cambiar el nombre preferido de una persona copiada. Demostrar que la SK se conserva y no aparece otra fila para esa NK.
2. **SCD2:** elegir un proveedor y una fecha de corte dentro del periodo con ordenes antes y despues. Cambiar `PaymentDays` en la copia del maestro a partir de esa fecha; cargar las versiones antes de cargar los hechos de prueba. Demostrar nueva SK, cierre de version anterior y una sola version actual. Las ordenes anteriores y posteriores deben resolver a versiones diferentes. Reprocesar una orden antigua y verificar que conserva la version historica correcta.
3. **Actualizacion de la fact:** elegir una linea, ajustar en staging su cantidad recibida a otro valor valido, su ultima fecha de recepcion y su marca de modificacion. Demostrar que se actualiza la misma fila de `fact_compras`, sin cambiar el conteo, y se recalculan pendiente e importe recibido. Repetir el lote y comprobar ausencia de cambios adicionales.
4. **Rechazo controlado:** introducir en una linea copiada una NK de producto inexistente. Demostrar deteccion y cuarentena o asignacion auditada a un miembro desconocido, sin perdida silenciosa.

Documentar NK seleccionadas, fecha efectiva, valores antes/despues, consultas de verificacion y resultados. Si el periodo no permite encontrar un proveedor con ordenes a ambos lados de la fecha de corte, ampliar el alcance de pruebas dentro de los datos disponibles y justificarlo.

### Etapa 5. Explotacion analitica y cierre

Entregar las 8 consultas SQL de negocio del relevamiento, ejecutadas **sobre el DW**, con resultados e interpretacion breve. Para una consulta de importes y otra de cantidades, incluir control equivalente sobre el OLTP.

Preparar una salida visual en Power BI o en el notebook con al menos tres visualizaciones: evolucion mensual de importe ordenado, ranking de proveedores y recepcion/pendientes por producto y empaque. Publicar definiciones y denominadores de los KPI. No se exige despliegue cloud ni licencia de Power BI.

Concluir con tres hallazgos sustentados en resultados, dos limitaciones y una propuesta de mejora. Si una consulta no devuelve casos, interpretar el resultado sin inventar observaciones.

---

## 6. Entrega

Cada equipo entregara una carpeta identificada con sus integrantes, con:

- Informe en Markdown o PDF: alcance, teoria, preguntas, Bus Matrix, decisiones, pruebas y conclusiones.
- Diagrama estrella y diccionario/matriz origen-destino, incluidos en el informe o como anexos.
- Script SQL de creacion de tablas, constraints e indices.
- Notebook o scripts Python del ETL, con resultados de una ejecucion completa y orden de ejecucion claro.
- Script SQL de controles y de las 8 consultas analiticas; evidencias antes/despues de las pruebas.
- Visualizaciones o reporte exportado y diccionario de KPI.
- Instrucciones de ejecucion con dependencias, parametros, permisos, periodo utilizado y separacion entre carga real y pruebas. No incluir secretos ni un backup completo de WWI.

El docente debe poder reproducir la carga en un destino vacio y repetirla sin cambios. Cada integrante debe poder explicar el grano, un join de extraccion, una regla SCD, la estrategia de carga de su tipo de fact y un control de reconciliacion.

## 7. Rubrica de evaluacion

| Componente | Puntos | Evidencia para obtener el puntaje completo |
| --- | ---: | --- |
| Teoria aplicada | 20 | Respuestas justificadas con el caso, conforme a la Parte A. |
| Requerimientos y relevamiento | 8 | Alcance verificable, 8 preguntas, MoSCoW y fuentes/campos/relaciones comprobados. |
| Modelo dimensional y diseno fisico | 16 | Grano estable, dimensiones necesarias, Bus Matrix, diccionario, PK/FK, unicidad, tipos e indices justificados. |
| Carga de dimensiones y SCD | 18 | Carga reproducible, NK/SK correctas, SCD1 y SCD2 demostrados, supuestos historicos explicitos. |
| Carga de la fact elegida | 18 | Medidas correctas, resolucion temporal, estrategia idempotente adecuada al tipo de fact, auditoria y manejo de rechazos. |
| Calidad y reconciliacion | 12 | Controles ejecutables, comparacion por periodo o corte pertinente, pruebas controladas y evidencias consistentes. |
| Analitica, visualizaciones y reproducibilidad | 8 | 8 consultas, KPI coherentes, 3 visualizaciones, conclusiones e instrucciones suficientes para repetir el trabajo. |
| **Total** | **100** | **20 teoricos + 80 practicos.** |

El puntaje se asigna por evidencia: completo cuando cumple todos los criterios del componente, parcial cuando funciona con omisiones identificadas y cero cuando no se entrega o no puede demostrarse. La defensa individual permite verificar la autoria y comprension de lo presentado.

**Condiciones minimas para considerar logrado el objetivo practico:** la nueva fact elegida y sus dimensiones existen y contienen datos; el grano no se duplica; la carga puede repetirse; se demuestra el comportamiento correspondiente a su tipo de fact; y se presenta una reconciliacion trazable. Elegir un proceso distinto de Compras no modifica el puntaje ni exige implementar tambien `fact_compras`. Unicamente el informe teorico, un diagrama sin implementacion o una copia del notebook de ventas no cumplen estas condiciones. El umbral numerico de aprobacion se rige por la normativa de la asignatura.

## 8. Material de referencia de la unidad

Consultar las clases y guias de la [Unidad IV](../documentacion/unidad_04_data_warehouse_y_modelado_dimensional/): fundamentos del DW, modelado dimensional y SCD, fases 01 a 05 de Kimball, topologias y guias de dimensiones y hechos.

Los notebooks de [dimensiones](../notebook/unidad_IV/01_kimball_create_DIM.ipynb) y [ventas](../notebook/unidad_IV/02_kimball_create_FACT_VENTAS.ipynb) son referencias de implementacion, no soluciones del nuevo caso. Adaptar sus patrones: el filtro de vendedores, la carga solo por insercion y el fallback a la version actual no resuelven automaticamente las necesidades del proceso elegido.

**Recorrido esperado:** requerimiento de negocio -> grano -> dimensiones y medidas -> diseno fisico -> ETL -> controles -> indicadores.
