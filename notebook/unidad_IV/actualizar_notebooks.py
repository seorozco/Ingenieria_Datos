"""
Script para actualizar los notebooks del pipeline_ingesta para usar la conexión centralizada.
"""

import json
import os
from pathlib import Path


def crear_celda_importacion():
    """Crea una celda de Python para importar la conexión centralizada."""
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Importar conexión centralizada desde el módulo\n",
            "import sys\n",
            "sys.path.insert(0, '..')\n",
            "\n",
            "from conexion_sqlserver import obtener_engines, SERVIDOR, BD_ORIGEN, BD_DESTINO, USUARIO\n",
            "\n",
            "# Obtener los engines\n",
            "engine_origen, engine_destino = obtener_engines()\n",
            "print(f'Conexiones establecidas correctamente.')\n",
            "print(f'Servidor: {SERVIDOR}')\n",
            "print(f'Origen: {BD_ORIGEN}')\n",
            "print(f'Destino: {BD_DESTINO}')\n"
        ]
    }


def actualizar_notebook(ruta_notebook):
    """Actualiza un notebook para incluir la conexión centralizada."""
    
    with open(ruta_notebook, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    # Verificar si ya existe una celda de conexión
    for cell in notebook.get('cells', []):
        if 'conexion_sqlserver' in ''.join(cell.get('source', [])):
            print(f"  [SKIP] Ya tiene celda de conexion: {ruta_notebook.name}")
            return False
    
    # Insertar la celda de conexión después del primer markdown
    celda_conexion = crear_celda_importacion()
    
    # Encontrar la posición para insertar (después del primer markdown)
    insert_pos = 1
    for i, cell in enumerate(notebook.get('cells', [])):
        if cell['cell_type'] == 'markdown':
            insert_pos = i + 1
            break
    
    notebook['cells'].insert(insert_pos, celda_conexion)
    
    # Guardar el notebook actualizado
    with open(ruta_notebook, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)
    
    print(f"  [OK] Actualizado: {ruta_notebook.name}")
    return True


def main():
    """Actualiza todos los notebooks en pipeline_ingesta."""
    
    pipeline_dir = Path(__file__).parent / 'pipeline_ingesta'
    notebooks = sorted(pipeline_dir.glob('*.ipynb'))
    
    print(f"\nActualizando {len(notebooks)} notebooks en {pipeline_dir}\n")
    
    actualizados = 0
    for notebook_path in notebooks:
        if actualizar_notebook(notebook_path):
            actualizados += 1
    
    print(f"\n[DONE] Se actualizaron {actualizados} notebooks")
    print("\nNota: Asegurate de que el modulo 'conexion_sqlserver.py' este en el directorio padre (unidad_IV/)")


if __name__ == '__main__':
    main()
