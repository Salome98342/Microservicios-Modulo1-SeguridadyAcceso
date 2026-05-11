# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# QUICKSTART.ps1 - Iniciar Microservicios y Hacer Pruebas
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Configuración
$projectPath = "c:\Users\salom\OneDrive\Documentos\7 Semestre\Desarrollo 3\Microservicios"
$pythonScriptPath = "$projectPath\setup_initial_data.py"

Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║      INICIO RÁPIDO - MICROSERVICIOS DE SEGURIDAD Y ACCESO        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

# Paso 1: Ir al directorio del proyecto
Write-Host "`n[1/4] 📁 Navegando al directorio del proyecto..." -ForegroundColor Yellow
Set-Location $projectPath
Write-Host "✅ Ubicación: $(Get-Location)" -ForegroundColor Green

# Paso 2: Levantar Docker Compose
Write-Host "`n[2/4] 🐳 Levantando microservicios con Docker Compose..." -ForegroundColor Yellow
docker-compose down -v 2>$null
Start-Sleep -Seconds 2
docker-compose up -d

Write-Host "⏳ Esperando 15 segundos a que las bases de datos estén listas..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host "📋 Estado de los servicios:" -ForegroundColor Cyan
docker-compose ps

# Paso 3: Instalar dependencias de Python
Write-Host "`n[3/4] 📦 Instalando dependencias de Python..." -ForegroundColor Yellow
pip install requests psycopg2-binary bcrypt --quiet

# Paso 4: Ejecutar script de inicialización
Write-Host "`n[4/4] ⚙️  Ejecutando script de inicialización de datos..." -ForegroundColor Yellow
python $pythonScriptPath

Write-Host "`n╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                    🎉 ¡LISTO PARA HACER PRUEBAS!                 ║" -ForegroundColor Green
Write-Host "╠════════════════════════════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║                                                                    ║" -ForegroundColor Green
Write-Host "║  📊 ENDPOINTS DISPONIBLES:                                        ║" -ForegroundColor Green
Write-Host "║  • http://localhost:8002/docs       (MS-Autenticación)           ║" -ForegroundColor Green
Write-Host "║  • http://localhost:8000/docs       (MS-Usuarios)                ║" -ForegroundColor Green
Write-Host "║  • http://localhost:8003/docs       (MS-Roles)                   ║" -ForegroundColor Green
Write-Host "║                                                                    ║" -ForegroundColor Green
Write-Host "║  🔐 CREDENCIALES DE PRUEBA:                                      ║" -ForegroundColor Green
Write-Host "║  • admin     / admin123                                           ║" -ForegroundColor Green
Write-Host "║  • estudiante / estud123                                         ║" -ForegroundColor Green
Write-Host "║                                                                    ║" -ForegroundColor Green
Write-Host "║  📚 PRÓXIMOS PASOS:                                               ║" -ForegroundColor Green
Write-Host "║  1. Abre Postman e importa: postman_auth_profile.json            ║" -ForegroundColor Green
Write-Host "║  2. Ejecuta '1️⃣  Login como ADMIN' para obtener token            ║" -ForegroundColor Green
Write-Host "║  3. Sigue el TESTING_GUIDE.md para el flujo completo             ║" -ForegroundColor Green
Write-Host "║  4. ¡Prueba crear usuarios y asignar roles!                      ║" -ForegroundColor Green
Write-Host "║                                                                    ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`n💡 Tip: Para ver logs en tiempo real, ejecuta:" -ForegroundColor Blue
Write-Host "   docker-compose logs -f" -ForegroundColor Gray

Write-Host "`n📖 Para detener los servicios:" -ForegroundColor Blue
Write-Host "   docker-compose down" -ForegroundColor Gray
