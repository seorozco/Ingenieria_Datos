"""
Script para resetear la contraseña del usuario ingesta_reader en SQL Server.
Intenta primero con Windows authentication del administrador.
"""

import pyodbc
import sys

def resetear_password_sqlserver():
    """
    Intenta resetear la contraseña usando autenticación Windows.
    """
    servidor = r'localhost\SQLEXPRESS02'
    nueva_password = '123456789'
    usuario = 'ingesta_reader'
    
    print(f"Intenta reseteando contraseña del usuario: {usuario}")
    print(f"Servidor: {servidor}")
    print(f"Nueva contraseña: {nueva_password}")
    print()
    
    # Detectar driver disponible
    drivers = pyodbc.drivers()
    if 'ODBC Driver 18 for SQL Server' in drivers:
        driver = 'ODBC Driver 18 for SQL Server'
    elif 'ODBC Driver 17 for SQL Server' in drivers:
        driver = 'ODBC Driver 17 for SQL Server'
    else:
        print('[ERROR] No se encontró ODBC Driver')
        return False
    
    print(f'Driver: {driver}')
    
    # Intentar conexión con Windows Authentication (usuario actual)
    try:
        print('\nIntentando con Windows Authentication...')
        conn_str = f'DRIVER={{{driver}}};SERVER={servidor};Trusted_Connection=yes;TrustServerCertificate=yes;'
        conn = pyodbc.connect(conn_str, timeout=10)
        print('[OK] Conectado con Windows Authentication')
        
        # Ejecutar comando para resetear password
        cursor = conn.cursor()
        
        # Verificar si el usuario existe
        cursor.execute(f"SELECT name FROM sys.sysusers WHERE name = '{usuario}'")
        resultado = cursor.fetchone()
        
        if resultado:
            print(f'[OK] Usuario {usuario} encontrado')
            
            # Resetear password
            try:
                sql_reset = f"ALTER LOGIN [{usuario}] WITH PASSWORD = '{nueva_password}'"
                cursor.execute(sql_reset)
                conn.commit()
                print(f'[OK] Contraseña reseteada exitosamente')
                print(f'Nuevo login: {usuario}')
                print(f'Nueva contraseña: {nueva_password}')
                return True
            except Exception as e:
                print(f'[ERROR] No se pudo resetear password: {e}')
                return False
        else:
            print(f'[ERROR] Usuario {usuario} NO encontrado en SQL Server')
            print('\nUsuarios disponibles en SQL Server:')
            cursor.execute("SELECT name FROM sys.sysusers WHERE islogin = 1")
            for row in cursor.fetchall():
                print(f'  - {row[0]}')
            return False
    
    except pyodbc.Error as e:
        print(f'[ERROR] No se pudo conectar con Windows Auth: {e}')
        print('\nIntentando alternativas...')
        
        # Alternativa: Intentar con credenciales vacías (si es un login en blanco)
        try:
            print('Intentando conexión sin credenciales...')
            conn_str = f'DRIVER={{{driver}}};SERVER={servidor};TrustServerCertificate=yes;'
            conn = pyodbc.connect(conn_str, timeout=5)
            print('[OK] Conectado')
            
            cursor = conn.cursor()
            cursor.execute(f"ALTER LOGIN [{usuario}] WITH PASSWORD = '{nueva_password}'")
            conn.commit()
            print(f'[OK] Contraseña reseteada')
            return True
        except Exception as e2:
            print(f'[ERROR] Tampoco funcionó: {e2}')
            print('\nPuede ser necesario:')
            print('1. Ejecutar este script como administrador')
            print('2. Usar SQL Server Management Studio para resetear la contraseña')
            print('3. Cambiar el modo de autenticación de SQL Server')
            return False

if __name__ == '__main__':
    try:
        exitoso = resetear_password_sqlserver()
        sys.exit(0 if exitoso else 1)
    except Exception as e:
        print(f'\n[ERROR FATAL] {e}')
        sys.exit(1)
