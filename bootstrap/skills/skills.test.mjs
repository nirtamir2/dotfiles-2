import { afterEach, test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtemp, mkdir, readFile, rm, symlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { parseDocument } from "yaml";

const command = join(import.meta.dirname, "../../bin/skills-explicit");
const homes = [];

afterEach(async () => {
  await Promise.all(homes.splice(0).map(home => rm(home, { recursive: true, force: true })));
});

async function home() {
  const path = await mkdtemp(join(tmpdir(), "dotfiles-skills-"));
  homes.push(path);
  return path;
}

async function skill(folder, frontmatter = "name: sample\ndescription: A sample\n", newline = "\n") {
  await mkdir(folder, { recursive: true });
  const path = join(folder, "SKILL.md");
  await writeFile(path, `---\n${frontmatter}---\n\n# Instructions\nKeep this body unchanged.\n`.replaceAll("\n", newline));
  return path;
}

function run(home, ...args) {
  const result = spawnSync(command, ["--home", home, "--project", home, ...args], { encoding: "utf8" });
  assert.ifError(result.error);
  return { stdout: result.stdout, stderr: result.stderr, exitCode: result.status };
}

async function flags(manifest) {
  const text = await readFile(manifest, "utf8");
  const frontmatter = /^---\r?\n([\s\S]*?)^---/m.exec(text)?.[1];
  assert.notEqual(frontmatter, undefined);
  const document = parseDocument(frontmatter);
  const metadata = parseDocument(await readFile(join(dirname(manifest), "agents/openai.yaml"), "utf8"));
  return {
    disabled: document.get("disable-model-invocation"),
    implicit: metadata.getIn(["policy", "allow_implicit_invocation"]),
  };
}

test("default run fixes all locations, follows shared links, and reruns without changes", async () => {
  const root = await home();
  const shared = await skill(join(root, ".agents/skills/shared"));
  await mkdir(join(root, ".claude/skills"), { recursive: true });
  await symlink(dirname(shared), join(root, ".claude/skills/shared"));
  await symlink(join(root, ".agents/skills"), join(root, ".agents/skills/loop"));
  const manifests = [
    shared,
    await skill(join(root, ".codex/skills/.system/bundled")),
    await skill(join(root, ".cursor/skills/local")),
    await skill(join(root, ".codex/plugins/cache/plugin/1/skills/plugin-skill")),
    await skill(join(root, ".claude/plugins/cache/plugin/1/skills/plugin-skill")),
    await skill(join(root, ".cursor/plugins/cache/plugin/1/skills/plugin-skill")),
  ];
  const before = await readFile(shared, "utf8");
  assert.equal(run(root, "--check").exitCode, 1);
  assert.equal(await readFile(shared, "utf8"), before);
  const applied = run(root);
  assert.equal(applied.exitCode, 0, applied.stderr);
  assert.ok(applied.stdout.includes("6 skills checked; 12 files updated."));
  for (const manifest of manifests) assert.deepEqual(await flags(manifest), { disabled: true, implicit: false });
  const snapshot = await readFile(shared, "utf8");
  const again = run(root);
  assert.equal(again.exitCode, 0);
  assert.ok(again.stdout.includes("6 skills checked; 0 files updated."));
  assert.equal(await readFile(shared, "utf8"), snapshot);
  assert.equal(run(root, "--check").exitCode, 0);
});

test("keeps instructions, comments, metadata, and CRLF line endings", async () => {
  const root = await home();
  const manifest = await skill(join(root, ".agents/skills/sample"),
    'name: sample\n# Keep this comment\ndescription: |\n  שלום\n  policy: stays in the description\ndisable-model-invocation: false # keep\n', "\r\n");
  const metadata = join(dirname(manifest), "agents/openai.yaml");
  await mkdir(dirname(metadata));
  await writeFile(metadata, 'interface:\r\n  display_name: "שלום"\r\npolicy:\r\n  products: [CODEX]\r\n  allow_implicit_invocation: true # keep\r\ndependencies:\r\n  tools: []\r\n');
  assert.equal(run(root).exitCode, 0);
  assert.deepEqual(await flags(manifest), { disabled: true, implicit: false });
  const text = await readFile(manifest, "utf8");
  assert.ok(text.includes("# Keep this comment\r\n"));
  assert.ok(text.includes("disable-model-invocation: true # keep\r\n"));
  assert.ok(text.endsWith("---\r\n\r\n# Instructions\r\nKeep this body unchanged.\r\n"));
  const document = parseDocument(await readFile(metadata, "utf8"));
  assert.deepEqual(document.toJS(), {
    interface: { display_name: "שלום" },
    policy: { products: ["CODEX"], allow_implicit_invocation: false },
    dependencies: { tools: [] },
  });
});

test("supports flow mappings and explicit roots without touching other skills", async () => {
  const root = await home();
  const untouched = await skill(join(root, ".agents/skills/untouched"));
  const before = await readFile(untouched, "utf8");
  const manifest = await skill(join(root, "separate/skill"), "{name: sample, description: Sample}\n");
  const metadata = join(dirname(manifest), "agents/openai.yaml");
  await mkdir(dirname(metadata));
  await writeFile(metadata, "{policy: {products: [CODEX]}, interface: {display_name: Sample}}\n");
  assert.equal(run(root, manifest).exitCode, 0);
  assert.deepEqual(await flags(manifest), { disabled: true, implicit: false });
  assert.equal(await readFile(untouched, "utf8"), before);
  assert.equal(run(root, "--check", manifest).exitCode, 0);
});

test("preflights invalid YAML and duplicate keys before changing any file", async () => {
  const root = await home();
  const valid = await skill(join(root, ".agents/skills/a-valid"));
  const invalid = await skill(join(root, ".agents/skills/z-invalid"));
  const before = await readFile(valid, "utf8");
  for (const frontmatter of ["name: [broken\n", "name: one\nname: two\n"]) {
    await writeFile(invalid, `---\n${frontmatter}---\nBody\n`);
    const result = run(root);
    assert.equal(result.exitCode, 1);
    assert.ok(result.stderr.includes(invalid));
    assert.equal(await readFile(valid, "utf8"), before);
  }
  assert.equal(run(root, join(root, "missing")).exitCode, 1);
});

test("bin command works through a directory symlink from another working directory", async () => {
  const root = await home();
  const manifest = await skill(join(root, "a skill with spaces"));
  const linkedBin = join(root, "linked-bin");
  await symlink(dirname(command), linkedBin);
  const result = spawnSync(join(linkedBin, "skills-explicit"), [manifest], { cwd: tmpdir(), encoding: "utf8" });
  assert.ifError(result.error);
  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(await flags(manifest), { disabled: true, implicit: false });
});
