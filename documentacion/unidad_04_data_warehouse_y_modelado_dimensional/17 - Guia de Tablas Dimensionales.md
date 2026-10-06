# Unidad IV · Guia de Tablas Dimensionales
## Como disenar dimensiones de calidad (WideWorldImporters)

---

## 1. Rol de una dimension

Una tabla dimensional responde el contexto del hecho:

- Quien? (cliente, vendedor)
- Que? (producto)
- Donde? (ciudad, estado, pais)
- Cuando? (tiempo)

---

## 2. Reglas practicas de diseno

1. Usar surrogate key entera como PK.
2. Mantener natural key para trazabilidad.
3. Aplanar jerarquias para simplificar analisis.
4. Incluir columnas de SCD cuando aplique.
5. Usar nombres de negocio, no nombres crudos de origen.

---

## 3. Plantilla de estructura general

```sql
CREATE TABLE dbo.DIM_X (
    XKey                int IDENTITY(1,1) NOT NULL PRIMARY KEY,
    XID_NK              int               NOT NULL,
    Nombre              nvarchar(100)     NOT NULL,
    Atributo1           nvarchar(100)     NULL,
    Atributo2           nvarchar(100)     NULL,
    FechaInicioVigencia date              NOT NULL,
    FechaFinVigencia    date              NULL,
    EsActual            bit               NOT NULL
);
```

---

## 4. Ejemplo 1: DIM_CLIENTE desde WWI

Fuente principal:

- Sales.Customers
- Sales.CustomerCategories
- Sales.BuyingGroups

Campos recomendados:

- CustomerID_NK
- CustomerName
- CustomerCategoryName
- BuyingGroupName
- FechaInicioVigencia
- FechaFinVigencia
- EsActual

---

## 5. Ejemplo 2: DIM_PRODUCTO desde WWI

Fuente principal:

- Warehouse.StockItems
- Warehouse.Colors
- Warehouse.PackageTypes

Campos recomendados:

- StockItemID_NK
- StockItemName
- ColorName
- UnitPackageName
- OuterPackageName
- Brand
- EsActual

---

## 6. Ejemplo 3: DIM_CIUDAD geografica

Fuente principal:

- Application.Cities
- Application.StateProvinces
- Application.Countries

Modelo aplanado:

- CityName
- StateProvinceName
- CountryName
- SalesTerritory

Esto evita joins innecesarios en BI.

---

## 7. Gestion de cambios SCD

| Tipo | Uso en clase | Ventaja | Costo |
|---|---|---|---|
| SCD 1 | Corregir errores no historicos | Simple | Pierde historia |
| SCD 2 | Cambios de categoria, segmento, region | Mantiene historia | Mayor volumen |
| SCD 3 | Comparar valor actual vs anterior | Facil comparacion | Historia limitada |

---

## 8. Errores frecuentes en estudiantes

- Cargar dimension sin natural key.
- Mezclar atributos de dos granos diferentes en la misma dimension.
- No definir fechas de vigencia en SCD2.
- Usar nombres tecnicos opacos para negocio.

---

## 9. Checklist de calidad de dimension

```text
[ ] Tiene surrogate key
[ ] Conserva natural key
[ ] Atributos descriptivos entendibles
[ ] Reglas SCD definidas
[ ] Sin duplicados activos para misma NK
[ ] Diccionario publicado
```
