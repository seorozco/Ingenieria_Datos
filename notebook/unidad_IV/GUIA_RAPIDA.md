# GUÍA RÁPIDA - PIPELINE DE INGESTA DE DATOS

## 🚀 Inicio Rápido (30 segundos)

### 1. Abrir PowerShell o CMD
```bash
# Navega a la carpeta del pipeline
cd C:\Users\Sergio Orozco\proyectos\Ingenieria_Datos\notebook\unidad_IV\pipeline_ingesta
```

### 2. Ejecutar el Pipeline Completo
```bash
python ejecutar_pipeline_completo.py
```

**Esperado:** Verás 3 pasos completándose (~15 segundos total):
```
✓ PASO 1: Extracción desde WideWorldImporters
✓ PASO 2: Validación de calidad
✓ PASO 3: Cuarentena de errores

Resultado: 100 registros procesados, 0 errores
```

---

## 📊 Ver Resultados

### Opción A: En Terminal
```bash
python verificar_bd.py
```

Output:
```
Base de datos: WideWorldImportersDW2
├─ raw.invoice_lines: 100 registros
├─ raw.validacion_calidad: 100 OK, 0 errores
└─ quarantine.invoice_lines: 0 registros
```

### Opción B: Archivos Generados
```
Carpeta: C:\Users\Sergio Orozco\proyectos\Ingenieria_Datos\notebook\unidad_IV\pipeline_ingesta\datos

datos/bronze/
├─ raw_invoice_lines_LOTE_01.csv    ← Datos RAW
├─ raw_invoice_lines_LOTE_02.csv
├─ raw_invoice_lines_LOTE_03.csv
├─ raw_invoice_lines_LOTE_04.csv
└─ reporte_calidad_*.csv              ← Reporte de validación

datos/cuarentena/
└─ (vacío si no hay errores)
```

### Opción C: En SQL Server
```sql
-- Conectar a WideWorldImportersDW2
SELECT * FROM raw.invoice_lines;                    -- 100 registros
SELECT * FROM raw.validacion_calidad;               -- Status de cada uno
SELECT * FROM quarantine.invoice_lines;             -- Si hay errores
```

---

## 🔧 Ejecutar Pasos Individuales

Si necesitas ejecutar un paso específico:

### Solo Extracción
```bash
python ejecutar_01_extraccion.py
# Resultado: Tabla raw.invoice_lines + archivo CSV
```

### Solo Validación
```bash
python ejecutar_02_profiling.py
# Resultado: Tabla raw.validacion_calidad + CSV de errores
```

### Solo Cuarentena
```bash
python ejecutar_03_cuarentena.py
# Resultado: Tabla quarantine.invoice_lines + CSV de cuarentena
```

---

## 📝 Usar en Python/Jupyter

### Importar el módulo de conexión
```python
from conexion_sqlserver import obtener_engines

# Obtener engines
engine_origen, engine_destino = obtener_engines()

# Leer datos
import pandas as pd
df = pd.read_sql_query("SELECT * FROM raw.invoice_lines LIMIT 10", engine_destino)
print(df)

# Escribir datos
df.to_sql('mi_tabla', engine_destino, if_exists='append', index=False)
```

### Ejecutar desde Jupyter
```python
import subprocess
resultado = subprocess.run(
    ["python", "ejecutar_pipeline_completo.py"],
    cwd=r"C:\Users\Sergio Orozco\proyectos\Ingenieria_Datos\notebook\unidad_IV\pipeline_ingesta",
    capture_output=True,
    text=True
)
print(resultado.stdout)
```

---

## 🐛 Solución de Problemas

### ❌ Error: "No module named 'sqlalchemy'"
```bash
pip install sqlalchemy pandas pyodbc
```

### ❌ Error: "Can't connect to SQL Server"
Verificar:
1. SQL Server está corriendo: `Services` → buscar `SQL Server`
2. Usuario existe: `SERVIDOR\ingesta_reader` con contraseña `123456789`
3. Firewall permite puerto 1433

**Si no funcionan los pasos anteriores:**
```bash
python verificar_conexion.py  # Script de diagnóstico
```

