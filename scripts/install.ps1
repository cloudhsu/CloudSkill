[CmdletBinding()]
param(
    [ValidateSet('codex', 'claude', 'both')]
    [string]$Tool = 'both',

    [ValidateSet('user', 'project')]
    [string]$Scope = 'user',

    [string]$ProjectPath = (Get-Location).Path,

    [switch]$SkipGuidance
)

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$SourceSkills = Join-Path $RepoRoot '.agents\skills'
$BeginMarker = '<!-- CLOUDSKILL:BEGIN -->'
$EndMarker = '<!-- CLOUDSKILL:END -->'

function Copy-CloudSkillSet {
    param([Parameter(Mandatory)][string]$Destination)

    New-Item -ItemType Directory -Force $Destination | Out-Null
    Get-ChildItem $SourceSkills -Directory | ForEach-Object {
        $target = Join-Path $Destination $_.Name
        if (Test-Path $target) {
            Remove-Item $target -Recurse -Force
        }
        Copy-Item $_.FullName $target -Recurse -Force
    }
}

function Set-ManagedBlock {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Content
    )

    $parent = Split-Path $Path -Parent
    if ($parent) { New-Item -ItemType Directory -Force $parent | Out-Null }

    $existing = if (Test-Path $Path) { Get-Content $Path -Raw -Encoding UTF8 } else { '' }
    $block = "$BeginMarker`n$($Content.Trim())`n$EndMarker"
    $pattern = [regex]::Escape($BeginMarker) + '.*?' + [regex]::Escape($EndMarker)

    if ([regex]::IsMatch($existing, $pattern, [Text.RegularExpressions.RegexOptions]::Singleline)) {
        $updated = [regex]::Replace(
            $existing,
            $pattern,
            [Text.RegularExpressions.MatchEvaluator]{ param($m) $block },
            [Text.RegularExpressions.RegexOptions]::Singleline
        )
    } elseif ([string]::IsNullOrWhiteSpace($existing)) {
        $updated = "$block`n"
    } else {
        $updated = "$($existing.TrimEnd())`n`n$block`n"
    }

    Set-Content $Path $updated -Encoding UTF8
}

$installCodex = $Tool -in @('codex', 'both')
$installClaude = $Tool -in @('claude', 'both')
$guidance = Get-Content (Join-Path $RepoRoot 'AGENTS.md') -Raw -Encoding UTF8

if ($Scope -eq 'user') {
    if ($installCodex) {
        Copy-CloudSkillSet (Join-Path $HOME '.agents\skills')
        if (-not $SkipGuidance) {
            Set-ManagedBlock (Join-Path $HOME '.codex\AGENTS.md') $guidance
        }
    }

    if ($installClaude) {
        Copy-CloudSkillSet (Join-Path $HOME '.claude\skills')
        if (-not $SkipGuidance) {
            $cloudSkillHome = Join-Path $HOME '.claude\cloudskill'
            New-Item -ItemType Directory -Force $cloudSkillHome | Out-Null
            Set-Content (Join-Path $cloudSkillHome 'AGENTS.md') $guidance -Encoding UTF8
            Set-ManagedBlock (Join-Path $HOME '.claude\CLAUDE.md') '@~/.claude/cloudskill/AGENTS.md'
        }
    }
} else {
    $project = (Resolve-Path $ProjectPath).Path

    if ($installCodex) {
        Copy-CloudSkillSet (Join-Path $project '.agents\skills')
    }
    if ($installClaude) {
        Copy-CloudSkillSet (Join-Path $project '.claude\skills')
    }

    if (-not $SkipGuidance) {
        Set-ManagedBlock (Join-Path $project 'AGENTS.md') $guidance
        if ($installClaude) {
            Set-ManagedBlock (Join-Path $project 'CLAUDE.md') '@AGENTS.md'
        }
    }
}

Write-Host "CloudSkill installation complete: tool=$Tool scope=$Scope skipGuidance=$SkipGuidance"
