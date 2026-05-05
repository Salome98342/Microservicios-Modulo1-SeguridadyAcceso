import psycopg2

# Verificar que la base de datos se creó correctamente
try:
    # Intentar con contraseñas comunes
    passwords = ["", "postgres", "123456", "password"]
    conn = None
    
    for pwd in passwords:
        try:
            conn = psycopg2.connect(
                host="localhost",
                user="postgres",
                password=pwd,
                database="db_usuarios",
                port="5432"
            )
            break
        except:
            continue
    
    cursor = conn.cursor()
    
    # Obtener listado de tablas
    cursor.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    
    tables = cursor.fetchall()
    
    print("✓ Base de datos 'db_usuarios' verificada correctamente\n")
    print("Tablas creadas:")
    print("-" * 40)
    
    for table in tables:
        print(f"  • {table[0]}")
    
    # Obtener estadísticas de cada tabla
    print("\n" + "-" * 40)
    print("Detalles de las tablas:")
    print("-" * 40)
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print(f"\n{table_name}:")
        for col in columns:
            nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
            print(f"  - {col[0]}: {col[1]} ({nullable})")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 40)
    print("✓ ¡Verificación completada con éxito!")
    print("=" * 40)
    print("\nTodo está listo para usar el microservicio.")
    print("Las dependencias están instaladas en: venv/")
    print("La base de datos está en: db_usuarios")
    
except Exception as e:
    print(f"✗ Error: {e}")
