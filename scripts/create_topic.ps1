$ErrorActionPreference = "Stop"

$Topic = $env:KAFKA_TOPIC
if ([string]::IsNullOrWhiteSpace($Topic)) { $Topic = "disinformation-stream" }

$Broker = $env:KAFKA_BROKER
if ([string]::IsNullOrWhiteSpace($Broker)) { $Broker = "localhost:9092" }

$repo = Split-Path -Parent $PSScriptRoot
$kafka = Join-Path $repo "tools\kafka_2.12-3.6.0"

Set-Location $kafka

try {
  .\bin\windows\kafka-topics.bat --create --topic $Topic --bootstrap-server $Broker --replication-factor 1 --partitions 1
  Write-Host "Topic created: $Topic"
} catch {
  Write-Host "Topic likely already exists (safe to ignore)."
}
