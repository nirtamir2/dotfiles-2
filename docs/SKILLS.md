# Verify skill invocation settings

Custom skills live in [nirtamir2/agent-skills](https://github.com/nirtamir2/agent-skills),
including the Twitter writing skill. The personal repository is private; authenticate
to GitHub before installing it. Its regular install command is in `packages/skills.txt`.
Only authored custom skills and their dependencies live there. Third-party skills,
including pstack and its Poteto Mode skill, are installed directly from upstream
using their own commands in `packages/skills.txt`. This dotfiles repository keeps
the installation list and the invocation-settings command.

The Skills CLI manages installed copies under `~/.agents/skills` and links them to
the selected agents. Keep that installed directory separate from your custom-skill
checkout so installation, updates, and policy enforcement cannot change source
files. No submodules or vendored third-party skills are needed.

## Install personal skills

The personal Git checkout lives at `~/dev/work/agent-skills`. Restore and install it with:

```sh
./setup agent-skills
```

This clones the private repository if the checkout is missing, then installs its
current contents globally for Codex, Claude Code, and Cursor. An existing checkout
is used as-is, including uncommitted skill edits. The command installs the Twitter
counter's pinned dependencies in the installed copy and checks explicit invocation
settings. It can be rerun after editing or pulling the checkout. GitHub authentication
is needed for the initial clone; Node, npm, npx, pnpm, and Git must be available.

Start a new agent session and use `$tweet` or `$project-start` in Codex, or `/tweet`
or `/project-start` in Claude Code and Cursor. Local-path installations are refreshed
with `./setup agent-skills`. To track published updates with `npx skills update --global`,
use the GitHub install
command in `packages/skills.txt` instead.

Install skills using the usual commands in `packages/skills.txt`. At the end,
run the JavaScript script to check all discovered skills and fix their settings:

```sh
pnpm --dir bootstrap/skills install --frozen-lockfile
./bin/skills-explicit
```

`./setup install` installs the script's dependencies normally and runs it as its
last stage. Once dotfiles are linked, run `skills-explicit` from any directory.
`./setup skills` runs the same command. The JavaScript implementation, package,
lockfile, and tests are isolated in `bootstrap/skills/`. The package contains only
the YAML dependency. Node and pnpm come from the regular Node setup.
If you pass `--skip-node`, they must already be available on your shell path.

The script sets the documented invocation controls:

| Tool | File within each skill | Setting | Explicit invocation |
| --- | --- | --- | --- |
| [Claude Code](https://code.claude.com/docs/en/skills#control-who-invokes-a-skill) and [Cursor](https://cursor.com/docs/skills) | `SKILL.md` frontmatter | `disable-model-invocation: true` | `/skill-name` |
| [Codex](https://learn.chatgpt.com/docs/build-skills#optional-metadata) | `agents/openai.yaml` | `policy.allow_implicit_invocation: false` | `$skill-name` |

It scans the user and current project `.agents/skills`, `.codex/skills`,
`.claude/skills`, and `.cursor/skills` directories, including bundled `.system`
skills. It also scans user plugin caches in `.codex/plugins/cache`,
`.claude/plugins/cache`, and `.cursor/plugins/cache`. Symlinks are followed and
each real skill is checked once. Missing default directories are skipped.

Instructions, comments, and other metadata are preserved. YAML formatting can
change in files that need an update. Invalid YAML fails before any files are
changed. A second run leaves correctly configured files untouched.

To verify without writing, use `--check`. It exits with status 1 if settings need
fixing or a file cannot be processed:

```sh
skills-explicit --check
```

To include another project's skills, use `--project DIR`. To scan only particular
skill directories or `SKILL.md` files, pass those paths directly:

```sh
skills-explicit --project /path/to/project
skills-explicit /path/to/agent-skills/skills
```

Regular skill or plugin updates can replace these settings. Run the script again
after installing or updating skills.

To update globally installed skills from their recorded sources, then reapply and
verify the invocation policy:

```sh
npx skills update --global
skills-explicit
skills-explicit --check
```

Maintain your custom skills by editing, committing, and pushing their repository,
then reinstalling it with the command in `packages/skills.txt`. Make lasting changes
to third-party skills in a fork and install that fork instead of editing installed
copies that an update will replace.
