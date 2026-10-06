# Laboratorio local - Calidad y gobierno del dato

## Alcance

Estos ejemplos se ejecutan en **Python local**, sin Databricks, Spark, cuentas cloud, SQL Server ni Great Expectations. pandas es la unica biblioteca externa utilizada para procesar tablas. `sqlite3`, `decimal`, `json`, `hashlib`, `hmac`, `secrets` y `unittest` forman parte de la biblioteca estandar de Python.

Jupyter e IPython proporcionan las celdas y la visualizacion de resultados; no son plataformas de procesamiento distribuido. `nbformat` y `nbclient` permiten comprobar y ejecutar notebooks automaticamente. Las dependencias se encuentran en [requirements.txt](requirements.txt).

El [manual de gobierno, calidad y DAMA](../../manueles/gobierno_del_dato/01_manual_gobierno_calidad_y_DAMA.md) explica politicas, roles, referencias, aprobaciones y medidas de produccion. Los notebooks implementan una demostracion, no una certificacion de conformidad con DAMA o normas ISO.

## Paso 1 - Preparar Python

Usar Python 3.10 o posterior. En una terminal PowerShell ubicada en la raiz del repositorio, crear un entorno dedicado si aun no existe:

```powershell
py -m venv notebook/unidad_III/.venv
```

Instalar dependencias usando explicitamente ese ejecutable evita modificar el entorno de otras unidades:

```powershell
.\notebook\unidad_III\.venv\Scripts\python.exe -m pip install -r notebook/unidad_III/requirements.txt
```

No hace falta activar el entorno ni cambiar la politica de ejecucion de PowerShell para utilizar el ejecutable directamente. La instalacion inicial descarga paquetes; las celdas no requieren Internet una vez instalados.

## Paso 2 - Seleccionar el kernel local

En VS Code, abrir un notebook, elegir **Seleccionar kernel**, seleccionar entornos Python y elegir el interprete de `notebook/unidad_III/.venv`. No elegir un cluster remoto.

Para usar tambien ese entorno desde otra interfaz Jupyter, se puede registrar un kernel local:

```powershell
.\notebook\unidad_III\.venv\Scripts\python.exe -m ipykernel install --user --name gobierno-datos-local --display-name "Python - Gobierno de datos local"
```

La seleccion del kernel determina que Python ejecuta las celdas. Instalar un paquete en una terminal distinta no garantiza que este disponible en el kernel seleccionado.

## Paso 3 - Ejecutar los ejemplos

| Notebook | Contenido | Resultado a comprobar |
| --- | --- | --- |
| [01 - Profiling](01_profiling_y_dimensiones.ipynb) | Blancos, tipos, parseo, dimensiones de calidad y referencia parcial de exactitud. | 12 filas: 4 aptas y 8 en cuarentena; exactitud evaluable solo en 2. |
| [02 - Contrato y reglas](02_contrato_y_reglas_calidad.ipynb) | Finalidad, Owner, version, esquema, acciones y puerta de publicacion. | Lote bloqueado y 5 pruebas `unittest` aprobadas. |
| [03 - ETL gobernado](03_etl_gobernado_y_cuarentena.ipynb) | Auditoria, hallazgos, integridad, minimizacion, carga y reconciliacion por moneda. | Subconjunto apto publicado, recarga sin duplicados y rollback ante conflicto. |
| [04 - Metadatos y privacidad](04_metadatos_linaje_y_privacidad.ipynb) | Glosario, catalogo, linaje por campo, vistas simuladas y HMAC. | Vista analitica sin email, rol no autorizado rechazado y token sin imprimir secreto. |
| [05 - Monitoreo e incidentes](05_monitoreo_e_incidentes.ipynb) | Tasas con denominadores, deriva de esquema, incidente y recuperacion. | Bloqueo de degradacion y recuperacion sin relajar umbrales. |

El orden es pedagogico. Cada notebook genera sus propios datos y puede ejecutarse de manera independiente. Ejecutar todas sus celdas de arriba hacia abajo; para repetir una demostracion, reiniciar el kernel y volver a ejecutarlo completo.

Las celdas de preparacion localizan [gobierno_demo.py](gobierno_demo.py) desde la raiz del repositorio o la carpeta de los notebooks. Ese modulo contiene solo el nucleo utilizado por los cinco ejemplos: datos ficticios, normalizacion, evaluacion por fila y sus auxiliares de esquema, importes e identificadores. Si aparece un error de ruta, comprobar el directorio de trabajo del kernel. Si aparece `ModuleNotFoundError`, comprobar el interprete seleccionado y la instalacion de requisitos.

Las funciones especificas estan definidas y explicadas en las celdas de cada notebook: profiling en el 01; puerta del contrato en el 02; carga SQLite y auditoria en el 03 y el 05; catalogo, linaje, tokenizacion y vistas en el 04. Las funciones de carga se muestran en ambos ejemplos para que ninguno dependa de ejecutar el otro. No es necesario buscar esas implementaciones en un archivo externo.

## Paso 4 - Interpretar los errores esperados

Un notebook correcto puede demostrar un lote BLOQUEADO, un acceso denegado o un conflicto revertido. Los errores previstos se capturan y verifican con aserciones. Un traceback no previsto o una asercion fallida si requieren investigacion.

La puerta de publicacion permite un maximo de 20% de filas rechazadas en este caso ficticio. El umbral es una decision didactica, no una obligacion de ISO o DAMA. Las advertencias no equivalen a filas rechazadas y varias reglas pueden fallar sobre una sola fila.

Publicar el subconjunto apto de prueba **no corrige el lote original**: las 8 filas defectuosas permanecen pendientes de investigacion. No eliminar datos reales para hacer pasar un indicador.

## Paso 5 - Comprender los limites

- Se usan ventas ficticias y dominios de email `.invalid`; no introducir datos personales reales.
- SQLite trabaja en memoria: al cerrar la conexion se pierden ventas, auditoria y hallazgos. La persistencia es un ejercicio posterior.
- Los rechazos completos se conservan en un dataframe; la base registra hallazgos, no una cuarentena durable de contenido.
- Las vistas por rol son una simulacion; no autentican ni impiden que quien controla el proceso lea el dataframe original.
- HMAC seudonimiza, no anonimiza ni cifra. Las claves efimeras no permiten vinculacion estable entre sesiones.
- El linaje JSON se inspira en W3C PROV, sin declarar conformidad con su formato.
- La referencia de exactitud es parcial y ficticia; no demuestra exactitud de toda la poblacion.
- Los metadatos con retencion pendiente, las aprobaciones simuladas y los eventos en memoria deben reemplazarse por decisiones y evidencias reales antes de produccion.

Leer las funciones locales junto con las explicaciones y ejercicios permite entender que partes son controles tecnicos y cuales son responsabilidades de gobierno. El modulo comun se consulta solo para el caso de datos y las reglas de base que comparten los cinco ejemplos.
