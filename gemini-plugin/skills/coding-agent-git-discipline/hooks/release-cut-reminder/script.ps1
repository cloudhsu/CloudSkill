param()

# Windows-native equivalent of script.sh.  Advisory only: this hook never
# blocks a push when diagnostics or logging are unavailable.

$ErrorActionPreference = "SilentlyContinue"

$threshold = 6
$thresholdText = [Environment]::GetEnvironmentVariable("RELEASE_CUT_REMINDER_THRESHOLD")
$parsedThreshold = 0
if ([int]::TryParse($thresholdText, [ref]$parsedThreshold) -and $parsedThreshold -gt 0) {
    $threshold = $parsedThreshold
}

try {
    $inputText = [Console]::In.ReadToEnd()
    $payload = $inputText | ConvertFrom-Json
    $command = [string]$payload.tool_input.command
} catch {
    exit 0
}

if ($command -notmatch '(^|&&|;)\s*git\s+push') {
    exit 0
}

$lastTag = ((git describe --tags --abbrev=0 2>$null) | Select-Object -First 1)
if ([string]::IsNullOrWhiteSpace($lastTag)) {
    exit 0
}
$lastTag = $lastTag.Trim()

$countText = ((git rev-list --count ("{0}..HEAD" -f $lastTag) 2>$null) | Select-Object -First 1)
$count = 0
if (-not [int]::TryParse([string]$countText, [ref]$count)) {
    exit 0
}

if ($count -lt $threshold) {
    exit 0
}

$logDirectory = Join-Path (Get-Location) ".cloudskill-hooks-state"
$logFile = Join-Path $logDirectory "hooks.log"
$timestamp = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
try {
    New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
    Add-Content -LiteralPath $logFile -Value ("{0}`trelease-cut-reminder`tADVISORY`t{1} commits since {2} (threshold {3})" -f $timestamp, $count, $lastTag, $threshold)
} catch {
    # Logging is best effort and must not change the advisory hook outcome.
}

$message = @"
=== Release Cut Reminder (advisory, not blocking) ===
  $count commits since the last tag ($lastTag) -- past the $threshold-commit
  check-in point. Worth considering a version bump / release cut now, before
  this grows into a large undocumented backlog.

  Not every push past this threshold is actually a good moment -- mid-batch
  work or an incomplete PR sequence is a valid reason to say 'not yet'.
==========================================
"@
[Console]::Error.WriteLine($message.TrimEnd())
exit 0
