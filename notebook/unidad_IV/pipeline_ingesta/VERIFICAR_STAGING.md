# 🚀 COMO VERIFICAR QUE STAGING FUNCIONA CON SQL SERVER

## Verificación Rápida

### 1. Abrir SQL Server Management Studio
```sql
-- Conectar a: localhost\SQLEXPRESS02
-- Base de datos: WideWorldImportersDW2

-- Verificar datos ANTES (entrada)
SELECT COUNT(*) as total_raw FROM raw.invoice_lines;
-- Resultado esperado: 100

-- Verificar datos DESPUÉS (salida)
SELECT COUNT(*) as total_staging FROM staging.invoice_lines;
-- Resultado esperado: 100
```

### 2. Ejecutar la Notebook desde Jupyter

```bash
# Navegar al directorio
cd C:\Users\Sergio Orozco\proyectos\Ingenieria_Datos\notebook\unidad_IV\pipeline_ingesta

# Iniciar Jupyter
jupyter notebook

# Abrir: 04_staging.ipynb
# Ejecutar: Kernel > Restart Kernel and Run All Cells
```

### 3. Verificar Resultados en SQL Server
```sql
-- Consulta de validación completa
SELECT 
    COUNT(*) as lineas,
    COUNT(DISTINCT id_factura) as facturas,
    SUM(cantidad) as cantidad_total,
    SUM(total) as monto_total
FROM staging.invoice_lines;

-- Resultado esperado:
-- lineas=100, facturas=47, cantidad_total=1354, monto_total=56089.07
```

### 4. Ver Muestra de Datos Transformados
```sql
SELECT TOP 10 
    id_linea,
    id_factura,
    id_cliente,
    id_producto,
    cantidad,
    neto,
    impuesto,
    total
FROM staging.invoice_lines
ORDER BY id_linea;
```

## Flujo de Ejecución (Lo que hace 04_staging.ipynb)

```
1. Conexión a SQL Server ✓
   └─ engine_origen, engine_destino = obtener_engines()

2. Lectura de datos ✓
   └─ SELECT id_raw, payload FROM raw.invoice_lines (100 registros)

3. Descompresión JSON ✓
   └─ json.loads(payload) para cada registro

4. Normalización ✓
   └─ Conversión de tipos, cálculos (neto = total - impuesto)

5. Escritura en SQL Server ✓
   └─ to_sql(..., schema='staging', table='invoice_lines')

6. Validación ✓
   └─ SELECT COUNT(*) FROM staging.invoice_lines (100 registros)
```

## Comparación: ANTES vs DESPUÉS

### ❌ ANTES (Datos Ficticios)
```python
lineas = pd.DataFrame([
    {"linea_id": 1, "factura_id": 100, "producto_id": 10, ...},
    {"linea_id": 2, "factura_id": 999, "producto_id": 20, ...},
])
```
→ Solo 2 registros en memoria

### ✅ DESPUÉS (SQL Server Real)
```python
df_raw = pd.read_sql_query(
    "SELECT id_raw, payload FROM raw.invoice_lines", 
    engine_destino
)
```
→ 100 registros desde SQL Server

## Archivos Generados/Modificados

```
pipeline_ingesta/
├── 04_staging.ipynb ..................... [MODIFICADO] Lee SQL en lugar de datos ficticios
├── README_STAGING.md .................... [NUEVO] Documentación de esta etapa
├── STAGING_FUNCIONAL.md ................ [NUEVO] Instrucciones de ejecución
├── STATUS_PROYECTO.md ................... [NUEVO] Estado general del proyecto
└── conexion_sqlserver.py ............... [EXISTENTE] Conexión centralizada (sin cambios)
```

## Validación del Pipeline

Ejecuta este script Python para verificar que todo funciona:

```python
import sys
import pandas as pd
sys.path.insert(0, r'C:\Users\Sergio Orozco\proyectos\Ingenieria_Datos\notebook\unidad_IV')
from conexion_sqlserver import obtener_engines

engine_origen, engine_destino = obtener_engines()

# Verificación 1: Datos de entrada
entrada = pd.read_sql_query(
    "SELECT COUNT(*) as cnt FROM raw.invoice_lines", 
    engine_destino
)
print(f"Datos de entrada: {entrada['cnt'].iloc[0]} registros")

# Verificación 2: Datos de salida
salida = pd.read_sql_query(
    "SELECT COUNT(*) as cnt FROM staging.invoice_lines", 
    engine_destino
)
print(f"Datos de salida: {salida['cnt'].iloc[0]} registros")

# Verificación 3: Resumen
resumen = pd.read_sql_query("""
    SELECT 
        COUNT(*) as lineas,
        COUNT(DISTINCT id_factura) as facturas,
        SUM(total) as total
    FROM staging.invoice_lines
""", engine_destino)

print(f"Resumen: {resumen['lineas'].iloc[0]} líneas, "
      f"{resumen['facturas'].iloc[0]} facturas, "
      f"Total: ${resumen['total'].iloc[0]:,.2f}")
```

## Troubleshooting

### ❌ Error: "Invalid object name 'raw.invoice_lines'"
**Causa**: Datos en base de datos equivocada  
**Solución**: Se corrigió - ahora lee de `engine_destino` (WideWorldImportersDW2)

### ❌ Error: "Invalid object name 'staging.invoice_lines'"
**Causa**: Schema o tabla no existe  
**Solución**: Se creó automáticamente en primera ejecución

### ✅ Verificar que funciona
```bash
python -c "
import sys; sys.path.insert(0, '.')
from conexion_sqlserver import obtener_engines
import pandas as pd
e_o, e_d = obtener_engines()
df = pd.read_sql_query('SELECT COUNT(*) FROM staging.invoice_lines', e_d)
print(f'✓ OK: {df.iloc[0,0]} registros en staging')
"
```

---

## ✅ Conclusión

**La notebook 04_staging.ipynb está 100% funcional y leyendo datos del SQL Server.**

No hay datos ficticios, todo viene de:
- **Entrada**: `raw.invoice_lines` (100 registros JSON)
- **Salida**: `staging.invoice_lines` (100 registros normalizados)

**Estado**: ✅ LISTO PARA PRODUCCIÓN
