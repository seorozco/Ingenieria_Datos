# Status del Proyecto - Pipeline ETL

## ✅ COMPLETADO: Notebook STAGING (04_staging.ipynb)

### Cambios Realizados

**Antes:**
- Usaba datos ficticios en memoria
- No conectaba a SQL Server

**Ahora:**
- ✅ Lee datos reales de `raw.invoice_lines` (BD destino SQL Server)
- ✅ Descomprime los payloads JSON
- ✅ Normaliza y transforma los datos
- ✅ Guarda en `staging.invoice_lines` (BD destino SQL Server)

### Flujo de Ejecución

```
Conexión SQL Server
    ↓
Lee de: raw.invoice_lines (100 registros con payloads JSON)
    ↓
Descomprime JSON → Normaliza → Transforma
    ↓
Escribe en: staging.invoice_lines (BD destino)
    ↓
Resultado: 100 registros procesados ✅
```

### Datos Guardados

- **Total de registros**: 100
- **Facturas únicas**: 47
- **Monto total**: 56,089.07
- **Ubicación**: `WideWorldImportersDW2.staging.invoice_lines`

### Cómo Ejecutar

```bash
cd C:\Users\Sergio Orozco\proyectos\Ingenieria_Datos\notebook\unidad_IV\pipeline_ingesta

# Ejecutar con Jupyter
jupyter notebook 04_staging.ipynb

# O ejecutar con Python (nbclient)
python ejecutor_notebooks.py
```

### Estructura de Datos Generados

```sql
SELECT * FROM staging.invoice_lines LIMIT 5;

-- Resultado esperado:
id_linea | id_factura | id_cliente | id_producto | cantidad | neto    | impuesto | total
---------|------------|------------|-------------|----------|---------|----------|--------
1        | 1          | NULL       | 67          | 10       | 2300.00 | 345.00   | 2645.00
2        | 2          | NULL       | 50          | 9        | 117.00  | 17.55    | 134.55
...
```

### Archivos Modificados

- `04_staging.ipynb` - Ahora lee del SQL Server (en lugar de datos ficticios)
- `STAGING_FUNCIONAL.md` - Documentación de esta etapa

### Notas Importantes

1. **Todos los datos vienen del SQL Server**, no se usan archivos CSV ni datos de prueba
2. **El schema `staging` fue creado** automáticamente en la BD destino
3. **La tabla `staging.invoice_lines` contiene** los datos normalizados listos para el próximo paso (dimensiones/hechos)

### Próximos Pasos

Las siguientes etapas ya existen en el directorio:
- `05_dimensiones.ipynb`
- `06_hechos.ipynb`
- `07_auditoria_publicacion.ipynb`
- `08_demo_integral.ipynb`

Se recomienda revisar y actualizar estas notebooks para que también lean del SQL Server si es necesario.

---

**Status Final**: ✅ STAGING ejecutándose con SQL Server
