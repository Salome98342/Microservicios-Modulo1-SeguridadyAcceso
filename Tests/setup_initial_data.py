#!/usr/bin/env python3
"""
Script para popular datos iniciales en los microservicios.
Ejecutar después de: docker-compose up -d

Requisitos:
- pip install requests psycopg2-binary bcrypt
"""

import sys
import time
import psycopg2
from psycopg2 import sql
import requests
import json
import hashlib
import base64
from datetime import datetime, timedelta
import uuid

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════

CONFIG = {
    # PostgreSQL - MS AUTENTICACIÓN
    "auth_db": {
        # Use 127.0.0.1 to force IPv4 (localhost may try IPv6 first)
        "host": "127.0.0.1",
        "port": 5433,
        "database": "auth_db",
        "user": "auth",
        "password": "auth"
    },
    # PostgreSQL - MS USUARIOS
    "usuarios_db": {
        # Use 127.0.0.1 for consistency
        "host": "127.0.0.1",
        "port": 5434,
        "database": "db_usuarios",
        "user": "postgres",
        "password": "postgres"
    },
    # PostgreSQL - MS ROLES
    "roles_db": {
        # Use 127.0.0.1 for consistency
        "host": "127.0.0.1",
        "port": 5432,
        "database": "db_roles",
        "user": "postgres",
        "password": "password"
    },
    # Microservicios URLs
    "auth_url": "http://localhost:8002",
    "usuarios_url": "http://localhost:8000",
    "roles_url": "http://localhost:8003",
    # Credenciales iniciales
    "admin_user": {
        "username": "admin",
        "password": "admin123",
        "email": "admin@universidad.edu.co"
    },
    "test_user": {
        "username": "estudiante",
        "password": "estud123",
        "email": "estudiante@universidad.edu.co"
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# COLORES PARA CONSOLA
# ═══════════════════════════════════════════════════════════════════════════

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ═══════════════════════════════════════════════════════════════════════════
# FUNCIONES DE CONEXIÓN BD
# ═══════════════════════════════════════════════════════════════════════════

def connect_db(config):
    """Conectar a PostgreSQL"""
    try:
        conn = psycopg2.connect(**config)
        return conn
    except psycopg2.OperationalError as e:
        print(f"{Colors.FAIL}❌ Error al conectar a BD (OperationalError): {e}{Colors.ENDC}")
        return None
    except UnicodeDecodeError as e:
        print(f"{Colors.FAIL}❌ UnicodeDecodeError al intentar conectar a BD: {e!r}{Colors.ENDC}")
        return None
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error inesperado al conectar a BD: {e!r}{Colors.ENDC}")
        return None

def wait_for_databases(max_retries=30):
    """Esperar a que las BDs estén listas"""
    print(f"\n{Colors.OKCYAN}⏳ Esperando que las bases de datos estén listas...{Colors.ENDC}")
    
    for retry in range(max_retries):
        try:
            # Intenta conectar a cada BD
            for db_name, config in [
                ("auth_db", CONFIG["auth_db"]),
                ("usuarios_db", CONFIG["usuarios_db"]),
                ("roles_db", CONFIG["roles_db"])
            ]:
                try:
                    conn = psycopg2.connect(**config, connect_timeout=2)
                    conn.close()
                except Exception as inner_e:
                    # Mostrar detalle pero no romper el loop; se reintentará
                    print(f"   {Colors.WARNING}No disponible aún: {db_name} -> {inner_e!r}{Colors.ENDC}")
                    raise
            
            print(f"{Colors.OKGREEN}✅ Todas las bases de datos están listas{Colors.ENDC}")
            return True
        except UnicodeDecodeError as e:
            print(f"   {Colors.FAIL}UnicodeDecodeError en intento {retry + 1}: {e!r}{Colors.ENDC}")
            # esperar y reintentar
            time.sleep(1)
        except psycopg2.OperationalError as e:
            print(f"   {Colors.WARNING}OperationalError intento {retry + 1}/{max_retries}: {e}{Colors.ENDC}", end='\r')
            time.sleep(1)
        except Exception as e:
            # Captura errores diversos (incluye inner exceptions de conexión)
            print(f"   {Colors.WARNING}Intento {retry + 1}/{max_retries} fallo: {e!r}{Colors.ENDC}", end='\r')
            time.sleep(1)
    
    print(f"{Colors.FAIL}❌ Las bases de datos no respondieron en tiempo{Colors.ENDC}")
    return False

# ═══════════════════════════════════════════════════════════════════════════
# SETUP USUARIOS
# ═══════════════════════════════════════════════════════════════════════════

def setup_usuarios_db():
    """Crear usuario ADMIN en MS-USUARIOS"""
    print(f"\n{Colors.HEADER}{'='*70}")
    print("📝 CONFIGURAR MS-USUARIOS")
    print(f"{'='*70}{Colors.ENDC}\n")
    
    conn = connect_db(CONFIG["usuarios_db"])
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # 1. Verificar tipos de documento
        cursor.execute("SELECT COUNT(*) FROM usr_tipos_documento;")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print(f"{Colors.OKCYAN}→ Insertando tipos de documento...{Colors.ENDC}")
            tipos_doc = [
                ("CC", "Cédula de Ciudadanía", "Documento de identidad colombiano"),
                ("TI", "Tarjeta de Identidad", "Tarjeta de identidad menor de edad"),
                ("CE", "Cédula de Extranjería", "Documento de extranjero"),
                ("PA", "Pasaporte", "Documento internacional"),
            ]
            for codigo, nombre, desc in tipos_doc:
                cursor.execute(
                    """INSERT INTO usr_tipos_documento (codigo, nombre, descripcion)
                       VALUES (%s, %s, %s) ON CONFLICT (codigo) DO NOTHING;""",
                    (codigo, nombre, desc)
                )
            conn.commit()
            print(f"{Colors.OKGREEN}✅ Tipos de documento creados{Colors.ENDC}")
        else:
            print(f"{Colors.OKGREEN}✓ Tipos de documento ya existen ({count}){Colors.ENDC}")
        
        # 2. Crear usuario ADMIN
        print(f"{Colors.OKCYAN}→ Creando usuario ADMIN...{Colors.ENDC}")
        
        # Hash bcrypt simulado (en producción usar bcrypt.hashpw)
        password_hash = hashlib.sha256(CONFIG["admin_user"]["password"].encode()).hexdigest()
        
        cursor.execute("""
            INSERT INTO usr_usuarios (username, email, password_hash, estado, rol_id)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (username) DO NOTHING
            RETURNING id;
        """, (
            CONFIG["admin_user"]["username"],
            CONFIG["admin_user"]["email"],
            password_hash,
            "activo",
            1  # rol_id temporal
        ))
        
        result = cursor.fetchone()
        if result:
            admin_id = result[0]
            print(f"{Colors.OKGREEN}✅ Usuario ADMIN creado (ID: {admin_id}){Colors.ENDC}")
            
            # 3. Crear perfil del usuario ADMIN
            print(f"{Colors.OKCYAN}→ Creando perfil ADMIN...{Colors.ENDC}")
            cursor.execute("""
                INSERT INTO usr_perfiles (
                    usuario_id, tipo_documento_id, numero_documento,
                    primer_nombre, primer_apellido, fecha_nacimiento,
                    genero, direccion_residencia, ciudad, departamento,
                    telefono_movil, contacto_emergencia_nombre,
                    contacto_emergencia_telefono
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (usuario_id) DO NOTHING;
            """, (
                admin_id, 1, "1000000001",
                "Admin", "Sistema", "1990-01-01",
                "masculino", "Calle Principal 123", "Bogotá", "Cundinamarca",
                "3001234567", "Admin Sistema", "3001234567"
            ))
            
            # 4. Crear preferencias de notificación
            cursor.execute("""
                INSERT INTO usr_preferencias_notificacion (
                    usuario_id, notif_email, notif_sms, notif_push, canal_preferido
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (usuario_id) DO NOTHING;
            """, (admin_id, True, True, True, "email"))
            
            conn.commit()
            print(f"{Colors.OKGREEN}✅ Perfil ADMIN creado{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}⚠ Usuario ADMIN ya existe{Colors.ENDC}")
        
        # 5. Crear usuario de prueba
        print(f"{Colors.OKCYAN}→ Creando usuario de PRUEBA...{Colors.ENDC}")
        password_hash_test = hashlib.sha256(CONFIG["test_user"]["password"].encode()).hexdigest()
        
        cursor.execute("""
            INSERT INTO usr_usuarios (username, email, password_hash, estado, rol_id)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (username) DO NOTHING
            RETURNING id;
        """, (
            CONFIG["test_user"]["username"],
            CONFIG["test_user"]["email"],
            password_hash_test,
            "activo",
            2  # rol_id diferente
        ))
        
        result = cursor.fetchone()
        if result:
            test_id = result[0]
            cursor.execute("""
                INSERT INTO usr_perfiles (
                    usuario_id, tipo_documento_id, numero_documento,
                    primer_nombre, primer_apellido, fecha_nacimiento,
                    genero, direccion_residencia, ciudad, departamento,
                    telefono_movil, contacto_emergencia_nombre,
                    contacto_emergencia_telefono
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (usuario_id) DO NOTHING;
            """, (
                test_id, 1, "1000000002",
                "Juan", "Estudiante", "2005-06-15",
                "masculino", "Calle Secondary 456", "Bogotá", "Cundinamarca",
                "3007654321", "María Estudiante", "3007654321"
            ))
            
            cursor.execute("""
                INSERT INTO usr_preferencias_notificacion (
                    usuario_id, notif_email, notif_sms, notif_push, canal_preferido
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (usuario_id) DO NOTHING;
            """, (test_id, True, False, True, "push"))
            
            conn.commit()
            print(f"{Colors.OKGREEN}✅ Usuario de PRUEBA creado{Colors.ENDC}")
        
        return True
        
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
        return False
    finally:
        conn.close()

# ═══════════════════════════════════════════════════════════════════════════
# SETUP ROLES
# ═══════════════════════════════════════════════════════════════════════════

def setup_roles_db():
    """Crear roles y permisos en MS-ROLES"""
    print(f"\n{Colors.HEADER}{'='*70}")
    print("🛡️  CONFIGURAR MS-ROLES")
    print(f"{'='*70}{Colors.ENDC}\n")
    
    conn = connect_db(CONFIG["roles_db"])
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # 1. Crear roles básicos
        print(f"{Colors.OKCYAN}→ Creando roles básicos...{Colors.ENDC}")
        roles = [
            ("admin", "Administrador del Sistema", "activo"),
            ("estudiante", "Estudiante Universitario", "activo"),
            ("docente", "Docente Universitario", "activo"),
            ("staff", "Personal Administrativo", "activo"),
        ]
        
        role_ids = {}
        for nombre, desc, estado in roles:
            cursor.execute("""
                INSERT INTO rol_roles (nombre, descripcion, estado)
                VALUES (%s, %s, %s)
                ON CONFLICT (nombre) DO UPDATE SET descripcion = %s
                RETURNING id;
            """, (nombre, desc, estado, desc))
            
            result = cursor.fetchone()
            if result:
                role_ids[nombre] = result[0]
        
        conn.commit()
        print(f"{Colors.OKGREEN}✅ {len(role_ids)} roles creados{Colors.ENDC}")
        
        # 2. Crear permisos básicos
        print(f"{Colors.OKCYAN}→ Creando permisos del sistema...{Colors.ENDC}")
        
        permisos = [
            # Usuarios
            ("USR.READ", "Consultar Usuarios", "Usuarios", "ms-usuarios", "Lectura de perfil", "consulta"),
            ("USR.CREATE", "Crear Usuario", "Usuarios", "ms-usuarios", "Creación de usuario", "creacion"),
            ("USR.UPDATE", "Actualizar Usuario", "Usuarios", "ms-usuarios", "Modificación de datos", "actualizacion"),
            ("USR.DELETE", "Eliminar Usuario", "Usuarios", "ms-usuarios", "Eliminación de usuario", "eliminacion"),
            
            # Roles
            ("ROL.READ", "Consultar Roles", "Roles", "ms-roles", "Lectura de roles", "consulta"),
            ("ROL.CREATE", "Crear Rol", "Roles", "ms-roles", "Creación de roles", "creacion"),
            ("ROL.UPDATE", "Actualizar Rol", "Roles", "ms-roles", "Modificación de roles", "actualizacion"),
            ("ROL.DELETE", "Eliminar Rol", "Roles", "ms-roles", "Eliminación de roles", "eliminacion"),
            
            # Autenticación
            ("AUTH.LOGIN", "Iniciar Sesión", "Autenticación", "ms-autenticacion", "Acceso al sistema", "consulta"),
            ("AUTH.LOGOUT", "Cerrar Sesión", "Autenticación", "ms-autenticacion", "Cierre de sesión", "consulta"),
            ("AUTH.ADMIN", "Administración Auth", "Autenticación", "ms-autenticacion", "Gestión de sesiones", "actualizacion"),
        ]
        
        permiso_ids = {}
        for codigo, nombre, modulo, microserv, funcionalidad, metodo in permisos:
            cursor.execute("""
                INSERT INTO rol_permisos (codigo, nombre, descripcion, modulo, 
                    microservicio_origen, funcionalidad_asociada, metodo_operacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (codigo) DO NOTHING
                RETURNING id;
            """, (codigo, nombre, f"Permiso: {nombre}", modulo, microserv, funcionalidad, metodo))
            
            result = cursor.fetchone()
            if result:
                permiso_ids[codigo] = result[0]
        
        conn.commit()
        print(f"{Colors.OKGREEN}✅ {len(permiso_ids)} permisos creados{Colors.ENDC}")
        
        # 3. Asignar permisos a roles
        print(f"{Colors.OKCYAN}→ Asignando permisos a roles...{Colors.ENDC}")
        
        # Admin: todos los permisos
        admin_permisos = list(permiso_ids.values())
        
        # Estudiante: solo lectura
        estudiante_permisos = [permiso_ids.get(p) for p in ["USR.READ", "AUTH.LOGIN", "AUTH.LOGOUT"] if p in permiso_ids]
        
        # Docente: lectura + crear calificaciones
        docente_permisos = [permiso_ids.get(p) for p in ["USR.READ", "AUTH.LOGIN", "AUTH.LOGOUT"] if p in permiso_ids]
        
        asignaciones = [
            (role_ids.get("admin"), admin_permisos),
            (role_ids.get("estudiante"), estudiante_permisos),
            (role_ids.get("docente"), docente_permisos),
        ]
        
        for rol_id, permisos_ids in asignaciones:
            if rol_id and permisos_ids:
                for permiso_id in permisos_ids:
                    cursor.execute("""
                        INSERT INTO rol_asignaciones_rol_permiso 
                            (rol_id, permiso_id, asignado_por_usuario_id)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (rol_id, permiso_id) DO NOTHING;
                    """, (rol_id, permiso_id, 1))
        
        conn.commit()
        print(f"{Colors.OKGREEN}✅ Permisos asignados a roles{Colors.ENDC}")
        
        return True
        
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
        return False
    finally:
        conn.close()

# ═══════════════════════════════════════════════════════════════════════════
# SETUP AUTENTICACIÓN
# ═══════════════════════════════════════════════════════════════════════════

def setup_auth_db():
    """Crear tokens de aplicación en MS-AUTENTICACIÓN"""
    print(f"\n{Colors.HEADER}{'='*70}")
    print("🔐 CONFIGURAR MS-AUTENTICACIÓN")
    print(f"{'='*70}{Colors.ENDC}\n")
    
    conn = connect_db(CONFIG["auth_db"])
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # 1. Crear tokens de aplicación para inter-servicios
        print(f"{Colors.OKCYAN}→ Creando tokens de aplicación...{Colors.ENDC}")
        
        app_tokens = [
            ("ms-usuarios", "Token para ms-usuarios"),
            ("ms-roles", "Token para ms-roles"),
            ("ms-autenticacion", "Token interno para autenticación"),
        ]
        
        tokens_generados = {}
        for nombre_servicio, descripcion in app_tokens:
            # Generar token
            token_value = str(uuid.uuid4()).replace("-", "")[:32]
            
            # Cifrar (simulado - en producción usar AES256)
            encrypted_token = base64.b64encode(token_value.encode()).decode()
            
            cursor.execute("""
                INSERT INTO app_tokens (
                    id, name_service, encrypted_token, description, status,
                    created_at, updated_by, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (name_service) DO NOTHING;
            """, (
                str(uuid.uuid4()),
                nombre_servicio,
                encrypted_token,
                descripcion,
                "activo",
                datetime.now().isoformat(),
                "admin",
                datetime.now().isoformat()
            ))
            
            tokens_generados[nombre_servicio] = token_value
        
        conn.commit()
        print(f"{Colors.OKGREEN}✅ {len(tokens_generados)} tokens de aplicación creados{Colors.ENDC}")
        
        # Mostrar tokens generados
        print(f"\n{Colors.WARNING}📋 TOKENS GENERADOS (guardar en variables de entorno):{Colors.ENDC}")
        for nombre, token in tokens_generados.items():
            print(f"   {nombre}: {token[:16]}...")
        
        return True
        
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
        return False
    finally:
        conn.close()

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔═══════════════════════════════════════════════════════════════════════╗")
    print("║   SCRIPT DE INICIALIZACIÓN - MICROSERVICIOS DE SEGURIDAD Y ACCESO   ║")
    print("╚═══════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")
    
    # Esperar a que las BDs estén listas
    if not wait_for_databases():
        return False
    
    # Setup de cada microservicio
    success = True
    success = setup_usuarios_db() and success
    success = setup_roles_db() and success
    success = setup_auth_db() and success
    
    if success:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}")
        print("╔═══════════════════════════════════════════════════════════════════════╗")
        print("║               ✅ INICIALIZACIÓN COMPLETADA CON ÉXITO                  ║")
        print("╠═══════════════════════════════════════════════════════════════════════╣")
        print("║  Credenciales de prueba:                                             ║")
        print(f"║  • ADMIN: {CONFIG['admin_user']['username']:40} / admin123       ║")
        print(f"║  • USER:  {CONFIG['test_user']['username']:40} / estud123       ║")
        print("║                                                                       ║")
        print("║  Próximos pasos:                                                     ║")
        print("║  1. Usar Postman para hacer login                                    ║")
        print("║  2. Guardar token JWT para siguiente requests                        ║")
        print("║  3. Ver TESTING_GUIDE.md para más detalles                           ║")
        print("╚═══════════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.ENDC}\n")
        return True
    else:
        print(f"\n{Colors.FAIL}❌ Inicialización fallida. Revisa los errores arriba.{Colors.ENDC}\n")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
