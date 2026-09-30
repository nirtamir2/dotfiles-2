# Set up a new Mac

Copy this complete working checkout to a permanent folder on the new Mac, open
Terminal, and run:

```sh
cd ~/dev/work/dotfiles-2  # or the actual location of your copied checkout
./setup install
```

Use `./setup install --dry-run` to preview the stages without changing anything.
The script includes the full existing extras list by default, as requested.
Nothing has been committed: cloning the remote today will NOT include this work.
Transfer the working folder, or commit/push it yourself when ready. Keep private
archives/exports in a separate secure transfer; they are ignored by Git.

## What the command does

1. Checks macOS and Command Line Tools. If Apple tools are missing, opens their
   installer and stops; finish that installation and rerun the same command.
2. Finds Homebrew or runs its official HTTPS installer, then installs the declared
   Homebrew Python runtime. Homebrew may ask for your administrator password.
3. Installs missing packages from the core, daily and extras Brewfiles, without
   requesting bulk upgrades. Dependencies may still be upgraded by Homebrew.
4. Installs missing Oh My Zsh plugins, Node LTS and pnpm. Node LTS becomes the fnm
   default. The historical global npm collection is a separate option.
5. Links core files, including `.zprofile`, `.zshenv` and the compact prompt, and
   the optional `schnizvim` namespace. Conflicts receive timestamped backups.
6. Seeds a fresh VS Code default profile from your current **Cursor Default**
   settings, keybindings, snippets and extension list. It never overwrites existing
   editor configuration. Home and Work exports remain available for manual import.
7. Seeds missing Warp settings/theme, GitHub CLI/dashboard settings and GPG config
   files. Existing files are preserved. No GPG keys or GitHub login tokens are copied.
8. Applies the reviewed macOS, Homerow and Zappy preference keys with per-key
   backups. Running Homerow/Zappy instances are skipped to avoid overwriting
   in-memory preferences; quit the apps and rerun `./setup desktop --apply` later.
9. Writes a local next-steps report and prints the log location.

The script is rerunnable: installed Homebrew packages and cloned shell plugins
are retained, existing dotfile links are no-ops, existing editor/Warp files are
preserved, and only missing editor extensions are retried. Node LTS may advance
when rerun later. Curated macOS/app preference keys are reapplied on reruns; use
`--skip-preferences` to preserve later customizations. The script does not remove
apps, reset Raycast, start arbitrary background services, or change the login shell.
macOS's usual login shell is zsh; confirm your account uses `/bin/zsh` if customized.

## Options

| Option | Effect |
| --- | --- |
| `--minimal` | Core and confirmed daily apps only; omit extras. |
| `--skip-node` | Preserve existing Node setup. |
| `--skip-vscode` | Skip fresh editor seeding and extension installs. |
| `--skip-preferences` | Skip desktop file seeding and preference writes. |
| `--with-node-globals` | Install the old global npm list; some packages may need accounts or be obsolete. |
| `--with-work` | Add Slack and Teams. |
| `--with-mas` | Add the saved App Store apps; requires App Store sign-in. |
| `--with-tmux` | Link tmux and install missing TPM; Ctrl-S then Shift-I installs its plugins. |

`./setup` alone remains help-only. `./setup link --replace` only activates core
links, without doing the new-Mac installation. `./setup doctor` is a read-only
check; `./setup doctor --report` writes the local checklist.

## Files to edit

- `Brewfile`, `packages/Brewfile.daily`, `packages/Brewfile.extras`: automatic packages.
- `preferences/macos.json`: active native macOS preference allowlist. The old
  `macos-defaults/*.yaml` files are mostly historical migration references;
  `zoom.yaml` and `dictation.yaml` also provide current optional restores with
  that tool. The native restore does not require the third-party tool.
  `macos-defaults/zoom.yaml` is also maintained for direct use with that tool.
- `preferences/desktop/`: reviewed app preferences, Warp template/theme, GitHub
  config and GPG config. Tokens, accounts and app databases are excluded.
- `editors/vscode/profiles/Cursor Default/`: fresh default editor baseline.
- `bootstrap/`: installer and restore helpers.

## Native screen zoom: Right Ctrl + wheel

Hold **Right Ctrl** and scroll the mouse wheel to zoom in or out. In
**System Settings → Accessibility → Zoom**, enable **Use scroll gesture with
modifier keys to zoom**, choose **Control**, and use **Full Screen** style.
macOS selects Control without distinguishing left/right; Right Ctrl is your
preferred key. These controls were verified live on 30 September 2026.

