[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateRange(1, [long]::MaxValue)]
    [long]$RunId,

    [ValidatePattern('^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$')]
    [string]$Repository = 'quintinmong/ufi001b-openwrt',

    [ValidatePattern('^[A-Za-z0-9_.-]+$')]
    [ValidateScript({ $_ -eq 'ufi001b-stable-squashfs' })]
    [string]$ArtifactName = 'ufi001b-stable-squashfs',

    [ValidatePattern('^[A-Za-z0-9_.-]+$')]
    [string]$DestinationName,

    [string]$WslDistribution = 'Ubuntu-24.04'
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$actionsRoot = Join-Path $repoRoot 'out\actions'
if (-not $DestinationName) {
    $DestinationName = [string]$RunId
}
$actionsRoot = [System.IO.Path]::GetFullPath($actionsRoot)
$runRoot = [System.IO.Path]::GetFullPath((Join-Path $actionsRoot $DestinationName))
if (-not $runRoot.StartsWith(
        $actionsRoot + [System.IO.Path]::DirectorySeparatorChar,
        [System.StringComparison]::OrdinalIgnoreCase
    )) {
    throw "Destination escapes the Actions output root: $DestinationName"
}
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

function Invoke-GitHubRest {
    param([Parameter(Mandatory = $true)][string]$Uri)

    for ($attempt = 1; $attempt -le 5; $attempt++) {
        try {
            return Invoke-RestMethod -Uri $Uri -Headers $headers
        }
        catch {
            if ($attempt -eq 5) {
                throw
            }
            Start-Sleep -Seconds (2 * $attempt)
        }
    }
}

function Save-GitHubArtifact {
    param(
        [Parameter(Mandatory = $true)][string]$Uri,
        [Parameter(Mandatory = $true)][string]$Path
    )

    for ($attempt = 1; $attempt -le 5; $attempt++) {
        try {
            Invoke-WebRequest -Uri $Uri -Headers $headers -OutFile $Path
            if ((Get-Item -LiteralPath $Path).Length -le 0) {
                throw 'Artifact download produced an empty file'
            }
            return
        }
        catch {
            if ($attempt -eq 5) {
                throw
            }
            Start-Sleep -Seconds (3 * $attempt)
        }
    }
}

$apiRoot = "https://api.github.com/repos/$Repository"
$run = Invoke-GitHubRest -Uri "$apiRoot/actions/runs/$RunId"
if ($run.status -ne 'completed' -or $run.conclusion -ne 'success') {
    throw "Run $RunId is not a successful completed run: status=$($run.status) conclusion=$($run.conclusion)"
}

$artifactResponse = Invoke-GitHubRest -Uri "$apiRoot/actions/runs/$RunId/artifacts"
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
Save-GitHubArtifact -Uri $artifact.archive_download_url -Path $archivePath

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
$verifier = 'scripts/verify-stable-artifact.py'
$command = 'cd ' + (Quote-BashLiteral $repoWsl) +
    ' && python3 ' + (Quote-BashLiteral $verifier) + ' ' + (Quote-BashLiteral $artifactWsl)
& wsl.exe -d $WslDistribution -- bash -lc $command
if ($LASTEXITCODE -ne 0) {
    throw "Offline artifact verification failed with exit code $LASTEXITCODE"
}

Write-Output "Downloaded and verified run $RunId artifact $ArtifactName"
Write-Output "Artifact directory: $verificationRoot"
Write-Output "Run metadata: $metadataPath"
