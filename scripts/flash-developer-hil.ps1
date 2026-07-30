[CmdletBinding()]
param(
    [ValidateSet('LocalCheck', 'Check', 'AuditProtected', 'FlashRootfs', 'FlashBoot')]
    [string]$Mode = 'Check',

    [string]$Confirmation = ''
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$workspaceRoot = Split-Path -Parent $repoRoot
$deviceRoot = Join-Path $workspaceRoot 'UFI001B_410wifi'
$candidateRunRoot = Join-Path $repoRoot 'out\actions\30503595724-retry1'
$candidateRoot = Join-Path $candidateRunRoot 'ufi001b-developer-ext4'
$candidateMetadata = Join-Path $candidateRunRoot 'run-metadata.json'
$emmcdl = Join-Path $workspaceRoot 'tools\emmcdl\Qualcomm Premium Tool V2.4\emmcdl.exe'
$loader = Join-Path $deviceRoot 'tools\prog_emmc_firehose_8916.mbn'
$backup = Join-Path $deviceRoot 'backup_manual\backup_manual.bin'
$protectedBackupRoot = Join-Path $deviceRoot 'backup_efs'
$logDir = Join-Path $deviceRoot 'logs\openwrt-25.12-hil'

$boot = (Get-ChildItem -LiteralPath $candidateRoot -Filter '*-ext4-boot.img' -File)
$rootfs = (Get-ChildItem -LiteralPath $candidateRoot -Filter '*-ext4-rootfs.img' -File)
if (@($boot).Count -ne 1 -or @($rootfs).Count -ne 1) {
    throw 'Expected exactly one developer ext4 boot image and one rootfs image.'
}
$boot = $boot.FullName
$rootfs = $rootfs.FullName

$revokedCandidateHashes = [ordered]@{
    'A1265330C1F8AD892DCD830B0F68689F255D3C3884BB2FC275DBF3581188507E' =
        'boot lacks the final DEVTMPFS/MMC_BLOCK root-mount chain'
    '8874BDE7229C5076FE5C00FA27FDAF57A32ABEC4629E0BB7139781DB33687B54' =
        'rootfs belongs to the revoked boot/kernel ABI'
}
foreach ($candidate in @($boot, $rootfs)) {
    $candidateHash = (Get-FileHash -LiteralPath $candidate -Algorithm SHA256).Hash.ToUpperInvariant()
    if ($revokedCandidateHashes.Contains($candidateHash)) {
        throw "Revoked HIL candidate $candidateHash ($($revokedCandidateHashes[$candidateHash])). Nothing was opened or written."
    }
}

$expected = [ordered]@{
    Repository = 'quintinmong/ufi001b-openwrt'
    RunId = 30503595724L
    HeadSha = '2D388CF815F80313A5E7B5963A073A9BBE661D38'
    ArtifactId = 8746656447L
    ArtifactName = 'ufi001b-developer-ext4'
    EmmcdlSha256 = '24540D815142A3D63C4BF4A01FD4DB0C0AEFB26794749D65480CE0A9F2BC83BB'
    LoaderSha256 = '959439AA5864685999B713C3ED12AD5FA408149648B670A9A9EF77BCC9DCAB14'
    BackupBytes = 3875520000L
    BackupSha256 = 'C7380138BFE9E4E509F90A900F6F7B580FFCFE52C2A577A8F12B8A4D7F2CA965'
    DiskBytes = 3875536896L
    BootFirstLba = 526336L
    BootLastLba = 657407L
    BootBytes = 67108864L
    BootImageBytes = 6379520L
    BootSha256 = '4FA5BBAC35685395FBD7F0FBF04394E0F82AF370B157937E37E4FDA817FF63BE'
    RootfsFirstLba = 659456L
    RootfsLastLba = 7569374L
    RootfsBytes = 3537878528L
    RootfsImageBytes = 536870912L
    RootfsSha256 = 'A1CC51903BEFF5E5916927572B53F406B26452E9ED1A8BE0A6C604373D2107AE'
}

$protectedHashes = [ordered]@{
    fsc = '5F70BF18A086007016E948B04AED3B82103A36BEA41755B6CDDFAF10ACE3C6EF'
    fsg = '5CEAAEB08434511BDAD19CA570D1AD9A85BE5051E3ECFE5E46A362685B14B45A'
    modemst1 = '35DDA854DEBBAAABA314649E89ECFF0C49764644AD17A5ADC3CCEEC46301548F'
    modemst2 = '651B0D3BAFBCD1AF54643D50B407D78523171E1B8C83D448CC7BA3676BA700EF'
}

$protectedFullHashes = [ordered]@{
    fsc = '5F70BF18A086007016E948B04AED3B82103A36BEA41755B6CDDFAF10ACE3C6EF'
    fsg = 'B7EB35B968806602F295C552C85D45C0222FBC3DD129A6E542BCAD108F10EC82'
    modemst1 = '880309D6151B4F98B953F4AF68D5E4EFC9EDEDB12C896F58AA37E2C2596684C6'
    modemst2 = '2EE62826779F6AE9BC7240666AFC4B83E0C794C353361F482D50948BDCFA9D31'
}

$protectedGeometry = [ordered]@{
    fsc = [pscustomobject]@{ FirstLba = 275488L; Sectors = 2L }
    fsg = [pscustomobject]@{ FirstLba = 393216L; Sectors = 4096L }
    modemst1 = [pscustomobject]@{ FirstLba = 267296L; Sectors = 4096L }
    modemst2 = [pscustomobject]@{ FirstLba = 271392L; Sectors = 4096L }
}

$expectedCurrentGpt = [ordered]@{
    cdt = [pscustomobject]@{ FirstLba = 131072L; Sectors = 4L }
    sbl1 = [pscustomobject]@{ FirstLba = 262144L; Sectors = 1024L }
    rpm = [pscustomobject]@{ FirstLba = 263168L; Sectors = 1024L }
    tz = [pscustomobject]@{ FirstLba = 264192L; Sectors = 2048L }
    hyp = [pscustomobject]@{ FirstLba = 266240L; Sectors = 1024L }
    sec = [pscustomobject]@{ FirstLba = 267264L; Sectors = 32L }
    modemst1 = $protectedGeometry.modemst1
    modemst2 = $protectedGeometry.modemst2
    fsc = $protectedGeometry.fsc
    fsg = $protectedGeometry.fsg
    aboot = [pscustomobject]@{ FirstLba = 524288L; Sectors = 2048L }
    boot = [pscustomobject]@{ FirstLba = 526336L; Sectors = 131072L }
    devinfo = [pscustomobject]@{ FirstLba = 657408L; Sectors = 2048L }
    rootfs = [pscustomobject]@{ FirstLba = 659456L; Sectors = 6909919L }
}

function Assert-File {
    param(
        [Parameter(Mandatory)] [string]$Path,
        [Parameter(Mandatory)] [long]$Bytes,
        [Parameter(Mandatory)] [string]$Sha256
    )
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Required file is missing: $Path"
    }
    $item = Get-Item -LiteralPath $Path
    if ($item.Length -ne $Bytes) {
        throw "Unexpected file length for $Path`: expected $Bytes, found $($item.Length)"
    }
    $actual = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToUpperInvariant()
    if ($actual -ne $Sha256) {
        throw "SHA-256 mismatch for $Path`: expected $Sha256, found $actual"
    }
}

