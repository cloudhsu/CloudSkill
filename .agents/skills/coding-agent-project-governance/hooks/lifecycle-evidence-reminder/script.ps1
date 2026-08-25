param()

# Windows-native equivalent of script.sh.  Advisory only: lifecycle evidence
# reminders never block a commit.

$ErrorActionPreference = "SilentlyContinue"

function Write-HookLog([string]$classification, [string]$detail) {
    try {
        $logDirectory = Join-Path (Get-Location) ".cloudskill-hooks-state"
        $logFile = Join-Path $logDirectory "hooks.log"
        New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
        $timestamp = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
        Add-Content -LiteralPath $logFile -Value ("{0}`tlifecycle-evidence-reminder`t{1}`t{2}" -f $timestamp, $classification, $detail)
    } catch {
        # Logging is best effort and must not change the advisory outcome.
    }
}

try {
    $inputText = [Console]::In.ReadToEnd()
    $payload = $inputText | ConvertFrom-Json
    $command = [string]$payload.tool_input.command
} catch {
    exit 0
}

if ($command -notmatch '(^|&&|;)\s*git\s+commit') {
    exit 0
}

if (-not (Test-Path -LiteralPath "SKILL_MANIFEST.json" -PathType Leaf) -or
    -not (Test-Path -LiteralPath ".agents\skills" -PathType Container)) {
    exit 0
}

$staged = @(git diff --cached --name-only --diff-filter=ACM 2>$null)
if ($staged.Count -eq 0) {
    exit 0
}

$changedSkills = @(
    $staged | ForEach-Object {
        if ($_ -match '^\.agents/skills/([^/]+)/(SKILL\.md|references/)') {
            $matches[1]
        }
    } | Sort-Object -Unique
)
if ($changedSkills.Count -eq 0) {
    exit 0
}

$missing = [System.Collections.Generic.List[string]]::new()
foreach ($skill in $changedSkills) {
    $lifecyclePath = ".agents/skills/$skill/lifecycle.json"
    if (-not ($staged -contains $lifecyclePath)) {
        $missing.Add("  - $skill")
    }
}

if ($missing.Count -eq 0) {
    exit 0
}

$detail = "SKILL.md/references changed without matching lifecycle.json: " + ($changedSkills -join ",")
Write-HookLog "ADVISORY" $detail
$message = @"
=== Lifecycle Evidence Reminder (advisory, not blocking) ===
  These skills' SKILL.md or references/ changed in this commit but their
  lifecycle.json did not:
$($missing -join [Environment]::NewLine)

  This is not always wrong (a pure wording/typo fix does not need it), but
  consider whether last_reviewed_version, stage, or a case-id list should move.
==============================================================
"@
[Console]::Error.WriteLine($message.TrimEnd())
exit 0
