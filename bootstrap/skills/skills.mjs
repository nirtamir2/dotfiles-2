#!/usr/bin/env node
import { mkdir, readFile, readdir, realpath, stat, writeFile } from "node:fs/promises";
import { homedir } from "node:os";
import { basename, dirname, join, resolve } from "node:path";
import { parseArgs } from "node:util";
import { isMap, parseDocument } from "yaml";

const skillRoots = [".agents/skills", ".codex/skills", ".claude/skills", ".cursor/skills"];
const pluginRoots = [".codex/plugins/cache", ".claude/plugins/cache", ".cursor/plugins/cache"];
const skipDirectories = new Set([".git", "node_modules", "__pycache__"]);

async function readIfPresent(path) {
  try {
    return await readFile(path, "utf8");
  } catch (error) {
    if (error.code === "ENOENT") return null;
    throw error;
  }
}

function parseMapping(text) {
  const document = parseDocument(text, { stringKeys: true });
  if (document.errors.length) throw new Error(document.errors.map(error => error.message).join("\n"));
  if (!isMap(document.contents)) throw new Error("Expected a YAML mapping");
  return document;
}

function serialize(document, original) {
  const text = document.toString({ lineWidth: 0 });
  return original.includes("\r\n") ? text.replaceAll("\n", "\r\n") : text;
}

async function planSkill(skill) {
  const original = await readFile(skill, "utf8");
  const match = /^---\r?\n([\s\S]*?)^---[^\S\r\n]*(?:\r?\n|$)/m.exec(original);
  const frontmatter = match?.[1];
  if (!match || match.index !== 0 || frontmatter === undefined) {
    throw new Error("SKILL.md needs YAML frontmatter between --- lines");
  }
  const document = parseMapping(frontmatter);
  const updates = [];
  if (document.get("disable-model-invocation") !== true) {
    document.set("disable-model-invocation", true);
    const start = original.indexOf("\n") + 1;
    updates.push({
      path: skill,
      before: original,
      after: original.slice(0, start) + serialize(document, frontmatter) + original.slice(start + frontmatter.length),
    });
  }

  const metadataPath = join(dirname(skill), "agents/openai.yaml");
  const before = await readIfPresent(metadataPath);
  const metadata = before?.trim() ? parseMapping(before) : parseMapping("{}\n");
  if (metadata.has("policy") && !isMap(metadata.get("policy", true))) {
    throw new Error("policy must be a YAML mapping");
  }
  if (metadata.getIn(["policy", "allow_implicit_invocation"]) !== false) {
    metadata.setIn(["policy", "allow_implicit_invocation"], false);
    updates.push({ path: metadataPath, before, after: serialize(metadata, before ?? "") });
  }
  return updates;
}

async function discover(path, visited, skills) {
  const actual = await realpath(path);
  if (visited.has(actual)) return;
  visited.add(actual);
  const info = await stat(actual);
  if (info.isFile()) {
    if (basename(actual) !== "SKILL.md") throw new Error(`Expected SKILL.md: ${path}`);
    skills.add(actual);
    return;
  }
  if (!info.isDirectory()) return;
  const entries = await readdir(actual, { withFileTypes: true });
  if (entries.some(entry => entry.name === "SKILL.md")) {
    skills.add(await realpath(join(actual, "SKILL.md")));
    return;
  }
  for (const entry of entries.sort((a, b) => a.name.localeCompare(b.name))) {
    if (skipDirectories.has(entry.name)) continue;
    if (entry.isDirectory() || entry.isSymbolicLink()) {
      await discover(join(actual, entry.name), visited, skills);
    }
  }
}

async function existingRoots(roots) {
  const existing = [];
  for (const path of roots) {
    try {
      await stat(path);
      existing.push(path);
    } catch (error) {
      if (error.code !== "ENOENT") throw error;
    }
  }
  return existing;
}

async function main() {
  const { values, positionals } = parseArgs({
    args: process.argv.slice(2),
    allowPositionals: true,
    options: {
      check: { type: "boolean", default: false },
      home: { type: "string", default: homedir() },
      project: { type: "string", default: process.cwd() },
      help: { type: "boolean", short: "h", default: false },
    },
  });
  if (values.help) {
    process.stdout.write("Usage: skills-explicit [--check] [--project DIR] [SKILL_ROOT ...]\nChecks all discovered skills and fixes invocation settings by default.\n");
    return 0;
  }
  const roots = positionals.length ? positionals.map(path => resolve(path)) : await existingRoots([
    ...skillRoots.map(path => join(values.home, path)),
    ...pluginRoots.map(path => join(values.home, path)),
    ...skillRoots.map(path => join(values.project, path)),
  ]);
  const skills = new Set();
  const visited = new Set();
  for (const root of roots) await discover(root, visited, skills);
  const updates = [];
  for (const skill of [...skills].sort()) {
    try {
      updates.push(...await planSkill(skill));
    } catch (error) {
      throw new Error(`${skill}: ${error.message}`);
    }
  }
  for (const update of updates) {
    if (!values.check) {
      if (await readIfPresent(update.path) !== update.before) throw new Error(`File changed during scan: ${update.path}`);
      await mkdir(dirname(update.path), { recursive: true });
      await writeFile(update.path, update.after);
    }
    process.stdout.write(`${values.check ? "needs update" : "updated"} ${update.path}\n`);
  }
  process.stdout.write(`${skills.size} skills checked; ${updates.length} files ${values.check ? "need updating" : "updated"}.\n`);
  return values.check && updates.length ? 1 : 0;
}

try {
  process.exitCode = await main();
} catch (error) {
  process.stderr.write(`Error: ${error.message}\n`);
  process.exitCode = 1;
}
