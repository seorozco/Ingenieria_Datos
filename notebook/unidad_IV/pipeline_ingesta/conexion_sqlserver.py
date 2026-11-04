"""
Módulo centralizado de conexión a SQL Server para Ingeniería de Datos.

Este módulo proporciona una manera reutilizable de conectarse a las bases de datos
WideWorldImporters (origen) y WideWorldImportersDW2 (destino) desde cualquier notebook.

Uso en notebook:
    from conexion_sqlserver import obtener_engines, SERVIDOR, BD_ORIGEN, BD_DESTINO
    
    engine_origen, engine_destino = obtener_engines()
"""

import urllib.parse
import pyodbc
from sqlalchemy import create_engine, text


# Parámetros de conexión centralizados
SERVIDOR = r'localhost\SQLEXPRESS02'
BD_ORIGEN = 'WideWorldImporters'
BD_DESTINO = 'WideWorldImportersDW2'
USUARIO = 'ingesta_reader'
CLAVE = '123456789'

# Rango de la dimensión tiempo
ANIO_INICIO = 2010
ANIO_FIN = 2035


def _obtener_driver_odbc():
    """Detecta automáticamente el ODBC Driver disponible para SQL Server."""
    drivers = pyodbc.drivers()
    if 'ODBC Driver 18 for SQL Server' in drivers:
        return 'ODBC Driver 18 for SQL Server'
    elif 'ODBC Driver 17 for SQL Server' in drivers:
        return 'ODBC Driver 17 for SQL Server'
    else:
        raise RuntimeError(
            'No se encontró ODBC Driver 17/18 para SQL Server. '
            'Instala "ODBC Driver 18 for SQL Server" desde Microsoft.'
        )


def construir_engine(base_datos: str):
    """
    Construye un engine SQLAlchemy para conectarse a una base de datos SQL Server.
    
    Args:
        base_datos (str): Nombre de la base de datos (e.g., 'WideWorldImporters')
    
    Returns:
        sqlalchemy.engine.Engine: Engine configurado para la conexión
    
    Raises:
        RuntimeError: Si no se encuentra un driver ODBC compatible
        pyodbc.Error: Si falla la conexión a SQL Server
    """
    driver = _obtener_driver_odbc()
    
    conn_str = (
        f'DRIVER={{{driver}}};'
        f'SERVER={SERVIDOR};'
        f'DATABASE={base_datos};'
        f'UID={USUARIO};'
        f'PWD={CLAVE};'
        'TrustServerCertificate=yes;'
    )
    params = urllib.parse.quote_plus(conn_str)
    return create_engine(f'mssql+pyodbc:///?odbc_connect={params}')


def obtener_engines():
    """
    Obtiene los engines configurados para origen y destino.
    
    Returns:
        tuple: (engine_origen, engine_destino)
    
    Raises:
        RuntimeError: Si no se puede establecer conexión con las bases de datos
    """
    engine_origen = construir_engine(BD_ORIGEN)
    engine_destino = construir_engine(BD_DESTINO)
    
    # Validar conexiones
    try:
        with engine_origen.connect() as conn:
            result = conn.execute(text('SELECT DB_NAME() AS bd')).mappings().first()
            print(f'Conexion OK (origen): {result["bd"]}')
    except Exception as e:
        raise RuntimeError(f'No se pudo conectar a {BD_ORIGEN}: {e}')
    
    try:
        with engine_destino.connect() as conn:
            result = conn.execute(text('SELECT DB_NAME() AS bd')).mappings().first()
            print(f'Conexion OK (destino): {result["bd"]}')
    except Exception as e:
        raise RuntimeError(f'No se pudo conectar a {BD_DESTINO}: {e}')
    
    return engine_origen, engine_destino


def test_conexion():
    """Prueba las conexiones a ambas bases de datos."""
    print(f'Servidor: {SERVIDOR}')
    print(f'Usuario: {USUARIO}')
    print(f'Base origen: {BD_ORIGEN}')
    print(f'Base destino: {BD_DESTINO}')
    print()
    
    try:
        engine_origen, engine_destino = obtener_engines()
        print('\n[OK] Todas las conexiones funcionan correctamente.')
        return True
    except Exception as e:
        print(f'\n[ERROR] No se pudo conectar a SQL Server.')
        print(f'\nDetalles del error: {e}')
        print(f'\nVerifica:')
        print(f'  1. SQL Server esta en ejecucion: {SERVIDOR}')
        print(f'  2. Las credenciales son correctas (usuario: {USUARIO})')
        print(f'  3. ODBC Driver 17 o 18 esta instalado')
        print(f'  4. Las bases de datos existen y son accesibles')
        return False


if __name__ == '__main__':
    test_conexion()
