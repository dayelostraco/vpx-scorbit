param(
    [string]$Python = '.venv/Scripts/python.exe',
    [string]$SecurityBin = 'local/security/venv/Scripts',
    [string]$Trivy = 'local/security/trivy/trivy.exe',
    [string]$Gitleaks = 'local/security/gitleaks/gitleaks.exe'
)
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
New-Item -ItemType Directory -Force local/security | Out-Null
function Invoke-Check([string]$Exe, [string[]]$Arguments) {
    & $Exe @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Check failed: $Exe (exit $LASTEXITCODE)" }
}
Invoke-Check $Python @('-m', 'coverage', 'run', '-m', 'unittest', 'discover', '-s', 'tests', '-v')
Invoke-Check $Python @('-m', 'coverage', 'json', '-o', 'local/security/coverage.json')
Invoke-Check $Python @('scripts/check_coverage.py', 'local/security/coverage.json')
Invoke-Check $Python @('scripts/audit_comments.py', 'local/security/comment-audit.json')
Invoke-Check "$SecurityBin/ruff.exe" @('check', 'tools', 'vpx_scorbit', 'tests', 'scripts')
Invoke-Check "$SecurityBin/ruff.exe" @('format', '--check', 'tools', 'vpx_scorbit', 'tests', 'scripts')
$env:SEMGREP_SEND_METRICS = 'off'
$env:SEMGREP_ENABLE_VERSION_CHECK = '0'
Invoke-Check "$SecurityBin/semgrep.exe" @('scan', '--config', 'p/python', '--config', 'p/security-audit',
    '--metrics', 'off', '--disable-version-check', '--error', '--exclude', 'local', '--exclude', '.venv',
    '--json', '--output', 'local/security/semgrep.json', '.')
Invoke-Check $Trivy @('fs', '--scanners', 'vuln,secret,misconfig', '--exit-code', '1',
    '--skip-dirs', '.git', '--skip-dirs', '.venv', '--skip-dirs', 'local',
    '--skip-dirs', 'docs/prior-research', '--format', 'json', '--output', 'local/security/trivy.json', '.')
Invoke-Check "$SecurityBin/pip-audit.exe" @('-r', 'requirements.txt', '--cache-dir', 'local/security/audit-cache',
    '--format', 'json', '--output', 'local/security/pip-audit.json')
Invoke-Check $Gitleaks @('git', '--redact', '--report-format', 'json', '--report-path', 'local/security/gitleaks.json', '.')
Write-Output 'Quality checks passed. Hardware, service integration and licensing qualification remain separate.'
