# Activation readiness — 26 September 2026

This folder is ready to become the source for the daily shell, Git configuration,
CLI helpers and prompt on this Mac. A new `./setup install` command now handles the automatic new-Mac stages; see
[NEW-MAC.md](NEW-MAC.md) and [the machine audit](MACHINE-AUDIT.md). It still needs
manual account/key/permission restoration.
The full core profile has not yet been linked; only the previously approved live
navigation, prompt and helper changes are active.

## Verified

- `./setup check` passes: syntax/data, isolated linking, conflict preflight,
  backups/restore, profile isolation, symlink boundaries and guide generation.
- The new `.zshrc` starts in an interactive terminal with no startup errors when
  TERM is set to a normal terminal type. VS Code is the default editor, `j` maps
  to zoxide, `mkcd` and package-script helpers exist, and this repo's bin is first.
- All four expected existing shell plugin entry points are present.
- All 124 source-inventory destinations exist. All original user bin files have
  a corresponding file in the new bin directory. Historical/private source is
  archived, not necessarily enabled or distributed through Git.
- Default core linking leaves live VS Code settings alone.

## Remaining boundaries

- `~/.bin`, `.npmrc`, Vim/Git support files and Oh My Zsh custom links still refer
  to `~/dotfiles`. Core linking replaces some, but not all, of these. Keep the old
  directory until a separate retirement pass moves remaining live dependencies.
  In particular, do not replace the credential-bearing npm config with the
  sanitized optional npm profile without preserving local authentication.
- Raycast current settings require Cloud Sync or a fresh export on a new Mac.
  Register the new repo's `raycast/scripts/quick open` and `raycast/scripts/custom`
  directories when moving away from the old script paths.
- App preferences, permissions, accounts, signing keys and private credentials
  are not fully restored by the dotfiles link command. Homerow hotkeys are
  documented snapshots, not automatically applied app preferences.
- The package check now uses `--no-upgrade`, matching installation behavior.
  Homebrew reports missing formulae gnupg, lazygit, pipx, tmux and trash. However,
  this Mac already has usable gpg and trash commands outside those formulae.
  lazygit, pipx and tmux are absent from PATH. They do not block core shell linking.
  Homebrew also reports stale circular dependency metadata for libtiff/webp;
  no package removal or repair was performed during this audit.
- Optional Schnitz Neovim still needs its vim profile linked; first launch
  downloads its plugin manager/plugins. Optional tmux requires its package and TPM.
- New-Mac installation and every historical helper's external service integration
  have not been exercised end to end.
- Changes remain uncommitted. `.private/` is ignored and does not travel with a clone.

## Activate core when ready

```sh
cd /Users/nirtamir/dev/work/dotfiles-2
./setup plan
./setup link --replace
```

The link command backs up conflicts and prints its restore command. Open a new
Warp tab afterwards. Avoid the `all` profile here: it also opts into replacing
VS Code and npm files. Package installation, optional profiles and macOS defaults
remain separate operations.