function Assert-FilePrefix {
    param(
        [Parameter(Mandatory)] [string]$Path,
        [Parameter(Mandatory)] [long]$Bytes,
        [Parameter(Mandatory)] [string]$Sha256
    )
    $item = Get-Item -LiteralPath $Path
    if ($item.Length -lt $Bytes) {
        throw "File is shorter than the required prefix for $Path`: $($item.Length) < $Bytes"
    }
    $stream = [System.IO.File]::Open($Path, 'Open', 'Read', 'Read')
    $hasher = [System.Security.Cryptography.IncrementalHash]::CreateHash(
        [System.Security.Cryptography.HashAlgorithmName]::SHA256
    )
    try {
        $buffer = [byte[]]::new(1MB)
        $remaining = $Bytes
        while ($remaining -gt 0) {
            $requested = [int][Math]::Min($buffer.Length, $remaining)
            $read = $stream.Read($buffer, 0, $requested)
            if ($read -le 0) {
                throw "Unexpected EOF while hashing prefix of $Path"
            }
            $hasher.AppendData($buffer, 0, $read)
            $remaining -= $read
        }
        $actual = [Convert]::ToHexString($hasher.GetHashAndReset())
    }
    finally {
        $hasher.Dispose()
        $stream.Dispose()
    }
    if ($actual -ne $Sha256) {
        throw "SHA-256 mismatch in first $Bytes bytes of $Path`: expected $Sha256, found $actual"
    }
}

