# Unidad IV · Guia de Tablas de Hechos
## Como disenar, construir y validar facts en Kimball (WideWorldImporters)

---

## 1. Rol de la tabla de hechos

La tabla de hechos representa eventos medibles del negocio y se conecta con dimensiones por claves foraneas.

Estructura minima:

- FK a dimensiones (tiempo, cliente, producto, vendedor, ciudad).
- Medidas numericas (cantidad, montos, margen).
- Dimensiones degeneradas cuando aplique (por ejemplo numero de factura).

Regla base:

- Una fact no es para guardar descripciones largas; eso pertenece a dimensiones.

---

## 2. Primera decision: granularidad

Granularidad propuesta para la unidad:

- 1 fila = 1 linea de factura (Sales.InvoiceLines).

Definir grano antes de codificar evita errores de modelado:

- Si mezclas "linea" con "cabecera" en una misma fact, rompes agregaciones.
- Si no declaras grano, no puedes validar duplicados correctamente.

Plantilla para documentar grano:

```text
Proceso: ventas facturadas
Grano: una fila por linea de factura
Clave de negocio del evento: NumeroFactura + NumeroLinea
```

---

## 3. Tipos de tablas de hechos

| Tipo | Definicion | Ejemplo WWI |
|---|---|---|
| Transaccional | 1 fila por evento | Linea de factura |
| Snapshot periodico | 1 fila por estado en periodo | Stock diario por producto |
| Accumulating snapshot | 1 fila por ciclo de proceso | Ciclo pedido-entrega-cobro |

Para este curso usamos fact transaccional.

---

## 4. Diseno funcional previo al DDL

Antes de crear la tabla, cerrar este mini contrato:

1. Proceso y grano definidos.
2. Dimensiones obligatorias identificadas.
3. Medidas clasificadas por aditividad.
4. Reglas de calidad definidas.
5. Regla de incrementalidad definida (idempotencia).

Mapa logico sugerido:

| Campo Fact | Origen WWI | Tipo |
|---|---|---|
| FechaKey | Sales.Invoices.InvoiceDate -> dim_tiempo | FK |
| ClienteKey | Sales.Invoices.CustomerID -> dim_cliente | FK |
| ProductoKey | Sales.InvoiceLines.StockItemID -> dim_producto | FK |
| VendedorKey | Sales.Invoices.SalespersonPersonID -> dim_vendedor | FK |
| CiudadKey | Sales.Customers.DeliveryCityID -> dim_ciudad | FK |
| NumeroFactura | Sales.Invoices.InvoiceID | Degenerada |
| NumeroLinea | secuencia por factura | Degenerada |
| Cantidad | Sales.InvoiceLines.Quantity | Medida |
| PrecioUnitario | Sales.InvoiceLines.UnitPrice | Medida |
| MontoNeto | Sales.InvoiceLines.ExtendedPrice | Medida |
| CostoEstimado | derivada | Medida |
| MargenBruto | Sales.InvoiceLines.LineProfit | Medida |

---

## 5. DDL base de FACT_VENTAS (T-SQL)

```sql
CREATE TABLE dbo.FACT_VENTAS (
    FactVentaKey   bigint IDENTITY(1,1) PRIMARY KEY,
    FechaKey       int           NOT NULL,
    ClienteKey     int           NOT NULL,
    ProductoKey    int           NOT NULL,
    VendedorKey    int           NOT NULL,
    CiudadKey      int           NOT NULL,
    NumeroFactura  nvarchar(20)  NOT NULL,
    NumeroLinea    int           NOT NULL,
    Cantidad       decimal(18,4) NOT NULL,
    PrecioUnitario decimal(18,4) NOT NULL,
    MontoNeto      decimal(18,2) NOT NULL,
    CostoEstimado  decimal(18,2) NULL,
    MargenBruto    decimal(18,2) NULL,
    CONSTRAINT UQ_FACT_VENTAS_DocLinea UNIQUE (NumeroFactura, NumeroLinea)
);
```

Notas:

- La constraint unica implementa idempotencia por clave de negocio.
- Las FK pueden declararse luego de validar calidad inicial de carga.

---

## 6. Medidas y aditividad

Clasificacion recomendada:

- Aditivas: Cantidad, MontoNeto, MargenBruto.
- Semi-aditivas: saldos en snapshots (no aplica a esta fact transaccional).
- No aditivas: PrecioUnitario, porcentajes.

Regla docente:

- Nunca sumar porcentajes.
- El precio unitario se analiza por promedio, no por suma.

---

## 7. Implementacion ETL paso a paso

### 7.1 Extraer

- Tomar Sales.InvoiceLines como base de eventos.
- Enriquecer con Sales.Invoices y Sales.Customers para las NK necesarias.

### 7.2 Transformar

- Derivar FechaKey en formato YYYYMMDD.
- Generar NumeroLinea deterministico por factura.
- Calcular medidas derivadas (por ejemplo CostoEstimado).

### 7.3 Resolver claves sustitutas (NK -> SK)

- SCD1: match directo por NK.
- SCD2: match por NK y vigencia (fecha del hecho dentro de rango).
- Si no hay match temporal por historico incompleto, documentar fallback a es_actual.

### 7.4 Cargar

- Insertar solo filas nuevas por NumeroFactura + NumeroLinea.
- Registrar filas rechazadas por SK faltante para auditoria.

---

## 8. Validaciones pertinentes (obligatorias)

## 8.1 Validacion de volumen

Objetivo: comparar orden de magnitud entre origen y destino.

