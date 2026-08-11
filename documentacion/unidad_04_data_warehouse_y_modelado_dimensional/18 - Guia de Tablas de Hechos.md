# Unidad IV · Guia de Tablas de Hechos
## Como disenar facts correctas en Kimball (WideWorldImporters)

---

## 1. Rol de la tabla de hechos

La tabla de hechos guarda eventos medibles del negocio y conecta con las dimensiones por claves foraneas.

Estructura minima:

- FK a dimensiones.
- Medidas numericas.
- Eventualmente dimensiones degeneradas (ej: NumeroFactura).

---

## 2. Primera decision: granularidad

Granularidad propuesta para unidad:

- 1 fila = 1 linea de factura (Sales.InvoiceLines).

Si el grano no esta claro, no se debe codificar.

---

## 3. Tipos de tablas de hechos

| Tipo | Definicion | Ejemplo WWI |
|---|---|---|
| Transaccional | 1 fila por evento | Linea de factura |
| Snapshot periodico | 1 fila por estado en periodo | Stock diario por producto |
| Accumulating snapshot | 1 fila por ciclo de proceso | Ciclo pedido-entrega-cobro |

---

## 4. DDL base de FACT_VENTAS (T-SQL)

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
    MargenBruto    decimal(18,2) NULL
);
```

---

## 5. Medidas: aditividad

- Aditivas: Cantidad, MontoNeto, MargenBruto.
- Semi-aditivas: saldos de snapshot de inventario.
- No aditivas: PrecioUnitario, porcentaje de descuento.

Regla docente:

- Nunca sumar porcentajes.

---

## 6. Integridad y performance

Controles minimos:

- FK validas a todas las dimensiones.
- No duplicar NumeroFactura + NumeroLinea en mismo lote.
- Cantidad > 0 salvo notas de credito modeladas aparte.

Indices sugeridos:

```sql
CREATE NONCLUSTERED INDEX IX_FV_FechaKey ON dbo.FACT_VENTAS(FechaKey);
CREATE NONCLUSTERED INDEX IX_FV_ProductoKey ON dbo.FACT_VENTAS(ProductoKey);
CREATE NONCLUSTERED INDEX IX_FV_ClienteKey ON dbo.FACT_VENTAS(ClienteKey);
```

---

## 7. Consultas de control para clase

```sql
-- Control de volumen mensual
SELECT t.Anio, t.Mes, COUNT(*) AS FilasFact
FROM dbo.FACT_VENTAS f
JOIN dbo.DIM_TIEMPO t ON f.FechaKey = t.FechaKey
GROUP BY t.Anio, t.Mes
ORDER BY t.Anio, t.Mes;

-- Control de margen por producto
SELECT p.StockItemName, SUM(f.MontoNeto) AS Venta, SUM(f.MargenBruto) AS Margen
FROM dbo.FACT_VENTAS f
JOIN dbo.DIM_PRODUCTO p ON f.ProductoKey = p.ProductoKey
GROUP BY p.StockItemName
ORDER BY Venta DESC;
```

---

## 8. Errores frecuentes

- Incluir texto descriptivo dentro de la fact en lugar de dimensionarlo.
- Definir dos granularidades en la misma tabla.
- Cargar facts sin resolver surrogate keys.
- Cargar medidas no reconciliadas contra fuente.

---

## 9. Checklist de cierre

```text
[ ] Granularidad declarada y respetada
[ ] Medidas tipificadas (aditiva/semi/no aditiva)
[ ] FK completas
[ ] Reconciliacion con origen WWI
[ ] Consultas de control aprobadas
```
