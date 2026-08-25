param()

# Windows-native equivalent of script.sh.  Advisory only: the HTML view
# reminder never blocks a commit.

$ErrorActionPreference = "SilentlyContinue"

function Write-HookLog([string]$classification, [string]$detail) {
    try {
        $logDirectory = Join-Path (Get-Location) ".cloudskill-hooks-state"
        $logFile = Join-Path $logDirectory "hooks.log"
        New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
        $timestamp = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
        Add-Content -LiteralPath $logFile -Value ("{0}`thtml-view-sync-reminder`t{1}`t{2}" -f $timestamp, $classification, $detail)
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

$staged = @(git diff --cached --name-only --diff-filter=ACM 2>$null)
if ($staged.Count -eq 0) {
    exit 0
}

$stale = [System.Collections.Generic.List[string]]::new()
foreach ($file in $staged) {
    if ($file -notmatch '\.md$' -or $file -notmatch '/') {
        continue
    }
    $domain = $file.Split('/')[0]
    $indexPath = "$domain/index.html"
    if (-not (Test-Path -LiteralPath $indexPath -PathType Leaf)) {
        continue
    }
    if ($staged -contains $indexPath) {
        continue
    }
    if (-not ($stale -contains $indexPath)) {
        $stale.Add("  - $indexPath (staged Markdown: $file)")
    }
}

if ($stale.Count -eq 0) {
    exit 0
}

Write-HookLog "ADVISORY" "governed Markdown changed without its domain index.html"
$message = @"
=== HTML Overview View Reminder (advisory, not blocking) ===
  This commit changes governed Markdown in a domain that already has a
  human-readable index.html overview, but the overview wasn't touched in
  the same commit:
$($stale -join [Environment]::NewLine)

  Not every edit needs the HTML view refreshed (wording/typo fixes don't),
  but a real decision or status change does. Confirm before committing.
==============================================================
"@
[Console]::Error.WriteLine($message.TrimEnd())
exit 0
