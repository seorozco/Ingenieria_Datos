# 📑 INDICE COMPLETO DE DOCUMENTACIÓN Y RECURSOS

## 🚀 Punto de Entrada Recomendado

### Según tu rol:

| Rol | Comienza por | Tiempo | Siguiente |
|-----|-------------|--------|-----------|
| **Usuario nuevo** | [GUIA_RAPIDA.md](GUIA_RAPIDA.md) | 30 min | [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md) |
| **Manager/Jefe** | [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md) | 5 min | [README.md](README.md) |
| **Developer** | [README.md](README.md) | 10 min | [CONEXION_SQLSERVER.md](CONEXION_SQLSERVER.md) |
| **Data Engineer** | [CONEXION_SQLSERVER.md](CONEXION_SQLSERVER.md) | 15 min | [VERIFICACION_FINAL.md](VERIFICACION_FINAL.md) |
| **QA/DQA** | [VERIFICACION_FINAL.md](VERIFICACION_FINAL.md) | 20 min | [RESUMEN_CAMBIOS.md](RESUMEN_CAMBIOS.md) |

---

## 📚 Documentación Completa

### 1. 🏠 README.md (Punto de Entrada Principal)
**Para:** Todos  
**Duración:** 10 minutos  
**Contenido:**
- Descripción general del proyecto
- Arquitectura del pipeline
- Comandos principales
- Estructura de carpetas
- Inicio rápido (30 segundos)

**Ir a:** [README.md](README.md)

---

### 2. 🏃 GUIA_RAPIDA.md (Quick Start)
**Para:** Usuarios nuevos que quieren empezar YA  
**Duración:** 30 minutos  
**Contenido:**
- Pasos para ejecutar pipeline
- Ver resultados (3 formas)
- Casos de uso comunes
- Solución de problemas
- Referencia de comandos

**Ir a:** [GUIA_RAPIDA.md](GUIA_RAPIDA.md)

---

### 3. 👔 RESUMEN_EJECUTIVO.md (Para Directivos)
**Para:** Managers, stakeholders, directivos  
**Duración:** 5 minutos  
**Contenido:**
- Objetivo logrado
- Resultados demostrados
- Arquitectura implementada
- Métricas de éxito
- Próximos pasos

**Ir a:** [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md)

---

### 4. 🔧 CONEXION_SQLSERVER.md (Técnico)
**Para:** Developers, data engineers, técnicos  
**Duración:** 15 minutos  
**Contenido:**
- Cómo funciona el módulo
- Cómo usarlo en código
- Funciones disponibles
- Ejemplos avanzados
- Troubleshooting técnico

**Ir a:** [CONEXION_SQLSERVER.md](CONEXION_SQLSERVER.md)

---

### 5. ✅ VERIFICACION_FINAL.md (Checklist Completo)
**Para:** QA, DQA, testers, verificadores  
**Duración:** 20 minutos  
**Contenido:**
- Checklist de objetivos
- Funcionalidades implementadas
- Resultados de pruebas
- Métricas de éxito
- Lecciones aprendidas

**Ir a:** [VERIFICACION_FINAL.md](VERIFICACION_FINAL.md)

---

### 6. 📝 RESUMEN_CAMBIOS.md (Historial)
**Para:** Auditoría, revisión, historial  
**Duración:** 15 minutos  
**Contenido:**
- Cambios realizados en sesión 1
- Cambios realizados en sesión 2
- Cambios realizados en sesión 3
- Cambios realizados en sesión 4
- Estructura completa de directorios

**Ir a:** [RESUMEN_CAMBIOS.md](RESUMEN_CAMBIOS.md)

---

### 7. 💡 REFERENCIA_RAPIDA.txt (Code Snippets)
**Para:** Copy & paste rápido  
**Duración:** 5 minutos  
**Contenido:**
- Ejemplos de conexión
- Consultas SQL útiles
- Snippets de Python
- Comandos PowerShell

**Ir a:** [REFERENCIA_RAPIDA.txt](REFERENCIA_RAPIDA.txt)

---

## 🐍 Scripts Python Disponibles

### En carpeta `pipeline_ingesta/`

#### 1. `ejecutar_pipeline_completo.py` ⭐ (PRINCIPAL)
```bash
# Ejecuta los 3 pasos del pipeline automáticamente
python ejecutar_pipeline_completo.py
```
**Hace:** Extrae → Valida → Cuarentena → Reporta  
**Tiempo:** ~15 segundos  
**Output:** Reporte en consola + datos en BD + archivos CSV

---

#### 2. `ejecutar_01_extraccion.py` (Paso 1)
```bash
# Solo extrae datos
python ejecutar_01_extraccion.py
```
**Hace:** Extrae 100 registros de WideWorldImporters  
**Genera:** 
- Tabla `raw.invoice_lines` en BD destino
- 4 archivos CSV en `datos/bronze/`

