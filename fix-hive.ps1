# Script to fix Hive Derby metastore issues
# This script will:
# 1. Fix docker-compose-latest.yml
# 2. Clean Derby files
# 3. Restart Hive container

Write-Host "Starting Hive repair process..." -ForegroundColor Yellow

# Step 1: Clean up Docker container and volumes
Write-Host "Stopping and removing existing Hive container..." -ForegroundColor Blue
docker-compose -f docker-compose-latest.yml stop hive-server
docker-compose -f docker-compose-latest.yml rm -f hive-server
docker rm -f hive-server 2>$null

# Step 2: Clean up Derby files
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

# Step 3: Remove volume if it exists
Write-Host "Removing Docker volumes..." -ForegroundColor Blue
docker volume rm analisis-prediksi-banjir_hive_metastore_data 2>$null

# Step 2: Stop and remove the existing Hive container
Write-Host "Stopping and removing existing Hive container..." -ForegroundColor Blue
docker-compose -f docker-compose-latest.yml stop hive-server
docker-compose -f docker-compose-latest.yml rm -f hive-server
docker rm -f hive-server 2>$null

# Step 3: Clean up Derby files
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

# Step 4: Remove volume if it exists
Write-Host "Removing Docker volumes..." -ForegroundColor Blue
docker volume rm analisis-prediksi-banjir_hive_metastore_data 2>$null

# Step 4: Modify the hive-site.xml to fix Derby issues
Write-Host "Updating hive-site.xml configuration..." -ForegroundColor Blue

$hiveSiteXml = ".\config\hive\hive-site.xml"
$hiveSiteContent = Get-Content -Path $hiveSiteXml -Raw

# Replace DB connection settings to fix Derby issues
$pattern = '<property>\s*<name>javax\.jdo\.option\.ConnectionURL</name>\s*<value>.*?</value>'
$replacement = '<property><name>javax.jdo.option.ConnectionURL</name><value>jdbc:derby:;databaseName=/opt/hive/data/metastore/metastore_db;create=true</value>'

$hiveSiteContent = $hiveSiteContent -replace $pattern, $replacement
Set-Content -Path $hiveSiteXml -Value $hiveSiteContent

# Step 5: Modify docker-compose-latest.yml to fix Hive service
Write-Host "Updating docker-compose-latest.yml..." -ForegroundColor Blue

$dockerComposePath = ".\docker-compose-latest.yml"
$dockerComposeContent = Get-Content -Path $dockerComposePath -Raw

# Find the hive-server section and replace it with a simpler version
$hiveServerSection = @"
  # ==================== SERVING LAYER (LATEST HIVE 4.0.1) ====================
  hive-server:
    image: apache/hive:4.0.1
    container_name: hive-server
    restart: always
    command: ["/bin/bash", "-c", "mkdir -p /opt/hive/data/metastore && sleep 10 && cd /opt/hive && bin/schematool -dbType derby -initSchema || true && bin/hiveserver2"]
    ports:
      - "9083:9083"
      - "10000:10000"
      - "10002:10002"
    environment:
      HIVE_CONF_DIR: '/opt/hive/conf'
      JAVA_HOME: '/usr/local/openjdk-8'
    volumes:
      - ./config/hive:/opt/hive/conf
      - ./hive/data:/opt/hive/data
    networks:
      - hadoop
    depends_on:
      - namenode
"@

# Use regex to replace the entire hive-server section
$pattern = '(?s)# =+ SERVING LAYER.*?hive-server:.*?depends_on:.*?- namenode'
$dockerComposeContent = $dockerComposeContent -replace $pattern, $hiveServerSection

# Save the updated docker-compose file
Set-Content -Path $dockerComposePath -Value $dockerComposeContent

# Step 6: Start the Hive container again using the original docker-compose file
Write-Host "Starting Hive container with fixed configuration..." -ForegroundColor Blue
docker-compose -f docker-compose-latest.yml up -d hive-server

# Step 7: Wait for Hive to start
Write-Host "Waiting for Hive to be ready..." -ForegroundColor Blue
Start-Sleep -Seconds 45

# Step 8: Test the connection
Write-Host "Testing Hive connection..." -ForegroundColor Blue
docker logs hive-server --tail 20
$testResult = docker exec hive-server /opt/hive/bin/beeline -u jdbc:hive2://localhost:10000 -e "SHOW DATABASES;" 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "Hive is ready!" -ForegroundColor Green
    Write-Host "You can now connect using: docker exec -it hive-server beeline -u jdbc:hive2://localhost:10000" -ForegroundColor Green
    
    # Try to create flood_predictions database
    Write-Host "Creating flood_predictions database..." -ForegroundColor Blue
    docker exec hive-server /opt/hive/bin/beeline -u jdbc:hive2://localhost:10000 -e "CREATE DATABASE IF NOT EXISTS flood_predictions;"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Database created successfully!" -ForegroundColor Green
    } else {
        Write-Host "Failed to create database." -ForegroundColor Red
    }
} else {
    Write-Host "Hive connection failed. Check logs with: docker logs hive-server" -ForegroundColor Red
}
