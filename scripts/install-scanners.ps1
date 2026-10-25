# Installs only isolated developer scanners, never Scorbit helpers or live assets.
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$releases = @(
    @{
        Name = 'trivy'; Version = '0.76.1'
        Url = 'https://github.com/aquasecurity/trivy/releases/download/v0.76.1/trivy_0.76.1_windows-64bit.zip'
        Sha256 = '1051f49cb22d5284f43425f72aad9cda63ca12ceb92e7caa06903490c82dc9bf'
    },
    @{
        Name = 'gitleaks'; Version = '8.30.1'
        Url = 'https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_windows_x64.zip'
        Sha256 = 'd29144deff3a68aa93ced33dddf84b7fdc26070add4aa0f4513094c8332afc4e'
    }
)
New-Item -ItemType Directory -Force local/security | Out-Null
foreach ($release in $releases) {
    $archive = "local/security/$($release.Name)-$($release.Version).zip"
    Invoke-WebRequest -Uri $release.Url -OutFile $archive
    if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash -ne $release.Sha256) {
        throw "Checksum mismatch: $($release.Name). Refusing to extract."
    }
    Expand-Archive -LiteralPath $archive -DestinationPath "local/security/$($release.Name)" -Force
    Write-Output "Installed verified $($release.Name) $($release.Version) under local/security."
}
