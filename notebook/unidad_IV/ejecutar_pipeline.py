"""
Script para ejecutar el pipeline completo usando nbclient.
Ejecuta cada notebook en orden y recolecta resultados.
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from nbclient import execute
import nbformat

# Configuración
PIPELINE_DIR = Path(__file__).parent / 'pipeline_ingesta'
LOG_DIR = PIPELINE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

NOTEBOOKS = [
    ('01', '01_extraccion_raw_FUNCIONAL.ipynb', 'Extracción a capa RAW'),
    ('02', '02_profiling_contratos_FUNCIONAL.ipynb', 'Profiling y validación de calidad'),
    ('03', '03_cuarentena_reproceso_FUNCIONAL.ipynb', 'Cuarentena y reproceso'),
]

def log_message(msg, level='INFO'):
    """Imprime mensaje con timestamp."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{timestamp}] [{level}] {msg}')

def ejecutar_notebook(notebook_path):
    """
    Ejecuta un notebook usando nbclient.
    Retorna (exitoso, notebook_ejecutado, error_msg)
    """
    try:
        # Leer notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = nbformat.read(f, as_version=4)
        
        log_message(f'  Celdas a ejecutar: {len(notebook.cells)}')
        
        # Ejecutar
        ejecutado = execute(
            notebook,
            timeout=600,  # 10 minutos por notebook
            kernel_name='python3',
            allow_errors=True  # Permitir errores pero continuar
        )
        
        return True, ejecutado, None
    
    except Exception as e:
        return False, None, str(e)

