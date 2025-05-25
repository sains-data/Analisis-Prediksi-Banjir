# Script untuk mempersiapkan push ke GitHub dengan docker-compose-fixed.yml sebagai file utama
# Created: May 25, 2025

# Menyimpan lokasi direktori saat ini
$currentDir = "M:\ITERA\Semester 6\Analisis Big Data\Tugas Besar\Analisis-Prediksi-Banjir"

# Menampilkan banner
Write-Host "==========================================================="
Write-Host "Persiapan Push ke GitHub - Analisis Prediksi Banjir"
Write-Host "==========================================================="

# 1. Menghapus docker-compose.yml yang lama (jika ada)
if (Test-Path "$currentDir\docker-compose.yml") {
    Write-Host "Menghapus file docker-compose.yml yang lama..." -ForegroundColor Yellow
    Remove-Item "$currentDir\docker-compose.yml" -Force
    Write-Host "✅ docker-compose.yml lama telah dihapus" -ForegroundColor Green
} else {
    Write-Host "⚠️ docker-compose.yml tidak ditemukan" -ForegroundColor Yellow
}

# 2. Mengubah nama docker-compose-fixed.yml menjadi docker-compose.yml
if (Test-Path "$currentDir\docker-compose-fixed.yml") {
    Write-Host "Mengubah nama docker-compose-fixed.yml menjadi docker-compose.yml..." -ForegroundColor Yellow
    Copy-Item "$currentDir\docker-compose-fixed.yml" -Destination "$currentDir\docker-compose.yml"
    Write-Host "✅ docker-compose-fixed.yml telah disalin ke docker-compose.yml" -ForegroundColor Green
} else {
    Write-Host "❌ ERROR: docker-compose-fixed.yml tidak ditemukan!" -ForegroundColor Red
    exit 1
}

# 3. Menghapus file-file temporary yang tidak diperlukan
$tempFiles = @(
    "test_query.hql",
    "spark_hive_test.py",
    "simple_spark_test.py"
)

foreach ($file in $tempFiles) {
    if (Test-Path "$currentDir\$file") {
        Write-Host "Menghapus file sementara: $file..." -ForegroundColor Yellow
        Remove-Item "$currentDir\$file" -Force
        Write-Host "✅ $file telah dihapus" -ForegroundColor Green
    } else {
        Write-Host "⚠️ $file tidak ditemukan" -ForegroundColor Yellow
    }
}

# 4. Membersihkan folder metastore derby
$metastoreDir = "$currentDir\hive\data\metastore"
if (Test-Path $metastoreDir) {
    Write-Host "Menghapus isi folder metastore Derby..." -ForegroundColor Yellow
    # Buat folder kosong untuk menjaga struktur
    if (-not (Test-Path "$currentDir\hive\data")) {
        New-Item -ItemType Directory -Path "$currentDir\hive\data" -Force | Out-Null
    }
    if (Test-Path $metastoreDir) {
        # Hapus folder metastore
        Remove-Item $metastoreDir -Recurse -Force
    }
    # Buat folder kosong metastore dengan file .gitkeep
    New-Item -ItemType Directory -Path $metastoreDir -Force | Out-Null
    "" | Out-File "$metastoreDir\.gitkeep" -Encoding UTF8
    Write-Host "✅ Folder metastore Derby telah dibersihkan" -ForegroundColor Green
} else {
    Write-Host "⚠️ Folder metastore Derby tidak ditemukan" -ForegroundColor Yellow
}

# 5. Menampilkan file dan folder yang siap untuk di-push
Write-Host "`nFile dan folder yang siap untuk di-push ke GitHub:" -ForegroundColor Cyan
$excludedPaths = @(
    '.git',
    '.ipynb_checkpoints',
    'spark/data',
    'hive/data/metastore'
)

$files = Get-ChildItem -Path $currentDir -Exclude $excludedPaths -Recurse -File | 
         Where-Object { $_.FullName -notmatch "($([String]::Join("|", $excludedPaths)))" }

Write-Host "Total file: $($files.Count)" -ForegroundColor White

# 6. Tampilkan langkah-langkah untuk push ke GitHub
Write-Host "`n==========================================================="
Write-Host "Langkah-langkah untuk push ke GitHub:"
Write-Host "==========================================================="
Write-Host "1. Jalankan perintah berikut untuk inisialisasi git (jika belum):" -ForegroundColor White
Write-Host "   git init" -ForegroundColor Yellow
Write-Host "2. Tambahkan remote origin (ganti URL dengan repository GitHub Anda):" -ForegroundColor White
Write-Host "   git remote add origin https://github.com/username/Analisis-Prediksi-Banjir.git" -ForegroundColor Yellow
Write-Host "3. Tambahkan semua file:" -ForegroundColor White
Write-Host "   git add ." -ForegroundColor Yellow
Write-Host "4. Commit perubahan:" -ForegroundColor White
Write-Host "   git commit -m 'Initial commit: Hadoop ecosystem with Derby-based Hive'" -ForegroundColor Yellow
Write-Host "5. Push ke GitHub:" -ForegroundColor White
Write-Host "   git push -u origin master" -ForegroundColor Yellow
Write-Host "===========================================================`n"

Write-Host "Persiapan push ke GitHub telah selesai!" -ForegroundColor Green
