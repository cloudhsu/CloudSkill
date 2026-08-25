param()

# Windows-native equivalent of script.sh.  Keep this hook advisory-only:
# diagnostics must never block a commit merely because the log path or git
# status probe is unavailable.

$ErrorActionPreference = "SilentlyContinue"

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

$null = git rev-parse --is-inside-work-tree 2>$null
if ($LASTEXITCODE -ne 0) {
    exit 0
}

$dirty = @(git status --porcelain 2>$null | Where-Object { $_ -match '^.[MD?]|^\?\?' })
if ($dirty.Count -eq 0) {
    exit 0
}

$logDirectory = Join-Path (Get-Location) ".cloudskill-hooks-state"
$logFile = Join-Path $logDirectory "hooks.log"
$timestamp = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")

try {
    New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
    Add-Content -LiteralPath $logFile -Value ("{0}`tshared-checkout-guard`tADVISORY`t{1} unstaged/untracked file(s) present at commit time" -f $timestamp, $dirty.Count)
} catch {
    # Logging is best effort and must not change the advisory hook outcome.
}

$preview = ($dirty | Select-Object -First 10 | ForEach-Object { "    $_" }) -join [Environment]::NewLine
$message = @"
=== Shared Checkout Guard (advisory, not blocking) ===
  $($dirty.Count) file(s) in this working tree are modified or untracked but NOT
  part of this commit:
$preview

  Before committing, confirm these are your own known leftovers and not another
  process's in-progress work. If unsure, isolate the change in another worktree.
==========================================
"@
[Console]::Error.WriteLine($message.TrimEnd())
exit 0
