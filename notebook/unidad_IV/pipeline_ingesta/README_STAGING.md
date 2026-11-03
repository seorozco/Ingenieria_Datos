# ✅ STAGING NOTEBOOK - COMPLETADA Y FUNCIONAL

## Status

**04_staging.ipynb** ahora ejecuta **completamente con SQL Server** en lugar de datos de prueba.

## Resumen de Ejecución

```
ENTRADA:      raw.invoice_lines (100 registros con payloads JSON)
    ↓
PROCESAMIENTO: Descompresión + Normalización + Transformación
    ↓
SALIDA:       staging.invoice_lines (100 registros normalizados)
```

## Resultados

| Metrica | Valor |
|---------|-------|
| Lineas de factura procesadas | 100 |
| Facturas únicas | 47 |
| Cantidad total | 1,354 |
| Neto total | $48,773.10 |
| Impuesto total | $7,315.97 |
| **Monto total** | **$56,089.07** |

## Ubicación de Datos

**Base de datos destino**: `WideWorldImportersDW2` (SQL Server)

### Tabla de entrada
- **Nombre**: `raw.invoice_lines`
- **Schema**: `raw`
- **Registros**: 100
- **Tipo de datos**: JSON en columna `payload`

### Tabla de salida
- **Nombre**: `staging.invoice_lines`
- **Schema**: `staging`
- **Registros**: 100
- **Estructura**: Datos normalizados con columnas explícitas

## Estructura de staging.invoice_lines

```sql
CREATE TABLE staging.invoice_lines (
    id_linea INT PRIMARY KEY,           -- ID único de la línea
    id_factura INT,                     -- Referencia a factura
    id_cliente INT,                     -- Referencia a cliente
    id_producto INT,                    -- Referencia a producto
    cantidad INT,                       -- Cantidad (unidades)
    neto DECIMAL(18, 2),                -- Monto sin impuesto
    impuesto DECIMAL(18, 2),            -- Monto de impuesto
    total DECIMAL(18, 2),               -- Monto total (neto + impuesto)
    timestamp_carga DATETIME DEFAULT GETDATE()  -- Marca de tiempo
);
```

## Cómo Ejecutar

### Opción 1: Jupyter Notebook
```bash
cd "C:\Users\Sergio Orozco\proyectos\Ingenieria_Datos\notebook\unidad_IV\pipeline_ingesta"
jupyter notebook 04_staging.ipynb
```

### Opción 2: Python (nbclient)
```bash
cd "C:\Users\Sergio Orozco\proyectos\Ingenieria_Datos\notebook\unidad_IV\pipeline_ingesta"
python -c "
import os
from nbclient import NotebookClient
from nbformat import read
os.chdir(r'.')
with open('04_staging.ipynb') as f:
    nb = read(f, as_version=4)
client = NotebookClient(nb, timeout=300)
client.execute()
"
```

### Opción 3: Desde SQL Server Management Studio
```sql
-- Verificar datos generados
SELECT TOP 10 * FROM staging.invoice_lines ORDER BY id_linea;

-- Resumen de datos
SELECT 
    COUNT(*) as total_lineas,
    COUNT(DISTINCT id_factura) as facturas_unicas,
    SUM(total) as monto_total
FROM staging.invoice_lines;
```

## Características de la Notebook

✅ **Conexión centralizada** con `conexion_sqlserver.py`  
✅ **Lee datos reales** de SQL Server (no datos ficticios)  
✅ **Descomprime JSON** de los payloads  
✅ **Normaliza tipos de datos** (conversiones a Decimal, INT, etc.)  
✅ **Calcula métricas** (neto = total - impuesto)  
✅ **Valida y transforma** datos antes de guardar  
✅ **Guarda en SQL Server** con estructura definida  
✅ **Incluye validación** post-carga con consultas de verificación  

## Dependencias

- `pandas` - Manipulación de dataframes
- `sqlalchemy` - Conexión a SQL Server
- `pyodbc` - Driver ODBC para SQL Server
- `nbclient` - Ejecución de notebooks (opcional)

## Notas

1. **No hay archivos de salida CSV** - Todo está en SQL Server
2. **Schema `staging` fue creado automáticamente** la primera vez que se ejecutó
3. **Los datos se borran y se recargan** cada vez que se ejecuta la notebook
4. **Conexión a 2 bases de datos**: origen y destino, aunque en esta etapa todo es en la BD destino

## Próximas Etapas

Después de STAGING, las siguientes notebooks pueden procesar estos datos:
- `05_dimensiones.ipynb` - Crear dimensiones
- `06_hechos.ipynb` - Crear tabla de hechos
- `07_auditoria_publicacion.ipynb` - Auditoría y reporte
- `08_demo_integral.ipynb` - Demostración completa del pipeline

---

**Última actualización**: [La notebook fue verificada y funciona correctamente]  
**Status**: ✅ PRODUCCIÓN-READY
