# Cleanup — 26 September 2026

No commits were created. Your live VS Code settings, shortcuts and snippets are
unchanged. Core linking now excludes VS Code; restoring saved editor files
requires `--profile vscode` (or the explicitly inclusive `all` profile).

## Removed from the maintained setup

| Removed | Reason | Recovery |
| --- | --- | --- |
| Karabiner config, `keyboard` link profile and core package declaration | You said you do not use it. Raycast's live Keyboard settings already map Right Option to Hyper, including Shift. | `.private/retired-2026-09-26/.config/karabiner/` |
| `optional/schniz/` | Keeping a second user's complete configuration as an alternative duplicates the setup and makes it harder to know what to edit. This included his terminal/window-manager configs, keyboard mapping, Git identity, old editor configs, OpenCode integration, old exports and personal service scripts. | `.private/retired-2026-09-26/optional/schniz/` and upstream Git history |
| `bin/SourceKittenDaemon`, `langserver-swift`, `reason-language-server`, `scry` | Four bundled Intel Mach-O binaries, about 36 MiB total, with no references in the maintained configuration. These should not be copied onto your normal PATH just because upstream tracked them. | `.private/retired-2026-09-26/bin/` |

Schnitz's requested modern Neovim setup remains in `.config/schnizvim/`.
His portable helpers and optional tmux config remain. This cleanup does not
uninstall macOS applications or delete the separate Karabiner source repository.
The installed-app inventory still lists Karabiner because it remains installed;
that inventory is evidence of presence, not an install plan or list of daily tools.

The old `~/dotfiles/README.md` now describes Raycast's native Hyper key instead of
instructing you to install Karabiner, and records Option-Space as the launcher.
The old folder remains in place pending clarification of whether you meant to
retire it entirely. Existing shell and Vim symlinks still depend on it.

## What I would improve next

| Item | Concrete problem | Current decision |
| --- | --- | --- |
| `gcr` and the related commit/reset functions | They commit, revert twice, then reset; intermediate failures do not stop the sequence. They also skip hooks. This is too much hidden state-changing behavior for a short alias. | Kept because they are your own workflow. Confirm whether you use them before rewriting or removing. |
| `git-force-pull` and `git-legacy` | They perform hard resets or broad history rewrites; `git-legacy` also cleans untracked files during its rebase loop. | Kept and documented; do not run as migration checks. |
| `freewifi` / `hack_the_space` | Old network-interface mutation helpers. The old alias even invokes OpenSSL when the aliases file loads. | `freewifi` was excluded from the new setup; the function and old repo version remain pending confirmation. |
| autojump + zoxide | Two directory-learning tools to maintain for similar jobs. | Resolved: zoxide handles `j`/`z` and `ji`/`zi`; old history merged once. |
| Ghostty/iTerm + Warp | User confirmed Warp and retired iTerm. | Warp core; Ghostty optional; iTerm config and shell/install integration archived or removed in both repos and the live shell. |
| Fig setup, old installer scripts and old app declarations | The old repo mixes current preferences with historical installers and installation notes. Running the whole thing again is not a reproducible restore. | Fig install instructions and shell hooks removed from old repo/live shell too. New setup uses reviewed package groups; original source stays private. |

Borders and Homerow are running and were retained. Installed apps and Raycast
extensions were not automatically classified as unused. Portable VS Code exports
retain your preferences; account-like metadata is excluded from public snapshots.

## Verification

`./setup check` passes, including default-profile editor isolation, explicit VS
Code profile linking, backup/restore, symlink boundaries and guide generation.
All 14 live VS Code settings/keybindings/snippet files recorded before cleanup
still match their SHA-256 hashes. All source-inventory destinations still exist.
`git diff --check` passes. Changes in both repositories are uncommitted.

## Navigation and terminal follow-up

- `shell/navigation.zsh` initializes zoxide once after shell completion setup;
  `j` aliases `z`, and `ji` aliases `zi`. Autojump is removed from the core Brewfile
  and Oh My Zsh plugin list. The old installer now installs zoxide instead.
- Live `~/.zshrc` and `~/dotfiles/config/home/.zshrc` receive the same targeted
  navigation change and removal of Fig/iTerm hooks. Other live shell preferences
  remain as before; this does not activate the full replacement shell.
- Existing autojump history was merged into zoxide using the installed version's
  `zoxide import --from autojump --merge` interface. Original histories and changed
  live/old-repo files are backed up in `.private/navigation-terminal-20260926-163656/`.
  Nothing imports history on every shell startup.
- `iterm/` and the old repo's iTerm plist are archived there. The source inventory
  points to the preserved original export. Historical installed inventories still
  list installed apps; no app uninstall command was run.
- Warp stays the Raycast Hyper+T target. Ghostty remains optional in extras;
  Herdr is discussed in the guide as an agent-workspace experiment, not installed.
- VS Code files remain untouched. Both repositories remain uncommitted.

## Compact prompt and capture guide follow-up

Adopted Schnitz's compact Starship layout (directory, Git branch, prompt character,
right-hand command duration) with Starship's default colors and character. The
configuration lives in `.config/starship.toml`, linked as `~/.starship.toml` and
selected through `STARSHIP_CONFIG`; the core link manifest includes it. The old
repo has a matching `config/home/.starship.toml` for its existing link layout.

Added `mkcd` to both repos' shell functions. It accepts one quoted path, creates
parents, handles spaces/leading dashes, and only changes directory if creation
succeeds. The old functions file is already linked into the live shell. Open a
new Warp tab for both changes. Original live/old-repo files and link details are
in `.private/prompt-capture-20260926-164838/`.

The guide now records native region screenshots: Control-Command-Shift-4 copies
to clipboard; Command-Shift-4 saves to `/tmp` (verified from live preferences).
Zappy is the user's confirmed image, GIF and quick-video tool; QuickTime Player
is preferred for better-quality video. Shottr was an earlier naming mix-up;
the former assumption that OBS/CapCut is the daily workflow was removed. No
screenshot preference, hotkey or clipboard content was changed.

## Confirmed capture apps and Homerow

The user confirmed Zappy, not Shottr, for images and quick GIF/video captures.
Shottr is installed and running; Spotlight records a launch today, which does not
establish whether it is used for captures. It remains installed and in the optional
package list pending a removal decision. Its protected preference file could not
be read; no usage counts or capture history were inferred from that file.

Homerow's live `com.superultra.Homerow` preferences were rechecked: Hyper+H shows
clickable hints; Hyper+J starts scrolling, with arrow-key scrolling enabled.
Raycast supplies Hyper through Right Option. The guide and both repos' Homerow
notes now state those mappings explicitly, ahead of the historical screenshots.
