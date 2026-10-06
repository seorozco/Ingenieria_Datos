# Unidad IV · Kimball Fase 01
## Planificacion y Requerimientos (caso WideWorldImporters)

> Asignatura: Ingenieria de Datos  
> Unidad: IV - Data Warehouse y Modelado Dimensional  
> Base de practica: SQL Server - WideWorldImporters

---

## Objetivo de la fase

Definir con claridad que problema de negocio vamos a resolver primero, para quien, con que metricas y con que nivel de detalle. En Kimball, si esta fase queda ambigua, todo el modelo se vuelve inestable.

---

## Resultado esperado en clase

Al terminar esta fase, el curso debe tener:

- Un proceso de negocio priorizado (primer Data Mart).
- Una lista de preguntas de negocio concretas.
- Una declaracion formal de granularidad.
- Una Bus Matrix inicial.
- Un alcance realista para el primer sprint del DWH.

---

## 1. Proceso de negocio inicial recomendado

Para WideWorldImporters, el mejor primer proceso para docencia es:

- Proceso: Ventas facturadas.
- Evento: cada linea de factura.
- Tabla fuente principal: Sales.InvoiceLines.
- Tablas de apoyo: Sales.Invoices, Sales.Customers, Warehouse.StockItems, Application.People.

Razon didactica:

- Tiene metrica economica clara.
- Tiene varias dimensiones naturales.
- Permite introducir SCD en clientes y productos.
- Se conecta facil con tableros de BI.

---

## 2. Preguntas de negocio que guian el modelo

Estas preguntas se convierten en requisitos funcionales:

1. Cuanto vendimos por mes, categoria y cliente?
2. Que clientes aportan mayor margen?
3. Como evolucionan las ventas por ciudad y estado?
4. Que vendedor mantiene mejor ticket promedio?
5. Que productos pierden margen por descuentos frecuentes?

Regla: si una pregunta no se puede responder con el modelo propuesto, el diseño aun no esta listo.

---

## 3. Declaracion de granularidad

Granularidad propuesta:

- Una fila en la tabla de hechos representa una linea de factura de venta en WideWorldImporters.

Interpretacion operativa:

- En una misma factura puede haber varias filas en la fact.
- Cada fila tiene 1 producto, 1 cliente, 1 fecha, 1 vendedor.
- Las metricas de monto, costo y margen se calculan en ese nivel.

---

## 4. Bus Matrix inicial (curso)

```text
Proceso de negocio                      dim_tiempo  dim_cliente  dim_producto  dim_vendedor  dim_ciudad
--------------------------------------------------------------------------------------------------------
Ventas facturadas                           X            X            X             X             X
Pedidos (ordenes comerciales)               X            X            X             X             X
Inventario (snapshot diario)                X                         X                           X
Compras a proveedores                       X                         X                           X
```

Dimension conformada minima para la unidad:

- dim_tiempo
- dim_cliente
- dim_producto
- dim_ciudad

---

## 5. Mapeo rapido de fuentes WWI

| Requisito | Tabla WWI | Campo clave |
|---|---|---|
| Fecha de venta | Sales.Invoices | InvoiceDate |
| Cliente | Sales.Customers | CustomerID |
| Vendedor | Application.People | PersonID |
| Producto | Warehouse.StockItems | StockItemID |
| Linea de venta | Sales.InvoiceLines | InvoiceLineID |
| Ubicacion cliente | Application.Cities | CityID |

Nota: En el ETL no conviene depender solo de nombres; usar IDs tecnicos y resolver descripciones en dimensiones.

---

## 6. Entregables de la fase (checklist docente)

```text
[ ] Documento de alcance aprobado (1 pagina)
[ ] Lista de preguntas de negocio (minimo 10)
[ ] Granularidad declarada y validada
[ ] Bus Matrix version 1
[ ] Priorizacion MoSCoW (Must/Should/Could/Won't)
```

---

## 7. Mini dinamica de clase (30 minutos)

1. Dividir el curso en 3 grupos.
2. Cada grupo propone 5 preguntas de negocio.
3. En plenario, clasificar preguntas por viabilidad con datos WWI.
4. Elegir 1 sola granularidad para toda la comision.
5. Cerrar con Bus Matrix comun.

---

## Riesgos comunes y como evitarlos

- Riesgo: empezar por tecnologia en lugar de negocio.
  - Mitigacion: cerrar preguntas de negocio antes de escribir SQL.
- Riesgo: granularidad mezclada (factura + linea en la misma fact).
  - Mitigacion: una sola unidad de evento por tabla de hechos.
- Riesgo: alcance demasiado amplio para una unidad.
  - Mitigacion: primer Data Mart centrado en ventas facturadas.

---

## Criterio de salida de fase

La fase se considera cerrada cuando cualquier estudiante puede responder:

- Que representa una fila de la fact?
- Que decisiones de negocio soporta el modelo?
- Que dimensiones son conformadas y por que?
