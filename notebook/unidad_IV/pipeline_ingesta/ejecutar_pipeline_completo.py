"""
Ejecutor de Pipeline Completo
Ejecuta los 3 pasos del pipeline de ingesta.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

PIPELINE_DIR = Path(__file__).parent
PASOS = [
    ('01', 'ejecutar_01_extraccion.py', 'Extracción a capa RAW'),
    ('02', 'ejecutar_02_profiling.py', 'Profiling y validación'),
    ('03', 'ejecutar_03_cuarentena.py', 'Cuarentena y reproceso'),
]

def log_message(msg, level='INFO'):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{timestamp}] [{level}] {msg}')

def main():
    log_message('='*70)
    log_message('INICIO PIPELINE COMPLETO DE INGESTA')
    log_message('='*70)
    
    resultados = []
    tiempo_inicio = datetime.now()
    
    for numero, script, descripcion in PASOS:
        log_message('')
        log_message('-'*70)
        log_message(f'{numero}. {descripcion}')
        log_message('-'*70)
        
        script_path = PIPELINE_DIR / script
        if not script_path.exists():
            log_message(f'Script no encontrado: {script}', 'ERROR')
            resultados.append((numero, script, 'NO_ENCONTRADO'))
            continue
        
        tiempo_inicio_paso = datetime.now()
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(PIPELINE_DIR),
                capture_output=True,
                text=True,
                timeout=300
            )
            
            tiempo_paso = (datetime.now() - tiempo_inicio_paso).total_seconds()
            
            # Mostrar output
            if result.stdout:
                for linea in result.stdout.split('\n'):
                    if linea.strip():
                        print(f'  {linea}')
            
            if result.returncode == 0:
                log_message(f'COMPLETADO en {tiempo_paso:.1f}s', 'SUCCESS')
                resultados.append((numero, script, 'COMPLETADO'))
            else:
                log_message(f'FALLIDO en {tiempo_paso:.1f}s', 'ERROR')
                if result.stderr:
                    for linea in result.stderr.split('\n')[:5]:
                        if linea.strip():
                            log_message(f'  {linea}', 'ERROR')
                resultados.append((numero, script, 'FALLIDO'))
        
        except subprocess.TimeoutExpired:
            log_message('TIMEOUT (más de 5 minutos)', 'ERROR')
            resultados.append((numero, script, 'TIMEOUT'))
        except Exception as e:
            log_message(f'EXCEPCION: {e}', 'ERROR')
            resultados.append((numero, script, 'EXCEPCION'))
    
    # Resumen final
    tiempo_total = (datetime.now() - tiempo_inicio).total_seconds()
    
    log_message('')
    log_message('='*70)
    log_message('RESUMEN FINAL')
    log_message('='*70)
    
    completados = sum(1 for _, _, estado in resultados if estado == 'COMPLETADO')
    fallidos = sum(1 for _, _, estado in resultados if estado != 'COMPLETADO')
    
    log_message(f'Total pasos: {len(resultados)}')
    log_message(f'Completados: {completados}')
    log_message(f'Fallidos: {fallidos}')
    log_message(f'Tiempo total: {tiempo_total:.1f}s')
    log_message('')
    
    for numero, script, estado in resultados:
        symbol = '[OK]' if estado == 'COMPLETADO' else '[XX]'
        log_message(f'{symbol} {numero}: {script} - {estado}')
    
    # Verificar archivos generados
    log_message('')
    log_message('='*70)
    log_message('ARCHIVOS GENERADOS')
    log_message('='*70)
    
    datos_dir = PIPELINE_DIR / 'datos'
    if datos_dir.exists():
        for subdir in ['bronze', 'cuarentena', 'silver', 'gold']:
            subdir_path = datos_dir / subdir
            if subdir_path.exists():
                archivos = list(subdir_path.glob('*'))
                if archivos:
                    total_bytes = sum(a.stat().st_size for a in archivos)
                    log_message(f'{subdir}: {len(archivos)} archivos ({total_bytes:,} bytes)')
                    for archivo in sorted(archivos)[-3:]:
                        tamano = archivo.stat().st_size
                        log_message(f'  - {archivo.name} ({tamano:,} bytes)')
    
    log_message('')
    log_message('='*70)
    log_message('PIPELINE COMPLETADO')
    log_message('='*70)
    
    return 0 if fallidos == 0 else 1

if __name__ == '__main__':
    try:
        exit_code = main()
    except KeyboardInterrupt:
        log_message('Pipeline interrumpido', 'WARNING')
        exit_code = 1
    except Exception as e:
        log_message(f'Error fatal: {e}', 'ERROR')
        exit_code = 1
    
    sys.exit(exit_code)