function Assert-CandidateProvenance {
    if (-not (Test-Path -LiteralPath $candidateMetadata -PathType Leaf)) {
        throw "Candidate run metadata is missing: $candidateMetadata"
    }
    $metadata = Get-Content -LiteralPath $candidateMetadata -Raw | ConvertFrom-Json
    if ($metadata.repository -ne $expected.Repository -or
        [long]$metadata.run_id -ne $expected.RunId -or
        $metadata.head_sha.ToUpperInvariant() -ne $expected.HeadSha -or
        [long]$metadata.artifact_id -ne $expected.ArtifactId -or
        $metadata.artifact_name -ne $expected.ArtifactName -or
        $metadata.conclusion -ne 'success') {
        throw 'Candidate provenance metadata does not match the approved successful Actions artifact.'
    }
}

function Get-BackupPartitions {
    param([Parameter(Mandatory)] [string]$Path)

    $stream = [System.IO.File]::Open($Path, 'Open', 'Read', 'Read')
    try {
        $reader = [System.IO.BinaryReader]::new($stream)
        $stream.Position = 512
        if ([System.Text.Encoding]::ASCII.GetString($reader.ReadBytes(8)) -ne 'EFI PART') {
            throw 'The full backup does not contain a valid primary GPT.'
        }
        $stream.Position = 512 + 72
        $entriesLba = $reader.ReadUInt64()
        $entryCount = $reader.ReadUInt32()
        $entrySize = $reader.ReadUInt32()
        $partitions = [ordered]@{}
        for ($index = 0; $index -lt $entryCount; $index++) {
            $stream.Position = [int64]($entriesLba * 512 + $index * $entrySize)
            $typeGuid = $reader.ReadBytes(16)
            if (@($typeGuid | Where-Object { $_ -ne 0 }).Count -eq 0) {
                continue
            }
            $null = $reader.ReadBytes(16)
            $firstLba = [int64]$reader.ReadUInt64()
            $lastLba = [int64]$reader.ReadUInt64()
            $null = $reader.ReadUInt64()
            $nameBytes = $reader.ReadBytes([Math]::Min(72, $entrySize - 56))
            $name = [System.Text.Encoding]::Unicode.GetString($nameBytes).TrimEnd([char]0)
            $partitions[$name] = [pscustomobject]@{
                FirstLba = $firstLba
                LastLba = $lastLba
                Bytes = ($lastLba - $firstLba + 1) * 512
            }
        }
        return $partitions
    }
    finally {
        $stream.Dispose()
    }
}

function Get-QdloaderPort {
    $devices = @(Get-PnpDevice -PresentOnly -ErrorAction Stop | Where-Object {
        $_.Status -eq 'OK' -and $_.InstanceId -like 'USB\VID_05C6&PID_9008*'
    })
    if ($devices.Count -ne 1) {
        throw "Expected exactly one Qualcomm 05C6:9008 device, found $($devices.Count)."
    }
    if ($devices[0].FriendlyName -notmatch '\((COM\d+)\)') {
        throw "Cannot determine the serial port from $($devices[0].FriendlyName)."
    }
    return $Matches[1]
}

