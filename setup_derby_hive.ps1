#!/usr/bin/env pwsh
# =============================================================================
# HIVE SERVER SETUP WITH DERBY DATABASE
# =============================================================================
# This script configures and starts Hive server with the embedded Derby database
# instead of PostgreSQL.
# =============================================================================

Write-Host "Starting Hive server setup with Derby database..." -ForegroundColor Yellow

# Step 1: Clean up any existing Hive containers and data
Write-Host "Cleaning up existing Hive containers and data..." -ForegroundColor Blue
docker-compose -f docker-compose-latest.yml stop hive-server
docker-compose -f docker-compose-latest.yml rm -f hive-server
docker rm -f hive-server 2>$null

# Step 2: Clean up Derby files to ensure clean start
Write-Host "Cleaning Derby lock files..." -ForegroundColor Blue
if (Test-Path ".\hive\data\metastore\metastore_db") {
    Remove-Item -Recurse -Force ".\hive\data\metastore\metastore_db"
}
if (Test-Path ".\hive\data\metastore\derby.log") {
    Remove-Item -Force ".\hive\data\metastore\derby.log"
}
if (!(Test-Path ".\hive\data\metastore")) {
    New-Item -ItemType Directory -Path ".\hive\data\metastore" -Force
}

# Step 3: Ensure HDFS directories are created
Write-Host "Creating required HDFS directories..." -ForegroundColor Blue
docker exec namenode hdfs dfs -mkdir -p /user/hive/warehouse
docker exec namenode hdfs dfs -mkdir -p /analisis-prediksi-banjir/data
docker exec namenode hdfs dfs -chmod -R 777 /user/hive/warehouse
docker exec namenode hdfs dfs -chmod -R 777 /analisis-prediksi-banjir

# Step 4: Start Hive with Derby configuration
Write-Host "Starting Hive server with Derby database..." -ForegroundColor Blue
docker-compose -f docker-compose-latest.yml up -d hive-server

# Step 5: Wait for Hive server to start
Write-Host "Waiting for Hive server to start..." -ForegroundColor Blue
Start-Sleep -Seconds 45

# Step 6: Show logs for debugging
Write-Host "Showing Hive startup logs..." -ForegroundColor Blue
docker logs hive-server --tail 20

# Step 7: Test connection to Hive
Write-Host "Testing Hive connection..." -ForegroundColor Blue
$testResult = docker exec hive-server /opt/hive/bin/beeline -u jdbc:hive2://localhost:10000 -e "SHOW DATABASES;" 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Hive is ready!" -ForegroundColor Green
    Write-Host "You can now connect using: docker exec -it hive-server beeline -u jdbc:hive2://localhost:10000" -ForegroundColor Green
    
    # Create the flood_predictions database
    Write-Host "Creating the flood_predictions database..." -ForegroundColor Blue
    docker exec hive-server /opt/hive/bin/beeline -u jdbc:hive2://localhost:10000 -e "CREATE DATABASE IF NOT EXISTS flood_predictions;"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ flood_predictions database created successfully." -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to create flood_predictions database." -ForegroundColor Red
    }
} else {
    Write-Host "❌ Hive connection failed. Trying to fix the issue..." -ForegroundColor Red
    
    # Additional troubleshooting steps
    Write-Host "Restarting Hive server..." -ForegroundColor Blue
    docker-compose -f docker-compose-latest.yml restart hive-server
    
    # Wait a bit longer for restart
    Start-Sleep -Seconds 60
    
    # Test again
    Write-Host "Testing Hive connection again..." -ForegroundColor Blue
    $testResult = docker exec hive-server /opt/hive/bin/beeline -u jdbc:hive2://localhost:10000 -e "SHOW DATABASES;" 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Hive is now ready!" -ForegroundColor Green
        Write-Host "You can now connect using: docker exec -it hive-server beeline -u jdbc:hive2://localhost:10000" -ForegroundColor Green
    } else {
        Write-Host "❌ Hive connection still failed. Please check the logs with: docker logs hive-server" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Hive WebUI is available at: http://localhost:10002" -ForegroundColor Cyan
Write-Host "Hive JDBC connection: jdbc:hive2://localhost:10000" -ForegroundColor Cyan
Write-Host ""
