param()

# Windows-native equivalent of script.sh.  This hook records and never blocks.

$ErrorActionPreference = "SilentlyContinue"

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

$rawOutputParts = @()
$exitCode = $null
try {
    $response = $payload.tool_response
    $output = $response.output
    if ($null -eq $output) { $output = $response.stdout }
    if ($null -eq $output) { $output = $payload.tool_output }
    if ($null -eq $output) { $output = $payload.output }
    if ($null -ne $output) { $rawOutputParts += [string]$output }

    $stderr = $response.stderr
    if ($null -eq $stderr) { $stderr = $payload.error }
    if ($null -ne $stderr) { $rawOutputParts += [string]$stderr }

    $exitCode = $response.exit_code
    if ($null -eq $exitCode) { $exitCode = $response.exitCode }
} catch {
    # Missing provider-specific fields degrade to unknown outcome.
}

$rawOutput = $rawOutputParts -join "`n"
$class = "unknown"
if ($rawOutput -match '(?i)authentication failed|could not read username|could not read password|403|permission denied \(publickey\)|support for password authentication was removed|remote: invalid username or password') {
    $class = "auth_failure"
} elseif ($rawOutput -match '(?i)protected branch|required status check|review required|branch is protected') {
    $class = "protection_rejection"
} elseif ([string]$exitCode -eq "0") {
    $class = "success"
} elseif ($rawOutput -match '(?i)! \[rejected\]|failed to push|error: failed') {
    $class = "other_failure"
}

$journalDirectory = Join-Path (Get-Location) ".cloudskill-hooks-state"
$journalFile = Join-Path $journalDirectory "push-auth-journal.jsonl"
$timestamp = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
try {
    New-Item -ItemType Directory -Path $journalDirectory -Force | Out-Null
    $record = @{ timestamp = $timestamp; class = $class } | ConvertTo-Json -Compress
    Add-Content -LiteralPath $journalFile -Value $record

    if ($class -ne "success" -and $class -ne "unknown") {
        $logFile = Join-Path $journalDirectory "hooks.log"
        Add-Content -LiteralPath $logFile -Value ("{0}`trecord-push-outcome`t{1}`tgit push outcome recorded" -f $timestamp, $class)
    }
} catch {
    # Recording is best effort and must not block a push by itself.
}

exit 0