function Invoke-Emmcdl {
    param(
        [Parameter(Mandatory)] [string[]]$Arguments,
        [Parameter(Mandatory)] [string]$LogPath,
        [Parameter(Mandatory)] [int]$TimeoutSeconds
    )

    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $emmcdl
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    foreach ($argument in $Arguments) {
        $startInfo.ArgumentList.Add($argument)
    }

    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $startInfo
    $null = $process.Start()
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    $timedOut = $false
    if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
        $process.Kill($true)
        $process.WaitForExit()
        $timedOut = $true
    }
    $stdout = $stdoutTask.GetAwaiter().GetResult()
    $stderr = $stderrTask.GetAwaiter().GetResult()
    $text = ($stdout + $stderr).TrimEnd()
    Set-Content -LiteralPath $LogPath -Value $text -Encoding utf8
    if ($text) {
        Write-Host $text
    }
    if ($timedOut) {
        throw "emmcdl command timed out after $TimeoutSeconds seconds. Re-enter clean 9008 mode. Log: $LogPath"
    }
    if ($process.ExitCode -ne 0 -or $text -match '(?im)^Traceback \(most recent call last\):') {
        throw "emmcdl command failed with exit code $($process.ExitCode). Log: $LogPath"
    }
    return $text
}

function Assert-CurrentGpt {
    param(
        [Parameter(Mandatory)] [string]$Port,
        [Parameter(Mandatory)] [string]$Stamp
    )
    $log = Join-Path $logDir "edl-gpt-$Stamp.log"
    $text = Invoke-Emmcdl -Arguments @(
        '-p', $Port, '-f', $loader, '-MaxPayloadSizeToTargetInBytes', '16384', '-gpt'
    ) -LogPath $log -TimeoutSeconds 120

    foreach ($name in $expectedCurrentGpt.Keys) {
        $entry = $expectedCurrentGpt[$name]
        $pattern = "(?im)^\s*\d+\. Partition Name: $([regex]::Escape($name)) Start LBA: $($entry.FirstLba) Size in LBA: $($entry.Sectors)\s*$"
        if ($text -notmatch $pattern) {
            throw "Current GPT entry differs for $name. Log: $log"
        }
    }
    if ($text -notmatch '(?im)^Status: 0 The operation completed successfully\.\s*$') {
        throw "emmcdl did not report a successful GPT read. Log: $log"
    }
    Write-Host "CURRENT GPT CHECK PASSED: $log" -ForegroundColor Green
}

function Assert-WriteConfirmation {
    param([Parameter(Mandatory)] [string]$ExpectedText)
    if ($Confirmation -cne $ExpectedText) {
        throw "Required -Confirmation '$ExpectedText'. Nothing was written."
    }
}

function Readback-And-Verify {
    param(
        [Parameter(Mandatory)] [string]$Port,
        [Parameter(Mandatory)] [string]$Name,
        [Parameter(Mandatory)] [long]$FirstLba,
        [Parameter(Mandatory)] [long]$Bytes,
        [Parameter(Mandatory)] [string]$Sha256,
        [Parameter(Mandatory)] [string]$Stamp
    )
    $readback = Join-Path $logDir "$Name-readback-$Stamp.bin"
    $log = Join-Path $logDir "edl-readback-$Name-$Stamp.log"
    $text = Invoke-Emmcdl -Arguments @(
        '-p', $Port, '-f', $loader, '-MaxPayloadSizeToTargetInBytes', '16384',
        '-d', "$FirstLba", "$($Bytes / 512)", '-o', $readback
    ) -LogPath $log -TimeoutSeconds 600
    if ($text -notmatch '(?im)^Status: 0 The operation completed successfully\.\s*$') {
        throw "emmcdl did not report a completed $Name readback. Log: $log"
    }
    Assert-File -Path $readback -Bytes $Bytes -Sha256 $Sha256
    Write-Host "$Name READBACK SHA-256 PASSED: $readback" -ForegroundColor Green
    return $readback
}

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

