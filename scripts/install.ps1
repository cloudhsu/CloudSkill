[CmdletBinding()]
param(
    [ValidateSet('codex', 'claude', 'both')]
    [string]$Tool = 'both',

    [ValidateSet('user', 'project')]
    [string]$Scope = 'user',

    [string]$ProjectPath = (Get-Location).Path,

    [string]$CloudSkillRepoPath,

    [string]$EvalInboxPath,

    [switch]$SkipGuidance,

    [switch]$SkipLocalConfig,

    [switch]$ConfigOnly
)

$ErrorActionPreference = 'Stop'
$ScriptRepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$RepoRoot = if ($CloudSkillRepoPath) { (Resolve-Path $CloudSkillRepoPath).Path } else { $ScriptRepoRoot }
$SourceSkills = Join-Path $RepoRoot '.agents\skills'
$BeginMarker = '<!-- CLOUDSKILL:BEGIN -->'
$EndMarker = '<!-- CLOUDSKILL:END -->'

foreach ($required in @('.agents\skills', 'AGENTS.md', 'VERSION', 'scripts\capture_eval_candidate.py')) {
    if (-not (Test-Path (Join-Path $RepoRoot $required))) {
        throw "CloudSkill repository is missing $required`: $RepoRoot"
    }
}

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

function Initialize-EvalInbox {
    param([Parameter(Mandatory)][string]$Inbox)

    New-Item -ItemType Directory -Force $Inbox | Out-Null
    foreach ($folder in @('candidates', 'manual-review', 'processed', 'rejected')) {
        New-Item -ItemType Directory -Force (Join-Path $Inbox $folder) | Out-Null
    }
    $terms = Join-Path $Inbox 'sensitive-terms.local.txt'
    if (-not (Test-Path $terms)) {
        @(
            '# One private identifier per line. This file is never committed by CloudSkill.',
            '# Add company, customer, project, product, machine, site, server, repository, and person names.',
            '# Lines beginning with # are comments.'
        ) | Set-Content $terms -Encoding UTF8
    }
    return $terms
}

function Write-LocalConfig {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Inbox,
        [Parameter(Mandatory)][string]$SensitiveTerms
    )

    $parent = Split-Path $Path -Parent
    New-Item -ItemType Directory -Force $parent | Out-Null
    $version = (Get-Content (Join-Path $RepoRoot 'VERSION') -Raw -Encoding UTF8).Trim()
    $config = [ordered]@{
        schema_version = '1.0'
        cloudskill_version = $version
        cloudbox_skills_repository = $RepoRoot
        eval_inbox = $Inbox
        sensitive_terms_path = $SensitiveTerms
        default_sanitization = $true
        save_raw_transcript = $false
        auto_modify_skills = $false
        auto_commit = $false
        auto_push = $false
    }
    $config | ConvertTo-Json -Depth 4 | Set-Content $Path -Encoding UTF8
}

$installCodex = $Tool -in @('codex', 'both')
$installClaude = $Tool -in @('claude', 'both')
$guidance = Get-Content (Join-Path $RepoRoot 'AGENTS.md') -Raw -Encoding UTF8
$project = if ($Scope -eq 'project') { (Resolve-Path $ProjectPath).Path } else { $null }

if ($ConfigOnly -and $SkipLocalConfig) {
    throw 'ConfigOnly cannot be combined with SkipLocalConfig.'
}

if (-not $ConfigOnly) {
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
}

if (-not $SkipLocalConfig) {
    $inbox = if ($EvalInboxPath) {
        [System.IO.Path]::GetFullPath($EvalInboxPath)
    } else {
        Join-Path $RepoRoot '.local\eval-inbox'
    }
    $terms = Initialize-EvalInbox $inbox
    if ($Scope -eq 'user') {
        $configPath = Join-Path $HOME '.cloudbox-skills\config.json'
    } else {
        $configDir = Join-Path $project '.cloudbox-skills'
        New-Item -ItemType Directory -Force $configDir | Out-Null
        $configPath = Join-Path $configDir 'config.local.json'
        Set-ManagedBlock (Join-Path $configDir '.gitignore') "config.local.json`neval-outbox/"
    }
    Write-LocalConfig $configPath $inbox $terms
    Write-Host "CloudSkill local config: $configPath"
    Write-Host "CloudSkill Eval Inbox: $inbox"
}

Write-Host "CloudSkill setup complete: tool=$Tool scope=$Scope configOnly=$ConfigOnly skipGuidance=$SkipGuidance skipLocalConfig=$SkipLocalConfig"
