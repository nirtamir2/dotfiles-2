# Migration decisions — 26 September 2026

The user requested a merge into this repository, keeping preferred tools and
adopting better infrastructure. They confirmed current Mac settings as the source
of truth, VS Code as the default editor with optional Schnitz Neovim, and a local
web guide. No full-repository links, apps, package installations or macOS defaults were changed.
The subsequent approved cleanup edits the live `.zshrc` for zoxide navigation and
removes Fig/iTerm startup hooks, with backups and a one-time autojump data import.
VS Code is now a separate opt-in link profile; the core setup leaves it alone.

## What was chosen

| Area | Result | Reason |
| --- | --- | --- |
| Layout | Schnitz's `.config/`, `bin/`, `bootstrap/`, Brewfiles | Simple, visible configuration and explicit installation entry points. |
| Link management | Explicit profile manifest with preview, backups and restore | Upstream `stow .` included another user's Git identity, keyboard and window manager; its links script hardcoded `~/Code/dotfiles`. Whole-directory replacement could affect unrelated files. Stow remains installed for independent use. Use `./setup`, not a blanket `stow .`. |
| Packages | Core, extras, work and App Store manifests; installed snapshot | Replaces scattered duplicate imperative installs, forced reinstalls, obsolete flags and automatic service starts. `--no-upgrade` preserves existing versions. No cleanup/uninstall command runs. |
| Editor | Current VS Code Default/Home/Work/Cursor Default | Current profiles contain newer bindings than the old repository. Portable exports omit app storage and account state. |
| Vim | Original `.vimrc`; Schnitz's modern Lua setup under `schnizvim` | Explore with `bin/schnizvim`; no global NVIM_APPNAME and no replacement of current NvChad/nvim. |
| Shell | User's Oh My Zsh and plugin choices | Avoid changing familiar completion/history behavior to Schnitz's zi setup. Startup no longer clones software, initializes fnm twice or spawns npm for NODE_PATH. |
| History | McFly + fzf + user's directory-specific `lc` | Leading-space commands are excluded from custom history too. `lc` fills the prompt for review instead of immediately evaluating the selection. |
| Navigation | zoxide with `j=z` and `ji=zi` | Keep familiar `j`; remove duplicate autojump initialization. Existing autojump history was merged once with a database backup. |
| Git | User aliases, identity files, signing intent and live case-insensitivity | `git co` remains commit. Keep current `gh` credential helper through PATH. Remove stale include paths, Schnitz's signing key and a broken token filter. Add rerere to remember conflict resolutions. |
| Window management | Raycast | User explicitly used Raycast instead of Rectangle/AeroSpace. Schnitz's AeroSpace was removed from the maintained tree. |
| Keyboard | Raycast native Hyper Key | Right Option → Hyper with Shift included, verified in the live UI. Karabiner is unused and removed from managed setup. |
| Terminals | Warp primary; Ghostty optional | User retired iTerm and Fig. Remove iTerm config/startup/install steps; retain Ghostty in extras without imposing Schnitz's tmux bindings. |
| Scripts | User scripts win collisions; portable upstream helpers retained | `gitroot` executable prints a path; user's shell function changes directory. `cdgr` now calls the executable explicitly. `wtfeat` no longer hardcodes Vercel paths or resets an existing branch. |
| Trash | Real macOS Trash CLI | User alias `t` is kept; the prior function moved files into `~/.trash` without safe collision handling. |
| macOS defaults | Curated user YAML plus portable old mac.sh preferences, separate command | Removed serialized Dock application/database state. Old security weakening and OS update commands are not run. |
| Raycast | Current hotkeys documented, original extension/scripts retained | Launcher is Option-Space, not the old README's Command-Space. No import/reset of settings. |

## Source inventory and coverage

`docs/source-inventory.json` records the SHA-256 of each authored file considered
and where its migrated or archived version lives. `.private/original-dotfiles/`
contains byte-for-byte originals, including `.npmrc`, `.my-config`, old profiles,
backup.zip, setup scripts and the historical Raycast export. This private archive
is intentionally ignored by Git; keep an encrypted personal backup for transfer.

