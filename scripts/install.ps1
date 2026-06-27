param(
  [switch]$Status,
  [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$SkillDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Heartbeat = Join-Path $SkillDir 'scripts\heartbeat.py'

function Require-Python {
  $cmd = Get-Command python -ErrorAction SilentlyContinue
  if (-not $cmd) { throw 'python is required on PATH' }
}

Require-Python

if ($Status) {
  python $Heartbeat --status
  exit 0
}

if ($DryRun) {
  Write-Output 'DRY RUN: would install/sync the skill and initialize ~/idea-hatching. Auto Mode would remain unchanged.'
  exit 0
}

python (Join-Path $SkillDir 'scripts\package.py') --sync | Out-Null
python (Join-Path $SkillDir 'scripts\init_workspace.py') | Out-Null
Write-Output 'Installed Idea Hatching skill and initialized workspace. Auto Mode is unchanged.'
