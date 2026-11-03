# RESUMEN DE CAMBIOS: Conexión Centralizada a SQL Server

## ¿Qué se ha hecho?

Se ha implementado un **módulo centralizado de conexión a SQL Server** que permite a todos los notebooks del pipeline `unidad_IV/pipeline_ingesta/` obtener datos del SQL Server usando las mismas credenciales y configuración.

---

## Archivos Creados

### 1. **conexion_sqlserver.py** (módulo principal)
Ubicación: `C:\Users\Sergio Orozco\proyectos\Ingenieria_Datos\notebook\unidad_IV\`

**Contenido:**
- Parámetros centralizados de conexión:
  - Servidor: `localhost\SQLEXPRESS02`
  - Base origen: `WideWorldImporters`
  - Base destino: `WideWorldImportersDW2`
  - Usuario: `ingesta_reader`
  - Contraseña: `123456789`

- Función `obtener_engines()`: Retorna dos engines SQLAlchemy (origen y destino)
- Función `construir_engine()`: Constructor interno con detección automática de ODBC driver
- Función `test_conexion()`: Verifica que ambas conexiones funcionan
- Detección automática de ODBC Driver 17 o 18

**Uso:**
```python
from conexion_sqlserver import obtener_engines
engine_origen, engine_destino = obtener_engines()
```

---

### 2. **actualizar_notebooks.py** (script de inyección)
Ubicación: `C:\Users\Sergio Orozco\proyectos\Ingenieria_Datos\notebook\unidad_IV\`

**Función:** Automáticamente añade una celda de conexión al inicio de cada notebook en el pipeline.

**Resultado:** 8 notebooks actualizados (02-08), 1 saltado (00 = solo educativo)

**Celdas inyectadas:**
```python
import sys
sys.path.insert(0, '..')
from conexion_sqlserver import obtener_engines, SERVIDOR, BD_ORIGEN, BD_DESTINO, USUARIO
engine_origen, engine_destino = obtener_engines()
```

---

### 3. **CONEXION_SQLSERVER.md** (documentación)
Guía completa en Markdown con:
- Descripción del módulo
- Ejemplos de uso
- Troubleshooting
- Consideraciones de seguridad
- Modificación de credenciales

---

### 4. **EJEMPLO_USO_CONEXION.ipynb** (notebook de demostración)
Paso a paso completo mostrando:
1. Importación del módulo
2. Lectura desde base origen
3. Creación de esquemas en destino
4. Inserción de datos
5. Verificación
6. Ejecutar SQL complejas
7. Casos comunes

---

### 5. **REFERENCIA_RAPIDA.txt** (cheat sheet)
Referencia rápida con ejemplos cortos para copiar/pegar:
- Importación mínima
- Lectura de datos
- Escritura de datos
- Ejecución de SQL
- Casos comunes

---

## Notebooks Actualizados

Todos estos notebooks ahora tienen una celda de conexión inyectada:

| # | Notebook | Estado | Propósito |
|---|----------|--------|----------|
| 00 | `00_preparacion_gobierno.ipynb` | ⚠ Sin cambios | Material educativo (no conecta) |
| 01 | `01_extraccion_raw.ipynb` | ✅ Actualizado | Extracción a capa RAW |
| 02 | `02_profiling_contratos.ipynb` | ✅ Actualizado | Análisis de calidad |
| 03 | `03_cuarentena_reproceso.ipynb` | ✅ Actualizado | Gestión de rechazos |
| 04 | `04_staging.ipynb` | ✅ Actualizado | Transformaciones iniciales |
| 05 | `05_dimensiones.ipynb` | ✅ Actualizado | Construcción de dimensiones |
| 06 | `06_hechos.ipynb` | ✅ Actualizado | Tabla de hechos |
| 07 | `07_auditoria_publicacion.ipynb` | ✅ Actualizado | Auditoría y publicación |
| 08 | `08_demo_integral.ipynb` | ✅ Actualizado | Demostración completa |

---

## Cómo Usar

### Opción 1: En cualquier notebook actualizado
Simplemente ejecuta la celda de conexión que ya está inyectada:

```python
# Esta celda ya viene en el notebook
engine_origen, engine_destino = obtener_engines()
```

### Opción 2: En un nuevo notebook
Copia estas 4 líneas al inicio:

```python
import sys
sys.path.insert(0, '..')
from conexion_sqlserver import obtener_engines, SERVIDOR, BD_ORIGEN, BD_DESTINO
engine_origen, engine_destino = obtener_engines()
```

### Opción 3: Lectura de datos
```python
import pandas as pd

