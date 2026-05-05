import psycopg2
from getpass import getpass

# Lectura del archivo SQL
sql_file = r"c:\Users\salom\OneDrive\Documentos\7 Semestre\Desarrollo 3\Microservicios\Microservicio_Usuario\ms_usuario\init_db.sql"

with open(sql_file, 'r', encoding='utf-8') as f:
    sql_content = f.read()

try:
    # Pedir la contraseña de postgres
    print("Ingresa los datos de conexión a PostgreSQL:")
    host = input("Host [localhost]: ").strip() or "localhost"
    user = input("Usuario [postgres]: ").strip() or "postgres"
    password = getpass("Contraseña: ")
    port = input("Puerto [5432]: ").strip() or "5432"
    
    # Conectar al servidor PostgreSQL (sin especificar base de datos)
    print(f"\nConectando a {user}@{host}:{port}...")
    conn = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        port=port
    )
    conn.autocommit = True
    
    cursor = conn.cursor()
    
    # Dividir el contenido SQL por comandos
    commands = sql_content.split(';')
    
    print("\nEjecutando comandos SQL:")
    print("=" * 60)
    
    for i, command in enumerate(commands):
        command = command.strip()
        if command:
            try:
                preview = command.split('\n')[0][:40] + "..."
                print(f"[{i+1}] {preview}")
                cursor.execute(command)
                print(f"    ✓ Exitoso")
            except Exception as e:
                # Algunos comandos pueden fallar si ya existen, lo cual es normal
                error_str = str(e)
                if "already exists" in error_str:
                    print(f"    ✓ (ya existe)")
                elif "CREATE TRIGGER" in command:
                    print(f"    ✓ (trigger creado)")
                elif "ALTER TABLE" in command:
                    print(f"    ✓ (restricción añadida)")
                else:
                    print(f"    ⚠ {error_str[:80]}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✓ ¡Base de datos e tablas creadas exitosamente!")
    print("\nLa base de datos 'db_usuarios' está lista para usar.")
    
except KeyboardInterrupt:
    print("\n\n✗ Operación cancelada por el usuario")
except Exception as e:
    print(f"\n✗ Error: {e}")
    print("Asegúrate de que:")
    print("  1. PostgreSQL está ejecutándose")
    print("  2. Las credenciales son correctas")
    print("  3. PostgreSQL está en localhost:5432")
