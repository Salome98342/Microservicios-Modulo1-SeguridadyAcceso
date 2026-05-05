$ErrorActionPreference = 'Stop'
$base = 'http://127.0.0.1:8000'

Write-Host '1) Health check'
$health = Invoke-RestMethod -Method Get -Uri "$base/health"
$health | ConvertTo-Json -Compress

Write-Host '2) Login exitoso (admin)'
$loginBody = @{
    username = 'admin'
    encrypted_password = 'enc_admin123'
    ip = '127.0.0.1'
    user_agent = 'demo-script'
    request_trace_id = 'demo-001'
} | ConvertTo-Json
$login = Invoke-RestMethod -Method Post -Uri "$base/v1/auth/login" -ContentType 'application/json' -Body $loginBody
$token = $login.access_token
[PSCustomObject]@{ user_id = $login.user_id; role = $login.role; session_id = $login.session_id } | ConvertTo-Json -Compress

Write-Host '3) Validacion de sesion'
$validateBody = @{ token = $token } | ConvertTo-Json
$validate = Invoke-RestMethod -Method Post -Uri "$base/v1/auth/session/validate" -ContentType 'application/json' -Body $validateBody
$validate | ConvertTo-Json -Compress

Write-Host '4) Bloqueo por intentos fallidos (maria)'
$codes = @()
for ($i = 1; $i -le 5; $i++) {
    $badBody = @{
        username = 'maria'
        encrypted_password = 'bad_password'
        ip = '127.0.0.1'
        user_agent = 'demo-script'
        request_trace_id = "demo-fail-$i"
    } | ConvertTo-Json
    try {
        Invoke-RestMethod -Method Post -Uri "$base/v1/auth/login" -ContentType 'application/json' -Body $badBody | Out-Null
        $codes += 200
    }
    catch {
        $codes += [int]$_.Exception.Response.StatusCode
    }
}
$codes | ConvertTo-Json -Compress
if ($codes[0] -eq 423) {
    Write-Host 'Nota: maria ya estaba bloqueada de una ejecucion previa.'
}

Write-Host '5) Logout admin'
$headers = @{ Authorization = "Bearer $token"; request_trace_id = 'demo-logout-001' }
$logout = Invoke-RestMethod -Method Post -Uri "$base/v1/auth/logout" -Headers $headers
$logout | ConvertTo-Json -Compress

Write-Host '6) Validar token luego de logout'
$validate2 = Invoke-RestMethod -Method Post -Uri "$base/v1/auth/session/validate" -ContentType 'application/json' -Body $validateBody
$validate2 | ConvertTo-Json -Compress

Write-Host 'Demo completada.'
