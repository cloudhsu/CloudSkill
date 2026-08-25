param()

# Windows-native equivalent of validate-push-readiness.sh. This is a
# blocking hook for the cloudbox-skills repository itself: git push is
# refused if the canonical Gemini/Codex projection is stale relative to
# .agents/skills/. Exit 0 = allow. Exit 2 = block.

$ErrorActionPreference = "SilentlyContinue"

$LogFile = Join-Path (Get-Location) ".cloudskill-hooks-state\hooks.log"

function Write-HookLog([string]$classification, [string]$detail) {
    try {
        $logDirectory = Join-Path (Get-Location) ".cloudskill-hooks-state"
        New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
        $timestamp = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
        Add-Content -LiteralPath $LogFile -Value ("{0}`tvalidate-push-readiness`t{1}`t{2}" -f $timestamp, $classification, $detail)
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

if ($command -notmatch '(^|&&|;)\s*git\s+push') {
    exit 0
}

# Only meaningful inside an actual cloudbox-skills checkout -- degrade
# silently (allow) anywhere else rather than erroring on a repo that
# happens to also use this hook file by coincidence.
$manifestPresent = Test-Path -LiteralPath "SKILL_MANIFEST.json" -PathType Leaf
$skillsDirPresent = Test-Path -LiteralPath ".agents\skills" -PathType Container
if (-not ($manifestPresent -and $skillsDirPresent)) {
    exit 0
}

$pythonCmd = $null
foreach ($candidate in @("python3.11", "python3", "python", "py")) {
    if (Get-Command $candidate -ErrorAction SilentlyContinue) {
        $pythonCmd = $candidate
        break
    }
}
if (-not $pythonCmd) {
    exit 0
}

$output = & $pythonCmd "scripts\sync_gemini_plugins.py" "--check" 2>&1 | Out-String
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) {
    $trimmedOutput = $output.Trim()
    $detail = ($trimmedOutput -replace '\r?\n', ' ')
    if ($detail.Length -gt 200) {
        $detail = $detail.Substring(0, 200)
    }

    if ($trimmedOutput -match "Traceback \(most recent call last\)") {
        Write-HookLog "BLOCKED_SCRIPT_ERROR" $detail
    } else {
        Write-HookLog "BLOCKED" $detail
    }

    $message = @"
=== Push Readiness: BLOCKED ===
  Gemini/Codex plugin projections are stale relative to .agents/skills/ --
  the exact gap that failed this repository's own CI on a real PR tonight.
  Run before pushing:
    $pythonCmd scripts\sync_gemini_plugins.py
    $pythonCmd scripts\sync_private_codex_plugin.py
  Then re-add and re-commit the projection files, and retry the push.
  Detail:
$trimmedOutput
================================
"@
    [Console]::Error.WriteLine($message.TrimEnd())
    exit 2
}

exit 0
