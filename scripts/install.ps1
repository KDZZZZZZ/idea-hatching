param(
  [switch]$Auto,
  [ValidateSet('periodic','always')][string]$Mode = 'periodic',
  [string]$Every = '30m',
  [switch]$Uninstall,
  [switch]$Status,
  [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$SkillDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Heartbeat = Join-Path $SkillDir 'scripts\heartbeat.py'
$TaskPeriodic = 'IdeaHatchingPeriodic'
$TaskAlways = 'IdeaHatchingAlways'

function Require-Python {
  $cmd = Get-Command python -ErrorAction SilentlyContinue
  if (-not $cmd) { throw 'python is required on PATH' }
}

function Copy-Skill {
  python (Join-Path $SkillDir 'scripts\package.py') --sync | Out-Null
}

function Remove-Tasks {
  schtasks /Delete /TN $TaskPeriodic /F 2>$null | Out-Null
  schtasks /Delete /TN $TaskAlways /F 2>$null | Out-Null
}

function Show-Status {
  python $Heartbeat --status
  schtasks /Query /TN $TaskPeriodic /FO LIST 2>$null
  schtasks /Query /TN $TaskAlways /FO LIST 2>$null
}

Require-Python

if ($Status) { Show-Status; exit 0 }
if ($Uninstall) {
  Remove-Tasks
  python $Heartbeat --stop
  Write-Output 'Auto Hatch scheduler tasks removed/disabled.'
  exit 0
}

if ($DryRun) {
  if ($Auto) {
    Write-Output "DRY RUN: would enable Auto Hatch mode=$Mode every=$Every"
  } else {
    Write-Output 'DRY RUN: would install/sync the skill and initialize ~/idea-hatching only. Auto Mode would remain off.'
  }
  exit 0
}

Copy-Skill
python (Join-Path $SkillDir 'scripts\init_workspace.py') | Out-Null

if (-not $Auto) {
  Write-Output 'Installed Idea Hatching skill and initialized workspace. Auto Mode is off.'
  exit 0
}

python $Heartbeat --mode $Mode --every $Every --status | Out-Null


Remove-Tasks
$Python = (Get-Command python).Source
if ($Mode -eq 'periodic') {
  $minutes = 30
  if ($Every -match '^(\d+)m$') { $minutes = [int]$Matches[1] }
  elseif ($Every -match '^(\d+)h$') { $minutes = [int]$Matches[1] * 60 }
  elseif ($Every -match '^(\d+)d$') { $minutes = [int]$Matches[1] * 1440 }
  else { throw 'Windows periodic scheduler currently supports m/h/d intervals, e.g. 30m, 2h, 1d' }
  schtasks /Create /TN $TaskPeriodic /SC MINUTE /MO $minutes /TR "`"$Python`" `"$Heartbeat`" --once" /F | Out-Null
  Write-Output "Enabled Auto Hatch: $TaskPeriodic every $Every."
} else {
  schtasks /Create /TN $TaskAlways /SC ONLOGON /TR "`"$Python`" `"$Heartbeat`" --loop" /F | Out-Null
  Write-Output "Enabled Auto Hatch: $TaskAlways on logon with cooldown $Every."
}