foreach ($required in @($emmcdl, $loader, $backup, $boot, $rootfs)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required file is missing: $required"
    }
}
Assert-File -Path $emmcdl -Bytes 177152L -Sha256 $expected.EmmcdlSha256
Assert-File -Path $loader -Bytes 93288L -Sha256 $expected.LoaderSha256
Assert-File -Path $backup -Bytes $expected.BackupBytes -Sha256 $expected.BackupSha256
Assert-CandidateProvenance
Assert-File -Path $boot -Bytes $expected.BootImageBytes -Sha256 $expected.BootSha256
Assert-File -Path $rootfs -Bytes $expected.RootfsImageBytes -Sha256 $expected.RootfsSha256

$bootHeader = [System.IO.File]::ReadAllBytes($boot)[0..7]
if ([System.Text.Encoding]::ASCII.GetString($bootHeader) -ne 'ANDROID!') {
    throw 'Developer boot candidate is not an Android boot image.'
}
$rootfsStream = [System.IO.File]::OpenRead($rootfs)
try {
    $rootfsStream.Position = 1080
    if ($rootfsStream.ReadByte() -ne 0x53 -or $rootfsStream.ReadByte() -ne 0xEF) {
        throw 'Developer rootfs candidate does not have an ext4 superblock.'
    }
}
finally {
    $rootfsStream.Dispose()
}

$saved = Get-BackupPartitions -Path $backup
if ($saved.Count -ne 14 -or
    $saved.boot.FirstLba -ne $expected.BootFirstLba -or
    $saved.boot.LastLba -ne $expected.BootLastLba -or
    $saved.boot.Bytes -ne $expected.BootBytes -or
    $saved.rootfs.FirstLba -ne $expected.RootfsFirstLba -or
    $saved.rootfs.LastLba -ne $expected.RootfsLastLba -or
    $saved.rootfs.Bytes -ne $expected.RootfsBytes) {
    throw 'Saved GPT does not match the approved 14-partition UFI001B geometry.'
}

if ($Mode -eq 'LocalCheck') {
    Write-Host 'LOCAL CHECK PASSED: backup, GPT, loader, Android boot and ext4 candidate are exact.' -ForegroundColor Green
    Write-Host 'No USB device was opened and no eMMC data was written.'
    exit 0
}

$conflicting = @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
    $_.ProcessName -match 'miko|premium|qfil|qpst|emmcdl' -and $_.Id -ne $PID
})
if ($conflicting.Count -gt 0) {
    throw 'Close all other EDL/Qualcomm GUI tools before continuing.'
}

$port = Get-QdloaderPort
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
Write-Host "Mode: $Mode; device: UFI001B MSM8916 on $port" -ForegroundColor Cyan
Write-Host "Full backup SHA-256: $($expected.BackupSha256)"
Write-Host 'Only p12 boot and p14 rootfs are permitted write targets.'

if ($Mode -eq 'Check') {
    Assert-CurrentGpt -Port $port -Stamp $stamp
    Write-Host 'CHECK PASSED. No eMMC data was written.' -ForegroundColor Green
    exit 0
}

if ($Mode -eq 'AuditProtected') {
    Assert-CurrentGpt -Port $port -Stamp $stamp
    foreach ($name in $protectedHashes.Keys) {
        $path = Join-Path $logDir "$name-pre-hil-$stamp.bin"
        $log = Join-Path $logDir "edl-read-$name-$stamp.log"
        $geometry = $protectedGeometry[$name]
        $text = Invoke-Emmcdl -Arguments @(
            '-p', $port, '-f', $loader, '-MaxPayloadSizeToTargetInBytes', '16384',
            '-d', "$($geometry.FirstLba)", "$($geometry.Sectors)", '-o', $path
        ) -LogPath $log -TimeoutSeconds 180
        if ($text -notmatch '(?im)^Status: 0 The operation completed successfully\.\s*$') {
            throw "emmcdl did not report a completed $name read. Log: $log"
        }
        $reference = Join-Path $protectedBackupRoot "$name.bin"
        $prefixBytes = (Get-Item -LiteralPath $reference).Length
        $partitionBytes = $geometry.Sectors * 512
        Assert-File -Path $reference -Bytes $prefixBytes -Sha256 $protectedHashes[$name]
        Assert-File -Path $path -Bytes $partitionBytes -Sha256 $protectedFullHashes[$name]
        Assert-FilePrefix -Path $path -Bytes $prefixBytes -Sha256 $protectedHashes[$name]
        Write-Host "$name MATCHES FULL PRE-HIL SNAPSHOT AND DEVICE-UNIQUE BACKUP PREFIX" -ForegroundColor Green
    }
    Write-Host 'PROTECTED PARTITION AUDIT PASSED. No eMMC data was written.' -ForegroundColor Green
    exit 0
}

