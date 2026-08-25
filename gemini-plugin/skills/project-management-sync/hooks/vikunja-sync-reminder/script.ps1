param()

# Windows-native equivalent of script.sh. Exit 2 once when a turn contains
# commit activity but does not mention the configured project tracker.

$ErrorActionPreference = "SilentlyContinue"

$trackerHint = [string]$env:PROJECT_TRACKER_HINT
if ([string]::IsNullOrWhiteSpace($trackerHint)) {
    $trackerHint = "vikunja"
}

function Write-HookLog([string]$classification, [string]$detail) {
    try {
        $logDirectory = Join-Path (Get-Location) ".cloudskill-hooks-state"
        $logFile = Join-Path $logDirectory "hooks.log"
        New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
        $timestamp = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
        Add-Content -LiteralPath $logFile -Value ("{0}`tvikunja-sync-reminder`t{1}`t{2}" -f $timestamp, $classification, $detail)
    } catch {
        # Logging is best effort and must not change the block decision.
    }
}

try {
    $inputText = [Console]::In.ReadToEnd()
    $payload = $inputText | ConvertFrom-Json
} catch {
    exit 0
}

if ([bool]$payload.stop_hook_active) {
    exit 0
}

$transcriptPath = [string]$payload.transcript_path
if ([string]::IsNullOrWhiteSpace($transcriptPath) -or -not (Test-Path -LiteralPath $transcriptPath -PathType Leaf)) {
    exit 0
}

try {
    $transcriptBytes = [IO.File]::ReadAllBytes($transcriptPath)
    $start = [Math]::Max(0, $transcriptBytes.Length - 300000)
    $recent = [Text.Encoding]::UTF8.GetString($transcriptBytes, $start, $transcriptBytes.Length - $start)
} catch {
    exit 0
}

if ([string]::IsNullOrEmpty($recent)) {
    exit 0
}

if ($recent -notmatch 'git\s+commit') {
    exit 0
}

if ($recent.IndexOf($trackerHint, [StringComparison]::OrdinalIgnoreCase) -ge 0) {
    exit 0
}

Write-HookLog "FORCED_CONTINUE" ("commit activity with no '{0}' mention in transcript" -f $trackerHint)
$message = @"
=== Tracker Sync Reminder: forcing one more pass (not a permanent block) ===
  This turn's transcript shows git commit activity with no mention of
  '$trackerHint' anywhere in it. Per project-management-sync's
  convention (see coding-agent-project-governance and the standing
  end-of-work sync habit): before actually stopping, decide explicitly
  whether anything from this turn belongs in the tracker as an outstanding
  item -- then either sync it, or state plainly that nothing needs tracking
  and why. This reminder will not repeat on this same stop attempt either
  way (stop_hook_active prevents that); it forces one explicit decision,
  not an unconditional task creation.
==============================================================
"@
[Console]::Error.WriteLine($message.TrimEnd())
exit 2
