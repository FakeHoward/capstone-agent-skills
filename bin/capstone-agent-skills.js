#!/usr/bin/env node
/**
 * Install Capstone agent skills for Cursor, Claude Code, and/or Codex.
 *
 * Same skills/ tree for every agent (Agent Skills SKILL.md). Destinations differ:
 *   cursor  personal ~/.cursor/skills   project .cursor/skills
 *   claude  personal ~/.claude/skills   project .claude/skills
 *   codex   personal ~/.agents/skills   project .agents/skills
 *
 * Also documents / pairs with:
 *   npx skills add FakeHoward/capstone-agent-skills -a cursor -a claude-code -a codex ...
 */

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..");
const SKILLS_ROOT = path.join(REPO_ROOT, "skills");

const AGENTS = {
  cursor: {
    aliases: ["cursor"],
    personal: () => path.join(os.homedir(), ".cursor", "skills"),
    project: (root) => path.join(root, ".cursor", "skills"),
    reservedFragments: ["skills-cursor"],
  },
  claude: {
    aliases: ["claude", "claude-code", "anthropic"],
    personal: () => path.join(os.homedir(), ".claude", "skills"),
    project: (root) => path.join(root, ".claude", "skills"),
    reservedFragments: [],
  },
  codex: {
    aliases: ["codex", "openai"],
    personal: () => path.join(os.homedir(), ".agents", "skills"),
    project: (root) => path.join(root, ".agents", "skills"),
    reservedFragments: [],
  },
};

function usage(exitCode = 0) {
  const text = `Usage: capstone-agent-skills [options]

Install Capstone skills for Cursor, Claude Code, and/or Codex from this package.

Options:
  --agent <name>[,name...]   cursor | claude | codex | all  (default: all)
  --scope personal|project   personal (default) or project
  --project-root <dir>       project root for --scope project (default: cwd)
  --target <dir>             override destination parent (for tests)
  --skill <name>[,name...]   install only named skills (default: all)
  --force                    replace existing skill dirs (backup + staged copy)
  --dry-run                  print actions only
  --list                     list skill ids and exit
  -h, --help                 show help

Examples:
  npx github:FakeHoward/capstone-agent-skills --agent all --scope personal
  npx github:FakeHoward/capstone-agent-skills --agent claude --scope project
  npx skills add FakeHoward/capstone-agent-skills -a cursor -a claude-code -a codex -g -y --skill '*' --copy
`;
  process.stdout.write(text);
  process.exit(exitCode);
}

function die(msg, code = 1) {
  process.stderr.write(`ERROR: ${msg}\n`);
  process.exit(code);
}

function normalizeSlashes(p) {
  return p.replace(/\\/g, "/").toLowerCase();
}

function assertNotReserved(dest, agentDef) {
  const norm = normalizeSlashes(dest);
  for (const frag of agentDef.reservedFragments) {
    if (
      norm === frag ||
      norm.endsWith(`/${frag}`) ||
      norm.includes(`/${frag}/`)
    ) {
      die(`refusing to install into reserved path fragment "${frag}": ${dest}`);
    }
  }
}

function resolveAgents(spec) {
  if (!spec || spec === "all" || spec === "*") {
    return ["cursor", "claude", "codex"];
  }
  const wanted = new Set();
  for (const raw of spec.split(/[,\s]+/).filter(Boolean)) {
    const key = raw.toLowerCase();
    let matched = null;
    for (const [id, def] of Object.entries(AGENTS)) {
      if (def.aliases.includes(key) || id === key) {
        matched = id;
        break;
      }
    }
    if (!matched) {
      die(`unknown agent "${raw}" (use cursor, claude, codex, or all)`, 2);
    }
    wanted.add(matched);
  }
  return [...wanted];
}

function listSkillDirs(filterNames) {
  if (!fs.existsSync(SKILLS_ROOT)) {
    die(`skills directory not found: ${SKILLS_ROOT}`);
  }
  const all = fs
    .readdirSync(SKILLS_ROOT, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .map((d) => d.name)
    .filter((name) => fs.existsSync(path.join(SKILLS_ROOT, name, "SKILL.md")))
    .sort();
  if (!filterNames || filterNames.length === 0) {
    return all;
  }
  const wanted = new Set(filterNames);
  const missing = [...wanted].filter((n) => !all.includes(n));
  if (missing.length) {
    die(`unknown skill(s): ${missing.join(", ")}`, 2);
  }
  return all.filter((n) => wanted.has(n));
}

function copyDirRecursive(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const from = path.join(src, entry.name);
    const to = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      copyDirRecursive(from, to);
    } else if (entry.isFile()) {
      fs.copyFileSync(from, to);
    }
  }
}

