import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const BIN = path.join(ROOT, "bin", "capstone-agent-skills.js");

function run(args, opts = {}) {
  return spawnSync(process.execPath, [BIN, ...args], {
    cwd: ROOT,
    encoding: "utf8",
    ...opts,
  });
}

test("lists all skills", () => {
  const r = run(["--list"]);
  assert.equal(r.status, 0, r.stderr);
  const lines = r.stdout.trim().split(/\r?\n/);
  assert.ok(lines.includes("capstone-core-api"));
  assert.ok(lines.includes("capstone-arch-x86"));
  assert.equal(lines.length, 41);
});

test("dry-run installs for cursor, claude, and codex", () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "cas-cli-"));
  try {
    for (const agent of ["cursor", "claude", "codex"]) {
      const dest = path.join(tmp, agent);
      const r = run([
        "--agent",
        agent,
        "--scope",
        "personal",
        "--target",
        dest,
        "--skill",
        "capstone-core-api",
        "--dry-run",
      ]);
      assert.equal(r.status, 0, r.stderr + r.stdout);
      assert.match(r.stdout, /WOULD_COPY/);
      assert.match(r.stdout, new RegExp(`agent=${agent}`));
      assert.ok(!fs.existsSync(path.join(dest, "capstone-core-api")));
    }
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});

test("copy, skip, force-backup, refuse skills-cursor", () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "cas-cli-"));
  try {
    const dest = path.join(tmp, "safe");
    const copy = run([
      "--agent",
      "claude",
      "--target",
      dest,
      "--skill",
      "capstone-core-api",
    ]);
    assert.equal(copy.status, 0, copy.stderr + copy.stdout);
    const skillMd = path.join(dest, "capstone-core-api", "SKILL.md");
    assert.ok(fs.existsSync(skillMd));

    const marker = path.join(dest, "capstone-core-api", "USER_EDIT.md");
    fs.writeFileSync(marker, "keep-me\n", "utf8");

    const skip = run([
      "--agent",
      "claude",
      "--target",
      dest,
      "--skill",
      "capstone-core-api",
    ]);
    assert.equal(skip.status, 0, skip.stderr + skip.stdout);
    assert.match(skip.stdout, /SKIP  exists:/);
    assert.ok(fs.existsSync(marker));

    const force = run([
      "--agent",
      "claude",
      "--target",
      dest,
      "--skill",
      "capstone-core-api",
      "--force",
    ]);
    assert.equal(force.status, 0, force.stderr + force.stdout);
    assert.match(force.stdout, /REPLACE/);
    assert.match(force.stdout, /backup:/);
    const backups = fs
      .readdirSync(dest)
      .filter((n) => n.startsWith("capstone-core-api.bak."));
    assert.equal(backups.length, 1);
    assert.ok(
      fs.existsSync(path.join(dest, backups[0], "USER_EDIT.md")),
      "user edit preserved in backup",
    );
    assert.ok(!fs.existsSync(marker));
    assert.ok(fs.existsSync(skillMd));

    const reserved = path.join(tmp, "skills-cursor");
    const refuse = run([
      "--agent",
      "cursor",
      "--target",
      reserved,
      "--skill",
      "capstone-core-api",
      "--dry-run",
    ]);
    assert.notEqual(refuse.status, 0);
    assert.match((refuse.stderr + refuse.stdout).toLowerCase(), /skills-cursor/);
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});

test("project scope uses agent-specific relative roots", () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "cas-proj-"));
  try {
    const expected = {
      cursor: path.join(tmp, ".cursor", "skills"),
      claude: path.join(tmp, ".claude", "skills"),
      codex: path.join(tmp, ".agents", "skills"),
    };
    for (const [agent, dest] of Object.entries(expected)) {
      const r = run([
        "--agent",
        agent,
        "--scope",
        "project",
        "--project-root",
        tmp,
        "--skill",
        "capstone-core-api",
      ]);
      assert.equal(r.status, 0, r.stderr + r.stdout);
      assert.ok(fs.existsSync(path.join(dest, "capstone-core-api", "SKILL.md")));
    }
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});
