# Nir's dotfiles

Your tools and current Mac settings, organized around Schnitz's `.config/`, `bin/`,
`bootstrap/`, and declarative package layout. VS Code remains the default editor;
Raycast remains the launcher and window manager. Oh My Zsh, Starship, fnm, pnpm,
McFly, zoxide, your Git vocabulary and custom scripts are retained.
Use `j name` or `z name` to jump; `ji name` or `zi name` opens an fzf chooser.
Warp is the primary terminal; Ghostty is optional. Fig and iTerm are retired.
The compact Starship prompt shows directory/branch and command duration.
`mkcd "parent/new project"` creates a directory and enters it.

**[Open the local tools & shortcuts guide](guide/index.html)** — or run `./setup guide`.
It includes 21 verified Raycast command hotkeys, the launcher shortcut, Homerow,
VS Code profiles, terminal workflows, optional Neovim/tmux, and installed packages.

## New Mac: one command

```sh
./setup install --dry-run       # preview only
./setup install                 # install core + daily + full extras, then configure
```

The new-Mac installer bootstraps Homebrew/Python, shell plugins, Node/pnpm,
backed-up dotfile links, a fresh VS Code baseline, and reviewed desktop settings.
Existing VS Code/Warp files stay intact. It saves a log and a manual-steps report.
Use `--minimal` to skip extras; `./setup install --help` lists the other options.

Copy this working checkout to the new Mac first: uncommitted changes and ignored
private exports are not available through a fresh Git clone. Account logins,
signing keys and macOS permissions require separate restoration.

- [New-Mac instructions](docs/NEW-MAC.md)
- [Current-Mac configuration audit](docs/MACHINE-AUDIT.md)
- `./setup doctor`: show remaining restore gaps without changing settings.

## Start here

```sh
./setup                         # help only; no changes
./setup check                   # offline validation, using a disposable home
./setup plan                    # preview core links against this Mac
./setup link --replace          # back up conflicts, then link the core config
```

The complete repository has **not** been linked on your Mac. The approved navigation
cleanup has been applied to your live shell: `j` now uses zoxide, with autojump
history imported; Fig and iTerm startup hooks are removed. New terminal tabs pick
up those changes. The approved compact prompt and `mkcd` helper are also active
for new shells; VS Code and macOS screenshot settings are unchanged. Your
original `~/dotfiles` remains in place; its keyboard instructions now point to Raycast. Review `plan` before linking. Existing
files and symlinks are backed up under `~/.local/state/dotfiles/backups/`; the
link command prints the exact restore command. A plain `./setup link` refuses
conflicts without changing any files. Repeated linking is a no-op.

The core profile links shell/Git config, your original Vim config, Git identity
includes and CLI helpers. VS Code files are excluded from the core profile. It links this repo as `~/.dotfiles`; the shell adds its `bin/` to PATH.
It does not replace `~/bin`, your current `nvim` config, Raycast settings, terminal
preferences, or keyboard mappings.
Do not move this repository after linking; restore first or relink from its new path.

## Install the tools you want

Individual commands require Homebrew/Python where applicable. `./setup install`
bootstraps Homebrew and its declared Python runtime; Apple Command Line Tools
installation may need you to finish its dialog and rerun.

```sh
./bootstrap/homebrew                 # check for Homebrew; print vendor instructions
./setup packages                     # report missing core packages
./setup packages core --apply        # install missing; no upgrades or removals
./setup packages daily --apply       # daily apps
./setup shell                        # install missing Oh My Zsh and plugins
./setup node                         # Node LTS and pnpm
./setup node --globals               # also install the historical global Node CLIs
./setup vscode                       # install default-profile VS Code extensions
./setup packages extras --apply      # additional tools from your old installers
./setup packages work --apply        # Slack and Teams
./setup packages mas --apply         # saved Mac App Store apps; requires mas/login
./setup defaults                     # apply preferences/macos.json with per-key backups
./setup desktop                      # preview portable app files and preferences
./setup desktop --apply              # seed files and apply macOS/Homerow/Zappy preferences
```

T3 Code is declared as `cask "t3-code"` in `packages/Brewfile.extras`, alongside
Codex. `./setup install` and `./setup packages extras --apply` install it
automatically through Homebrew; `./setup install --minimal` skips it.

