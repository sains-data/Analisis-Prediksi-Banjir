# Script to restart Hive service and clean Derby locks
# Usage: .\restart_hive.ps1

Write-Host "Restarting Hive service to fix Derby metastore issues..." -ForegroundColor Yellow

# Stop Hive container
Write-Host "Stopping Hive container..." -ForegroundColor Blue
docker-compose -f docker-compose-latest.yml stop hive-server

# Clean up Derby lock files
Write-Host "Cleaning Derby lock files and Docker volumes..." -ForegroundColor Blue

# Clean local directories
if (Test-Path ".\hive\data\metastore\metastore_db") {
    Remove-Item -Recurse -Force ".\hive\data\metastore\metastore_db"
}
if (Test-Path ".\hive\data\metastore\derby.log") {
    Remove-Item -Force ".\hive\data\metastore\derby.log"
}
if (!(Test-Path ".\hive\data\metastore")) {
    New-Item -ItemType Directory -Path ".\hive\data\metastore" -Force
}

# Clean Docker volume for Hive metastore
Write-Host "Removing Hive metastore Docker volume..." -ForegroundColor Blue
docker volume rm analisis-prediksi-banjir_hive_metastore_data 2>$null

# Remove container to force recreation
Write-Host "Removing Hive container to force recreation..." -ForegroundColor Blue
docker-compose -f docker-compose-latest.yml rm -f hive-server

# Start Hive container
Write-Host "Starting Hive container..." -ForegroundColor Blue
docker-compose -f docker-compose-latest.yml up -d hive-server

# Wait for service to be ready
Write-Host "Waiting for Hive to be ready..." -ForegroundColor Blue
Start-Sleep -Seconds 45

# Show logs for debugging
Write-Host "Showing Hive startup logs..." -ForegroundColor Blue
docker logs hive-server --tail 20

# Test connection
Write-Host "Testing Hive connection..." -ForegroundColor Blue
$testResult = docker exec hive-server /opt/hive/bin/beeline -u jdbc:hive2://localhost:10000 -e "SHOW DATABASES;" 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "Hive is ready!" -ForegroundColor Green
    Write-Host "You can now connect using: docker exec -it hive-server beeline -u jdbc:hive2://localhost:10000" -ForegroundColor Green
} else {
    Write-Host "Hive connection failed. Check logs with: docker logs hive-server" -ForegroundColor Red
}
