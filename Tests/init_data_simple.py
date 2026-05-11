#!/usr/bin/env python3
"""
Script simplificado para poblar datos iniciales.
Evita problemas de encoding con errores en español.
"""

import time
import psycopg2
from psycopg2 import sql

# Configuración
ROLES_CONFIG = {
    "host": "127.0.0.1",
    "port": 5432,
    "database": "db_roles",
    "user": "postgres",
    "password": "password"
}

AUTH_CONFIG = {
    "host": "127.0.0.1",
    "port": 5433,
    "database": "auth_db",
    "user": "auth",
    "password": "auth"
}

USUARIOS_CONFIG = {
    "host": "127.0.0.1",
    "port": 5434,
    "database": "db_usuarios",
    "user": "postgres",
    "password": "postgres"
}

def test_connection(config, name, max_retries=15):
    """Intenta conectarse a una BD."""
    print(f"\n[*] Probando conexión a {name}...")
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(**config, connect_timeout=2)
            conn.close()
            print(f"[✓] {name} OK")
            return True
        except Exception as e:
            print(f"    Intento {attempt + 1}/{max_retries}: {type(e).__name__}")
            time.sleep(1)
    
    print(f"[✗] {name} NO RESPONDE")
    return False

def seed_roles(config):
    """Carga datos semilla en ms-roles."""
    print("\n[*] Cargando datos en ms-roles...")
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # Verificar si ya existen roles
        cursor.execute("SELECT COUNT(*) FROM rol_roles;")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"[✓] ms-roles ya tiene {count} roles")
            cursor.close()
            conn.close()
            return True
        
        # Crear roles
        roles = [
            ("ADMIN", "Rol con acceso total al sistema."),
            ("USUARIO", "Rol para usuarios generales."),
            ("MODERADOR", "Rol para gestión moderada del sistema."),
        ]
        
        for nombre, descripcion in roles:
            cursor.execute(
                "INSERT INTO rol_roles (nombre, descripcion, estado) VALUES (%s, %s, 'activo');",
                (nombre, descripcion)
            )
        
        conn.commit()
        print(f"[✓] {len(roles)} roles insertados")
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[✗] Error: {e}")
        return False

def seed_usuarios(config):
    """Carga datos semilla en ms-usuarios."""
    print("\n[*] Cargando datos en ms-usuarios...")
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # Verificar si ya existen usuarios
        cursor.execute("SELECT COUNT(*) FROM usr_usuarios;")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"[✓] ms-usuarios ya tiene {count} usuarios")
            cursor.close()
            conn.close()
            return True
        
        # Crear usuarios
        import hashlib
        
        admin_pass = hashlib.sha256("admin123".encode()).hexdigest()
        test_pass = hashlib.sha256("estud123".encode()).hexdigest()
        
        users = [
            ("admin", "admin@universidad.edu.co", admin_pass, 1),
            ("estudiante", "estudiante@universidad.edu.co", test_pass, 2),
        ]
        
        for username, email, password_hash, rol_id in users:
            cursor.execute(
                "INSERT INTO usr_usuarios (username, email, password_hash, estado, rol_id) "
                "VALUES (%s, %s, %s, 'activo', %s) ON CONFLICT (username) DO NOTHING;",
                (username, email, password_hash, rol_id)
            )
        
        conn.commit()
        print(f"[✓] {len(users)} usuarios insertados")
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[✗] Error: {e}")
        return False

def main():
    print("=" * 70)
    print("INICIALIZACIÓN SIMPLIFICADA - MICROSERVICIOS")
    print("=" * 70)
    
    # Probar conexiones
    all_ok = True
    all_ok = test_connection(ROLES_CONFIG, "ms-roles (5432)") and all_ok
    all_ok = test_connection(AUTH_CONFIG, "ms-autenticacion (5433)") and all_ok
    all_ok = test_connection(USUARIOS_CONFIG, "ms-usuarios (5434)") and all_ok
    
    if not all_ok:
        print("\n[✗] No se pudieron conectar a todas las bases de datos")
        return False
    
    print("\n[✓] Todas las bases de datos están listas")
    
    # Cargar datos
    seed_roles(ROLES_CONFIG)
    seed_usuarios(USUARIOS_CONFIG)
    
    print("\n" + "=" * 70)
    print("✓ INICIALIZACIÓN COMPLETADA")
    print("=" * 70)
    print("\nCredenciales de prueba:")
    print("  - Admin:     admin / admin123")
    print("  - Estudiante: estudiante / estud123")
    print("\nPróximo paso: Login en http://localhost:8002/api/v1/auth/login")
    
    return True

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