---

#### 3. `ejecutar_02_profiling.py` (Paso 2)
```bash
# Solo valida datos
python ejecutar_02_profiling.py
```
**Hace:** Valida calidad de 100 registros  
**Genera:**
- Tabla `raw.validacion_calidad` en BD
- Reportes en `datos/bronze/`

---

#### 4. `ejecutar_03_cuarentena.py` (Paso 3)
```bash
# Solo aísla problemas
python ejecutar_03_cuarentena.py
```
**Hace:** Identifica registros con errores críticos  
**Genera:**
- Tabla `quarantine.invoice_lines` en BD
- Archivos en `datos/cuarentena/`

---

#### 5. `verificar_bd.py` (Verificación)
```bash
# Ver resultados
python verificar_bd.py
```
**Hace:** Consulta estadísticas en BD  
**Muestra:**
- Cantidad de registros por tabla
- Status de validación
- Registros en cuarentena

---

### En carpeta raíz `notebook/unidad_IV/`

#### `conexion_sqlserver.py` (Módulo Central)
```python
from conexion_sqlserver import obtener_engines

engine_origen, engine_destino = obtener_engines()
# Ahora puedes usar en pandas, sqlalchemy, etc.
```

---

## 📊 Estructura de Datos

### Base de Datos: `WideWorldImportersDW2`

```
└─ Schema: raw
   ├─ Tabla: invoice_lines (100 registros)
   │  ├─ lote_id: STRING - ID único del batch
   │  ├─ tabla_origen: STRING - Tabla origen
   │  ├─ numero_fila: INT - Fila en origen
   │  ├─ payload: JSON - Datos originales
   │  ├─ hash_sha256: STRING - Hash de integridad
   │  └─ fecha_carga: DATETIME - Timestamp
   │
   └─ Tabla: validacion_calidad (100 registros)
      ├─ lote_id: STRING
      ├─ tabla_origen: STRING
      ├─ numero_fila: INT
      ├─ tipo_error: STRING - OK/NULO/NEGATIVO
      ├─ campo_con_error: STRING
      └─ fecha_validacion: DATETIME

└─ Schema: quarantine
   └─ Tabla: invoice_lines (0 registros)
      ├─ lote_id: STRING
      ├─ payload: JSON
      ├─ tipo_error: STRING
      └─ fecha_cuarentena: DATETIME
```

---

## 📁 Archivos Generados

### Carpeta `datos/bronze/` (RAW data)
```
raw_invoice_lines_LOTE_01.csv    (35.7 KB)
raw_invoice_lines_LOTE_02.csv    (35.7 KB)
raw_invoice_lines_LOTE_03.csv    (35.7 KB)
raw_invoice_lines_LOTE_04.csv    (35.7 KB)
reporte_calidad_LOTE_01.csv      (reportes)
reporte_calidad_LOTE_02.csv      (reportes)
```

### Carpeta `datos/cuarentena/` (Errores)
```
(vacía - sin registros problemáticos)
```

---

## 🔍 Búsqueda Rápida

### "Quiero..."

