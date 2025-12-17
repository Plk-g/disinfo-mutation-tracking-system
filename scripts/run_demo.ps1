$ErrorActionPreference = "Stop"

$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

# ---- Required: Mongo URI ----
if ([string]::IsNullOrWhiteSpace($env:MONGO_URI)) {
  throw "MONGO_URI is not set. Example: `$env:MONGO_URI='mongodb+srv://user:pass@...'"
}

# ---- Start Zookeeper + Kafka in separate windows ----
Write-Host "Starting Zookeeper (new window)..."
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$repo\scripts\start_zookeeper.ps1`""

Start-Sleep -Seconds 6

Write-Host "Starting Kafka broker (new window)..."
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$repo\scripts\start_kafka.ps1`""

Start-Sleep -Seconds 10

# ---- Create topic ----
Write-Host "Creating topic..."
powershell -ExecutionPolicy Bypass -File "$repo\scripts\create_topic.ps1"

# ---- Run demo producer -> consumer -> verify ----
Write-Host "Running demo producer..."
python "$repo\scripts\producer_demo.py"

Write-Host "Running stream consumer..."
python "$repo\scripts\stream_consumer.py"

Write-Host "Verifying Mongo outputs..."
python "$repo\scripts\verify_mongo.py"

Write-Host "Demo complete (Kafka/ZK still running in their windows)"
