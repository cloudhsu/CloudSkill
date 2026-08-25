param()

# Windows-native equivalent of script.sh.  This is a blocking hook: exit 2
# is intentional when the bounded authentication retry rule is triggered.

$ErrorActionPreference = "SilentlyContinue"

function Write-HookLog([string]$classification, [string]$detail) {
    try {
        $logDirectory = Join-Path (Get-Location) ".cloudskill-hooks-state"
        $logFile = Join-Path $logDirectory "hooks.log"
        New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
        $timestamp = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
        Add-Content -LiteralPath $logFile -Value ("{0}`tblock-push-auth-loop`t{1}`t{2}" -f $timestamp, $classification, $detail)
    } catch {
        # Logging is best effort and must not change the block decision.
    }
}

try {
    $inputText = [Console]::In.ReadToEnd()
    $payload = $inputText | ConvertFrom-Json
    $command = [string]$payload.tool_input.command
} catch {
    exit 0
}

$isPush = $command -match '(^|&&|;)\s*git\s+push'
$isLogin = $command -match '(^|&&|;)\s*gh\s+auth\s+login'
if (-not $isPush -and -not $isLogin) {
    exit 0
}

$journalFile = Join-Path (Get-Location) ".cloudskill-hooks-state\push-auth-journal.jsonl"
if (-not (Test-Path -LiteralPath $journalFile -PathType Leaf)) {
    exit 0
}

$threshold = 2
$staleMinutes = 30
$consecutive = 0
$now = [DateTimeOffset]::UtcNow

try {
    $lines = @(Get-Content -LiteralPath $journalFile)
    [Array]::Reverse($lines)
    foreach ($line in $lines) {
        if ([string]::IsNullOrWhiteSpace($line)) {
            continue
        }
        try {
            $entry = $line | ConvertFrom-Json
            $timestamp = [DateTimeOffset]::Parse([string]$entry.timestamp)
        } catch {
            break
        }
        if (($now - $timestamp).TotalMinutes -gt $staleMinutes) {
            break
        }
        if ([string]$entry.class -ne "auth_failure") {
            break
        }
        $consecutive++
    }
} catch {
    $consecutive = 0
}

if ($consecutive -lt $threshold) {
    exit 0
}

Write-HookLog "BLOCKED" "$consecutive consecutive auth_failure entries within ${staleMinutes}m"
$message = @"
=== Push-Auth Loop Breaker: BLOCKED ===
  $consecutive consecutive git push attempts recorded the same authentication-failure
  class within the last $staleMinutes minutes ($journalFile).
  Per references/git-push-auth-recovery.md: stop here. Report BLOCKED/MANUAL REQUIRED
  with the local commit hash and the recorded failure class. The operator may run
  'gh auth login' or refresh credentials manually -- this agent must not do it
  automatically or retry the push again until that happens.
========================================
"@
[Console]::Error.WriteLine($message.TrimEnd())
exit 2
