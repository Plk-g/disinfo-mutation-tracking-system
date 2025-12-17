$ErrorActionPreference = "Stop"

$repo = Split-Path -Parent $PSScriptRoot
$kafka = Join-Path $repo "tools\kafka_2.12-3.6.0"

if (!(Test-Path $kafka)) {
  throw "Kafka not found at $kafka. Download/extract Kafka into tools\ first."
}

Set-Location $kafka
.\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties
