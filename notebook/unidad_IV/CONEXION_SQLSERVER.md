# Conexión Centralizada a SQL Server

## Descripción General

Este proyecto utiliza un módulo centralizado de conexión a SQL Server llamado `conexion_sqlserver.py` que proporciona credenciales y configuración unificadas para todos los notebooks del pipeline de ingesta de datos.

## Archivo Principal: `conexion_sqlserver.py`

Este módulo contiene:

- **Parámetros centralizados** de conexión:
  - `SERVIDOR`: Instancia de SQL Server
  - `BD_ORIGEN`: Base de datos de origen (WideWorldImporters)
  - `BD_DESTINO`: Base de datos destino (WideWorldImportersDW2)
  - `USUARIO`: Usuario de ingesta
  - `CLAVE`: Contraseña
  - `ANIO_INICIO` y `ANIO_FIN`: Rango para dimensión tiempo

- **Función `obtener_engines()`**: Retorna dos engines SQLAlchemy
  - `engine_origen`: Conexión a base de datos origen
  - `engine_destino`: Conexión a base de datos destino
  - Valida ambas conexiones automáticamente

- **Función `construir_engine(base_datos)`**: Constructor interno que:
  - Detecta automáticamente el driver ODBC disponible (18 o 17)
  - Configura la cadena de conexión
  - Maneja el TrustServerCertificate

## Uso en Notebooks

### Forma Simple (Recomendada)

En cualquier notebook dentro de `pipeline_ingesta/`, añade una celda al inicio:

```python
import sys
sys.path.insert(0, '..')

from conexion_sqlserver import obtener_engines, SERVIDOR, BD_ORIGEN, BD_DESTINO

# Obtener los engines
engine_origen, engine_destino = obtener_engines()
print(f'Conexion OK: {BD_ORIGEN} -> {BD_DESTINO}')
```

### Uso de los Engines

Con los engines obtenidos, puedes:

```python
import pandas as pd
from sqlalchemy import text

# Leer datos del origen
query = "SELECT TOP 10 * FROM Sales.Customers"
df = pd.read_sql_query(query, engine_origen)

# Escribir datos al destino
df.to_sql('tabla_destino', engine_destino, schema='dw', if_exists='append')

# Ejecutar comandos SQL
with engine_destino.begin() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS dw"))
```

## Notebooks Actualizados

Los siguientes notebooks ya han sido actualizados con la celda de conexión:

1. ✅ `01_extraccion_raw.ipynb` - Extracción a capa RAW
2. ✅ `02_profiling_contratos.ipynb` - Análisis de calidad
3. ✅ `03_cuarentena_reproceso.ipynb` - Gestión de rechazos
4. ✅ `04_staging.ipynb` - Transformaciones iniciales
5. ✅ `05_dimensiones.ipynb` - Construcción de dimensiones
6. ✅ `06_hechos.ipynb` - Construcción de tabla de hechos
7. ✅ `07_auditoria_publicacion.ipynb` - Registro de auditoría
8. ✅ `08_demo_integral.ipynb` - Demostración completa

**Nota:** El notebook `00_preparacion_gobierno.ipynb` es exclusivamente educativo y ejecuta ejemplos en memoria sin conectarse a la base de datos.

## Verificar Conexiones

Prueba manualmente la conexión:

```bash
cd C:\Users\Sergio Orozco\proyectos\Ingenieria_Datos\notebook\unidad_IV
python conexion_sqlserver.py
```

Salida esperada:
```
Servidor: localhost\SQLEXPRESS02
Usuario: ingesta_reader
Base origen: WideWorldImporters
Base destino: WideWorldImportersDW2

✓ Conexión OK (origen): WideWorldImporters
✓ Conexión OK (destino): WideWorldImportersDW2

✓ Todas las conexiones funcionan correctamente.
```

## Requisitos

- **Python 3.8+** con los paquetes:
  - `sqlalchemy` >= 2.0
  - `pyodbc`
  - `pandas`

- **SQL Server** con ODBC Driver 17 o 18 instalado

- **Credenciales**: Usuario `ingesta_reader` con permisos de lectura en origen y lectura/escritura en destino

## Modificar Credenciales

Si necesitas cambiar servidor, usuario o contraseña:

1. Edita `conexion_sqlserver.py` en la sección "Parámetros de conexión centralizados"
2. Los cambios aplicarán automáticamente a todos los notebooks

```python
# Linea ~15-19 en conexion_sqlserver.py
SERVIDOR = r'tu_servidor\SQLEXPRESS02'
BD_ORIGEN = 'WideWorldImporters'
BD_DESTINO = 'WideWorldImportersDW2'
USUARIO = 'tu_usuario'
CLAVE = 'tu_clave'
```

## Seguridad

⚠️ **IMPORTANTE**: Las credenciales están hardcodeadas en este ejemplo educativo.

En producción, debes:

1. Usar variables de entorno: `os.getenv('SQL_SERVER_USER')`
2. Gestionar secretos con Azure Key Vault, AWS Secrets Manager, etc.
3. Implementar autenticación Windows en lugar de SQL
4. Aplicar principio de menor privilegio (permisos mínimos necesarios)
5. Auditar acceso a bases de datos

## Archivos Relacionados

- `01_kimball_create_DIM.ipynb` - Notebook de referencia con explicación de conexión
- `actualizar_notebooks.py` - Script que inyecta la celda de conexión en todos los notebooks
- `README.md` - Documentación general del pipeline

## Troubleshooting

### Error: "No se encontró ODBC Driver"

Instala ODBC Driver 18:
```
https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
```

### Error: "Login failed for user"

- Verifica que el usuario existe en SQL Server
- Confirma permisos en ambas bases de datos
- Valida que la contraseña sea correcta

### Error: "Cannot reach server"

- Verifica que SQL Server está ejecutándose
- Confirma el nombre/IP del servidor
- Prueba con `sqlcmd` desde línea de comandos

## Contacto

Para consultas sobre la conexión o actualizaciones, revisa la documentación del proyecto o contacta al administrador de datos.
