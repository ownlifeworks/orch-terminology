param()

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$dataDir = Join-Path $root "data"
$sourceDir = Join-Path $dataDir "catalog"
$outputPath = Join-Path $dataDir "catalog.json"

if (-not (Test-Path -LiteralPath $sourceDir)) {
    throw "Catalog source directory not found: $sourceDir"
}

$sourceFiles = Get-ChildItem -Recurse -File -Filter *.json -LiteralPath $sourceDir | Sort-Object FullName
if (-not $sourceFiles) {
    throw "No catalog source JSON files found under $sourceDir"
}

$index = @{}
foreach ($file in $sourceFiles) {
    $raw = Get-Content -Raw -LiteralPath $file.FullName
    $payload = $raw | ConvertFrom-Json
    if ($payload -isnot [System.Collections.IEnumerable] -and $raw.TrimStart().StartsWith("[")) {
        $payload = @($payload)
    }
    if ($payload -isnot [System.Collections.IEnumerable]) {
        throw "Catalog source file must contain a JSON array: $($file.FullName)"
    }

    foreach ($entry in $payload) {
        if ($null -eq $entry.vendorId -or $null -eq $entry.libraryId -or $null -eq $entry.instrumentId) {
            throw "Invalid catalog entry in $($file.FullName)"
        }

        $entryKey = "$($entry.vendorId)|$($entry.libraryId)|$($entry.instrumentId)"
        if (-not $index.ContainsKey($entryKey)) {
            $index[$entryKey] = [ordered]@{
                vendorId = $entry.vendorId
                libraryId = $entry.libraryId
                instrumentId = $entry.instrumentId
                articulations = @{}
            }
        }

        foreach ($articulation in $entry.articulations) {
            if ($null -eq $articulation.articulationId) {
                throw "Invalid articulation in $($file.FullName)"
            }

            $articulationKey = [string]$articulation.articulationId
            if (-not $index[$entryKey].articulations.ContainsKey($articulationKey)) {
                $index[$entryKey].articulations[$articulationKey] = @()
            }

            $index[$entryKey].articulations[$articulationKey] += @($articulation.variantIds)
        }
    }
}

$orderedEntries = @($index.Values | Sort-Object `
    @{ Expression = { $_.vendorId } }, `
    @{ Expression = { $_.libraryId } }, `
    @{ Expression = { $_.instrumentId } })

$catalog = foreach ($entry in $orderedEntries) {
    $articulations = foreach ($artKey in ($entry.articulations.Keys | Sort-Object)) {
        [ordered]@{
            articulationId = $artKey
            variantIds = @($entry.articulations[$artKey] | Sort-Object -Unique)
        }
    }

    [ordered]@{
        vendorId = $entry.vendorId
        libraryId = $entry.libraryId
        instrumentId = $entry.instrumentId
        articulations = @($articulations)
    }
}

$catalogJson = $catalog | ConvertTo-Json -Depth 8
Set-Content -LiteralPath $outputPath -Value ($catalogJson + "`n") -Encoding utf8

Write-Host "Catalog sources combined: $($sourceFiles.Count)"
Write-Host "Catalog entries written: $($catalog.Count)"
Write-Host "Output: $outputPath"
