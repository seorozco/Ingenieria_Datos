# Pipeline de ventas con auditoria y linaje

Los notebooks ejecutan un flujo real sobre SQL Server: `WideWorldImporters` -> `WideWorldImportersDW2`. La conexion se configura en [conexion_sqlserver.py](conexion_sqlserver.py).

## Ejecucion

Instalar las dependencias del [requirements.txt](requirements.txt), seleccionar el kernel de Python y ejecutar todas las celdas de cada notebook en orden. No hay un ejecutor automatico externo.

```powershell
python -m pip install -r notebook/unidad_IV/pipeline_ingesta/requirements.txt
```

| Paso | Lineas de factura | Cabeceras |
| --- | --- | --- |
| 00 | [Gobierno y catalogo](00_preparacion_gobierno.ipynb) | Compartido |
| 01 | [Extraccion RAW](01_extraccion_raw_invoice_line.ipynb) | [Extraccion RAW](01_extraccion_raw_Invoices.ipynb) |
| 02 | [Profiling](02_profiling_contratos_invoice_line.ipynb) | [Profiling](02_profiling_contratos_Invoices.ipynb) |
| 03 | [Cuarentena](03_cuarentena_reproceso_invoice_line.ipynb) | [Cuarentena](03_cuarentena_reproceso_Invoices.ipynb) |
| 04 | [Staging](04_staging_invoice_line.ipynb) | [Staging](04_staging_Invoices.ipynb) |
| 05 | Dimensiones previamente cargadas en `dw` | Inspeccion auditada en el paso 7 |
| 06 | [Tabla de hechos](06_hechos.ipynb) | Usa ambas ramas |
| 07 | [Auditoria y publicacion](07_auditoria_publicacion.ipynb) | Compartido |
| 08 | [Reporte integral y linaje](08_demo_integral.ipynb) | Compartido |

Completar ambas ramas antes del paso 6. Ejecutar la celda final de cada notebook: una etapa sin cierre queda `EN_CURSO`, no `OK`.

Las cinco dimensiones deben existir antes de cargar hechos. El paso 7 registra el linaje NK -> SK de las versiones observadas y su auditoria, sin modificar dimensiones ni depender de cambios en notebooks externos. Esa inspeccion no reconstruye la auditoria historica de su carga.

## Datos y controles

- RAW conserva payload, `id_raw`, lote y hash SHA-256.
- Profiling registra incidencias y la clasificacion de cada registro.
- Cuarentena aisla errores criticos. Staging excluye cuarentena historica y errores criticos, y retira rechazados cargados previamente.
- `dw.fact_ventas` usa las cinco dimensiones y grano estable `(InvoiceID, InvoiceLineID)`. No se renumeran las lineas al excluir registros.
- Neto es total menos impuesto. Si falta `LineProfit`, margen y costo permanecen NULL.
- El paso 6 bloquea conflictos con hechos existentes; no los sobrescribe ni migra numeracion ordinal automaticamente.
- El paso 7 exige balance, FK, unicidad, reconciliacion y auditoria/linaje de cada etapa. Los hechos aprobados se consultan en `dw.fact_ventas_publicadas`.
- El paso 8 verifica la publicacion vigente y rechazos posteriores, muestra el recorrido del linaje y exporta CSV en `datos/reportes/`.

## Auditoria de cada elemento

[auditoria_pipeline.py](auditoria_pipeline.py) es el modulo compartido; no es un ejecutor de cargas.

Cada etapa registra inicio, resultado o error en `auditoria.ejecuciones_etapa`, relaciones por registro en `auditoria.linaje_registros` y un archivo JSONL propio en `logs/`. Los logs incluyen hora UTC e identificador de ejecucion, pero no payloads ni credenciales. Los errores de celdas se capturan en el kernel; los controles finales detectan resultados no persistidos.

| Elemento | Relacion registrada |
| --- | --- |
| Gobierno | Mapa documental, identificado como METADATOS |
| Extraccion | Clave del origen -> `raw.*.id_raw`, lote y hash |
| Profiling | RAW -> clasificacion persistida en linaje e incidencias SQL |
| Cuarentena | RAW -> `quarantine.*` |
| Staging | RAW -> `staging.*`, lote y hash |
| Dimensiones | Clave natural -> clave sustituta de cada version |
| Hechos | Dos registros de staging y cinco dimensiones -> hecho |
| Publicacion | Hecho -> vista publicada, con identificador de publicacion |
| Reporte | Hecho publicado -> archivo generado |

`calidad:`, `catalogo:` y `archivo:` identifican destinos logicos de clasificacion, metadatos y archivos; no son tablas de negocio inexistentes. Sus relaciones quedan en la tabla real de linaje.

El paso 7 guarda tambien `auditoria.publicaciones` y `auditoria.linaje_ventas`: un vinculo directo reconstruido y reconciliado entre cada hecho y sus dos registros RAW. La falta de auditoria historica no se reemplaza por un exito inventado: la publicacion se bloquea e informa los puntos faltantes.

Las relaciones y el estado OK se confirman juntos al cierre de cada etapa. No existe una unica transaccion global para todas las cargas: si falla la auditoria no se revierten automaticamente cargas previas, pero se bloquea su publicacion.

## Requisitos operativos

SQL Server y ODBC Driver 17/18 deben estar disponibles. La cuenta de destino necesita permisos para las cargas y para crear tablas/vistas y escribir auditoria. Gobierno no implementa permisos, anonimizado ni retencion; los reportes pueden contener datos comerciales y nombres.

Esta actualizacion se verifico con datos y bases temporales, sin ejecutar cargas contra SQL Server. Se conservan los datos y logs existentes; los reportes antiguos de conteos fijos no son evidencia de las ejecuciones nuevas.