function timestampUtc() {
  return new Date().toISOString().replace(/[-:]/g, "").replace(/\.\d+Z$/, "Z");
}

function installOne(srcDir, destDir, { force, dryRun }) {
  const name = path.basename(srcDir);
  const dest = path.join(destDir, name);
  if (fs.existsSync(dest) && !force) {
    process.stdout.write(`SKIP  exists: ${dest}\n`);
    return "skip";
  }
  if (dryRun) {
    const action = fs.existsSync(dest) ? "WOULD_REPLACE" : "WOULD_COPY";
    process.stdout.write(`${action} ${srcDir} -> ${dest} dry_run=True\n`);
    return "dry";
  }
  fs.mkdirSync(destDir, { recursive: true });
  const staging = path.join(
    destDir,
    `.${name}.staging.${process.pid}.${timestampUtc()}`,
  );
  let backup = null;
  try {
    if (fs.existsSync(staging)) {
      fs.rmSync(staging, { recursive: true, force: true });
    }
    copyDirRecursive(srcDir, staging);
    if (fs.existsSync(dest)) {
      backup = path.join(destDir, `${name}.bak.${timestampUtc()}`);
      fs.renameSync(dest, backup);
      process.stdout.write(`REPLACE ${dest} backup: ${backup}\n`);
    } else {
      process.stdout.write(`COPY   ${dest}\n`);
    }
    fs.renameSync(staging, dest);
    return "ok";
  } catch (err) {
    if (fs.existsSync(staging)) {
      fs.rmSync(staging, { recursive: true, force: true });
    }
    if (backup && fs.existsSync(backup) && !fs.existsSync(dest)) {
      fs.renameSync(backup, dest);
    }
    throw err;
  }
}

function parseArgs(argv) {
  const opts = {
    agent: "all",
    scope: "personal",
    projectRoot: process.cwd(),
    target: null,
    skills: null,
    force: false,
    dryRun: false,
    list: false,
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "-h" || a === "--help") usage(0);
    if (a === "--list") {
      opts.list = true;
      continue;
    }
    if (a === "--force") {
      opts.force = true;
      continue;
    }
    if (a === "--dry-run") {
      opts.dryRun = true;
      continue;
    }
    if (a === "--agent") {
      opts.agent = argv[++i];
      continue;
    }
    if (a === "--scope") {
      opts.scope = argv[++i];
      continue;
    }
    if (a === "--project-root") {
      opts.projectRoot = path.resolve(argv[++i]);
      continue;
    }
    if (a === "--target") {
      opts.target = path.resolve(argv[++i]);
      continue;
    }
    if (a === "--skill") {
      const raw = argv[++i];
      opts.skills = raw.split(/[,\s]+/).filter(Boolean);
      continue;
    }
    die(`unknown argument: ${a}`, 2);
  }
  if (opts.scope !== "personal" && opts.scope !== "project") {
    die("--scope must be personal or project", 2);
  }
  return opts;
}

function main() {
  const opts = parseArgs(process.argv.slice(2));
  const skillNames = listSkillDirs(opts.skills);
  if (opts.list) {
    for (const name of skillNames) {
      process.stdout.write(`${name}\n`);
    }
    process.exit(0);
  }

  const agents = resolveAgents(opts.agent);
  let copied = 0;
  let skipped = 0;

  for (const agentId of agents) {
    const def = AGENTS[agentId];
    const destParent = opts.target
      ? opts.target
      : opts.scope === "personal"
        ? def.personal()
        : def.project(opts.projectRoot);
    const resolvedDest = path.resolve(destParent);
    assertNotReserved(resolvedDest, def);
    process.stdout.write(
      `\n# agent=${agentId} scope=${opts.scope} dest=${resolvedDest}\n`,
    );
    for (const name of skillNames) {
      const src = path.join(SKILLS_ROOT, name);
      const result = installOne(src, resolvedDest, {
        force: opts.force,
        dryRun: opts.dryRun,
      });
      if (result === "skip") skipped += 1;
      else copied += 1;
    }
  }

  process.stdout.write(
    `\nDone. agents=${agents.join(",")} skills=${skillNames.length} ` +
      `actions=${copied} skipped=${skipped} dry_run=${opts.dryRun}\n`,
  );
}

try {
  main();
} catch (err) {
  die(err instanceof Error ? err.message : String(err));
}
