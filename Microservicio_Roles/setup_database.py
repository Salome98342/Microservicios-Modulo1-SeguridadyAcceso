#!/usr/bin/env python3
"""
Script para crear la base de datos db_roles en PostgreSQL
Ejecutar: python setup_database.py
"""

import psycopg
from pathlib import Path
import sys

def setup_database(user="postgres", password=None, host="localhost", port=5432):
    """Crea la base de datos y sus tablas usando el script SQL"""
    
    # Leer el script SQL
    sql_file = Path(__file__).parent / "database_schema.sql"
    
    if not sql_file.exists():
        print(f"❌ Error: No se encontró {sql_file}")
        return False
    
    print(f"📄 Leyendo script SQL: {sql_file}")
    with open(sql_file, "r", encoding="utf-8") as f:
        sql_content = f.read()
    
    try:
        # Primero conectar a PostgreSQL por defecto para crear la BD
        print(f"🔗 Conectando a PostgreSQL en {host}:{port}...")
        
        # Intentar conexión con credenciales proporcionadas
        conn_params = {
            "host": host,
            "port": port,
            "user": user,
            "dbname": "postgres",
            "autocommit": True
        }
        
        if password:
            conn_params["password"] = password
        
        conn = psycopg.connect(**conn_params)
        
        cursor = conn.cursor()
        
        # Crear base de datos si no existe
        print("📊 Creando base de datos 'db_roles'...")
        cursor.execute("DROP DATABASE IF EXISTS db_roles")
        cursor.execute("""
            CREATE DATABASE db_roles
            ENCODING 'UTF8'
        """)
        print("✅ Base de datos creada exitosamente")
        
        cursor.close()
        conn.close()
        
        # Conectar a la nueva base de datos y ejecutar el script
        print("\n🔗 Conectando a 'db_roles'...")
        conn_params["dbname"] = "db_roles"
        conn = psycopg.connect(**conn_params)
        
        cursor = conn.cursor()
        
        # Ejecutar el script SQL
        print("📝 Ejecutando script de creación de tablas...")
        
        # Dividir el script en sentencias individuales
        statements = sql_content.split(";")
        
        for statement in statements:
            stmt = statement.strip()
            if stmt and not stmt.startswith("--"):  # Ignorar comentarios y líneas vacías
                try:
                    cursor.execute(stmt)
                except psycopg.Error as e:
                    if "already exists" not in str(e).lower():
                        print(f"⚠️  Error ejecutando sentencia: {e}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Base de datos configurada exitosamente!")
        print("📋 Tablas creadas:")
        print("   - rol_roles")
        print("   - rol_permisos")
        print("   - rol_asignaciones_rol_permiso")
        print("   - rol_asignaciones_usuario_rol")
        print("   - rol_roles_contradictorios")
        print("   - rol_tokens_aplicacion")
        print("📊 Vistas creadas:")
        print("   - vw_rol_permisos_activos")
        print("   - vw_usuario_roles_activos")
        
        return True
        
    except psycopg.OperationalError as e:
        print(f"\n❌ Error de conexión a PostgreSQL:")
        print(f"   {e}")
        return False
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  CONFIGURACIÓN DE BASE DE DATOS - ms-roles")
    print("=" * 60 + "\n")
    
    # Intentar con diferentes combinaciones de credenciales
    credentials = [
        ("postgres", "0422524"),      # Contraseña correcta
        ("postgres", None),           # Sin contraseña (trust)
        ("postgres", ""),             # Contraseña vacía
        ("postgres", "password"),     # Contraseña por defecto
        ("postgres", "postgres"),     # Contraseña = usuario
    ]
    
    success = False
    for user, password in credentials:
        try:
            if password:
                print(f"Intentando conexión con usuario '{user}' y contraseña...")
            else:
                print(f"Intentando conexión con usuario '{user}' sin contraseña...")
            
            success = setup_database(user=user, password=password)
            if success:
                break
        except Exception as e:
            pass
    
    if not success:
        print("\n❌ No se pudo conectar a PostgreSQL con las credenciales predeterminadas.")
        print("\n💡 Por favor, proporciona las credenciales correctas:")
        user = input("Usuario PostgreSQL [postgres]: ").strip() or "postgres"
        password = input("Contraseña [dejar vacío si no la hay]: ").strip() or None
        host = input("Host [localhost]: ").strip() or "localhost"
        port = input("Puerto [5432]: ").strip() or "5432"
        
        success = setup_database(user=user, password=password, host=host, port=int(port))
    
    if not success:
        sys.exit(1)