df = pd.read_sql_query("SELECT TOP 10 * FROM Sales.Customers", engine_origen)
```

### Opción 4: Escritura de datos
```python
df.to_sql('tabla_destino', engine_destino, schema='dw', if_exists='append', index=False)
```

---

## Estructura de Archivos

```
unidad_IV/
├── conexion_sqlserver.py              ← Módulo principal (NUEVA)
├── actualizar_notebooks.py            ← Script de inyección (NUEVA)
├── CONEXION_SQLSERVER.md              ← Documentación (NUEVA)
├── EJEMPLO_USO_CONEXION.ipynb         ← Demo (NUEVA)
├── REFERENCIA_RAPIDA.txt              ← Cheat sheet (NUEVA)
├── 01_kimball_create_DIM.ipynb        ← Referencia original (sin cambios)
├── requirements.txt
└── pipeline_ingesta/
    ├── 00_preparacion_gobierno.ipynb     (sin cambios - educativo)
    ├── 01_extraccion_raw.ipynb          (✅ con conexión)
    ├── 02_profiling_contratos.ipynb     (✅ con conexión)
    ├── 03_cuarentena_reproceso.ipynb    (✅ con conexión)
    ├── 04_staging.ipynb                 (✅ con conexión)
    ├── 05_dimensiones.ipynb             (✅ con conexión)
    ├── 06_hechos.ipynb                  (✅ con conexión)
    ├── 07_auditoria_publicacion.ipynb   (✅ con conexión)
    ├── 08_demo_integral.ipynb           (✅ con conexión)
    └── README.md
```

---

## Ventajas

✅ **Centralizado:** Una única fuente de verdad para credenciales y configuración

✅ **Reutilizable:** Importa desde cualquier notebook

✅ **Automático:** ODBC driver se detecta automáticamente

✅ **Transacciones:** Manejo seguro de conexiones con contextos

✅ **Educativo:** Ejemplos incluidos en el repo

✅ **Mantenible:** Cambiar credenciales = editar 1 archivo

---

## Cambios en Credenciales

Si necesitas cambiar servidor, usuario o contraseña:

1. Abre `conexion_sqlserver.py`
2. Edita las líneas 18-23:
   ```python
   SERVIDOR = r'tu_servidor\SQLEXPRESS02'
   BD_ORIGEN = 'WideWorldImporters'
   BD_DESTINO = 'WideWorldImportersDW2'
   USUARIO = 'tu_usuario'
   CLAVE = 'tu_clave'
   ```
3. Los cambios aplican automáticamente a todos los notebooks

---

## Seguridad

⚠️ **ADVERTENCIA:** Este es un ejemplo educativo con credenciales hardcodeadas.

En producción, debes implementar:
- Variables de entorno
- Azure Key Vault / AWS Secrets Manager
- Autenticación Windows (si es posible)
- Auditoría de acceso
- Permisos mínimos (principio de menor privilegio)

---

## Troubleshooting

### "No se encontró ODBC Driver"
Instala ODBC Driver 18 desde:
https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

### "Login failed for user"
- Verifica que el usuario existe en SQL Server
- Confirma los permisos
- Valida contraseña correcta

### "Cannot reach server"
- Verifica que SQL Server está ejecutándose
- Confirma nombre/IP del servidor
- Prueba con `sqlcmd`

---

## Próximos Pasos Recomendados

1. **Ejecutar los ejemplos:** Abre `EJEMPLO_USO_CONEXION.ipynb` para ver cómo funciona
2. **Leer la documentación:** Revisa `CONEXION_SQLSERVER.md` para más detalles
3. **Usar en tus notebooks:** Copia el patrón de importación a nuevos notebooks
4. **Versión de producción:** Implementa gestión segura de secretos

---

## Contacto y Ayuda

- Ver `CONEXION_SQLSERVER.md` para documentación completa
- Ver `REFERENCIA_RAPIDA.txt` para ejemplos rápidos
- Ejecutar `EJEMPLO_USO_CONEXION.ipynb` para demostración interactiva
- Ver logs en PowerShell si hay errores de conexión

---

**Fecha de creación:** 2026-11-03  
**Versión:** 1.0  
**Autor:** Copilot