Assert-CurrentGpt -Port $port -Stamp $stamp

if ($Mode -eq 'FlashRootfs') {
    Assert-WriteConfirmation -ExpectedText 'FLASH-UFI001B-DEVELOPER-ROOTFS'
    $log = Join-Path $logDir "edl-flash-rootfs-$stamp.log"
    Write-Host 'Writing ONLY p14 rootfs. Do not disconnect power.' -ForegroundColor Red
    $text = Invoke-Emmcdl -Arguments @(
        '-p', $port, '-f', $loader, '-MaxPayloadSizeToTargetInBytes', '16384',
        '-b', 'rootfs', $rootfs
    ) -LogPath $log -TimeoutSeconds 600
    if ($text -notmatch '(?im)^Status: 0 The operation completed successfully\.\s*$') {
        throw "emmcdl did not report a completed rootfs write. Log: $log"
    }
    $readbackArgs = @{
        Port = $port
        Name = 'rootfs'
        FirstLba = $expected.RootfsFirstLba
        Bytes = $expected.RootfsImageBytes
        Sha256 = $expected.RootfsSha256
        Stamp = $stamp
    }
    $readback = Readback-And-Verify @readbackArgs
    $resolved = (Resolve-Path -LiteralPath $readback).Path
    if ($resolved -notmatch '^([A-Za-z]):\\(.*)$') {
        throw "Cannot convert readback path for WSL e2fsck: $resolved"
    }
    $wslPath = "/mnt/$($Matches[1].ToLowerInvariant())/$($Matches[2].Replace('\', '/'))"
    & wsl.exe -d Ubuntu-24.04 -- e2fsck -f -n $wslPath
    if ($LASTEXITCODE -ne 0) {
        throw "Readback ext4 check failed with exit code $LASTEXITCODE."
    }
    Write-Host 'ROOTFS FLASH, READBACK, SHA-256 AND EXT4 CHECK PASSED.' -ForegroundColor Green
    exit 0
}

Assert-WriteConfirmation -ExpectedText 'FLASH-UFI001B-DEVELOPER-BOOT'
$log = Join-Path $logDir "edl-flash-boot-$stamp.log"
Write-Host 'Writing ONLY p12 boot. Do not disconnect power.' -ForegroundColor Red
$text = Invoke-Emmcdl -Arguments @(
    '-p', $port, '-f', $loader, '-MaxPayloadSizeToTargetInBytes', '16384',
    '-b', 'boot', $boot
) -LogPath $log -TimeoutSeconds 300
if ($text -notmatch '(?im)^Status: 0 The operation completed successfully\.\s*$') {
    throw "emmcdl did not report a completed boot write. Log: $log"
}
$readbackArgs = @{
    Port = $port
    Name = 'boot'
    FirstLba = $expected.BootFirstLba
    Bytes = $expected.BootImageBytes
    Sha256 = $expected.BootSha256
    Stamp = $stamp
}
$null = Readback-And-Verify @readbackArgs
Write-Host 'BOOT FLASH, READBACK AND SHA-256 CHECK PASSED.' -ForegroundColor Green
Write-Host 'Unplug the device normally and reconnect without holding reset to begin HIL.' -ForegroundColor Yellow
