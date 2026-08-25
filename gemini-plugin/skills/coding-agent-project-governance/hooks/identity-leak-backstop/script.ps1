param()

# Windows-native equivalent of script.sh.  Exit 2 is intentional when a
# staged field-shaped addition contains the checkout's configured identity.

$ErrorActionPreference = "SilentlyContinue"

function Write-HookLog([string]$classification, [string]$detail) {
    try {
        $logDirectory = Join-Path (Get-Location) ".cloudskill-hooks-state"
        $logFile = Join-Path $logDirectory "hooks.log"
        New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
        $timestamp = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
        Add-Content -LiteralPath $logFile -Value ("{0}`tidentity-leak-backstop`t{1}`t{2}" -f $timestamp, $classification, $detail)
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

if ($command -notmatch '(^|&&|;)\s*git\s+commit') {
    exit 0
}

$email = ((git config user.email 2>$null) | Select-Object -First 1)
$name = ((git config user.name 2>$null) | Select-Object -First 1)
if ($null -ne $email) { $email = $email.Trim() }
if ($null -ne $name) { $name = $name.Trim() }
if ([string]::IsNullOrWhiteSpace($email) -and [string]::IsNullOrWhiteSpace($name)) {
    exit 0
}

$stagedFiles = @(git diff --cached --name-only --diff-filter=ACM 2>$null)
if ($stagedFiles.Count -eq 0) {
    exit 0
}

$binaryExtensions = @(".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".ico", ".woff")
$hits = [System.Collections.Generic.List[string]]::new()

foreach ($file in $stagedFiles) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
        continue
    }
    $extension = [IO.Path]::GetExtension([string]$file).ToLowerInvariant()
    if ($binaryExtensions -contains $extension -or $extension -like ".woff*") {
        continue
    }

    $addedLines = @(git diff --cached -- $file 2>$null | Where-Object {
        $_ -match '^\+' -and $_ -notmatch '^\+\+\+'
    })
    if ($addedLines.Count -eq 0) {
        continue
    }

    foreach ($needle in @($email, $name)) {
        if ([string]::IsNullOrWhiteSpace($needle)) {
            continue
        }
        foreach ($line in $addedLines) {
            $fieldShaped = $line -match ':' -or $line -match '^\+[\s]*-'
            if ($fieldShaped -and $line.Contains($needle)) {
                $hits.Add(('  {0}: contains "{1}" (this checkout''s own git identity) in a field-shaped added line' -f $file, $needle))
            }
        }
    }
}

if ($hits.Count -eq 0) {
    exit 0
}

$identityParts = @()
if (-not [string]::IsNullOrWhiteSpace($email)) { $identityParts += "email: $email" }
if (-not [string]::IsNullOrWhiteSpace($name)) { $identityParts += "name: $name" }
Write-HookLog "BLOCKED" "staged addition contains this checkout's own git identity in a field-shaped line"
$message = @"
=== Identity Leak Backstop: BLOCKED ===
  A staged change adds this checkout's own configured git identity
  ($($identityParts -join ', '))
  into what looks like a document field.
$($hits -join [Environment]::NewLine)

  Per coding-agent-project-governance/references/no-fabricated-identity.md:
  never fill an unrequested attribution/owner/proposer/submitted-by field
  from ambient session identity. If the task did not supply this fact,
  omit the field or use a generic placeholder instead.

  If this really is a requested attribution, report BLOCKED and ask the user
  to confirm and commit it themselves outside this agent session.
==========================================
"@
[Console]::Error.WriteLine($message.TrimEnd())
exit 2
