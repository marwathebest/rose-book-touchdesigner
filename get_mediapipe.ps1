# get_mediapipe.ps1
# Downloads MediaPipe.tox (187 MB, too big for GitHub) from the official
# mediapipe-touchdesigner v0.6.0 release and puts it in .\toxes\
# Run once:  right-click > Run with PowerShell   (or: powershell -ExecutionPolicy Bypass -File get_mediapipe.ps1)

$ErrorActionPreference = 'Stop'
$here   = Split-Path -Parent $MyInvocation.MyCommand.Path
$target = Join-Path $here 'toxes\MediaPipe.tox'
$url    = 'https://github.com/torinmb/mediapipe-touchdesigner/releases/download/v0.6.0/release.zip'
$size   = 187002508

if ((Test-Path $target) -and ((Get-Item $target).Length -eq $size)) {
    Write-Host 'MediaPipe.tox is already here. Nothing to do.'
    exit 0
}

$zip = Join-Path $env:TEMP 'mediapipe-touchdesigner-v0.6.0.zip'
Write-Host 'Downloading mediapipe-touchdesigner v0.6.0 (~188 MB)...'
$ProgressPreference = 'SilentlyContinue'
Invoke-WebRequest -Uri $url -OutFile $zip

Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [System.IO.Compression.ZipFile]::OpenRead($zip)
try {
    $entry = $archive.Entries | Where-Object { $_.FullName -eq 'release/toxes/MediaPipe.tox' }
    if (-not $entry) { throw 'MediaPipe.tox was not found in the release zip.' }
    New-Item -ItemType Directory -Force (Split-Path $target) | Out-Null
    [System.IO.Compression.ZipFileExtensions]::ExtractToFile($entry, $target, $true)
} finally {
    $archive.Dispose()
}
Remove-Item $zip

if ((Get-Item $target).Length -ne $size) { throw 'MediaPipe.tox size does not match v0.6.0.' }
Write-Host "Done: $target"
Write-Host 'Now open rose_book.toe in TouchDesigner.'
