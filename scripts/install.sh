#!/usr/bin/env bash
# Copy Capstone agent skill directories into a Cursor skills root.
# Prefer the multi-agent installer for Claude/Codex/Cursor:
#   npx github:FakeHoward/capstone-agent-skills --agent all
#   npx skills add FakeHoward/capstone-agent-skills -a cursor -a claude-code -a codex ...
# Existing skill dirs are skipped unless --force. Refuses skills-cursor.
#
# With --force, each existing destination skill is renamed to
# <name>.bak.<UTC timestamp> before the staged copy is moved into place.
# On failure the previous directory is restored when possible. Backups are kept
# so local edits are not discarded. --target is canonicalized to an absolute path.
set -euo pipefail

SCOPE="personal"
REPO_ROOT=""
PROJECT_ROOT=""
TARGET=""
FORCE=0
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: install.sh [--scope personal|project] [--repo-root DIR] [--project-root DIR]
                  [--target DIR] [--force] [--dry-run] [-h|--help]

Copies skills/*/ (directories containing SKILL.md) into a Cursor skills root.
Default personal dest: ~/.cursor/skills
Default project dest:  <project-root>/.cursor/skills  (project-root defaults to cwd)
--target overrides the destination parent (canonicalized; safe for tests).

--force replaces an existing skill via backup+staged copy:
  1) copy source into a staging dir under the destination parent
  2) rename existing dest to <name>.bak.<timestamp>
  3) move staging into place
  On error, staging is removed and the backup is renamed back when needed.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope)
      SCOPE="${2:-}"
      shift 2
      ;;
    --repo-root)
      REPO_ROOT="${2:-}"
      shift 2
      ;;
    --project-root)
      PROJECT_ROOT="${2:-}"
      shift 2
      ;;
    --target)
      TARGET="${2:-}"
      shift 2
      ;;
    --force)
      FORCE=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ "$SCOPE" != "personal" && "$SCOPE" != "project" ]]; then
  echo "ERROR: --scope must be personal or project" >&2
  exit 2
fi

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
if [[ -n "$REPO_ROOT" ]]; then
  repo_root="$(CDPATH= cd -- "$REPO_ROOT" && pwd)"
else
  repo_root="$(CDPATH= cd -- "$script_dir/.." && pwd)"
fi

skills_root="$repo_root/skills"
if [[ ! -d "$skills_root" ]]; then
  echo "ERROR: skills directory not found: $skills_root" >&2
  exit 1
fi

assert_not_skills_cursor() {
  local path="$1"
  local norm
  norm="$(printf '%s' "$path" | tr '\\' '/' | tr '[:upper:]' '[:lower:]')"
  case "$norm" in
    *'/skills-cursor' | *'/skills-cursor/'* | 'skills-cursor' | 'skills-cursor/'*)
      echo "ERROR: refusing to install into skills-cursor: $path" >&2
      exit 1
      ;;
  esac
}

canonicalize_dir() {
  local path="$1"
  local create="${2:-0}"
  if [[ "$create" -eq 1 ]]; then
    mkdir -p -- "$path"
  fi
  if [[ -d "$path" ]]; then
    (CDPATH= cd -- "$path" && pwd)
    return 0
  fi
  # Dry-run against a missing target: resolve via parent + basename when possible.
  local parent base
  parent="$(dirname -- "$path")"
  base="$(basename -- "$path")"
  if [[ -d "$parent" ]]; then
    printf '%s/%s\n' "$(CDPATH= cd -- "$parent" && pwd)" "$base"
    return 0
  fi
  printf '%s\n' "$path"
}

install_skill_dir() {
  local src="$1"
  local dest="$2"
  local dest_parent="$3"
  local name="$4"
  local stamp stage backup backed_up=0

  stamp="$(date -u +%Y%m%d%H%M%S 2>/dev/null || date +%Y%m%d%H%M%S)"
  stage="$dest_parent/.install-staging-${name}-${stamp}"
  backup="${dest}.bak.${stamp}"

  rm -rf -- "$stage"
  # shellcheck disable=SC2064
  trap 'rm -rf -- "$stage"' RETURN

  cp -R -- "$src" "$stage"

  if [[ -e "$dest" ]]; then
    if [[ -e "$backup" ]]; then
      echo "ERROR: backup path already exists: $backup" >&2
      return 1
    fi
    mv -- "$dest" "$backup"
    backed_up=1
  fi

  if ! mv -- "$stage" "$dest"; then
    if [[ "$backed_up" -eq 1 && ! -e "$dest" && -e "$backup" ]]; then
      mv -- "$backup" "$dest" || true
      echo "ROLLBACK  restored $dest from $backup"
    fi
    return 1
  fi

  trap - RETURN
  if [[ "$backed_up" -eq 1 ]]; then
    echo "REPLACE  $name -> $dest (backup: $backup)"
  else
    echo "COPY  $name -> $dest"
  fi
}

if [[ -n "$TARGET" ]]; then
  dest_parent_raw="$TARGET"
else
  if [[ "$SCOPE" == "personal" ]]; then
    dest_parent_raw="${HOME}/.cursor/skills"
  else
    project_root="${PROJECT_ROOT:-$PWD}"
    project_root="$(CDPATH= cd -- "$project_root" && pwd)"
    dest_parent_raw="${project_root}/.cursor/skills"
  fi
fi

assert_not_skills_cursor "$dest_parent_raw"

if [[ "$DRY_RUN" -eq 1 ]]; then
  dest_parent="$(canonicalize_dir "$dest_parent_raw" 0)"
else
  dest_parent="$(canonicalize_dir "$dest_parent_raw" 1)"
fi

assert_not_skills_cursor "$dest_parent"

# Collect skill dirs (portable: no mapfile required).
skill_dirs=()
while IFS= read -r -d '' d; do
  skill_dirs+=("$d")
done < <(find "$skills_root" -mindepth 1 -maxdepth 1 -type d -name 'capstone-*' -print0 | sort -z)

# Fallback if naming differs: any dir with SKILL.md
if [[ ${#skill_dirs[@]} -eq 0 ]]; then
  while IFS= read -r -d '' d; do
    if [[ -f "$d/SKILL.md" ]]; then
      skill_dirs+=("$d")
    fi
  done < <(find "$skills_root" -mindepth 1 -maxdepth 1 -type d -print0 | sort -z)
fi

filtered=()
for d in "${skill_dirs[@]+"${skill_dirs[@]}"}"; do
  if [[ -f "$d/SKILL.md" ]]; then
    filtered+=("$d")
  fi
done
skill_dirs=("${filtered[@]+"${filtered[@]}"}")

if [[ ${#skill_dirs[@]} -eq 0 ]]; then
  echo "ERROR: no skill directories with SKILL.md under $skills_root" >&2
  exit 1
fi

copied=0
skipped=0
backed_up=0

for src in "${skill_dirs[@]}"; do
  name="$(basename -- "$src")"
  dest="$dest_parent/$name"
  assert_not_skills_cursor "$dest"

  if [[ -e "$dest" && "$FORCE" -eq 0 ]]; then
    echo "SKIP  exists: $dest"
    skipped=$((skipped + 1))
    continue
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    if [[ -e "$dest" ]]; then
      echo "WOULD_REPLACE_WITH_BACKUP  $src -> $dest"
      backed_up=$((backed_up + 1))
    else
      echo "WOULD_COPY  $src -> $dest"
    fi
    copied=$((copied + 1))
    continue
  fi

  existed=0
  if [[ -e "$dest" ]]; then
    existed=1
  fi
  install_skill_dir "$src" "$dest" "$dest_parent" "$name"
  if [[ "$existed" -eq 1 ]]; then
    backed_up=$((backed_up + 1))
  fi
  copied=$((copied + 1))
done

echo
echo "scope=$SCOPE dest=$dest_parent skills=${#skill_dirs[@]} copied=$copied skipped=$skipped backed_up=$backed_up force=$FORCE dry_run=$DRY_RUN"
if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "Dry run only; no files were changed."
elif [[ "$backed_up" -gt 0 ]]; then
  echo "Previous skill dirs kept as <name>.bak.<timestamp> next to the new copy."
fi
