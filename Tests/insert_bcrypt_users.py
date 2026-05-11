#!/usr/bin/env python3
"""
Generar hashes bcrypt válidos e insertarlos en ms-usuarios.
"""

import bcrypt
import psycopg2

# Configuración
USUARIOS_CONFIG = {
    "host": "127.0.0.1",
    "port": 5434,
    "database": "db_usuarios",
    "user": "postgres",
    "password": "postgres"
}

# Generar hashes bcrypt
def generar_hash_bcrypt(password):
    """Genera un hash bcrypt válido."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()

def insertar_usuarios():
    """Inserta usuarios con hashes bcrypt válidos."""
    try:
        conn = psycopg2.connect(**USUARIOS_CONFIG)
        cursor = conn.cursor()
        
        # Generar hashes
        admin_hash = generar_hash_bcrypt("admin123")
        estud_hash = generar_hash_bcrypt("estud123")
        
        print(f"[*] Hash admin: {admin_hash}")
        print(f"[*] Hash estudiante: {estud_hash}")
        
        # Limpiar usuarios previos (opcional)
        cursor.execute("DELETE FROM usr_usuarios WHERE username IN ('admin', 'estudiante');")
        
        # Insertar usuarios
        cursor.execute(
            "INSERT INTO usr_usuarios (username, email, password_hash, estado, rol_id) "
            "VALUES (%s, %s, %s, %s, %s);",
            ("admin", "admin@universidad.edu.co", admin_hash, "activo", 1)
        )
        
        cursor.execute(
            "INSERT INTO usr_usuarios (username, email, password_hash, estado, rol_id) "
            "VALUES (%s, %s, %s, %s, %s);",
            ("estudiante", "estudiante@universidad.edu.co", estud_hash, "activo", 2)
        )
        
        conn.commit()
        
        # Verificar inserción
        cursor.execute("SELECT id, username, email FROM usr_usuarios WHERE username IN ('admin', 'estudiante');")
        results = cursor.fetchall()
        
        print(f"\n[✓] Usuarios insertados:")
        for row in results:
            print(f"    ID: {row[0]}, Username: {row[1]}, Email: {row[2]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[✗] Error: {e}")
        return False

if __name__ == "__main__":
    print("="*70)
    print("INSERTAR USUARIOS CON BCRYPT")
    print("="*70)
    insertar_usuarios()
    print("\n[✓] Credenciales de prueba:")
    print("    admin / admin123")
    print("    estudiante / estud123")
