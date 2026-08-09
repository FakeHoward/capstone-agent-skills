#Requires -Version 5.1
<#
.SYNOPSIS
  Copy Capstone agent skill directories into a Cursor skills root.

.DESCRIPTION
  Prefer the multi-agent installer for Claude/Codex/Cursor:
    npx github:FakeHoward/capstone-agent-skills --agent all
    npx skills add FakeHoward/capstone-agent-skills -a cursor -a claude-code -a codex ...

  Copies each skills/<name>/ directory that contains SKILL.md into a personal
  or project Cursor skills folder. Existing skill directories are skipped unless
  -Force is set. Refuses destinations under skills-cursor.

  With -Force, each existing destination skill is renamed to
  <name>.bak.<yyyyMMddHHmmss> before the new copy is moved into place.
  Staging uses a temporary directory under the destination parent; on failure
  the previous skill directory is restored from the backup when possible.
  Backup directories are kept so local edits are not discarded.

.PARAMETER Scope
  personal (default) or project.

.PARAMETER RepoRoot
  capstone-agent-skills repo root. Default: parent of scripts/.

.PARAMETER ProjectRoot
  Consumer repo root when Scope=project. Default: current directory.

.PARAMETER Target
  Override destination parent directory (for tests or custom layouts).
  Canonicalized to an absolute path. When set, Scope still validates but the
  default path is ignored.

.PARAMETER Force
  Replace existing skill directories via backup+staged copy (see DESCRIPTION).

.PARAMETER DryRun
  Print actions without copying.
#>
[CmdletBinding()]
param(
    [ValidateSet("personal", "project")]
    [string]$Scope = "personal",

    [string]$RepoRoot = "",

    [string]$ProjectRoot = "",

    [string]$Target = "",

    [switch]$Force,

    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-RepoRoot {
    param([string]$Explicit)
    if ($Explicit) {
        return (Resolve-Path -LiteralPath $Explicit).Path
    }
    return (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
}

function Assert-NotSkillsCursor {
    param([string]$Path)
    $norm = $Path.Replace("/", "\").ToLowerInvariant()
    if ($norm -match '(^|\\)skills-cursor(\\|$)') {
        throw "Refusing to install into skills-cursor (Cursor built-in skill tree): $Path"
    }
}

function Get-DefaultDestination {
    param(
        [string]$ScopeName,
        [string]$Project
    )
    if ($ScopeName -eq "personal") {
        return (Join-Path $env:USERPROFILE ".cursor\skills")
    }
    $root = if ($Project) { $Project } else { (Get-Location).Path }
    return (Join-Path $root ".cursor\skills")
}

function Resolve-CanonicalDirectory {
    param(
        [string]$Path,
        [switch]$Create
    )
    $full = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Path)
    if ($Create -and -not (Test-Path -LiteralPath $full)) {
        New-Item -ItemType Directory -Force -Path $full | Out-Null
    }
    if (-not (Test-Path -LiteralPath $full -PathType Container)) {
        throw "Destination parent is not a directory: $full"
    }
    return (Resolve-Path -LiteralPath $full).Path
}

function Install-SkillDirectory {
    param(
        [string]$Source,
        [string]$Dest,
        [string]$DestParent,
        [string]$Name
    )
    $stamp = Get-Date -Format "yyyyMMddHHmmss"
    $stage = Join-Path $DestParent (".install-staging-$Name-$stamp")
    $backup = "$Dest.bak.$stamp"
    $backedUp = $false

    try {
        if (Test-Path -LiteralPath $stage) {
            Remove-Item -LiteralPath $stage -Recurse -Force
        }
        Copy-Item -LiteralPath $Source -Destination $stage -Recurse -Force

        if (Test-Path -LiteralPath $Dest) {
            if (Test-Path -LiteralPath $backup) {
                throw "Backup path already exists: $backup"
            }
            Rename-Item -LiteralPath $Dest -NewName (Split-Path -Leaf $backup)
            $backedUp = $true
        }

        Rename-Item -LiteralPath $stage -NewName $Name
        if ($backedUp) {
            Write-Host "REPLACE  $Name -> $Dest (backup: $backup)"
        } else {
            Write-Host "COPY  $Name -> $Dest"
        }
    } catch {
        if (Test-Path -LiteralPath $stage) {
            Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue
        }
        if ($backedUp -and -not (Test-Path -LiteralPath $Dest) -and (Test-Path -LiteralPath $backup)) {
            Rename-Item -LiteralPath $backup -NewName $Name -ErrorAction SilentlyContinue
            Write-Host "ROLLBACK  restored $Dest from $backup"
        }
        throw
    }
}

$repo = Resolve-RepoRoot -Explicit $RepoRoot
$skillsRoot = Join-Path $repo "skills"
if (-not (Test-Path -LiteralPath $skillsRoot -PathType Container)) {
    throw "Skills directory not found: $skillsRoot"
}

$destParentRaw = if ($Target) {
    $Target
} else {
    Get-DefaultDestination -ScopeName $Scope -Project $ProjectRoot
}

Assert-NotSkillsCursor -Path $destParentRaw

if ($DryRun) {
    # Canonicalize when possible without creating the destination.
    if (Test-Path -LiteralPath $destParentRaw) {
        $destParent = Resolve-CanonicalDirectory -Path $destParentRaw
    } else {
        $destParent = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($destParentRaw)
    }
} else {
    $destParent = Resolve-CanonicalDirectory -Path $destParentRaw -Create
}

Assert-NotSkillsCursor -Path $destParent

$skillDirs = @(
    Get-ChildItem -LiteralPath $skillsRoot -Directory |
        Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName "SKILL.md") } |
        Sort-Object Name
)

if ($skillDirs.Count -eq 0) {
    throw "No skill directories with SKILL.md under $skillsRoot"
}

$copied = 0
$skipped = 0
$backedUp = 0

foreach ($dir in $skillDirs) {
    $dest = Join-Path $destParent $dir.Name
    Assert-NotSkillsCursor -Path $dest

    if ((Test-Path -LiteralPath $dest) -and -not $Force) {
        Write-Host "SKIP  exists: $dest"
        $skipped++
        continue
    }

    if ($DryRun) {
        if (Test-Path -LiteralPath $dest) {
            Write-Host "WOULD_REPLACE_WITH_BACKUP  $($dir.FullName) -> $dest"
            $backedUp++
        } else {
            Write-Host "WOULD_COPY  $($dir.FullName) -> $dest"
        }
        $copied++
        continue
    }

    $existed = Test-Path -LiteralPath $dest
    Install-SkillDirectory -Source $dir.FullName -Dest $dest -DestParent $destParent -Name $dir.Name
    if ($existed) {
        $backedUp++
    }
    $copied++
}

Write-Host ""
Write-Host "scope=$Scope dest=$destParent skills=$($skillDirs.Count) copied=$copied skipped=$skipped backed_up=$backedUp force=$Force dry_run=$DryRun"
if ($DryRun) {
    Write-Host "Dry run only; no files were changed."
} elseif ($backedUp -gt 0) {
    Write-Host "Previous skill dirs kept as <name>.bak.<timestamp> next to the new copy."
}
