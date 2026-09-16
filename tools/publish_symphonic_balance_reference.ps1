param(
    [string] $ProjectRef = "szsmcqlscqnvigakwubu",
    [string] $Bucket = "symphonic-balance-reference",
    [string] $ObjectName = "instrument-properties.json",
    [string] $WebsiteSupabaseDir = "C:\dev\OwnLifeAudioWebsite"
)

$ErrorActionPreference = "Stop"

function Invoke-CheckedCommand {
    param([scriptblock] $Command)

    $output = & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code $LASTEXITCODE"
    }

    return $output
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$jsonPath = Join-Path $repoRoot "data\instrument-properties.json"

Invoke-CheckedCommand { python (Join-Path $repoRoot "tools\validate_terminology.py") } | Out-Host

Push-Location $WebsiteSupabaseDir
try {
    Invoke-CheckedCommand { supabase db query "insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types) values ('$Bucket', '$Bucket', true, 10485760, array['application/json']) on conflict (id) do update set public = excluded.public, file_size_limit = excluded.file_size_limit, allowed_mime_types = excluded.allowed_mime_types;" --linked } | Out-Host

    $keysJson = Invoke-CheckedCommand { supabase projects api-keys --project-ref $ProjectRef --output json }
    $serviceKey = (($keysJson | ConvertFrom-Json) | Where-Object { $_.id -eq "service_role" } | Select-Object -First 1).api_key
    if (-not $serviceKey) {
        throw "Could not retrieve Supabase service_role API key."
    }

    $headers = @{
        apikey = $serviceKey
        Authorization = "Bearer $serviceKey"
        "x-upsert" = "true"
        "cache-control" = "max-age=60"
    }
    $uploadUrl = "https://$ProjectRef.supabase.co/storage/v1/object/$Bucket/$ObjectName"
    Invoke-RestMethod -Method Post -Uri $uploadUrl -Headers $headers -ContentType "application/json" -InFile $jsonPath | Out-Null
}
finally {
    Pop-Location
}

$url = "https://$ProjectRef.supabase.co/storage/v1/object/public/$Bucket/$ObjectName"
Write-Host "Published $jsonPath"
Write-Host "URL: $url"