### ❌ Error: "Permission denied" en archivos
Verificar que las carpetas tienen permisos de escritura:
```powershell
icacls "C:\Users\Sergio Orozco\proyectos\Ingenieria_Datos\notebook\unidad_IV\pipeline_ingesta\datos" /grant:r "$env:USERNAME`:F" /T
```

### ❌ Error: "No se encuentra el archivo"
Asegúrate de estar en la carpeta correcta:
```bash
cd C:\Users\Sergio Orozco\proyectos\Ingenieria_Datos\notebook\unidad_IV\pipeline_ingesta
dir  # Verifica que ves los archivos .py
```

---

## 📊 Estructura de Datos

### Tabla: raw.invoice_lines
```
Columna              | Tipo       | Descripción
---------------------|------------|----------------------------
lote_id             | STRING     | ID único del batch
tabla_origen        | STRING     | "Sales.InvoiceLines"
numero_fila         | INT        | Fila en la BD origen
payload             | JSON       | Datos originales (preserva formato)
hash_sha256         | STRING     | Hash para integridad
fecha_carga         | DATETIME   | Timestamp de extracción
```

### Tabla: raw.validacion_calidad
```
Columna              | Tipo       | Descripción
---------------------|------------|----------------------------
lote_id             | STRING     | Referencia al batch
tabla_origen        | STRING     | "Sales.InvoiceLines"
numero_fila         | INT        | Fila procesada
tipo_error          | STRING     | "NULO" / "NEGATIVO" / "OK"
campo_con_error     | STRING     | Nombre del campo problemático
valor_problemático  | STRING     | Valor que causó error
fecha_validacion    | DATETIME   | Timestamp
```

### Tabla: quarantine.invoice_lines
```
Columna              | Tipo       | Descripción
---------------------|------------|----------------------------
lote_id             | STRING     | ID del batch
tabla_origen        | STRING     | "Sales.InvoiceLines"
numero_fila         | INT        | Fila en BD origen
payload             | JSON       | Registro completo
tipo_error          | STRING     | Motivo de cuarentena
fecha_cuarentena    | DATETIME   | Timestamp
resuelta            | BIT        | 1=Resuelta, 0=Pendiente
```

---

## 🎯 Casos de Uso Comunes

### 1. "Quiero ver los últimos 100 registros"
```bash
python verificar_bd.py
```

### 2. "Quiero re-ejecutar el pipeline"
```bash
# Los datos anteriores se sobrescriben automáticamente
python ejecutar_pipeline_completo.py
```

### 3. "Quiero extraer más datos (TOP 1000)"
Editar `ejecutar_01_extraccion.py`:
```python
# Línea ~50: Cambiar
query = "SELECT TOP 100 * FROM Sales.InvoiceLines"
# Por:
query = "SELECT TOP 1000 * FROM Sales.InvoiceLines"

# Luego ejecutar
python ejecutar_01_extraccion.py
```

### 4. "Quiero importar datos a mi Notebook"
```python
# En tu Notebook (Jupyter)
import pandas as pd
from conexion_sqlserver import obtener_engines

engine_origen, engine_destino = obtener_engines()
df = pd.read_sql_query("SELECT * FROM raw.invoice_lines", engine_destino)
# Ahora puedes trabajar con df como un DataFrame normal
```

### 5. "Quiero ver qué se extrajo"
```bash
# Ver archivos generados
dir datos\bronze

# Abrir en Excel
start datos\bronze\raw_invoice_lines_LOTE_01.csv
```

---

## 🔐 Seguridad

### ⚠️ IMPORTANTE: Cambiar Contraseña en Producción

El archivo `conexion_sqlserver.py` contiene:
```python
CLAVE = '123456789'  # ← CAMBIAR ESTO EN PRODUCCIÓN
```

**Opciones seguras:**
1. Variables de entorno (recomendado)
```bash
set SQLSERVER_PASSWORD=micontraseña_segura
# Luego en Python:
import os
clave = os.getenv('SQLSERVER_PASSWORD')
```

2. Archivo de configuración externa
```python
import json
with open('config.json') as f:
    config = json.load(f)
    clave = config['password']
```

3. Azure Key Vault
```python
from azure.keyvault.secrets import SecretClient
client = SecretClient(vault_url="...", credential=...)
clave = client.get_secret("sqlserver-password").value
```

---

## 📞 Referencia Rápida de Comandos

| Tarea | Comando |
|-------|---------|
| Ejecutar pipeline completo | `python ejecutar_pipeline_completo.py` |
| Ver datos en BD | `python verificar_bd.py` |
| Solo extracción | `python ejecutar_01_extraccion.py` |
| Solo validación | `python ejecutar_02_profiling.py` |
| Solo cuarentena | `python ejecutar_03_cuarentena.py` |
| Ver archivos | `dir datos\bronze` |
| Abrir archivo CSV | `start datos\bronze\raw_invoice_lines_LOTE_01.csv` |
| Instalar dependencias | `pip install sqlalchemy pandas pyodbc` |

---

## 📚 Documentación Completa

Para más detalles, ver:
- **CONEXION_SQLSERVER.md** - Módulo de conexión (avanzado)
- **RESUMEN_EJECUTIVO.md** - Visión general del proyecto
- **RESUMEN_CAMBIOS.md** - Historial de cambios
- **REFERENCIA_RAPIDA.txt** - Ejemplos de código

---

## ✅ Checklist de Verificación

Después de ejecutar el pipeline, verifica:

- [ ] No hay errores en la consola
- [ ] Se generaron archivos en `datos/bronze`
- [ ] `python verificar_bd.py` muestra 100 registros
- [ ] Tabla `raw.invoice_lines` tiene datos en SQL Server
- [ ] Carpeta `datos/cuarentena` está vacía (sin errores)
- [ ] Tiempo total de ejecución < 30 segundos

---

**¿Necesitas más ayuda?** Ver CONEXION_SQLSERVER.md o ejecuta:
```bash
python ejecutar_pipeline_completo.py --help
```

---

**Última actualización:** 2026-11-03  
**Versión:** 1.0 - Funcional