```sql
SELECT COUNT(*) AS FilasOrigen FROM Sales.InvoiceLines;
SELECT COUNT(*) AS FilasFact FROM dbo.FACT_VENTAS;
```

Interpretacion:

- Diferencias pueden existir por incrementalidad.
- Si la diferencia es extrema, revisar joins y filtros.

## 8.2 Validacion de duplicados de negocio

Objetivo: garantizar 1 fila por evento de grano.

```sql
SELECT NumeroFactura, NumeroLinea, COUNT(*) AS Repeticiones
FROM dbo.FACT_VENTAS
GROUP BY NumeroFactura, NumeroLinea
HAVING COUNT(*) > 1;
```

Resultado esperado: 0 filas.

## 8.3 Validacion de integridad referencial

Objetivo: detectar FK huerfanas.

```sql
SELECT
    SUM(CASE WHEN t.FechaKey IS NULL THEN 1 ELSE 0 END) AS HuerfanasTiempo,
    SUM(CASE WHEN c.ClienteKey IS NULL THEN 1 ELSE 0 END) AS HuerfanasCliente,
    SUM(CASE WHEN p.ProductoKey IS NULL THEN 1 ELSE 0 END) AS HuerfanasProducto,
    SUM(CASE WHEN v.VendedorKey IS NULL THEN 1 ELSE 0 END) AS HuerfanasVendedor,
    SUM(CASE WHEN ci.CiudadKey IS NULL THEN 1 ELSE 0 END) AS HuerfanasCiudad
FROM dbo.FACT_VENTAS f
LEFT JOIN dbo.DIM_TIEMPO t   ON f.FechaKey = t.FechaKey
LEFT JOIN dbo.DIM_CLIENTE c  ON f.ClienteKey = c.ClienteKey
LEFT JOIN dbo.DIM_PRODUCTO p ON f.ProductoKey = p.ProductoKey
LEFT JOIN dbo.DIM_VENDEDOR v ON f.VendedorKey = v.VendedorKey
LEFT JOIN dbo.DIM_CIUDAD ci  ON f.CiudadKey = ci.CiudadKey;
```

Resultado esperado: todos los contadores en 0.

## 8.4 Validacion de reglas de negocio

Objetivo: detectar valores imposibles o anomalias.

```sql
SELECT
    SUM(CASE WHEN Cantidad <= 0 THEN 1 ELSE 0 END) AS CantidadNoPositiva,
    SUM(CASE WHEN PrecioUnitario < 0 THEN 1 ELSE 0 END) AS PrecioNegativo,
    SUM(CASE WHEN MontoNeto < 0 THEN 1 ELSE 0 END) AS MontoNetoNegativo
FROM dbo.FACT_VENTAS;
```

## 8.5 Reconciliacion contra origen

Objetivo: validar medidas agregadas.

```sql
-- Origen mensual
SELECT YEAR(i.InvoiceDate) AS Anio, MONTH(i.InvoiceDate) AS Mes,
       SUM(CAST(il.ExtendedPrice AS decimal(18,2))) AS MontoOrigen
FROM Sales.InvoiceLines il
JOIN Sales.Invoices i ON il.InvoiceID = i.InvoiceID
GROUP BY YEAR(i.InvoiceDate), MONTH(i.InvoiceDate);

-- Destino mensual
SELECT t.Anio, t.Mes,
       SUM(f.MontoNeto) AS MontoDW
FROM dbo.FACT_VENTAS f
JOIN dbo.DIM_TIEMPO t ON f.FechaKey = t.FechaKey
GROUP BY t.Anio, t.Mes;
```

Interpretacion:

- Diferencias cercanas a 0 indican reconciliacion correcta.
- Diferencias altas exigen revisar duplicados, filtros o mapeos SK.

---

## 9. Integridad y performance

Controles minimos:

- FK validas a todas las dimensiones.
- No duplicar NumeroFactura + NumeroLinea en mismo lote.
- Cantidad > 0 (salvo notas de credito modeladas aparte).

Indices sugeridos:

```sql
CREATE NONCLUSTERED INDEX IX_FV_FechaKey ON dbo.FACT_VENTAS(FechaKey);
CREATE NONCLUSTERED INDEX IX_FV_ProductoKey ON dbo.FACT_VENTAS(ProductoKey);
CREATE NONCLUSTERED INDEX IX_FV_ClienteKey ON dbo.FACT_VENTAS(ClienteKey);
CREATE NONCLUSTERED INDEX IX_FV_VendedorKey ON dbo.FACT_VENTAS(VendedorKey);
```

Sugerencias adicionales:

- Particionar por fecha cuando el volumen crezca.
- Evitar funciones sobre columnas indexadas en filtros de reportes.

---

## 10. Errores frecuentes

- Incluir texto descriptivo en la fact en lugar de dimensionarlo.
- Definir dos granularidades en la misma tabla.
- Cargar facts sin resolver surrogate keys.
- Cargar medidas no reconciliadas contra fuente.
- No separar filas rechazadas (pierde trazabilidad de calidad).

---

## 11. Checklist de cierre (entrega de clase)

```text
[ ] Grano declarado y respetado: 1 fila = 1 linea de factura
[ ] Mapeo NK -> SK completo (incluyendo reglas SCD2)
[ ] Sin duplicados por NumeroFactura + NumeroLinea
[ ] FK huerfanas = 0
[ ] Reglas de negocio basicas en rango esperado
[ ] Reconciliacion con origen explicada y aprobada
[ ] Evidencia de consultas de control anexada
```