def guardar_notebook(notebook, output_path):
    """Guarda notebook ejecutado."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            nbformat.write(notebook, f)
        return True
    except Exception as e:
        log_message(f'Error al guardar notebook: {e}', 'ERROR')
        return False

def contar_errores_notebook(notebook):
    """Cuenta errores en notebook ejecutado."""
    errores = 0
    for cell in notebook.cells:
        if cell.cell_type == 'code':
            for output in cell.get('outputs', []):
                if output.get('output_type') == 'error':
                    errores += 1
    return errores

def main():
    """Ejecuta el pipeline completo."""
    
    log_message('=' * 70)
    log_message('INICIO DE PIPELINE DE INGESTA DE DATOS')
    log_message('=' * 70)
    log_message(f'Directorio: {PIPELINE_DIR}')
    log_message(f'Logs: {LOG_DIR}')
    log_message(f'Timestamp: {datetime.now().isoformat()}')
    
    resultados = []
    tiempo_inicio = datetime.now()
    
    for numero, notebook_name, descripcion in NOTEBOOKS:
        log_message('')
        log_message('-' * 70)
        log_message(f'{numero}. {descripcion}')
        log_message('-' * 70)
        
        notebook_path = PIPELINE_DIR / notebook_name
        output_filename = notebook_name.replace('.ipynb', f'_EJECUTADO_{datetime.now().strftime("%Y%m%d_%H%M%S")}.ipynb')
        output_path = LOG_DIR / output_filename
        
        if not notebook_path.exists():
            log_message(f'Notebook no encontrado: {notebook_path}', 'ERROR')
            resultados.append({
                'numero': numero,
                'notebook': notebook_name,
                'estado': 'NO_ENCONTRADO',
                'errores': 0,
                'detalles': 'Archivo no existe',
                'tiempo_ejecucion': 0
            })
            continue
        
        log_message(f'Ruta: {notebook_path}')
        log_message(f'Ejecutando...')
        
        tiempo_inicio_nb = datetime.now()
        exitoso, notebook_ejecutado, error_msg = ejecutar_notebook(str(notebook_path))
        tiempo_ejecucion = (datetime.now() - tiempo_inicio_nb).total_seconds()
        
        if exitoso:
            # Contar errores en la ejecución
            num_errores = contar_errores_notebook(notebook_ejecutado)
            
            # Guardar notebook ejecutado
            guardado = guardar_notebook(notebook_ejecutado, str(output_path))
            
            if num_errores == 0:
                estado = 'COMPLETADO'
                nivel = 'SUCCESS'
            else:
                estado = 'COMPLETADO_CON_ERRORES'
                nivel = 'WARNING'
            
            log_message(f'[{nivel}] Notebook completado en {tiempo_ejecucion:.1f}s', nivel)
            log_message(f'  Errores de ejecución: {num_errores}')
            log_message(f'  Guardado: {output_filename}')
            
            resultados.append({
                'numero': numero,
                'notebook': notebook_name,
                'estado': estado,
                'errores': num_errores,
                'detalles': f'Guardado en {output_filename}',
                'tiempo_ejecucion': tiempo_ejecucion
            })
        else:
            log_message(f'[ERROR] Fallo al ejecutar {notebook_name}', 'ERROR')
            log_message(f'  Detalles: {error_msg[:300]}', 'ERROR')
            log_message(f'  Tiempo: {tiempo_ejecucion:.1f}s')
            
            resultados.append({
                'numero': numero,
                'notebook': notebook_name,
                'estado': 'FALLIDO',
                'errores': -1,
                'detalles': error_msg[:200],
                'tiempo_ejecucion': tiempo_ejecucion
            })
    
    # Resumen final
    tiempo_total = (datetime.now() - tiempo_inicio).total_seconds()
    
    log_message('')
    log_message('=' * 70)
    log_message('RESUMEN FINAL')
    log_message('=' * 70)
    
    total = len(resultados)
    completados = sum(1 for r in resultados if r['estado'] == 'COMPLETADO')
    completados_con_errores = sum(1 for r in resultados if r['estado'] == 'COMPLETADO_CON_ERRORES')
    fallidos = sum(1 for r in resultados if r['estado'] == 'FALLIDO')
    no_encontrados = sum(1 for r in resultados if r['estado'] == 'NO_ENCONTRADO')
    
    log_message(f'Total notebooks: {total}')
    log_message(f'Completados exitosamente: {completados}')
    log_message(f'Completados con errores: {completados_con_errores}')
    log_message(f'Fallidos: {fallidos}')
    log_message(f'No encontrados: {no_encontrados}')
    log_message(f'Tiempo total: {tiempo_total:.1f}s')
    log_message('')
    
    for resultado in resultados:
        if resultado['estado'] == 'COMPLETADO':
            symbol = '[OK]'
        elif resultado['estado'] == 'COMPLETADO_CON_ERRORES':
            symbol = '[WW]'
        else:
            symbol = '[XX]'
        
        tiempo = resultado['tiempo_ejecucion']
        log_message(f'{symbol} {resultado["numero"]}: {resultado["notebook"]} - {resultado["estado"]} ({tiempo:.1f}s)')
    
    log_message('')
    log_message('=' * 70)
    log_message('ARCHIVOS GENERADOS')
    log_message('=' * 70)
    
    # Logs de ejecución
    log_message(f'Directorio logs: {LOG_DIR}')
    if LOG_DIR.exists():
        archivos = list(LOG_DIR.glob('*.ipynb'))
        log_message(f'Notebooks ejecutados: {len(archivos)}')
        for archivo in sorted(archivos)[-5:]:
            log_message(f'  - {archivo.name}')
    
    # Datos generados
    log_message('')
    datos_dir = PIPELINE_DIR / 'datos'
    if datos_dir.exists():
        log_message(f'Datos generados: {datos_dir}')
        for subdir_name in ['bronze', 'cuarentena', 'silver', 'gold']:
            subdir_path = datos_dir / subdir_name
            if subdir_path.exists():
                archivos = list(subdir_path.glob('*'))
                if archivos:
                    total_bytes = sum(os.path.getsize(a) for a in archivos)
                    log_message(f'  {subdir_name}: {len(archivos)} archivos ({total_bytes:,} bytes)')
                    for archivo in sorted(archivos)[-3:]:
                        tamano = os.path.getsize(archivo)
                        log_message(f'    - {archivo.name} ({tamano:,} bytes)')
    
    log_message('')
    log_message('=' * 70)
    log_message('CONEXION A SQL SERVER')
    log_message('=' * 70)
    
    # Verificar datos en BD
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from conexion_sqlserver import obtener_engines
        from sqlalchemy import text
        
        engine_origen, engine_destino = obtener_engines()
        
        with engine_destino.connect() as conn:
            # Contar registros en cada tabla
            tablas = [
                ('raw.invoice_lines', 'Registros RAW'),
                ('raw.validacion_calidad', 'Validaciones'),
                ('quarantine.invoice_lines', 'En cuarentena')
            ]
            
            for tabla, etiqueta in tablas:
                try:
                    result = conn.execute(text(f'SELECT COUNT(*) as cnt FROM {tabla}')).scalar()
                    log_message(f'  {etiqueta}: {result:,} registros')
                except:
                    log_message(f'  {etiqueta}: N/A (tabla no existe)')
    
    except Exception as e:
        log_message(f'No se pudo verificar BD: {e}', 'WARNING')
    
    log_message('')
    log_message('=' * 70)
    log_message('EJECUCION COMPLETADA')
    log_message('=' * 70)
    
    return 0 if fallidos == 0 else 1

if __name__ == '__main__':
    try:
        exit_code = main()
    except KeyboardInterrupt:
        log_message('\nPipeline interrumpido por usuario', 'WARNING')
        exit_code = 1
    except Exception as e:
        log_message(f'\nError fatal: {e}', 'ERROR')
        exit_code = 1
    
    sys.exit(exit_code)
