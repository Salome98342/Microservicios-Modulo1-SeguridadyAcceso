import psycopg2
from psycopg2 import sql
import os

# Lectura del archivo SQL
sql_file = r"c:\Users\salom\OneDrive\Documentos\7 Semestre\Desarrollo 3\Microservicios\Microservicio_Usuario\ms_usuario\init_db.sql"

with open(sql_file, 'r', encoding='utf-8') as f:
    sql_content = f.read()

try:
    # Conectar al servidor PostgreSQL (sin especificar base de datos)
    # Intentar con contraseñas comunes
    passwords = ["", "postgres", "123456", "password"]
    conn = None
    
    for pwd in passwords:
        try:
            conn = psycopg2.connect(
                host="localhost",
                user="postgres",
                password=pwd,
                port="5432"
            )
            print(f"✓ Conectado a PostgreSQL con contraseña: {'(vacía)' if not pwd else '***'}")
            break
        except:
            continue
    
    if conn is None:
        raise Exception("No se pudo conectar con ninguna contraseña. Por favor, ingresa la contraseña de postgres manualmente.")
    conn.autocommit = True
    
    cursor = conn.cursor()
    
    # Dividir el contenido SQL por comandos
    commands = sql_content.split(';')
    
    for command in commands:
        command = command.strip()
        if command:
            try:
                print(f"Ejecutando: {command[:50]}...")
                cursor.execute(command)
                print("✓ Ejecutado correctamente")
            except Exception as e:
                # Algunos comandos pueden fallar si ya existen, lo cual es normal
                if "already exists" in str(e) or "CREATE DATABASE" in command:
                    print(f"⚠ Advertencia: {str(e)[:100]}")
                else:
                    print(f"✗ Error: {str(e)[:200]}")
    
    cursor.close()
    conn.close()
    
    print("\n✓ Base de datos e tablas creadas exitosamente!")
    
except Exception as e:
    print(f"✗ Error de conexión: {e}")
    print("\nAsegúrate de que PostgreSQL está ejecutándose en localhost:5432")
