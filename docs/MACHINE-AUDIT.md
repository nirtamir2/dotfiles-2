# Current Mac configuration audit — 26 September 2026

There were real restore gaps beyond the original `~/dotfiles` contents. This audit
used current file locations, selected preference keys and the already verified
shortcut inventory. It did not treat every installed app as a daily dependency.
No new-Mac install or live settings restore was run on this computer.

| Area | Found on this Mac | What is now handled |
| --- | --- | --- |
| Login environment | `.zprofile` initializes Homebrew and pyenv; `.zshenv` loads Rust/Rover/Vite+ | Portable, guarded versions are in the core link manifest. Optional runtime installers still need separate installation. |
| Warp | `.warp/settings.toml`, Classic Vivid theme, Hack 18pt, vertical tabs, 110% zoom | Reviewed preferences and the exact selected theme are saved; the installer seeds missing files with the destination home path. No session DB, agent permissions, account or MCP data copied. |
| Homerow | Hyper+H hints, Hyper+J scroll, arrow scrolling, launch-at-login | Reviewed preference keys are captured and restored while the app is closed; Accessibility and login-item approval remain manual. |
| Zappy | Selection/window shortcuts, capture-mode keys, MP4/high quality and UI preferences | 17 reviewed keys, including encoded shortcut values, are captured without tokens, identity or captured images/history. App sign-in and Screen Recording remain manual. |
| Fonts | Warp uses Hack; current coding profile uses JetBrains Mono | Added both fonts to the daily package manifest. |
| Daily apps | Homerow/Zappy/Chrome/Obsidian were outside the automatic core | Added a daily group. Default install includes core + daily + the entire existing extras list, per user preference. |
| GitHub CLI | HTTPS preference and `gh co` alias; gh-dash layout | Non-authentication configuration captured and seeded if absent. `gh auth login` remains manual; gh-dash itself is optional. |
| GPG | Default signing key ID and agent cache timing | Config files are seeded without overwriting existing ones, with private filesystem permissions. Secret keys and owner trust must be transferred securely. |
| VS Code | Default/Home/Work/Cursor Default snapshots already captured | Fresh installs now get the user's current Cursor Default settings as the default profile plus extensions. Existing VS Code config is preserved. Named profile exports remain available. |
| macOS | Dock/Finder/typing/keyboard/status-bar/screenshot preferences | A reviewed JSON allowlist is applied with native `defaults`, with selective backups. Most YAML is historical source material; `zoom.yaml` and `dictation.yaml` provide current optional restores. |
| Dictation (30 September follow-up) | Built-in macOS Dictation enabled; Right Command twice; US English and Hebrew; Automatic microphone | Enablement, languages and shortcut 164 are included in the native restore, with a matching optional `macos-defaults/dictation.yaml`. Shortcut apply/restore preserves other entries. Microphone selection and macOS speech asset downloads need new-Mac verification. |
| Native screen zoom (verified 30 September 2026) | Right Ctrl + mouse wheel; Accessibility → Zoom has scroll gesture enabled, modifier Control, style Full Screen | Gesture toggle and both saved Control modifier masks added to the active JSON allowlist and `macos-defaults/zoom.yaml`. Install/defaults applies the keys with backups; verify Full Screen style after restore. |
| Raycast | Native Hyper, 21 global command hotkeys and launcher documented; settings DB encrypted | Full settings export/Cloud Sync is still needed. Script folders must be registered. The installer does not reconstruct encrypted app databases or accounts. |
| SSH | `.ssh/config` consists of Include directives | Securely transfer the config AND referenced files/agent setup. The public dotfiles repo does not receive host/account details or keys. |
| npm | Live `.npmrc` still links to the old repository and contains authentication | Keep the old path until authentication is moved to a private local file. New-Mac installer does not apply the sanitized optional npm profile over credentials. |
| Navigation history | Autojump data was already merged into zoxide on this Mac | New Mac starts with a fresh learning database unless history is transferred privately. History is not tracked. |
| Services | LaunchAgents for Borders, Syncthing, Watchman and older tools | Do not copy machine-specific LaunchAgents. Borders has no separate config in the checked default locations; its launch arguments use defaults. Review and explicitly enable required services. |
| Yarn | Old update timestamp; Console Ninja plugin at an absolute user path | Not copied. Let the extension/tool recreate its own integration on the new machine. |
| Other configs | Existing fish, NvChad/nvim, AeroSpace and various agent/service configs | Not assumed active or safe to copy wholesale. Fish/AeroSpace were not chosen for this setup; current nvim remains separate from optional schnizvim. Review agent/MCP settings privately. |

## Useful details to review

- Warp's current Open File action names **WebStorm**, even though VS Code is your
  preferred editor. The portable Warp snapshot preserves that setting rather than
  silently changing it. The full extras list installs WebStorm; a minimal install
  should choose VS Code in Warp's UI if needed.
- Warp's privacy preferences disable telemetry and crash reporting; those reviewed
  choices are included. Its agent policies are not transplanted to a new machine.
- Zappy's current saved video setting is **high**, MP4. The guide's preference for
  QuickTime describes your workflow, not a claim that Zappy is configured to low.
- Shottr remains optional/installed pending your removal decision. It is included
  when installing the existing extras list, as requested; edit that manifest if
  you decide to retire it.
- Core linking does not retarget every old symlink. `.bin`, npm and legacy Oh My
  Zsh custom links should be audited before deleting the old checkout. `doctor`
  lists known direct references without reading credentials.

## Not covered by ordinary dotfiles

Signing keys, SSH/npm tokens, keychain passwords, application accounts/licenses,
macOS privacy grants, Raycast's full export, browser sync, Obsidian vault data,
projects, local databases, Syncthing data and private agent configs. The installer
writes a concrete checklist for these; it does not claim to reproduce them.

The single entry point and recovery instructions are in [NEW-MAC.md](NEW-MAC.md).
The current work is uncommitted, so the remote repository is not yet a copy of
this working folder. No commit or push was performed.
