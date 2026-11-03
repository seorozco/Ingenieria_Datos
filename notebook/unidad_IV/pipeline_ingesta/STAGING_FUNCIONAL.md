# Pipeline ETL - Etapa STAGING

## Estado: ✅ FUNCIONAL

La notebook `04_staging.ipynb` ahora **lee datos del SQL Server** en lugar de usar datos de prueba.

### Flujo de Datos

```
raw.invoice_lines (SQL Server - BD Destino)
        ↓
    [DESCOMPRIMIR JSON]
        ↓
    [NORMALIZAR]
        ↓
staging.invoice_lines (SQL Server - BD Destino)
```

### Ejecución

```bash
# Desde C:\Users\Sergio Orozco\proyectos\Ingenieria_Datos\notebook\unidad_IV\pipeline_ingesta\

# Opción 1: Ejecutar directamente en Jupyter
jupyter notebook 04_staging.ipynb

# Opción 2: Ejecutar con nbclient (Python)
python -c "
import os
from nbclient import NotebookClient
from nbformat import read

os.chdir(r'C:\Users\Sergio Orozco\proyectos\Ingenieria_Datos\notebook\unidad_IV\pipeline_ingesta')

with open('04_staging.ipynb') as f:
    nb = read(f, as_version=4)

client = NotebookClient(nb, timeout=300)
client.execute()
"
```

### Resultados

Después de ejecutar:

- **Registros procesados**: 100
- **Facturas únicas**: 47
- **Total general**: 56,089.07

**Tabla de destino**: `staging.invoice_lines` (BD destino - WideWorldImportersDW2)

### Columnas en staging.invoice_lines

| Columna | Tipo | Descripción |
|---------|------|-------------|
| id_linea | INT (PK) | ID de la línea de factura |
| id_factura | INT | ID de la factura |
| id_cliente | INT | ID del cliente |
| id_producto | INT | ID del producto |
| cantidad | INT | Cantidad ordenada |
| neto | DECIMAL(18,2) | Monto sin impuesto |
| impuesto | DECIMAL(18,2) | Monto de impuesto |
| total | DECIMAL(18,2) | Monto total (neto + impuesto) |
| timestamp_carga | DATETIME | Marca de tiempo de carga |

### Validación de Datos

```sql
-- Verificar en SQL Server
SELECT COUNT(*) as total FROM staging.invoice_lines
SELECT TOP 5 * FROM staging.invoice_lines ORDER BY id_linea
```

### Nota Importante

**Los datos ya están en SQL Server**, no se usan datos de prueba ni archivos CSV.
Toda la información viene de:
- **Entrada**: `raw.invoice_lines` (tabla en BD destino)
- **Salida**: `staging.invoice_lines` (tabla en BD destino)