`./setup install` applies the saved scroll-to-zoom toggle and Control modifier
unless `--skip-preferences` is used. To reapply just the curated system settings,
run `./setup defaults`; it creates per-key backups. The toggle is
`com.apple.universalaccess:closeViewScrollWheelToggle`; the Control mask is
`HIDScrollZoomModifierMask = 262144` in both `com.apple.AppleMultitouchTrackpad`
and `com.apple.driver.AppleBluetoothMultitouch.trackpad`, matching this Mac.

To use the installed **macos-defaults** tool directly from this checkout:

```sh
macos-defaults --dry-run apply macos-defaults/zoom.yaml
macos-defaults apply macos-defaults/zoom.yaml
```

The direct tool command does not create the setup preference backup. After
restoring, log out and back in if needed, test **Right Ctrl + wheel**, and confirm
**Full Screen** style in Zoom settings. The saved keys cover the scroll gesture
and modifier; the current full-screen style is documented for verification.

Reference: [Apple’s Zoom settings](https://support.apple.com/guide/mac-help/change-zoom-settings-for-accessibility-mh40579/mac).

## Native macOS Dictation

Your default dictation app is **built-in macOS Dictation**. Press **Right Command
twice** to start or stop. The live settings were verified on 30 September 2026:
Dictation on, **English (United States)** and **Hebrew (Israel)** selected, and
microphone source **Automatic**.

The default `./setup install`, `./setup defaults`, or `./setup desktop --apply`
restore enablement, language selection and the shortcut from
`preferences/macos.json`. Shortcut 164 is merged into `AppleSymbolicHotKeys`,
preserving other shortcuts. Its backup/restore affects only that entry.

You can alternatively use the installed `macos-defaults` tool:

```sh
macos-defaults --dry-run apply macos-defaults/dictation.yaml
macos-defaults apply macos-defaults/dictation.yaml
```

The YAML merges dictionaries; it does not replace the full shortcut table. The
tool keeps its own `.plist.prev` backups rather than the setup preference journal.
After applying, log out and back in if needed and check **System Settings →
Keyboard → Dictation**. Confirm enablement, both languages, **Press Right Command
Key Twice**, and **Automatic** microphone source. macOS handles speech model
downloads and any enablement/permission prompts on the new Mac; models and
device-specific microphone identifiers are not transferred.

See [the dictation workflow](../manual-install/dictation.md) and
`preferences/dictation.json` for the verified reference. Handy and other
dictation apps remain optional alternatives.

## Still required from you on a new Mac

- **Raycast:** fresh export or Cloud Sync; the documented shortcut table is not a
  settings export. Restore extension preferences/accounts and register this repo's
  two script directories. Verify Hyper and launcher shortcuts after import.
- **Private authentication:** SSH includes/agent setup, npm registry tokens, GPG
  signing keys and trust, GitHub login, app accounts and licenses. Your Git config
  signs commits, so restore the matching key before expecting commits to work.
- **Permissions:** Accessibility, Screen Recording and microphone prompts are
  controlled by macOS. They cannot be carried over as ordinary dotfiles.
- **Data:** Obsidian vaults, projects, local databases, Syncthing folders/config,
  browser profiles and optional shell/zoxide history need separate transfer/sync.
- **Optional runtimes/services:** Rust/Rover/Vite+ environment hooks are guarded
  but their installers are not run. Borders and Syncthing may need explicit service
  enablement after review. Do not copy all LaunchAgents blindly.
- **Agent tools:** review private agent/MCP configuration and skills separately.
- **Unavailable packages:** entries already commented out in extras are listed in
  `packages/availability-review.json`; third-party taps may require trust or be
  unavailable. Install failures stop the run and are logged; fix and rerun.

## Backups and failure handling

Logs and reports live in `~/.local/state/dotfiles/` with private permissions.
Core link backups include an exact `./setup restore .../manifest.json` command.
Preference backups have a separate `./setup desktop --restore PATH` command;
this restores only the affected keys, not whole app databases. Quit affected apps
first. Seeded app files are ordinary editable copies, not symlinks to the repository.

Never run the historical installer in `~/dotfiles` as part of this new workflow.
Don't remove that old directory until `./setup doctor` reports that its remaining
live links (especially credential-bearing npm configuration) have been migrated.

## What was tested

Offline tests cover stage plans/options, fresh and existing VS Code behavior,
failed extension reporting, desktop file preservation, selective preference
backups/restore, running-app skips and symlink boundaries. Existing core
link/restore checks also pass. A complete fresh-Mac installation, external tap
availability and app-specific behavior after importing preferences still need a
real new Mac or disposable macOS VM; the destructive install was not run here.

References: [Homebrew installation](https://docs.brew.sh/Installation),
[VS Code CLI](https://code.visualstudio.com/docs/configure/command-line),
[Warp file locations](https://docs.warp.dev/terminal/settings/file-locations).