Excluded from the source archive: Git internals, node_modules, IDE cache metadata,
Cursor History/workspaceStorage/globalStorage and .DS_Store. These are generated
state, not reproducible configuration; editor history contained credential-like
values. The later cleanup updates `~/dotfiles/README.md` to describe Raycast native Hyper and the current launcher shortcut.

The original manual-install notes, images, custom fonts and Raycast extension
source are retained. Historical note claims about pricing/availability are not
asserted as current in the guide. Empty directories and generated dependencies
need not be copied. Conflicting Schnitz files were initially retained as references, then removed
from the maintained tree during cleanup. The ignored `.private/retired-2026-09-26/`
archive and repository Git history preserve them.

## Remaining manual restore steps

- Raycast: Cloud Sync or a fresh export for current settings. The encrypted local
  databases cannot be read as plain SQLite. The guide contains every assigned
  command hotkey visible under Shortcuts → Hotkey Set (21), plus the launcher.
- Raycast scripts: register both script directories. The custom grammar script
  needs a running local Ollama server and the `phi3` model. `my-stuff` needs its
  existing extension preferences/accounts. No credentials were migrated into Git.
- Terminals: Warp is in the core Brewfile; Ghostty is in extras. iTerm exports
  remain only in private archives. Fig setup and initialization were removed.
- VS Code: import the profile exports on a new machine. Default profile extension
  installation is `./setup vscode`; profile imports carry their own extension IDs.
  Cursor-specific `composerMode.agent` is preserved but may be unavailable in VS Code.
- Git signing: keep your existing GPG keys in your local keyring; public signing
  key IDs and identities are retained. Secret keys are not copied. Ensure `gpg`
  and `gh` are available when using signing and GitHub credentials.
- Python CLI: `pipx install git-smart-squash` restores the `ss` tool without writing
  into Homebrew's managed Python environment.
- Go CLI: after installing Go, `go install github.com/claudiodangelis/qrcp@latest`
  replaces the historical `go get` installation command.
- Rust: install through the official rustup instructions if required. Your old
  Rust script installed the toolchain but listed no additional crates.
- Fonts: retained FiraCodeiScript files under `static/` can be opened in Font Book.
  Install JetBrains Mono for the current VS Code profile if it is missing.
- Skills: `packages/skills.txt` preserves the user's regular install commands.
  Install selected skills as usual, then run `skills-explicit` to verify
  and disable automatic invocation. `./setup install` runs the script at the end.
  See [skill invocation settings](SKILLS.md).
- Work apps and Mac App Store apps are separate opt-in groups; App Store restore
  needs `mas` installed and an authenticated App Store session.
- Missing/disabled Homebrew declarations are listed in `packages/availability-review.json`.
  Tap entries were preserved/qualified from the old scripts and are not guaranteed
  available until checked with their vendor. No alternative app was substituted.

## Guide evidence

- Raycast: live Settings → General and Shortcuts → Hotkey Set on 2026-09-26.
- Hyper Key: live Raycast Settings → Keyboard, verified Right Option and Include Shift.
  An old Karabiner profile contained the same mapping but is not the active mechanism.
- Homerow: installed app bundle `com.superultra.Homerow` and its current preferences.
  An obsolete `com.dexterleng.Homerow` plist reverses H/J; it was not used.
- VS Code: current user files and named profile settings/shortcuts. Removed-binding
  entries are excluded from the guide; command contexts are retained.
- Installed tools: `brew list` and `brew info --json=v2 --installed`, with metadata
  fallback from Homebrew's official formula/cask API. This is a point-in-time
  inventory, not an assertion that every installed package is used daily.
- AltTab/Vimium: historical user setup notes; the guide marks them unverified live.
- Neovim/tmux: actual repository keymap/config definitions, explicitly optional.

## Validation boundaries

Offline checks exercise linking and restore in a temporary home and parse the
changed entry-point shells/configs. The guide is inspected in a local browser.
Package installation, account login, actual macOS defaults application, Raycast
restore and first-time Neovim/plugin downloads are not executed as migration tests.
Preserved legacy scripts retain their original behavior except the documented
portability/cancellation/Trash fixes. Some deliberately rewrite Git history;
retaining them does not make running them a safe validation step.

The guide additionally inventories 75 locally present Raycast extension manifests
and 123 application bundles. Presence alone does not prove that an extension is
enabled or that its account connection still works.
