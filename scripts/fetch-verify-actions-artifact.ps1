[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateRange(1, [long]::MaxValue)]
    [long]$RunId,

    [ValidatePattern('^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$')]
    [string]$Repository = 'quintinmong/ufi001b-openwrt',

    [string]$ArtifactName = 'ufi001b-developer-ext4',

    [string]$WslDistribution = 'Ubuntu-24.04'
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$actionsRoot = Join-Path $repoRoot 'out\actions'
$runRoot = Join-Path $actionsRoot ([string]$RunId)
$artifactRoot = Join-Path $runRoot $ArtifactName
$archivePath = Join-Path $runRoot ($ArtifactName + '.zip')
$metadataPath = Join-Path $runRoot 'run-metadata.json'

function Convert-ToWslPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    $resolved = [System.IO.Path]::GetFullPath($Path)
    if ($resolved -notmatch '^([A-Za-z]):\\(.*)$') {
        throw "Only drive-letter paths can be converted to WSL paths: $resolved"
    }
    $drive = $Matches[1].ToLowerInvariant()
    $tail = $Matches[2].Replace('\', '/')
    return "/mnt/$drive/$tail"
}

function Quote-BashLiteral {
    param([Parameter(Mandatory = $true)][string]$Value)
    $singleQuote = [char]39
    $replacement = [string]$singleQuote + '"' + [string]$singleQuote + '"' + [string]$singleQuote
    return [string]$singleQuote + $Value.Replace([string]$singleQuote, $replacement) + [string]$singleQuote
}

if (Test-Path -LiteralPath $runRoot) {
    throw "Refusing to mix or overwrite an existing run directory: $runRoot"
}

$credentialInput = "protocol=https`nhost=github.com`n`n"
$credentialOutput = $credentialInput | git credential fill
$tokenLine = $credentialOutput |
    Where-Object { $_ -like 'password=*' } |
    Select-Object -First 1
if (-not $tokenLine) {
    throw 'GitHub credential is unavailable from git credential fill'
}
$headers = @{
    Authorization = 'Bearer ' + $tokenLine.Substring(9)
    Accept = 'application/vnd.github+json'
    'X-GitHub-Api-Version' = '2022-11-28'
}

$apiRoot = "https://api.github.com/repos/$Repository"
$run = Invoke-RestMethod -Uri "$apiRoot/actions/runs/$RunId" -Headers $headers
if ($run.status -ne 'completed' -or $run.conclusion -ne 'success') {
    throw "Run $RunId is not a successful completed run: status=$($run.status) conclusion=$($run.conclusion)"
}

$artifactResponse = Invoke-RestMethod -Uri "$apiRoot/actions/runs/$RunId/artifacts" -Headers $headers
$matches = @($artifactResponse.artifacts | Where-Object { $_.name -eq $ArtifactName })
if ($matches.Count -ne 1) {
    throw "Expected exactly one artifact named $ArtifactName, found $($matches.Count)"
}
$artifact = $matches[0]
if ($artifact.expired) {
    throw "Artifact $ArtifactName has expired"
}
if ([long]$artifact.workflow_run.id -ne $RunId) {
    throw "Artifact belongs to unexpected run $($artifact.workflow_run.id)"
}

New-Item -ItemType Directory -Path $artifactRoot -Force | Out-Null
Invoke-WebRequest -Uri $artifact.archive_download_url -Headers $headers -OutFile $archivePath

Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [System.IO.Compression.ZipFile]::OpenRead($archivePath)
try {
    $rootPrefix = [System.IO.Path]::GetFullPath($artifactRoot) + [System.IO.Path]::DirectorySeparatorChar
    foreach ($entry in $archive.Entries) {
        $destination = [System.IO.Path]::GetFullPath((Join-Path $artifactRoot $entry.FullName))
        if (-not $destination.StartsWith($rootPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Artifact contains an unsafe archive path: $($entry.FullName)"
        }
    }
}
finally {
    $archive.Dispose()
}
[System.IO.Compression.ZipFile]::ExtractToDirectory($archivePath, $artifactRoot)

$sumFiles = @(Get-ChildItem -LiteralPath $artifactRoot -Filter SHA256SUMS -File -Recurse)
if ($sumFiles.Count -ne 1) {
    throw "Expected one SHA256SUMS after extraction, found $($sumFiles.Count)"
}
$verificationRoot = $sumFiles[0].Directory.FullName

$metadata = [ordered]@{
    repository = $Repository
    run_id = $RunId
    run_url = $run.html_url
    head_sha = $run.head_sha
    event = $run.event
    conclusion = $run.conclusion
    artifact_id = [long]$artifact.id
    artifact_name = $artifact.name
    artifact_size_in_bytes = [long]$artifact.size_in_bytes
    downloaded_at_utc = [DateTime]::UtcNow.ToString('o')
}
$metadata | ConvertTo-Json | Set-Content -LiteralPath $metadataPath -Encoding utf8

$repoWsl = Convert-ToWslPath -Path $repoRoot
$artifactWsl = Convert-ToWslPath -Path $verificationRoot
$command = 'cd ' + (Quote-BashLiteral $repoWsl) +
    ' && python3 scripts/verify-developer-artifact.py ' + (Quote-BashLiteral $artifactWsl)
& wsl.exe -d $WslDistribution -- bash -lc $command
if ($LASTEXITCODE -ne 0) {
    throw "Offline artifact verification failed with exit code $LASTEXITCODE"
}

Write-Output "Downloaded and verified run $RunId artifact $ArtifactName"
Write-Output "Artifact directory: $verificationRoot"
Write-Output "Run metadata: $metadataPath"
