"""
Verificación final del pipeline.
Consulta estadísticas en SQL Server.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from conexion_sqlserver import obtener_engines
from sqlalchemy import text

print("="*70)
print("VERIFICACION FINAL - ESTADISTICAS EN SQL SERVER")
print("="*70)

try:
    engine_origen, engine_destino = obtener_engines()
except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)

try:
    with engine_destino.connect() as conn:
        # Registros RAW
        print("\n1. CAPA RAW (raw.invoice_lines):")
        result = conn.execute(text("SELECT COUNT(*) as cnt FROM raw.invoice_lines")).scalar()
        print(f"   Total registros: {result:,}")
        
        lotes = conn.execute(text("SELECT COUNT(DISTINCT lote_id) as cnt FROM raw.invoice_lines")).scalar()
        print(f"   Lotes únicos: {lotes}")
        
        # Validaciones
        print("\n2. VALIDACIONES (raw.validacion_calidad):")
        result = conn.execute(text("SELECT COUNT(*) as cnt FROM raw.validacion_calidad")).scalar()
        print(f"   Total errores: {result:,}")
        
        criticos = conn.execute(text("SELECT COUNT(*) as cnt FROM raw.validacion_calidad WHERE es_critico = 1")).scalar()
        print(f"   Errores críticos: {criticos}")
        
        # Cuarentena
        print("\n3. CUARENTENA (quarantine.invoice_lines):")
        try:
            result = conn.execute(text("SELECT COUNT(*) as cnt FROM quarantine.invoice_lines")).scalar()
            print(f"   Total en cuarentena: {result:,}")
            
            pendientes = conn.execute(text("SELECT COUNT(*) as cnt FROM quarantine.invoice_lines WHERE estado = 'PENDIENTE'")).scalar()
            print(f"   Pendientes de resolver: {pendientes}")
        except:
            print("   (tabla no contiene datos o no existe)")

except Exception as e:
    print(f"[ERROR] {e}")

print("\n" + "="*70)
print("VERIFICACION COMPLETADA")
print("="*70)