Native screen zoom (**Right Ctrl + mouse wheel**) is included in `./setup install`
and `./setup defaults`. You can also use the installed `macos-defaults` tool with
`macos-defaults apply macos-defaults/zoom.yaml` (preview with `--dry-run`). See
[Zoom restore instructions](docs/NEW-MAC.md#native-screen-zoom-right-ctrl--wheel)
for the settings location and verification steps.

Everyday dictation uses **built-in macOS Dictation**: press **Right Command
twice** to start or stop. US English and Hebrew are enabled, with automatic
microphone selection. `./setup install` and `./setup defaults` restore the saved
Dictation settings and shortcut. You can also run
`macos-defaults apply macos-defaults/dictation.yaml` (preview with `--dry-run`).
See [Dictation restore instructions](docs/NEW-MAC.md#native-macos-dictation)
for new-Mac verification.

`packages/Brewfile.installed` is a machine snapshot, including dependencies; it
is not an automatic install target. `packages/availability-review.json` and
`packages/legacy-review.txt` record declarations that need manual attention.
Unavailable/disabled core-catalog entries are commented out in extras. Third-party
tap installation and account-dependent commands have not been exercised.

`packages/skills.txt` preserves your requested skill-install commands for manual
use. Python's `git-smart-squash`, Go's `qrcp`, Rust, custom fonts,
and manual apps have restore instructions in [docs/MIGRATION.md](docs/MIGRATION.md).

## Optional workflows

```sh
./setup plan --profile vim
./setup link --profile vim
./bin/schnizvim                   # isolated NVIM_APPNAME=schnizvim

./setup plan --profile tmux
./setup link --profile tmux

# Only when you deliberately want to replace editor settings:
./setup plan --profile vscode
./setup link --profile vscode --replace
```

Profiles: `core`, `vim`, `tmux`, `vscode`, `npm`, or `all`. The npm profile links
only the sanitized npm preferences; it never imports a saved auth token. Merge
your credentials locally before opting in. `all` includes this optional npm
replacement and VS Code settings, so review its plan carefully.

The link manager refuses to traverse a symlinked parent directory. Existing
unrelated configuration directories stay intact.

Schnitz's Neovim first launch downloads lazy.nvim and plugins. His lockfile is
retained. LSP servers and optional integrations may need setup. For tmux, install
TPM in `~/.tmux/plugins/tpm` if missing, then press `Ctrl-S`, `Shift-I` inside tmux.
Unused upstream alternatives, personal integrations and four bundled language-server
binaries were removed from the maintained tree. See [the cleanup report](docs/CLEANUP.md).

## VS Code and Raycast

Default and all three live VS Code profiles are preserved. Import `Home.code-profile`,
`Work.code-profile`, or `Cursor Default.code-profile` from `editors/vscode/` using
VS Code's Import Profile command on a new Mac. Existing local profile IDs are
resolved by name only when opting into `--profile vscode`; new profile IDs are never fabricated.
Your current live settings, shortcuts and snippets have not been modified.

Raycast scripts are in `raycast/scripts/quick open/` and `raycast/scripts/custom/`.
Register both directories in Raycast's Script Commands settings after switching.
`raycast/my-stuff/` retains your custom extension source and lockfile. Its existing
external endpoints and project-specific configuration still need your accounts.

Right Option → Hyper is handled by Raycast itself (Keyboard → Hyper Key, Include
Shift enabled). Karabiner is unnecessary for this mapping and has been removed
from managed configuration and installation.

Live Raycast hotkeys were read from its Settings UI on 2026-09-26. Its current
settings databases are encrypted; they were not modified or copied. Restore a
new Mac through Cloud Sync or a fresh Raycast export. The old 2025 export is in
`.private/original-dotfiles/raycast/` and is **not** a current settings backup.

## Local overrides and backups

- `~/.zshrc.local`: private environment variables and machine-specific additions.
- `~/.gitconfig.local`: private Git overrides, included after the shared defaults.
- `.private/`: Git-ignored original source archive and migration metadata. It can
  contain credentials and is not transferred by cloning this repository.
- `docs/source-inventory.json`: original authored-file hashes and migration destinations.
- [docs/MIGRATION.md](docs/MIGRATION.md): decisions, exceptions and restore notes.

Never serve the whole repository as a website. Open `guide/index.html` directly,
or serve only `guide/` with `python3 -m http.server 8768 --bind 127.0.0.1 --directory guide`.
Rebuild with `python3 guide/build.py` after editing reviewed shortcut/inventory data.

## Validation

`./setup check` validates shell syntax, Brewfile syntax and configuration data,
then tests guide generation/navigation, Homebrew selector cancellation, dry runs,
conflict refusal, idempotent linking, backup restoration,
changed-file protection, profile discovery and symlink boundaries in a temporary
home. CI runs those checks without installing packages or altering runner settings.

Infrastructure references: [Homebrew Bundle](https://docs.brew.sh/Brew-Bundle-and-Brewfile),
[Neovim startup and NVIM_APPNAME](https://neovim.io/doc/user/starting/).

Based on [Schnitz's dotfiles](https://github.com/Schniz/dotfiles) and Nir's existing
Stefan Judis-derived setup. The upstream license is retained.