#### ...ejecutar el pipeline
→ [GUIA_RAPIDA.md](GUIA_RAPIDA.md#-inicio-rápido-30-segundos)

#### ...entender la arquitectura
→ [README.md](README.md#-arquitectura) + [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md#-arquitectura-implementada)

#### ...usar en Python
→ [REFERENCIA_RAPIDA.txt](REFERENCIA_RAPIDA.txt) + [CONEXION_SQLSERVER.md](CONEXION_SQLSERVER.md#-cómo-usar-en-python)

#### ...ver resultados en BD
→ [GUIA_RAPIDA.md](GUIA_RAPIDA.md#-ver-resultados)

#### ...solucionar un problema
→ [GUIA_RAPIDA.md](GUIA_RAPIDA.md#-solución-de-problemas)

#### ...revisar lo que se hizo
→ [VERIFICACION_FINAL.md](VERIFICACION_FINAL.md) + [RESUMEN_CAMBIOS.md](RESUMEN_CAMBIOS.md)

#### ...copiar código de ejemplo
→ [REFERENCIA_RAPIDA.txt](REFERENCIA_RAPIDA.txt)

#### ...entender credenciales
→ [CONEXION_SQLSERVER.md](CONEXION_SQLSERVER.md#configuración)

---

## 🎯 Tabla de Navegación Rápida

| Necesito | Archivo | Sección |
|----------|---------|---------|
| Empezar YA | GUIA_RAPIDA.md | Inicio Rápido |
| Entender qué es | README.md | Qué es Este Proyecto |
| Ver arquitectura | README.md | Arquitectura |
| Resultados del proyecto | RESUMEN_EJECUTIVO.md | Resultados Demostrados |
| Ver checklist | VERIFICACION_FINAL.md | Verificación Final |
| Código de ejemplo | REFERENCIA_RAPIDA.txt | Todo |
| Historial de cambios | RESUMEN_CAMBIOS.md | Todo |
| Módulo de conexión | CONEXION_SQLSERVER.md | Todo |
| Solucionar problemas | GUIA_RAPIDA.md | Solución de Problemas |
| Configurar credenciales | CONEXION_SQLSERVER.md | Configuración |
| Comandos disponibles | GUIA_RAPIDA.md | Referencia Rápida |

---

## 📞 Flujos de Soporte

### "No funciona"
1. Lee: [GUIA_RAPIDA.md](GUIA_RAPIDA.md#-solución-de-problemas)
2. Verifica: `python verificar_db.py`
3. Revisa: Errores en `pipeline_ingesta/logs/`

### "Quiero entender mejor"
1. Lee: [README.md](README.md)
2. Lee: [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md)
3. Explora: Los scripts Python

### "Quiero modificar el código"
1. Lee: [CONEXION_SQLSERVER.md](CONEXION_SQLSERVER.md)
2. Consulta: [REFERENCIA_RAPIDA.txt](REFERENCIA_RAPIDA.txt)
3. Revisa: [RESUMEN_CAMBIOS.md](RESUMEN_CAMBIOS.md) para ver estructura

### "Necesito verificar que todo funciona"
1. Lee: [VERIFICACION_FINAL.md](VERIFICACION_FINAL.md)
2. Ejecuta: `python ejecutar_pipeline_completo.py`
3. Verifica: `python verificar_bd.py`

---

## 🎓 Ruta de Aprendizaje Recomendada

### Día 1: Introducción (2 horas)
- [ ] Leer [README.md](README.md) (10 min)
- [ ] Leer [GUIA_RAPIDA.md](GUIA_RAPIDA.md) (30 min)
- [ ] Ejecutar `python ejecutar_pipeline_completo.py` (5 min)
- [ ] Ver archivos generados en `datos/bronze/` (5 min)
- [ ] Ejecutar `python verificar_bd.py` (2 min)

### Día 2: Comprensión Profunda (2 horas)
- [ ] Leer [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md) (5 min)
- [ ] Leer [CONEXION_SQLSERVER.md](CONEXION_SQLSERVER.md) (15 min)
- [ ] Explorar scripts Python (30 min)
- [ ] Ejecutar pasos individuales (20 min)
- [ ] Experimentar en Jupyter (30 min)

### Día 3: Dominación (2 horas)
- [ ] Leer [VERIFICACION_FINAL.md](VERIFICACION_FINAL.md) (20 min)
- [ ] Leer [RESUMEN_CAMBIOS.md](RESUMEN_CAMBIOS.md) (15 min)
- [ ] Modificar scripts (30 min)
- [ ] Crear consultas personalizadas (30 min)
- [ ] Documentar tus cambios (25 min)

---

## 💾 Dónde Encontrar Cada Cosa

| Qué | Dónde |
|-----|-------|
| Scripts ejecutables | `pipeline_ingesta/` |
| Módulo de conexión | `conexion_sqlserver.py` |
| Documentación | Archivos `.md` en raíz |
| Datos procesados | `pipeline_ingesta/datos/bronze/` |
| Registros problemáticos | `pipeline_ingesta/datos/cuarentena/` |
| Configuración de BD | `conexion_sqlserver.py` líneas 15-20 |
| Ejemplos de uso | `REFERENCIA_RAPIDA.txt` |
| Historial de cambios | `RESUMEN_CAMBIOS.md` |

---

## 🎯 Objetivo Completado

```
✅ Crear conexión centralizada a SQL Server
✅ Implementar extracción RAW (PASO 1)
✅ Implementar validación de calidad (PASO 2)
✅ Implementar cuarentena (PASO 3)
✅ Crear orquestador del pipeline
✅ Crear script de verificación
✅ Documentación completa
✅ Ejemplos de uso
✅ Código comentado
```

---

## 🚀 Próxima Acción

**Elige una opción:**

1. **Ejecutar ahora:**
   ```bash
   cd pipeline_ingesta
   python ejecutar_pipeline_completo.py
   ```

2. **Aprender primero:**
   → Abre [GUIA_RAPIDA.md](GUIA_RAPIDA.md)

3. **Ver resumen ejecutivo:**
   → Abre [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md)

4. **Revisar código:**
   → Abre `pipeline_ingesta/ejecutar_01_extraccion.py`

---

**Última actualización:** 2026-11-03  
**Versión:** 1.0  
**Estado:** ✅ Completado
